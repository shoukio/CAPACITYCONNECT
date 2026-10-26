from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms.models import BaseInlineFormSet

from accounts.models import Profile
from .models import Course, CourseLesson, Enrollment


class EnrollmentInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors) or not self.instance.pk:
            return

        active_enrollments = sum(
            1
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE", False)
            and form.cleaned_data.get("user")
        )
        if active_enrollments > self.instance.enrollment_limit:
            raise ValidationError("The selected learners exceed course capacity.")


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    formset = EnrollmentInlineFormSet
    fields = ("user", "enrolled_at")
    readonly_fields = ("enrolled_at",)
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = get_user_model().objects.filter(
                profile__role=Profile.Role.LEARNER
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    fields = ("order", "title", "duration_minutes", "content")
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = (CourseLessonInline, EnrollmentInline)
    list_display = (
        "title",
        "category",
        "level",
        "current_enrollment_count",
        "enrollment_limit",
        "available_slots",
        "is_featured",
        "is_published",
        "updated_at",
    )
    list_filter = ("category", "level", "is_featured", "is_published")
    search_fields = ("title", "category", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "created_at",
        "updated_at",
        "current_enrollment_count",
        "available_slots",
    )
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "summary", "description")}),
        (
            "Course details",
            {
                "fields": (
                    "level",
                    "duration_hours",
                    "enrollment_limit",
                    "current_enrollment_count",
                    "available_slots",
                    "is_featured",
                    "is_published",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            current_enrollment_count=Count("enrollments")
        )

    @admin.display(description="Enrolled learners")
    def current_enrollment_count(self, obj):
        return obj.current_enrollments


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("enrolled_at", "course")
    search_fields = ("user__username", "user__email", "course__title")
    list_select_related = ("user", "course")
    date_hierarchy = "enrolled_at"
    readonly_fields = ("enrolled_at",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = get_user_model().objects.filter(
                profile__role=Profile.Role.LEARNER
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
