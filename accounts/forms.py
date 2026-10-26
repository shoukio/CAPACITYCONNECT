from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Profile


class AdministratorAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "not_administrator": (
            "These credentials do not belong to an administrator account."
        ),
    }

    def clean(self):
        cleaned_data = super().clean()
        user = self.get_user()
        if user is None:
            return cleaned_data

        profile = Profile.objects.filter(user=user).only("role").first()
        role_group = dict(Profile.Role.choices)[Profile.Role.ADMINISTRATOR]
        if (
            not user.is_staff
            or profile is None
            or profile.role != Profile.Role.ADMINISTRATOR
            or not user.groups.filter(name=role_group).exists()
        ):
            raise ValidationError(
                self.error_messages["not_administrator"],
                code="not_administrator",
            )
        return cleaned_data


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user