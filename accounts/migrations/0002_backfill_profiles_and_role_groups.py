from django.conf import settings
from django.db import migrations


ROLE_GROUP_NAMES = {
    "administrator": "Administrator",
    "trainer": "Trainer",
    "learner": "Learner",
}


def backfill_profiles_and_groups(apps, schema_editor):
    database = schema_editor.connection.alias
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    Group = apps.get_model("auth", "Group")
    Profile = apps.get_model("accounts", "Profile")

    for user in User.objects.using(database).all().iterator():
        default_role = "administrator" if user.is_superuser else "learner"
        profile, _ = Profile.objects.using(database).get_or_create(
            user_id=user.pk,
            defaults={"role": default_role},
        )
        group_name = ROLE_GROUP_NAMES.get(profile.role)
        if group_name is None:
            raise ValueError(
                f"Unsupported profile role {profile.role!r} for user {user.pk}."
            )
        group, _ = Group.objects.using(database).get_or_create(name=group_name)
        user.groups.add(group)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            backfill_profiles_and_groups,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
