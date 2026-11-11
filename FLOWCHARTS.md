# PLACEMENTPILOT
## Flowcharts

The diagrams below use Mermaid syntax. They can be viewed in GitHub, VS Code with a Mermaid extension, or a Mermaid-compatible Markdown viewer.

---

## 1. Overall System Flow

```mermaid
flowchart TD
    A([Start]) --> B[Open PlacementPilot]
    B --> C{Existing account?}
    C -- No --> D[Student registration]
    D --> E[Create user and student profile]
    C -- Yes --> F[Choose login portal]
    E --> F
    F --> G[Authenticate credentials]
    G --> H{Credentials valid?}
    H -- No --> I[Show login error]
    I --> F
    H -- Yes --> J[Identify user role]
    J --> K{Role}
    K -- Student --> L[Student dashboard]
    K -- Administrator --> M[Administrator dashboard]
    K -- Recruiter --> N[Recruiter dashboard]
    L --> O[Profile, drives, resume, applications]
    M --> P[Manage students, companies, recruiters, drives]
    N --> Q[Manage own drives and applicants]
    O --> R[Database updates and notifications]
    P --> R
    Q --> R
    R --> S([End])
```

---

## 2. Student Eligibility Flow

```mermaid
flowchart TD
    A([Start]) --> B[Read student profile and placement drive]
    B --> C{CGPA meets minimum?}
    C -- No --> C1[Add CGPA failure reason]
    C -- Yes --> D{Backlogs within limit?}
    C1 --> D
    D -- No --> D1[Add backlog failure reason]
    D -- Yes --> E{Department allowed?}
    D1 --> E
    E -- No --> E1[Add department failure reason]
    E -- Yes --> F{Drive active and deadline valid?}
    E1 --> F
    F -- No --> F1[Add closed-drive reason]
    F -- Yes --> G[Compare required skills]
    F1 --> G
    G --> H{Any required skills missing?}
    H -- Yes --> H1[Add missing-skill reason]
    H -- No --> I{LeetCode threshold configured?}
    H1 --> I
    I -- No --> J{Any reasons collected?}
    I -- Yes --> K{Solved count meets threshold?}
    K -- No --> K1[Add LeetCode reason]
    K -- Yes --> J
    K1 --> J
    J -- No --> L[Mark eligible]
    J -- Yes --> M[Mark not eligible and show reasons]
    L --> N([End])
    M --> N
```

---

## 3. Application Submission Flow

```mermaid
flowchart TD
    A([Student opens a drive]) --> B[Load student profile]
    B --> C[Evaluate eligibility]
    C --> D{Eligible?}
    D -- No --> E[Display reasons and disable application]
    D -- Yes --> F[Check existing application]
    F --> G{Already applied?}
    G -- Yes --> H[Display already-applied message]
    G -- No --> I[Create application with Pending status]
    I --> J[Create submission notification]
    J --> K[Display confirmation]
    E --> L([End])
    H --> L
    K --> L
```

---

## 4. Resume Analyzer Flow

```mermaid
flowchart TD
    A([Start]) --> B[Choose or reuse resume]
    B --> C{File present and within size limit?}
    C -- No --> D[Show validation error]
    C -- Yes --> E{Supported extension?}
    E -- No --> F[Show unsupported file error]
    E -- Yes --> G[Extract text from PDF, DOCX, TXT or MD]
    G --> H{Readable text found?}
    H -- No --> I[Show no-readable-text error]
    H -- Yes --> J[Search predefined skill keywords]
    J --> K[Compare with student profile skills]
    K --> L[Compare found skills with active drive requirements]
    L --> M[Calculate skill gaps and match percentages]
    M --> N[Display analysis results]
    D --> O([End])
    F --> O
    I --> O
    N --> O
```

---

## 5. Application Status Update Flow

```mermaid
flowchart TD
    A([Start]) --> B[Admin or recruiter opens application]
    B --> C{Authorized role?}
    C -- No --> D[Reject access]
    C -- Yes --> E{Recruiter owns this drive?}
    E -- No, recruiter --> D
    E -- Yes or administrator --> F[Select new status]
    F --> G[Validate and save status]
    G --> H[Create notification for student]
    H --> I[Show update confirmation]
    D --> J([End])
    I --> J
```
