from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Company, PlacementDrive, Application

INPUT_CLASS = "form-control"

class StyledFormMixin:
    def style_fields(self):
        for field in self.fields.values():
            old = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (old + " " + INPUT_CLASS).strip()
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)

class StudentRegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    department = forms.CharField(max_length=80)
    graduation_year = forms.IntegerField(min_value=2025, max_value=2040, initial=2029)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "department", "graduation_year", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

class ProfileForm(StyledFormMixin, forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = [
            "phone", "department", "cgpa", "backlogs", "graduation_year", "skills",
            "github_profile_url", "hackerrank_profile_url",
            "leetcode_username", "leetcode_profile_url", "leetcode_solved_count",
        ]
        widgets = {
            "skills": forms.Textarea(attrs={"placeholder": "Python, SQL, communication..."}),
            "cgpa": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "github_profile_url": forms.URLInput(attrs={"placeholder": "https://github.com/your-username/"}),
            "hackerrank_profile_url": forms.URLInput(attrs={"placeholder": "https://www.hackerrank.com/profile/your-username"}),
            "leetcode_profile_url": forms.URLInput(attrs={"placeholder": "https://leetcode.com/u/yourname/"}),
        }
        help_texts = {
            "github_profile_url": "Paste your public GitHub profile link. Never enter a GitHub password or access token.",
            "hackerrank_profile_url": "Paste your public HackerRank profile link. Never enter a HackerRank password.",
            "leetcode_solved_count": "Enter the total solved count shown on your public LeetCode profile. Self-reported until verified.",
            "leetcode_username": "Username only; never enter your LeetCode password.",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        duplicate = User.objects.filter(email__iexact=email)
        if self.user:
            duplicate = duplicate.exclude(pk=self.user.pk)
        if duplicate.exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
        self.style_fields()

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.first_name = self.cleaned_data["first_name"]
                self.user.last_name = self.cleaned_data["last_name"]
                self.user.email = self.cleaned_data["email"]
                self.user.save()
        return profile

class CompanyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "industry", "website", "location", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.style_fields()

class DriveForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PlacementDrive
        fields = ["title", "company", "description", "eligible_departments", "min_cgpa", "max_backlogs", "package_lpa", "required_skills", "min_leetcode_solved", "deadline", "is_active"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 3})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.style_fields()

class RecruiterCreateForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField()
    company_name = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    class Meta:
        model = User
        fields = ["username", "first_name", "email", "company_name", "password1", "password2"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.style_fields()

class ApplicationStatusForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.style_fields()
