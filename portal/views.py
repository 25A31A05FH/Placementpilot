from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .decorators import role_required
from .forms import (StudentRegistrationForm, ProfileForm, CompanyForm, DriveForm,
                    RecruiterCreateForm, ApplicationStatusForm)
from .models import Profile, Company, PlacementDrive, Application, Notification
from .utils import eligibility_for, extract_resume_text, find_skills


def user_role(user):
    if user.is_staff or user.is_superuser:
        return "admin"
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.role


def home(request):
    drives = PlacementDrive.objects.filter(is_active=True, deadline__gte=timezone.localdate()).select_related("company")[:3]
    context = {
        "drive_count": PlacementDrive.objects.filter(is_active=True).count(),
        "company_count": Company.objects.count(),
        "student_count": Profile.objects.filter(role="student").count(),
        "featured_drives": drives,
    }
    return render(request, "portal/home.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user, role="student", department=form.cleaned_data["department"], graduation_year=form.cleaned_data["graduation_year"])
        login(request, user)
        messages.success(request, "Your student account has been created. Complete your profile to check eligibility.")
        return redirect("profile")
    return render(request, "portal/register.html", {"form": form})


def login_view(request):
    """Show the portal chooser; keep POST compatibility for existing sign-in links."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        return _portal_login(request, expected_role=None)
    return render(request, "portal/login_choice.html")


def _portal_login(request, expected_role):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None
    if request.method == "POST":
        identity = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=identity, password=password)
        if user is None and "@" in identity:
            match = User.objects.filter(email__iexact=identity).first()
            if match:
                user = authenticate(request, username=match.username, password=password)

        if user:
            actual_role = "admin" if user.is_staff or user.is_superuser else (
                Profile.objects.filter(user=user).values_list("role", flat=True).first()
            )
            if expected_role and actual_role != expected_role:
                portal_name = dict(Profile.ROLE_CHOICES).get(expected_role, expected_role.title())
                error = f"This account does not have access to the {portal_name} portal. Please use the correct login section."
            else:
                login(request, user)
                remember_me = request.POST.get("remember_me") == "on"
                # Only the session duration and remembered username are stored; never the password.
                request.session.set_expiry(60 * 60 * 24 * 14 if remember_me else 0)
                next_url = request.GET.get("next", "")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
                ):
                    response = redirect(next_url)
                else:
                    response = redirect("dashboard")
                if remember_me:
                    response.set_cookie(
                        "pp_remembered_username", identity, max_age=60 * 60 * 24 * 30,
                        httponly=True, samesite="Lax", secure=request.is_secure()
                    )
                else:
                    response.delete_cookie("pp_remembered_username", samesite="Lax")
                return response
        else:
            error = "The username/email or password was not recognised."

    portal_title = {
        "student": "Student",
        "admin": "Administrator",
        "recruiter": "Recruiter",
    }.get(expected_role, "PlacementPilot")
    return render(request, "portal/login.html", {
        "error": error,
        "portal_role": expected_role,
        "portal_title": portal_title,
        "remembered_username": request.COOKIES.get("pp_remembered_username", ""),
        "remember_checked": bool(request.COOKIES.get("pp_remembered_username")),
    })


def student_login(request):
    return _portal_login(request, expected_role="student")


def admin_login(request):
    return _portal_login(request, expected_role="admin")


def recruiter_login(request):
    return _portal_login(request, expected_role="recruiter")


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been signed out.")
    return redirect("home")


@login_required
def dashboard(request):
    role = user_role(request.user)
    if role == "admin":
        context = {
            "role": role,
            "student_count": Profile.objects.filter(role="student").count(),
            "company_count": Company.objects.count(),
            "drive_count": PlacementDrive.objects.count(),
            "application_count": Application.objects.count(),
            "pending_count": Application.objects.filter(status="pending").count(),
            "recent_applications": Application.objects.select_related("student", "drive", "drive__company")[:7],
            "top_drives": PlacementDrive.objects.annotate(app_count=Count("applications")).order_by("-app_count")[:5],
        }
    elif role == "recruiter":
        own_drives = PlacementDrive.objects.filter(created_by=request.user)
        context = {
            "role": role,
            "drives": own_drives.annotate(app_count=Count("applications")),
            "application_count": Application.objects.filter(drive__created_by=request.user).count(),
            "pending_count": Application.objects.filter(drive__created_by=request.user, status="pending").count(),
            "recent_applications": Application.objects.filter(drive__created_by=request.user).select_related("student", "drive", "drive__company")[:8],
        }
    else:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        applications = Application.objects.filter(student=request.user).select_related("drive", "drive__company")
        open_drives = PlacementDrive.objects.filter(is_active=True, deadline__gte=timezone.localdate()).select_related("company")
        eligible_drives = [drive for drive in open_drives if eligibility_for(profile, drive)[0]]
        eligible_count = len(eligible_drives)
        context = {
            "role": role,
            "profile": profile,
            "application_count": applications.count(),
            "shortlisted_count": applications.filter(status="shortlisted").count(),
            "selected_count": applications.filter(status="selected").count(),
            "eligible_count": eligible_count,
            "recent_applications": applications[:5],
            "recommended_drives": eligible_drives[:4],
        }
    context["unread_notifications"] = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, "portal/dashboard.html", context)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile, user=request.user)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        profile.coding_stats_updated_at = timezone.now()
        # A changed count must be reviewed again by the placement office.
        profile.leetcode_verified = False
        profile.save(update_fields=["coding_stats_updated_at", "leetcode_verified"])
        messages.success(request, "Your profile and LeetCode details have been updated. Your completion count is self-reported until verified by the placement office.")
        return redirect("profile")
    return render(request, "portal/form_page.html", {"form": form, "title": "Your profile", "subtitle": "Keep your academic details, skills and LeetCode profile details up to date. Never enter your LeetCode password here.", "button": "Save profile"})


@login_required
def drive_list(request, force_eligible=False):
    drives = PlacementDrive.objects.filter(is_active=True, deadline__gte=timezone.localdate()).select_related("company")
    department = request.GET.get("department", "").strip()
    search = request.GET.get("q", "").strip()
    if search:
        drives = drives.filter(title__icontains=search) | drives.filter(company__name__icontains=search)
    drives = list(drives)
    if department:
        drives = [drive for drive in drives if not drive.department_list or department.lower() in drive.department_list]

    is_student = user_role(request.user) == "student"
    profile = Profile.objects.get_or_create(user=request.user)[0] if is_student else None
    if is_student:
        for drive in drives:
            drive.is_eligible_for_user, drive.ineligibility_reasons = eligibility_for(profile, drive)
            drive.coding_verification_pending = bool(
                drive.min_leetcode_solved and profile.leetcode_solved_count >= drive.min_leetcode_solved and not profile.leetcode_verified
            )
        if force_eligible or request.GET.get("eligible") == "1":
            drives = [drive for drive in drives if drive.is_eligible_for_user]
    return render(request, "portal/drives.html", {
        "drives": drives, "search": search, "department": department,
        "is_student": is_student, "eligible_only": force_eligible or request.GET.get("eligible") == "1",
    })


@login_required
def eligible_drives(request):
    return drive_list(request, force_eligible=True)


@login_required
def drive_detail(request, pk):
    drive = get_object_or_404(PlacementDrive.objects.select_related("company"), pk=pk)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    eligible, reasons = eligibility_for(profile, drive)
    existing = Application.objects.filter(student=request.user, drive=drive).first()
    can_apply = user_role(request.user) == "student" and eligible and not existing
    verification_pending = []
    if drive.min_leetcode_solved and profile.leetcode_solved_count >= drive.min_leetcode_solved and not profile.leetcode_verified:
        verification_pending.append("LeetCode completion count")
    return render(request, "portal/drive_detail.html", {
        "drive": drive, "eligible": eligible, "reasons": reasons, "existing": existing,
        "can_apply": can_apply, "verification_pending": verification_pending,
    })


@require_POST
@role_required("student")
def apply_to_drive(request, pk):
    drive = get_object_or_404(PlacementDrive, pk=pk)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    eligible, reasons = eligibility_for(profile, drive)
    if not eligible:
        messages.error(request, "You cannot apply: " + " ".join(reasons))
    else:
        application, created = Application.objects.get_or_create(student=request.user, drive=drive)
        if created:
            messages.success(request, f"Your application for {drive.title} has been submitted.")
            Notification.objects.create(user=request.user, message=f"Application submitted: {drive.title} at {drive.company.name}.")
        else:
            messages.info(request, "You have already applied to this drive.")
    return redirect("drive_detail", pk=pk)


@login_required
def applications(request):
    role = user_role(request.user)
    qs = Application.objects.select_related("student", "drive", "drive__company")
    if role == "student":
        qs = qs.filter(student=request.user)
    elif role == "recruiter":
        qs = qs.filter(drive__created_by=request.user)
    return render(request, "portal/applications.html", {"applications": qs, "show_action": role != "student"})


@role_required("admin", "recruiter")
def update_application(request, pk):
    application = get_object_or_404(Application.objects.select_related("drive"), pk=pk)
    if user_role(request.user) == "recruiter" and application.drive.created_by_id != request.user.id:
        return HttpResponseForbidden("You cannot manage this application.")
    form = ApplicationStatusForm(request.POST or None, instance=application)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        Notification.objects.create(user=updated.student, message=f"Your application for {updated.drive.title} is now {updated.get_status_display().lower()}.")
        messages.success(request, "Application status updated and student notified.")
        return redirect("applications")
    return render(request, "portal/form_page.html", {"form": form, "title": "Update application", "subtitle": f"{application.student.username} · {application.drive.title}", "button": "Update status"})


@login_required
def resume_analyzer(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    result = None
    error = None
    if request.method == "POST":
        uploaded = request.FILES.get("resume")
        source = uploaded or (profile.resume if profile.resume else None)
        if not source:
            error = "Choose a resume file first."
        elif source.size > 5 * 1024 * 1024:
            error = "The maximum file size is 5 MB."
        else:
            try:
                text = extract_resume_text(source)
                if uploaded:
                    profile.resume = uploaded
                    profile.save(update_fields=["resume"])
                found = find_skills(text)
                profile_skills = {s.strip().lower() for s in profile.skills.split(",") if s.strip()}
                matched = sorted(set(found) & profile_skills) if profile_skills else found
                missing = sorted(set(found) - set(matched)) if profile_skills else []
                drive_matches = []
                for drive in PlacementDrive.objects.filter(is_active=True, deadline__gte=timezone.localdate()).select_related("company"):
                    gaps = sorted(set(drive.skill_list) - set(found))
                    drive_matches.append({"drive": drive, "gaps": gaps, "match": round(100 * (len(drive.skill_list) - len(gaps)) / len(drive.skill_list)) if drive.skill_list else 100})
                result = {"skills": found, "matched": matched, "missing": missing, "drives": drive_matches[:6]}
            except Exception as exc:
                error = str(exc)
    return render(request, "portal/resume.html", {"profile": profile, "result": result, "error": error})


@login_required
def notifications(request):
    items = Notification.objects.filter(user=request.user)
    if request.method == "POST":
        items.filter(is_read=False).update(is_read=True)
        messages.success(request, "Notifications marked as read.")
        return redirect("notifications")
    return render(request, "portal/notifications.html", {"notifications": items})


@role_required("admin")
def admin_students(request):
    students = Profile.objects.filter(role="student").select_related("user").order_by("user__first_name", "user__username")
    q = request.GET.get("q", "").strip()
    if q:
        from django.db.models import Q
        students = students.filter(Q(user__username__icontains=q) | Q(user__first_name__icontains=q) | Q(user__email__icontains=q) | Q(department__icontains=q))
    return render(request, "portal/students.html", {"students": students, "q": q})


@role_required("admin")
def create_student(request):
    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user, role="student", department=form.cleaned_data["department"], graduation_year=form.cleaned_data["graduation_year"])
        messages.success(request, "Student account created.")
        return redirect("students")
    return render(request, "portal/form_page.html", {"form": form, "title": "Add a student", "subtitle": "Create a student login and initial academic profile.", "button": "Create student"})


@role_required("admin")
def edit_student(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk, role="student")
    form = ProfileForm(request.POST or None, instance=profile, user=profile.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student profile updated.")
        return redirect("students")
    return render(request, "portal/form_page.html", {"form": form, "title": f"Edit {profile.user.get_full_name() or profile.user.username}", "subtitle": "Update the student's academic and contact information.", "button": "Save student"})


@require_POST
@role_required("admin")
def delete_student(request, pk):
    profile = get_object_or_404(Profile, pk=pk, role="student")
    profile.user.delete()
    messages.success(request, "Student account and related applications deleted.")
    return redirect("students")


@role_required("admin")
def manage_companies(request):
    form = CompanyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Company added."); return redirect("companies")
    companies = Company.objects.annotate(drive_count=Count("drives"))
    return render(request, "portal/companies.html", {"form": form, "companies": companies})


@role_required("admin")
def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Company details updated.")
        return redirect("companies")
    return render(request, "portal/form_page.html", {"form": form, "title": f"Edit {company.name}", "subtitle": "Update the hiring partner details.", "button": "Save company"})


@role_required("admin")
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        company.delete(); messages.success(request, "Company deleted.")
    return redirect("companies")


@role_required("admin", "recruiter")
def manage_drives(request):
    qs = PlacementDrive.objects.select_related("company").annotate(app_count=Count("applications"))
    if user_role(request.user) == "recruiter":
        qs = qs.filter(created_by=request.user)
    return render(request, "portal/manage_drives.html", {"drives": qs})


@role_required("admin", "recruiter")
def drive_applicants(request, pk):
    drive = get_object_or_404(
        PlacementDrive.objects.select_related("company"), pk=pk
    )
    if user_role(request.user) == "recruiter" and drive.created_by_id != request.user.id:
        return HttpResponseForbidden("You cannot view applicants for this drive.")
    applicants = drive.applications.select_related(
        "student", "drive", "drive__company"
    ).order_by("-applied_at")
    return render(request, "portal/drive_applicants.html", {
        "drive": drive,
        "applications": applicants,
    })


@role_required("admin", "recruiter")
def drive_form(request, pk=None):
    instance = get_object_or_404(PlacementDrive, pk=pk) if pk else None
    if instance and user_role(request.user) == "recruiter" and instance.created_by_id != request.user.id:
        return HttpResponseForbidden("You cannot edit this drive.")
    form = DriveForm(request.POST or None, instance=instance)
    if user_role(request.user) == "recruiter":
        recruiter_profile, _ = Profile.objects.get_or_create(user=request.user)
        linked_company = Company.objects.filter(name__iexact=recruiter_profile.company_name).first()
        if linked_company:
            form.fields["company"].queryset = Company.objects.filter(pk=linked_company.pk)
    if request.method == "POST" and form.is_valid():
        drive = form.save(commit=False)
        if not drive.created_by_id:
            drive.created_by = request.user
        drive.save()
        messages.success(request, "Placement drive saved.")
        return redirect("manage_drives")
    return render(request, "portal/form_page.html", {"form": form, "title": "Edit placement drive" if instance else "Create placement drive", "subtitle": "Set eligibility criteria and application deadline.", "button": "Save drive"})


@require_POST
@role_required("admin", "recruiter")
def delete_drive(request, pk):
    drive = get_object_or_404(PlacementDrive, pk=pk)
    if user_role(request.user) == "recruiter" and drive.created_by_id != request.user.id:
        return HttpResponseForbidden("You cannot delete this drive.")
    drive.delete(); messages.success(request, "Placement drive deleted.")
    return redirect("manage_drives")


@role_required("admin")
def recruiters(request):
    form = RecruiterCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        company_name = form.cleaned_data["company_name"].strip()
        if not Company.objects.filter(name__iexact=company_name).exists():
            form.add_error("company_name", "Add this company in Company management before creating its recruiter account.")
        else:
            user = form.save()
            Profile.objects.create(user=user, role="recruiter", company_name=company_name)
            messages.success(request, "Recruiter account created.")
            return redirect("recruiters")
    items = Profile.objects.filter(role="recruiter").select_related("user")
    return render(request, "portal/recruiters.html", {"form": form, "recruiters": items})


def handler403(request, exception=None):
    return render(request, "portal/error.html", {"code": "403", "message": "You do not have permission to view this page."}, status=403)


def handler404(request, exception=None):
    return render(request, "portal/error.html", {"code": "404", "message": "We could not find that page."}, status=404)
