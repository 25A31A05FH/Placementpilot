from pathlib import Path
import re
from pypdf import PdfReader
from docx import Document

SKILL_KEYWORDS = [
    "python", "java", "c", "c++", "javascript", "typescript", "react", "html", "css",
    "django", "flask", "sql", "mysql", "postgresql", "mongodb", "git", "github",
    "data structures", "algorithms", "machine learning", "deep learning", "pandas",
    "numpy", "power bi", "excel", "linux", "aws", "azure", "docker", "communication",
    "problem solving", "rest api", "node.js", "tailwind", "bootstrap", "figma"
]


def extract_resume_text(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    uploaded_file.seek(0)
    if suffix == ".txt" or suffix == ".md":
        text = uploaded_file.read().decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        reader = PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        document = Document(uploaded_file)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        raise ValueError("Unsupported file. Upload PDF, DOCX, TXT or MD.")
    if not text.strip():
        raise ValueError("No readable text was found. The PDF may be scanned; try a text-based PDF.")
    return text


def find_skills(text):
    lowered = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.add(skill)
    return sorted(found)


def eligibility_for(profile, drive):
    """Evaluate every criterion configured for a placement drive.

    The return shape stays (eligible: bool, reasons: list[str]) so existing
    views and templates can use the same contract.
    """
    reasons = []
    if float(profile.cgpa) < float(drive.min_cgpa):
        reasons.append(f"CGPA {profile.cgpa} is below the required {drive.min_cgpa}.")
    if profile.backlogs > drive.max_backlogs:
        reasons.append(f"You have {profile.backlogs} backlogs; maximum allowed is {drive.max_backlogs}.")
    departments = drive.department_list
    if departments and (profile.department or "").strip().lower() not in departments:
        reasons.append("Your department is not included in this drive.")
    if not drive.is_open:
        reasons.append("This placement drive is closed or past its deadline.")

    profile_skills = {
        item.strip().casefold()
        for item in (profile.skills or "").split(",")
        if item.strip()
    }
    # Compare skills without regard to letter case, but keep the spelling
    # entered by the recruiter in the explanation (for example, "SQL").
    required_skill_names = [
        item.strip()
        for item in (drive.required_skills or "").split(",")
        if item.strip()
    ]
    missing_skills = [
        skill for skill in required_skill_names
        if skill.casefold() not in profile_skills
    ]
    if missing_skills:
        reasons.append(
            "Add these required skills to your profile: "
            + ", ".join(missing_skills)
            + "."
        )

    if drive.min_leetcode_solved and profile.leetcode_solved_count < drive.min_leetcode_solved:
        if not profile.leetcode_username and not profile.leetcode_profile_url:
            reasons.append(f"Add your LeetCode profile and reach at least {drive.min_leetcode_solved} solved problems.")
        else:
            reasons.append(f"LeetCode solved count ({profile.leetcode_solved_count}) is below the required {drive.min_leetcode_solved}.")

    return not reasons, reasons
