from django.db import IntegrityError, transaction

from .models import Course, Enrollment


class EnrollmentError(Exception):
    pass


class CourseFullError(EnrollmentError):
    pass


class AlreadyEnrolledError(EnrollmentError):
    pass


class CourseUnavailableError(EnrollmentError):
    pass


@transaction.atomic
def enroll_learner(*, user, course_id):
    course = Course.objects.select_for_update().filter(
        pk=course_id,
        is_published=True,
    ).first()
    if course is None:
        raise CourseUnavailableError("This course is not available for enrollment.")

    if Enrollment.objects.filter(user=user, course=course).exists():
        raise AlreadyEnrolledError("You are already enrolled in this course.")

    if Enrollment.objects.filter(course=course).count() >= course.enrollment_limit:
        raise CourseFullError("This course has no available seats.")

    try:
        enrollment = Enrollment.objects.create(user=user, course=course)
    except IntegrityError as error:
        raise AlreadyEnrolledError(
            "You are already enrolled in this course."
        ) from error
    return enrollment
