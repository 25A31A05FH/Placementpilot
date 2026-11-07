from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from .models import Profile, Company, PlacementDrive, Application
from .utils import eligibility_for

class PlacementPilotFlowTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="hanish", password="TestPass123!", email="hanish@example.test")
        self.profile = Profile.objects.create(user=self.student, role="student", department="CSE", cgpa=8.2, backlogs=0)
        self.company = Company.objects.create(name="Example Tech")
        self.drive = PlacementDrive.objects.create(title="Python Developer", company=self.company, eligible_departments="CSE, IT", min_cgpa=7.0, max_backlogs=0, deadline=timezone.localdate() + timedelta(days=10))

    def test_eligible_student_passes(self):
        self.assertEqual(eligibility_for(self.profile, self.drive), (True, []))

    def test_low_cgpa_student_fails(self):
        self.profile.cgpa = 6.0
        self.profile.save()
        eligible, reasons = eligibility_for(self.profile, self.drive)
        self.assertFalse(eligible)
        self.assertTrue(any("CGPA" in reason for reason in reasons))

    def test_leetcode_threshold_is_part_of_eligibility(self):
        self.drive.min_leetcode_solved = 30
        self.drive.save()
        eligible, reasons = eligibility_for(self.profile, self.drive)
        self.assertFalse(eligible)
        self.assertTrue(any("LeetCode" in reason for reason in reasons))

        self.profile.leetcode_username = "hanish_lc"
        self.profile.leetcode_solved_count = 40
        self.profile.save()
        self.assertEqual(eligibility_for(self.profile, self.drive), (True, []))

    def test_missing_required_skill_blocks_eligibility(self):
        self.drive.required_skills = "Python, SQL"
        self.drive.save()
        self.profile.skills = "Python"
        self.profile.save()
        eligible, reasons = eligibility_for(self.profile, self.drive)
        self.assertFalse(eligible)
        self.assertTrue(any("SQL" in reason for reason in reasons))

    def test_student_can_see_eligible_drive_list(self):
        self.client.login(username="hanish", password="TestPass123!")
        response = self.client.get("/eligible-drives/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")

    def test_remember_me_keeps_session_for_fourteen_days(self):
        response = self.client.post("/login/", {
            "username": "hanish", "password": "TestPass123!", "remember_me": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 14)
        self.assertIn("pp_remembered_username", response.cookies)

    def test_login_without_remember_me_expires_on_browser_close(self):
        response = self.client.post("/login/", {
            "username": "hanish", "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_student_can_apply_once(self):
        self.client.login(username="hanish", password="TestPass123!")
        response = self.client.post(f"/drives/{self.drive.pk}/apply/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Application.objects.filter(student=self.student, drive=self.drive).count(), 1)

    def test_login_page_offers_separate_student_and_admin_portals(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student portal")
        self.assertContains(response, "Administrator portal")

    def test_student_cannot_sign_in_through_admin_portal(self):
        response = self.client.post("/admin-login/", {
            "username": "hanish", "password": "TestPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "does not have access to the Administrator portal")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_can_sign_in_and_manage_drives(self):
        admin_user = User.objects.create_user(username="placement_admin", password="AdminPass123!")
        Profile.objects.create(user=admin_user, role="admin")
        response = self.client.post("/admin-login/", {
            "username": "placement_admin", "password": "AdminPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")
        self.assertEqual(self.client.get("/manage/drives/").status_code, 200)

    def test_admin_can_view_students_who_applied_to_a_drive(self):
        Application.objects.create(student=self.student, drive=self.drive)
        admin_user = User.objects.create_user(username="placement_admin", password="AdminPass123!")
        Profile.objects.create(user=admin_user, role="admin")
        self.client.force_login(admin_user)
        response = self.client.get(f"/manage/drives/{self.drive.pk}/applicants/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hanish")
        self.assertContains(response, "Student applications")

    def test_student_cannot_view_admin_drive_applicants_page(self):
        self.client.login(username="hanish", password="TestPass123!")
        response = self.client.get(f"/manage/drives/{self.drive.pk}/applicants/")
        self.assertEqual(response.status_code, 302)

    def test_account_without_profile_can_use_student_portal(self):
        unprofiled = User.objects.create_user(username="new_student", password="StudentPass123!")
        response = self.client.post("/student-login/", {
            "username": "new_student", "password": "StudentPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")

    def test_promote_placement_admin_command_assigns_admin_role_without_changing_password(self):
        from django.core.management import call_command
        admin_user = User.objects.create_user(username="promoted_user", password="ExistingPass123!")
        call_command("promote_placement_admin", username="promoted_user")
        admin_user.refresh_from_db()
        admin_user.profile.refresh_from_db()
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.profile.role, "admin")
        self.assertTrue(admin_user.check_password("ExistingPass123!"))

    def test_student_can_save_github_and_hackerrank_profile_urls(self):
        from .forms import ProfileForm
        form = ProfileForm(data={
            "first_name": "Hari", "last_name": "Hanish", "email": self.student.email,
            "phone": "", "department": "CSE", "cgpa": "8.20", "backlogs": "0",
            "graduation_year": "2029", "skills": "Python, SQL",
            "github_profile_url": "https://github.com/hanish",
            "hackerrank_profile_url": "https://www.hackerrank.com/profile/hanish",
            "leetcode_username": "hanish_lc",
            "leetcode_profile_url": "https://leetcode.com/u/hanish_lc/",
            "leetcode_solved_count": "50",
        }, instance=self.profile, user=self.student)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.github_profile_url, "https://github.com/hanish")
        self.assertEqual(saved.hackerrank_profile_url, "https://www.hackerrank.com/profile/hanish")

    def test_invalid_github_profile_url_is_rejected(self):
        from .forms import ProfileForm
        form = ProfileForm(data={
            "first_name": "Hari", "last_name": "", "email": self.student.email,
            "phone": "", "department": "CSE", "cgpa": "8.20", "backlogs": "0",
            "graduation_year": "2029", "skills": "", "github_profile_url": "not-a-url",
            "hackerrank_profile_url": "", "leetcode_username": "",
            "leetcode_profile_url": "", "leetcode_solved_count": "0",
        }, instance=self.profile, user=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn("github_profile_url", form.errors)

    def test_admin_provision_command_creates_account_and_does_not_reset_existing_password(self):
        import os
        from unittest.mock import patch
        from django.core.management import call_command
        with patch.dict(os.environ, {
            "PLACEMENT_ADMIN_USERNAME": "placement_admin_2026",
            "PLACEMENT_ADMIN_PASSWORD": "OneTimeAdminPass!2026",
        }):
            call_command("promote_placement_admin")
        admin_user = User.objects.get(username="placement_admin_2026")
        admin_user.profile.refresh_from_db()
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.profile.role, "admin")
        self.assertTrue(admin_user.check_password("OneTimeAdminPass!2026"))
        with patch.dict(os.environ, {
            "PLACEMENT_ADMIN_USERNAME": "placement_admin_2026",
            "PLACEMENT_ADMIN_PASSWORD": "ShouldNotReplace!2026",
        }):
            call_command("promote_placement_admin")
        admin_user.refresh_from_db()
        self.assertTrue(admin_user.check_password("OneTimeAdminPass!2026"))

