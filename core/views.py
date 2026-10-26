from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView

from accounts.models import Profile
from .forms import AdminCourseForm
from .mixins import AdministratorRequiredMixin, RoleRequiredMixin
from .models import Course, CourseLesson
from .services import (
    AlreadyEnrolledError,
    CourseFullError,
    CourseUnavailableError,
    enroll_learner,
)


def home(request):
    categories = [
        {
            "name": "Leadership",
            "description": "Build confident, people-first leaders at every level.",
            "icon": "↗",
            "tone": "lavender",
        },
        {
            "name": "Digital skills",
            "description": "Grow practical technology and data capabilities.",
            "icon": "⌘",
            "tone": "mint",
        },
        {
            "name": "Communication",
            "description": "Make collaboration clearer across every team.",
            "icon": "✳",
            "tone": "peach",
        },
        {
            "name": "Wellbeing",
            "description": "Support sustainable, healthy ways of working.",
            "icon": "♡",
            "tone": "blue",
        },
    ]
    courses = Course.objects.filter(is_published=True)
    return render(
        request,
        "core/home.html",
        {
            "categories": categories,
            "featured_courses": courses.filter(is_featured=True)
            .annotate(current_enrollment_count=Count("enrollments"))[:3],
            "course_count": courses.count(),
            "category_count": courses.values("category").distinct().count(),
        },
    )


def course_list(request):
    courses = Course.objects.filter(is_published=True).annotate(
        current_enrollment_count=Count("enrollments")
    )
    return render(request, "core/course_list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.annotate(current_enrollment_count=Count("enrollments")),
        slug=slug,
        is_published=True,
    )
    is_enrolled = request.user.is_authenticated and course.enrollments.filter(
        user=request.user
    ).exists()
    is_administrator = (
        request.user.is_authenticated
        and request.user.is_staff
        and Profile.objects.filter(
            user=request.user,
            role=Profile.Role.ADMINISTRATOR,
        ).exists()
    )
    return render(
        request,
        "core/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "can_view_lessons": is_enrolled or is_administrator,
        },
    )


def lesson_detail(request, slug, lesson_id):
    lesson = get_object_or_404(
        CourseLesson.objects.select_related("course"),
        pk=lesson_id,
        course__slug=slug,
        course__is_published=True,
    )
    is_enrolled = request.user.is_authenticated and lesson.course.enrollments.filter(
        user=request.user
    ).exists()
    is_administrator = (
        request.user.is_authenticated
        and request.user.is_staff
        and Profile.objects.filter(
            user=request.user,
            role=Profile.Role.ADMINISTRATOR,
        ).exists()
    )
    if not is_enrolled and not is_administrator:
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        raise PermissionDenied

    lessons = list(lesson.course.lessons.all())
    lesson_index = lessons.index(lesson)
    return render(
        request,
        "core/lesson_detail.html",
        {
            "lesson": lesson,
            "lessons": lessons,
            "previous_lesson": lessons[lesson_index - 1] if lesson_index else None,
            "next_lesson": (
                lessons[lesson_index + 1]
                if lesson_index + 1 < len(lessons)
                else None
            ),
        },
    )


class CourseEnrollmentView(RoleRequiredMixin, View):
    required_role = Profile.Role.LEARNER

    def post(self, request, slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        try:
            enroll_learner(user=request.user, course_id=course.pk)
        except AlreadyEnrolledError as error:
            messages.info(request, str(error))
        except CourseFullError as error:
            messages.error(request, str(error))
        except CourseUnavailableError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f"You are enrolled in {course.title}.")
        return redirect("core:course_detail", slug=course.slug)


class DashboardRedirectView(LoginRequiredMixin, View):
    dashboard_names = {
        Profile.Role.LEARNER: "core:learner_dashboard",
        Profile.Role.TRAINER: "core:trainer_dashboard",
        Profile.Role.ADMINISTRATOR: "core:administrator_dashboard",
    }

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).only("role").first()
        if profile is None or profile.role not in self.dashboard_names:
            raise PermissionDenied

        group_name = dict(Profile.Role.choices)[profile.role]
        if not request.user.groups.filter(name=group_name).exists():
            raise PermissionDenied

        return redirect(self.dashboard_names[profile.role])


class LearnerDashboardView(RoleRequiredMixin, TemplateView):
    required_role = Profile.Role.LEARNER
    template_name = "core/dashboards/learner.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["enrollments"] = self.request.user.course_enrollments.select_related(
            "course"
        )
        return context


class TrainerDashboardView(RoleRequiredMixin, TemplateView):
    required_role = Profile.Role.TRAINER
    template_name = "core/dashboards/trainer.html"


class AdministratorDashboardView(AdministratorRequiredMixin, TemplateView):
    template_name = "core/dashboards/administrator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.annotate(
            current_enrollment_count=Count("enrollments")
        )
        return context


class AdminCourseCreateView(AdministratorRequiredMixin, CreateView):
    form_class = AdminCourseForm
    template_name = "core/admin_course_form.html"

    def get_success_url(self):
        return reverse("core:administrator_dashboard")

    def form_valid(self, form):
        messages.success(self.request, "The course was created successfully.")
        return super().form_valid(form)
