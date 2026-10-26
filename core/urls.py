from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.DashboardRedirectView.as_view(), name="dashboard"),
    path(
        "dashboard/learner/",
        views.LearnerDashboardView.as_view(),
        name="learner_dashboard",
    ),
    path(
        "dashboard/trainer/",
        views.TrainerDashboardView.as_view(),
        name="trainer_dashboard",
    ),
    path(
        "dashboard/administrator/",
        views.AdministratorDashboardView.as_view(),
        name="administrator_dashboard",
    ),
    path(
        "dashboard/administrator/courses/add/",
        views.AdminCourseCreateView.as_view(),
        name="admin_course_create",
    ),
    path("courses/", views.course_list, name="course_list"),
    path(
        "courses/<slug:slug>/lessons/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
    path(
        "courses/<slug:slug>/enroll/",
        views.CourseEnrollmentView.as_view(),
        name="course_enroll",
    ),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
]
