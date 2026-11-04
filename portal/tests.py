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
