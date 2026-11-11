# PLACEMENTPILOT
## Algorithms and Pseudocode

This document describes the principal logic present in the PlacementPilot repository.

---

## 1. Student Eligibility Evaluation

### Purpose
Determine whether a student's profile satisfies the conditions configured for a placement drive.

### Inputs
- Student profile: CGPA, backlogs, department, skills, LeetCode solved count.
- Placement drive: minimum CGPA, maximum backlogs, eligible departments, deadline/active status, required skills, minimum LeetCode solved count.

### Algorithm
1. Start with an empty list of reasons.
2. Compare the student's CGPA with the drive's minimum CGPA. Add a reason if it is too low.
3. Compare the student's backlog count with the permitted maximum. Add a reason if it exceeds the limit.
4. If the drive specifies departments, check whether the student's department is included.
5. Check whether the drive is active and its deadline has not passed.
6. Convert the student's listed skills into a normalized set and compare them with the required skills.
7. If the drive specifies a non-zero LeetCode threshold, compare the student's stored solved count with that threshold.
8. If no reasons were added, return eligible = TRUE. Otherwise return eligible = FALSE with the reasons.

### Pseudocode
```text
FUNCTION eligibility_for(profile, drive)
    reasons = []

    IF profile.cgpa < drive.min_cgpa
        ADD "CGPA requirement not met" TO reasons

    IF profile.backlogs > drive.max_backlogs
        ADD "Backlog limit exceeded" TO reasons

    IF drive has department restrictions
       AND profile.department is not in allowed departments
        ADD "Department not eligible" TO reasons

    IF drive is inactive OR deadline has passed
        ADD "Drive is closed" TO reasons

    FOR each required skill in drive.required_skills
        IF required skill is not in profile.skills
            ADD missing-skill reason TO reasons

    IF drive.min_leetcode_solved > 0
       AND profile.leetcode_solved_count < drive.min_leetcode_solved
        ADD "LeetCode threshold not met" TO reasons

    IF reasons is empty
        RETURN (TRUE, [])
    ELSE
        RETURN (FALSE, reasons)
END FUNCTION
```

### Complexity
Let `S` be the number of required skills for a drive and `P` the number of skills stored in the student profile. Profile skills are converted to a set; membership checks are expected O(1) on average. The skill comparison is expected O(S) after set creation. With profile normalization included, the overall skill-check work is O(P + S). The other checks are constant-time. Therefore, one eligibility evaluation is approximately O(P + S).

**Implementation note:** The current `eligibility_for` function compares the stored LeetCode solved count with the configured threshold. A verification flag exists on the profile and is used to communicate verification state in the application, but the eligibility function itself does not block eligibility solely because the flag is unverified.

---

## 2. Eligible Placement Drive Listing

### Purpose
Display active, non-expired placement drives and optionally filter the list to only those for which the logged-in student meets the configured criteria.

### Pseudocode
```text
FUNCTION list_drives(student, filters)
    drives = active drives whose deadline has not passed

    IF search text exists
        filter drives by title or company name

    IF department filter exists
        keep drives open to that department or all departments

    FOR each drive in drives
        (eligible, reasons) = eligibility_for(student.profile, drive)
        store eligibility result for display

    IF eligible-only filter is enabled
        keep only drives marked eligible

    RETURN drives
END FUNCTION
```

### Complexity
If there are `D` candidate drives and each eligibility evaluation costs O(P + S), computing eligibility for all drives is approximately O(D × (P + S)), excluding database query and rendering costs.

---

## 3. Application Submission

### Purpose
Allow an eligible student to apply to a placement drive while preventing duplicate applications for the same student-drive pair.

### Pseudocode
```text
FUNCTION apply_to_drive(student, drive)
    profile = get_or_create_profile(student)
    (eligible, reasons) = eligibility_for(profile, drive)

    IF eligible is FALSE
        show reasons
        STOP

    application, created = get_or_create_application(student, drive)

    IF created is TRUE
        create notification for student
        show application submitted message
    ELSE
        show already-applied message
END FUNCTION
```

### Complexity
The eligibility calculation is approximately O(P + S). Application lookup/creation is handled through the database and is supported by a unique database constraint on `(student, drive)`.

---

## 4. Application Status Update

### Purpose
Allow an authorized administrator or the recruiter responsible for a drive to update an application.

### Pseudocode
```text
FUNCTION update_application(actor, application, new_status)
    IF actor is not administrator AND actor is not recruiter
        DENY access

    IF actor is recruiter AND application.drive.created_by != actor
        DENY access

    validate new_status
    save application status
    create notification for the student
    show success message
END FUNCTION
```

### Complexity
The authorization checks and status assignment are constant-time after the relevant records are retrieved, excluding database operations.

---

## 5. Resume Text Extraction and Skill Matching

### Purpose
Extract readable text from a supported resume and identify skills using a predefined keyword catalogue.

### Supported file types
- PDF
- DOCX
- TXT
- Markdown (`.md`)

### Pseudocode
```text
FUNCTION analyze_resume(file, student_profile, active_drives)
    validate file type and file size
    text = extract readable text from file

    IF text is empty
        return readable-text error

    found_skills = find predefined keywords in lowercase text

    IF student profile has listed skills
        matched_skills = found_skills INTERSECTION profile skills
        missing_profile_skills = found_skills - matched_skills
    ELSE
        matched_skills = found_skills
        missing_profile_skills = []

    FOR each active drive
        gaps = drive.required_skills - found_skills
        IF drive has no required skills
            match percentage = 100
        ELSE
            match percentage =
                100 * (number of required skills - number of gaps)
                / number of required skills

    RETURN found skills, matched skills, missing skills,
           and a limited list of drive comparisons
END FUNCTION
```

### Complexity
Let `T` be the number of characters in extracted resume text, `K` the number of configured skill keywords, `D` the number of active drives, and `R` the average number of required skills per drive. Keyword detection scans the text for each configured keyword, so a simple upper-bound description is O(K × T) for this implementation. Drive comparison is approximately O(D × R), excluding text extraction library costs.

**Important:** This is keyword-based assistance. It is not an AI resume score, semantic skill assessment, or proof that a candidate is proficient in a skill.
