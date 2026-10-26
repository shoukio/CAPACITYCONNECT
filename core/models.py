from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from accounts.models import Profile


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.CharField(max_length=80)
    summary = models.CharField(max_length=280)
    description = models.TextField()
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )
    duration_hours = models.PositiveSmallIntegerField(default=1)
    enrollment_limit = models.PositiveIntegerField(default=30)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at", "title"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(enrollment_limit__gte=1),
                name="course_enrollment_limit_positive",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "course"
            candidate = base_slug
            suffix = 2
            while Course.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.enrollment_limit < 1:
            raise ValidationError(
                {"enrollment_limit": "Course capacity must be at least one seat."}
            )
        if self.pk and self.enrollment_limit < self.enrollments.count():
            raise ValidationError(
                {
                    "enrollment_limit": (
                        "Capacity cannot be less than the number of learners "
                        "already enrolled."
                    )
                }
            )

    def __str__(self):
        return self.title

    @property
    def current_enrollments(self):
        annotated_count = getattr(self, "current_enrollment_count", None)
        if annotated_count is not None:
            return annotated_count
        return self.enrollments.count()

    @property
    def available_slots(self):
        return max(self.enrollment_limit - self.current_enrollments, 0)


class CourseLesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    order = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=160)
    content = models.TextField()
    duration_minutes = models.PositiveSmallIntegerField(default=15)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=("course", "order"),
                name="unique_course_lesson_order",
            ),
            models.CheckConstraint(
                condition=models.Q(order__gte=1),
                name="course_lesson_order_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gte=1),
                name="course_lesson_duration_positive",
            ),
        ]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "course"),
                name="unique_user_course_enrollment",
            ),
        ]
        indexes = [
            models.Index(fields=("course", "enrolled_at"), name="enroll_course_date_idx"),
        ]

    def clean(self):
        super().clean()
        if not self.user_id or not self.course_id:
            return

        if not Profile.objects.filter(
            user_id=self.user_id,
            role=Profile.Role.LEARNER,
        ).exists():
            raise ValidationError({"user": "Only learner accounts can be enrolled."})

        if not self.course.is_published:
            raise ValidationError(
                {"course": "Learners can only be assigned to published courses."}
            )

        existing_enrollments = Enrollment.objects.filter(
            course_id=self.course_id
        ).exclude(pk=self.pk)
        if existing_enrollments.count() >= self.course.enrollment_limit:
            raise ValidationError(
                {"course": "This course has no available seats."}
            )

    def __str__(self):
        return f"{self.user} — {self.course}"
