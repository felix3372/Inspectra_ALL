import re

# Job level mapping in descending order of seniority
JOB_LEVELS = [
    ("C-Level", [
        r"\bceo\b", r"\bc[ -]?level\b", r"\bc[ -]?suite\b", r"\bcoo\b", r"\bcfo\b", r"\bcto\b", r"\bcmo\b", r"\bciso\b",
        r"\bcso\b", r"\bcio\b", r"\bcdo\b", r"\bcro\b", r"\bcco\b", r"\bchro\b", r"\bchief\b"
    ]),
    ("VP", [
        r"\bvp\b", r"\bsvp\b", r"\bavp\b", r"\bev[ -]?p\b", r"vice president", r"senior vice president",
        r"assistant vice president", r"associate vice president", r"executive vice president"
    ]),
    ("Director", [
        r"\bdirector\b", r"global director", r"director of", r"managing director", r"\bcontroller\b",
    ]),
    ("Head", [
        r"\bhead of\b", r"\bhead\b"
    ]),
    ("Manager", [
        r"\bmanager\b", r"\bsupervisor\b", r"\blead\b"
    ]),
    ("Staff", [
        r"\bengineer\b", r"\bdeveloper\b", r"\banalyst\b", r"\bspecialist\b", r"\bconsultant\b",
        r"\badmin\b", r"\bcoordinator\b", r"\bassociate\b", r"\brepresentative\b", r"\bassistant\b",
        r"\btechnician\b", r"\bdesigner\b", r"\barchitect\b", r"\bscientist\b", r"\bresearcher\b", r"\bAdministrator\b"
    ]),
    ("Other", [])  # Fallback if none matched
]

def job_level_from_title(title, *args, **kwargs):
    """
    Returns the highest job level found in the title, based on your categories.
    Ignores extra arguments for pipeline compatibility.
    """
    normalized = str(title or "").lower().strip()
    if not normalized or normalized in ["-", "n/a", "none"]:
        return "Unknown"
    for level, patterns in JOB_LEVELS:
        for pat in patterns:
            if re.search(pat, normalized):
                return level
    return "Other"

def job_level_validator(wb, ws):
    headers = [cell.value for cell in ws[1]]
    # Ensure both required columns exist
    if "Job Title" not in headers or "Job Level" not in headers:
        # Optionally, raise an error or just skip this validator
        return wb, ws

    col_title = headers.index("Job Title") + 1
    col_level = headers.index("Job Level") + 1

    for row in range(2, ws.max_row + 1):
        title = ws.cell(row, col_title).value
        level = job_level_from_title(title)
        ws.cell(row, col_level).value = level

    return wb, ws
