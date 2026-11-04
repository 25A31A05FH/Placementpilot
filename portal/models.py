from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [("student", "Student"), ("admin", "Administrator"), ("recruiter", "Recruiter")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default="student")
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=80, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    backlogs = models.PositiveSmallIntegerField(default=0)
    graduation_year = models.PositiveSmallIntegerField(default=2027)
    skills = models.TextField(blank=True, help_text="Comma-separated skills, e.g. Python, SQL, React")
    # Public profile references and self-reported public completion counts.
    # Do not collect or store third-party platform passwords or session cookies.
    leetcode_username = models.CharField(max_length=100, blank=True)
    leetcode_profile_url = models.URLField(blank=True)
    leetcode_solved_count = models.PositiveIntegerField(default=0)
    leetcode_verified = models.BooleanField(default=False, help_text="Placement-office verification flag")
    coding_stats_updated_at = models.DateTimeField(null=True, blank=True)
    resume = models.FileField(upload_to="resumes/%Y/%m/", blank=True)
    company_name = models.CharField(max_length=150, blank=True, help_text="For recruiter accounts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Company(models.Model):
    name = models.CharField(max_length=160, unique=True)
    industry = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class PlacementDrive(models.Model):
    title = models.CharField(max_length=180)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="drives")
    description = models.TextField(blank=True)
    eligible_departments = models.CharField(max_length=300, blank=True, help_text="Comma-separated; leave blank for all departments")
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    max_backlogs = models.PositiveSmallIntegerField(default=0)
    package_lpa = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    required_skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills; all listed skills are treated as required")
    min_leetcode_solved = models.PositiveIntegerField(default=0, help_text="0 means LeetCode is not an eligibility condition")
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_drives")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["deadline", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.company.name}"

    @property
    def department_list(self):
        return [item.strip().lower() for item in self.eligible_departments.split(",") if item.strip()]

    @property
    def skill_list(self):
        return [item.strip().lower() for item in self.required_skills.split(",") if item.strip()]

    @property
    def is_open(self):
        return self.is_active and self.deadline >= timezone.localdate()

class Application(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("shortlisted", "Shortlisted"), ("rejected", "Rejected"), ("selected", "Selected")]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="placement_applications")
    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [models.UniqueConstraint(fields=["student", "drive"], name="unique_student_drive_application")]

    def __str__(self):
        return f"{self.student.username} → {self.drive.title}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
