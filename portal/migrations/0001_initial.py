# Initial migration for PlacementPilot.
import django.db.models.deletion
import django.core.validators
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, unique=True)),
                ("industry", models.CharField(blank=True, max_length=120)),
                ("website", models.URLField(blank=True)),
                ("location", models.CharField(blank=True, max_length=160)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("student", "Student"), ("admin", "Administrator"), ("recruiter", "Recruiter")], default="student", max_length=12)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("department", models.CharField(blank=True, max_length=80)),
                ("cgpa", models.DecimalField(decimal_places=2, default=0, max_digits=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ("backlogs", models.PositiveSmallIntegerField(default=0)),
                ("graduation_year", models.PositiveSmallIntegerField(default=2027)),
                ("skills", models.TextField(blank=True, help_text="Comma-separated skills, e.g. Python, SQL, React")),
                ("resume", models.FileField(blank=True, upload_to="resumes/%Y/%m/")),
                ("company_name", models.CharField(blank=True, help_text="For recruiter accounts", max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PlacementDrive",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("eligible_departments", models.CharField(blank=True, help_text="Comma-separated; leave blank for all departments", max_length=300)),
                ("min_cgpa", models.DecimalField(decimal_places=2, default=0, max_digits=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ("max_backlogs", models.PositiveSmallIntegerField(default=0)),
                ("package_lpa", models.DecimalField(decimal_places=2, default=0, max_digits=6, validators=[django.core.validators.MinValueValidator(0)])),
                ("required_skills", models.CharField(blank=True, help_text="Comma-separated skills", max_length=500)),
                ("deadline", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="drives", to="portal.company")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="managed_drives", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["deadline", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("shortlisted", "Shortlisted"), ("rejected", "Rejected"), ("selected", "Selected")], default="pending", max_length=12)),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("drive", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="portal.placementdrive")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="placement_applications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-applied_at"]},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.CharField(max_length=255)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="application",
            constraint=models.UniqueConstraint(fields=("student", "drive"), name="unique_student_drive_application"),
        ),
    ]
