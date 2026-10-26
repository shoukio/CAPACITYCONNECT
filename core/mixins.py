from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from accounts.models import Profile


ROLE_GROUP_NAMES = {value: label for value, label in Profile.Role.choices}


class RoleRequiredMixin(LoginRequiredMixin):
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        profile = Profile.objects.filter(user=request.user).only("role").first()
        if (
            self.required_role is None
            or profile is None
            or profile.role != self.required_role
            or not request.user.groups.filter(
                name=ROLE_GROUP_NAMES[self.required_role]
            ).exists()
        ):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class AdministratorRequiredMixin(RoleRequiredMixin):
    required_role = Profile.Role.ADMINISTRATOR

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)