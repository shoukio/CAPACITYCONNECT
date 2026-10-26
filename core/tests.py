from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Course, CourseLesson, Enrollment


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class HomePageTests(TestCase):
    def test_home_page_loads_with_expected_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build skills that move")
        self.assertContains(response, "Leadership")
        self.assertContains(response, "Digital skills")
        self.assertContains(response, "0 published courses")

    def test_home_page_uses_shared_layout(self):
        response = self.client.get(reverse("core:home"))

        self.assertTemplateUsed(response, "core/home.html")
        self.assertContains(response, "Capacity Connect")

    def test_home_page_shows_published_featured_courses_and_stats(self):
        featured = Course.objects.create(
            title="Team Leadership",
            category="Leadership",
            summary="Build skills for leading teams.",
            description="A practical course.",
            is_featured=True,
        )
        Course.objects.create(
            title="Draft Course",
            category="Leadership",
            summary="Not ready to publish.",
            description="Draft content.",
            is_published=False,
            is_featured=True,
        )

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, featured.title)
        self.assertContains(response, "1 published course across 1 learning category")
        self.assertNotContains(response, "Draft Course")


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CoursePageTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Practical Communication",
            category="Communication",
            summary="Communicate clearly across teams.",
            description="Course overview and learning outcomes.",
            level=Course.Level.INTERMEDIATE,
            duration_hours=3,
        )

    def test_course_list_shows_published_courses(self):
        response = self.client.get(reverse("core:course_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, "Communicate clearly across teams.")
        self.assertContains(response, 'class="section-heading catalogue-heading"')

    def test_course_detail_shows_course_information(self):
        response = self.client.get(
            reverse("core:course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, "Course overview and learning outcomes.")
        self.assertContains(response, "Intermediate")

    def test_course_detail_shows_lesson_titles_but_keeps_content_locked(self):
        lesson = CourseLesson.objects.create(
            course=self.course,
            order=1,
            title="Understand the basics",
            content="This lesson includes private learning material.",
        )

        response = self.client.get(
            reverse("core:course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertContains(response, lesson.title)
        self.assertContains(response, "Enroll to access")
        self.assertNotContains(response, "This lesson includes private learning material.")

    def test_enrolled_learner_can_read_lesson_and_open_next_lesson(self):
        first_lesson = CourseLesson.objects.create(
            course=self.course,
            order=1,
            title="First learning step",
            content="Read the explanation and try the example.",
        )
        second_lesson = CourseLesson.objects.create(
            course=self.course,
            order=2,
            title="Practice the next skill",
            content="Use the new skill in a small exercise.",
        )
        learner = get_user_model().objects.create_user(
            username="course-learner",
            password="test-password",
        )
        self.course.enrollments.create(user=learner)
        self.client.force_login(learner)

        response = self.client.get(
            reverse(
                "core:lesson_detail",
                kwargs={"slug": self.course.slug, "lesson_id": first_lesson.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Read the explanation and try the example.")
        self.assertContains(response, second_lesson.title)

    def test_non_enrolled_learner_cannot_open_lesson_content(self):
        lesson = CourseLesson.objects.create(
            course=self.course,
            order=1,
            title="Members-only lesson",
            content="Private course content.",
        )
        learner = get_user_model().objects.create_user(
            username="not-enrolled",
            password="test-password",
        )
        self.client.force_login(learner)

        response = self.client.get(
            reverse(
                "core:lesson_detail",
                kwargs={"slug": self.course.slug, "lesson_id": lesson.pk},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_guest_is_sent_to_login_before_opening_lesson(self):
        lesson = CourseLesson.objects.create(
            course=self.course,
            order=1,
            title="Protected lesson",
            content="Private course content.",
        )

        response = self.client.get(
            reverse(
                "core:lesson_detail",
                kwargs={"slug": self.course.slug, "lesson_id": lesson.pk},
            )
        )

        lesson_url = reverse(
            "core:lesson_detail",
            kwargs={"slug": self.course.slug, "lesson_id": lesson.pk},
        )
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={lesson_url}",
        )

    def test_unpublished_courses_are_not_publicly_accessible(self):
        self.course.is_published = False
        self.course.save()

        listing = self.client.get(reverse("core:course_list"))
        detail = self.client.get(
            reverse("core:course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertNotContains(listing, self.course.title)
        self.assertEqual(detail.status_code, 404)

    def test_course_slugs_are_generated_and_unique(self):
        another_course = Course.objects.create(
            title=self.course.title,
            category="Communication",
            summary="A second course.",
            description="Another course overview.",
        )

        self.assertEqual(self.course.slug, "practical-communication")
        self.assertEqual(another_course.slug, "practical-communication-2")


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CourseAdminTests(TestCase):
    def test_staff_can_manage_courses_in_django_admin(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:core_course_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add course")

    def test_admin_displays_course_capacity_and_enrollment(self):
        course = Course.objects.create(
            title="Capacity Planning",
            category="Leadership",
            summary="Learn to plan capacity.",
            description="Course description.",
            enrollment_limit=4,
        )
        learner = get_user_model().objects.create_user(
            username="enrolled",
            password="Safe-Password-139!",
        )
        course.enrollments.create(user=learner)
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Safe-Password-139!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:core_course_changelist"))

        self.assertContains(response, "Capacity Planning")
        self.assertContains(response, "4")
        self.assertContains(response, "3")

    def test_course_admin_inline_only_offers_learner_accounts(self):
        course = Course.objects.create(
            title="Introduction to Python",
            category="Programming",
            summary="Learn Python fundamentals.",
            description="Course description.",
        )
        learner = get_user_model().objects.create_user(
            username="eligible-learner",
            password="test-password",
        )
        trainer = get_user_model().objects.create_user(
            username="not-a-learner",
            password="test-password",
        )
        trainer.profile.role = "trainer"
        trainer.profile.save()
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(administrator)

        response = self.client.get(
            reverse("admin:core_course_change", args=[course.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, learner.username)
        self.assertNotContains(response, trainer.username)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CourseEnrollmentTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Building Better Teams",
            category="Leadership",
            summary="Build practical team leadership skills.",
            description="Course details.",
            enrollment_limit=2,
        )
        self.learner = get_user_model().objects.create_user(
            username="learner-one",
            password="Safe-Password-139!",
        )

    def enroll_url(self):
        return reverse("core:course_enroll", kwargs={"slug": self.course.slug})

    def test_learner_enrollment_decreases_available_slots(self):
        self.client.force_login(self.learner)

        before = self.client.get(
            reverse("core:course_detail", kwargs={"slug": self.course.slug})
        )
        response = self.client.post(self.enroll_url())
        after = self.client.get(
            reverse("core:course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertContains(before, "2 seats available")
        self.assertRedirects(
            response,
            reverse("core:course_detail", kwargs={"slug": self.course.slug}),
        )
        self.assertEqual(self.course.enrollments.count(), 1)
        self.assertContains(after, "1 seat available")
        self.assertContains(after, "You’re enrolled in this course.")

    def test_duplicate_enrollment_does_not_consume_another_seat(self):
        self.client.force_login(self.learner)

        self.client.post(self.enroll_url())
        self.client.post(self.enroll_url())

        self.assertEqual(self.course.enrollments.count(), 1)
        self.assertEqual(self.course.available_slots, 1)

    def test_full_course_rejects_additional_learner(self):
        self.course.enrollment_limit = 1
        self.course.save()
        other_learner = get_user_model().objects.create_user(
            username="learner-two",
            password="Safe-Password-139!",
        )
        self.course.enrollments.create(user=other_learner)
        self.client.force_login(self.learner)

        self.client.post(self.enroll_url())

        self.assertEqual(self.course.enrollments.count(), 1)
        self.assertEqual(self.course.available_slots, 0)

    def test_only_learners_can_enroll(self):
        trainer = get_user_model().objects.create_user(
            username="trainer",
            password="Safe-Password-139!",
        )
        trainer.profile.role = "trainer"
        trainer.profile.save()
        self.client.force_login(trainer)

        response = self.client.post(self.enroll_url())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.course.enrollments.count(), 0)

    def test_guests_must_sign_in_before_enrolling(self):
        response = self.client.post(self.enroll_url())

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
        self.assertEqual(self.course.enrollments.count(), 0)

    def test_admin_dashboard_shows_actual_course_seats(self):
        self.course.enrollments.create(user=self.learner)
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Safe-Password-139!",
        )
        self.client.force_login(administrator)

        response = self.client.get(reverse("core:administrator_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Building Better Teams")
        self.assertContains(response, "1")
        self.assertContains(response, "seats available of 2")

    def test_admin_can_assign_course_and_learner_sees_it_on_dashboard(self):
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(administrator)

        response = self.client.post(
            reverse("admin:core_enrollment_add"),
            {"user": self.learner.pk, "course": self.course.pk},
        )

        self.assertRedirects(response, reverse("admin:core_enrollment_changelist"))
        self.assertTrue(
            Enrollment.objects.filter(user=self.learner, course=self.course).exists()
        )

        self.client.force_login(self.learner)
        dashboard = self.client.get(reverse("core:learner_dashboard"))

        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, self.course.title)
        self.assertContains(dashboard, "Open course")

    def test_assigned_courses_are_private_to_the_enrolled_learner(self):
        other_learner = get_user_model().objects.create_user(
            username="learner-two",
            password="test-password",
        )
        self.course.enrollments.create(user=self.learner)
        self.client.force_login(other_learner)

        response = self.client.get(reverse("core:learner_dashboard"))

        self.assertContains(response, "No courses assigned yet.")
        self.assertNotContains(response, self.course.title)

    def test_admin_cannot_assign_course_to_non_learner(self):
        trainer = get_user_model().objects.create_user(
            username="trainer",
            password="test-password",
        )
        trainer.profile.role = "trainer"
        trainer.profile.save()
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(administrator)

        response = self.client.post(
            reverse("admin:core_enrollment_add"),
            {"user": trainer.pk, "course": self.course.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Enrollment.objects.filter(user=trainer, course=self.course).exists()
        )

    def test_only_administrators_can_create_courses(self):
        self.client.force_login(self.learner)

        response = self.client.get(reverse("core:admin_course_create"))

        self.assertEqual(response.status_code, 403)

    def test_administrator_can_create_course_with_capacity(self):
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Safe-Password-139!",
        )
        self.client.force_login(administrator)

        response = self.client.post(
            reverse("core:admin_course_create"),
            {
                "title": "New Manager Essentials",
                "category": "Leadership",
                "summary": "A manager development course.",
                "description": "New course content.",
                "level": Course.Level.BEGINNER,
                "duration_hours": 2,
                "enrollment_limit": 15,
                "is_featured": "",
                "is_published": "on",
            },
        )

        created = Course.objects.get(title="New Manager Essentials")
        self.assertRedirects(response, reverse("core:administrator_dashboard"))
        self.assertEqual(created.available_slots, 15)
        self.assertTrue(created.is_published)

    def test_administrator_cannot_create_a_course_with_zero_capacity(self):
        administrator = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Safe-Password-139!",
        )
        self.client.force_login(administrator)

        response = self.client.post(
            reverse("core:admin_course_create"),
            {
                "title": "Another course",
                "category": "Leadership",
                "summary": "A course summary.",
                "description": "Course content.",
                "level": Course.Level.BEGINNER,
                "duration_hours": 2,
                "enrollment_limit": 0,
                "is_featured": "",
                "is_published": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Course.objects.filter(title="Another course").exists())

    def test_course_capacity_cannot_be_reduced_below_current_enrollment(self):
        self.course.enrollments.create(user=self.learner)
        second_learner = get_user_model().objects.create_user(
            username="learner-three",
            password="Safe-Password-139!",
        )
        self.course.enrollments.create(user=second_learner)
        self.course.enrollment_limit = 1

        with self.assertRaises(ValidationError) as error:
            self.course.full_clean()
        self.assertIn("already enrolled", str(error.exception))


class CodingCourseSeedTests(TestCase):
    def test_seed_command_creates_ten_courses_with_lessons_idempotently(self):
        call_command("seed_coding_courses", verbosity=0)

        self.assertEqual(Course.objects.count(), 10)
        self.assertEqual(Course.objects.filter(is_published=True).count(), 10)
        self.assertEqual(CourseLesson.objects.count(), 30)
        self.assertEqual(
            set(Course.objects.values_list("category", flat=True)),
            {
                "Programming",
                "Web Development",
                "Data and Databases",
                "Developer Tools",
                "Leadership",
                "Digital skills",
                "Communication",
                "Wellbeing",
            },
        )

        call_command("seed_coding_courses", verbosity=0)

        self.assertEqual(Course.objects.count(), 10)
        self.assertEqual(CourseLesson.objects.count(), 30)
