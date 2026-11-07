from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0004_update_required_skills_help_text")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="github_profile_url",
            field=models.URLField(blank=True, help_text="Public GitHub profile URL"),
        ),
        migrations.AddField(
            model_name="profile",
            name="hackerrank_profile_url",
            field=models.URLField(blank=True, help_text="Public HackerRank profile URL"),
        ),
    ]
