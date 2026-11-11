# PLACEMENTPILOT
## Project Abstract

### Abstract
PlacementPilot is a web-based campus placement management portal developed to organize and simplify placement-related activities within an educational institution. The system provides three role-based workspaces: Student, Administrator, and Recruiter. It brings student academic profiles, company information, placement drives, eligibility checks, applications, recruitment updates, and notifications together in one application.

Students can register, maintain their academic and skill profiles, save public coding-platform profile details, browse placement drives, view eligibility reasons, apply to eligible opportunities, track application status, and analyze their resumes. The resume analyzer extracts readable text from PDF, DOCX, TXT, and Markdown files, identifies skills using a predefined keyword list, and compares those skills with configured placement-drive requirements.

Administrators can manage students, companies, recruiters, and placement drives. Recruiters can manage the drives assigned to them, view applicants, and update application statuses. The application uses rule-based eligibility evaluation based on criteria such as minimum CGPA, maximum backlogs, department, drive deadline, required skills, and an optional LeetCode solved-problem threshold.

PlacementPilot is implemented using Python and Django, with Django templates, HTML, CSS, and JavaScript for the user interface. It supports SQLite for local development and can be configured to use MySQL for deployment. The project aims to reduce manual coordination, improve transparency, and make placement information easier to access for students and placement teams.

### Keywords
Campus Placement, Django, Python, Role-Based Access, Eligibility Checking, Resume Analysis, Skill Matching, Placement Drive, Application Tracking.

### Problem Statement
Placement activities often involve separate records for student details, company requirements, eligibility lists, applications, and recruitment updates. Managing these activities manually can cause duplicated work, delays, and difficulty communicating accurate information to students. A centralized system is required to maintain placement data and support a consistent workflow for students, administrators, and recruiters.

### Objectives
1. Provide a centralized platform for placement-related information.
2. Maintain student academic, contact, skills, and resume details.
3. Allow administrators to manage companies, recruiters, students, and placement drives.
4. Evaluate student eligibility using configurable drive criteria.
5. Allow eligible students to submit applications and track their progress.
6. Help identify resume skills and compare them with placement-drive requirements.
7. Notify students when applications are submitted or their status changes.
8. Provide separate workspaces and permissions for different user roles.

### Scope
The current implementation supports role-based access, student profiles, company and drive management, rule-based eligibility, application status tracking, notifications, and keyword-based resume analysis. It is a college-project implementation and should be strengthened with additional operational controls before being used with real institutional records.
