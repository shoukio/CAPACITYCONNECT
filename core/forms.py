from django import forms

from .models import Course


class AdminCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            "title",
            "category",
            "summary",
            "description",
            "level",
            "duration_hours",
            "enrollment_limit",
            "is_featured",
            "is_published",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_enrollment_limit(self):
        limit = self.cleaned_data["enrollment_limit"]
        if limit < 1:
            raise forms.ValidationError("Course capacity must be at least one seat.")
        if self.instance.pk:
            enrolled_count = self.instance.enrollments.count()
            if limit < enrolled_count:
                raise forms.ValidationError(
                    f"Capacity cannot be less than the {enrolled_count} "
                    "learner(s) already enrolled."
                )
        return limit
