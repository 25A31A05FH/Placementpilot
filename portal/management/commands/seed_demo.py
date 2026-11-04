from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from portal.models import Profile, Company, PlacementDrive, Application

class Command(BaseCommand):
    help = "Create fictional companies, placement drives and optional demo accounts."

    def add_arguments(self, parser):
        parser.add_argument("--with-users", action="store_true", help="Also create demo student and recruiter accounts.")

    def handle(self, *args, **options):
        student = recruiter = None
        if options["with_users"]:
            student, created = User.objects.get_or_create(username="student_demo", defaults={"email": "student@example.test", "first_name": "Demo", "last_name": "Student"})
            if created:
                student.set_password("DemoPass123!"); student.save()
            Profile.objects.update_or_create(user=student, defaults={"role": "student", "department": "CSE", "cgpa": 8.2, "backlogs": 0, "graduation_year": timezone.localdate().year + 2, "skills": "Python, SQL, data structures, communication"})
            recruiter, created = User.objects.get_or_create(username="recruiter_demo", defaults={"email": "recruiter@example.test", "first_name": "Demo Recruiter"})
            if created:
                recruiter.set_password("DemoPass123!"); recruiter.save()
            Profile.objects.update_or_create(user=recruiter, defaults={"role": "recruiter", "company_name": "Nova Systems"})

        companies_data = [
            ("Nova Systems", "Information Technology", "Hyderabad"),
            ("BluePeak Analytics", "Data & Analytics", "Bengaluru"),
            ("Aster Digital", "Software Services", "Pune"),
        ]
        companies = {}
        for name, industry, location in companies_data:
            company, _ = Company.objects.get_or_create(name=name, defaults={"industry": industry, "location": location})
            companies[name] = company
        drives_data = [
            ("Graduate Software Engineer", "Nova Systems", "Python, SQL, data structures", 7.0, 0, 6.5, 50),
            ("Junior Data Analyst", "BluePeak Analytics", "Python, SQL, excel, communication", 6.0, 1, 5.0, 15),
            ("Frontend Developer Trainee", "Aster Digital", "JavaScript, react, html, css", 7.0, 0, 4.5, 30),
        ]
        first_drive = None
        for title, company_name, skills, cgpa, backlogs, package, leetcode_min in drives_data:
            drive, _ = PlacementDrive.objects.get_or_create(title=title, company=companies[company_name], defaults={
                "description": "Fictional sample placement drive for demonstrating PlacementPilot workflows.",
                "eligible_departments": "CSE, IT, ECE",
                "min_cgpa": cgpa,
                "max_backlogs": backlogs,
                "package_lpa": package,
                "required_skills": skills,
                "min_leetcode_solved": leetcode_min,
                "deadline": timezone.localdate() + timedelta(days=30),
                "is_active": True,
                "created_by": recruiter if recruiter and company_name == "Nova Systems" else None,
            })
            if first_drive is None:
                first_drive = drive
        if student and first_drive:
            Application.objects.get_or_create(student=student, drive=first_drive)
        self.stdout.write(self.style.SUCCESS("Sample companies and drives are ready. All sample organisations and vacancies are fictional."))
        if options["with_users"]:
            self.stdout.write("Demo student: student_demo / DemoPass123!")
            self.stdout.write("Demo recruiter: recruiter_demo / DemoPass123!")
