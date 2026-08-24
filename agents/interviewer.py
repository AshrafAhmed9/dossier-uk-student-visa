"""The deterministic engine chooses what to ask; Gemini only words it.

This keeps a high-information interview without allowing model output to
change legal requirements or case status.
"""
from dataclasses import dataclass
from agents.notebook import Notebook


QUESTIONS = {
    "study_in_london": "Will your course be in London?",
    "course_months": "How many months is your course?",
    "outstanding_course_fees_gbp": "What course fees remain outstanding on your CAS, in GBP?",
    "bank_balance_gbp": "What is the current available balance in the account you plan to rely on, in GBP?",
    "funds_held_since": "On what date did the balance first stay at or above the required amount?",
    "evidence_closing_date": "What is the closing date on your most recent bank evidence?",
    "months_in_uk_with_permission": "How many months have you lived in the UK with permission?",
    "applying_permission_to_stay": "Are you applying from inside the UK for permission to stay?",
}


@dataclass(frozen=True)
class NextQuestion:
    key: str
    question: str
    reason: str


def choose_next_question(notebook: Notebook) -> NextQuestion | None:
    # Exemption first because it can prune the rest of the financial graph.
    for key in QUESTIONS:
        if key not in notebook.notes:
            style = notebook.value("question_style", "clear and direct")
            return NextQuestion(key, f"{QUESTIONS[key]} ({style}.)", "This fact resolves the next highest-impact requirement.")
    return None
