from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("portal", "0002_coding_platform_eligibility")]

    operations = [
        migrations.RemoveField(model_name="profile", name="hackerrank_username"),
        migrations.RemoveField(model_name="profile", name="hackerrank_profile_url"),
        migrations.RemoveField(model_name="profile", name="hackerrank_solved_count"),
        migrations.RemoveField(model_name="profile", name="hackerrank_verified"),
        migrations.RemoveField(model_name="placementdrive", name="min_hackerrank_solved"),
    ]
