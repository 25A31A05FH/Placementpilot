from django.db import migrations, models


def add_sample_coding_thresholds(apps, schema_editor):
    Company = apps.get_model("portal", "Company")
    PlacementDrive = apps.get_model("portal", "PlacementDrive")
    sample_rules = [
        ("Graduate Software Engineer", "Nova Systems", 25, 50),
        ("Junior Data Analyst", "BluePeak Analytics", 10, 15),
        ("Frontend Developer Trainee", "Aster Digital", 0, 30),
    ]
    for title, company_name, hackerrank_min, leetcode_min in sample_rules:
        company = Company.objects.filter(name=company_name).first()
        if company:
            PlacementDrive.objects.filter(title=title, company=company).update(
                min_hackerrank_solved=hackerrank_min,
                min_leetcode_solved=leetcode_min,
            )


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="profile", name="hackerrank_username",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="profile", name="hackerrank_profile_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="profile", name="hackerrank_solved_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile", name="hackerrank_verified",
            field=models.BooleanField(default=False, help_text="Placement-office verification flag"),
        ),
        migrations.AddField(
            model_name="profile", name="leetcode_username",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="profile", name="leetcode_profile_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="profile", name="leetcode_solved_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile", name="leetcode_verified",
            field=models.BooleanField(default=False, help_text="Placement-office verification flag"),
        ),
        migrations.AddField(
            model_name="profile", name="coding_stats_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="placementdrive", name="min_hackerrank_solved",
            field=models.PositiveIntegerField(default=0, help_text="0 means HackerRank is not an eligibility condition"),
        ),
        migrations.AddField(
            model_name="placementdrive", name="min_leetcode_solved",
            field=models.PositiveIntegerField(default=0, help_text="0 means LeetCode is not an eligibility condition"),
        ),
        migrations.RunPython(add_sample_coding_thresholds, migrations.RunPython.noop),
    ]
