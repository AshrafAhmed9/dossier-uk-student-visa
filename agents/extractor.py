"""Evidence extraction is confirmation-first; nothing extracted becomes a fact silently."""
from dataclasses import dataclass
from datetime import date
import json
import re


@dataclass(frozen=True)
class ExtractedEvidence:
    account_holder: str | None = None
    institution: str | None = None
    closing_balance_gbp: int | None = None
    closing_date: date | None = None
    needs_confirmation: bool = True


def extraction_prompt() -> str:
    return (
        "You extract candidate facts from UK student-visa financial evidence. "
        "Read only the supplied image. Return exactly one JSON object, with no markdown and no commentary, "
        "using these keys: account_holder (string or null), institution (string or null), "
        "closing_balance_gbp (integer GBP amount or null), closing_date (YYYY-MM-DD or null). "
        "Use null when a value is missing, ambiguous, or not clearly visible. Do not infer a value. "
        "This is a candidate extraction only; the user must confirm it before it becomes a fact."
    )


def _json_object(text: str) -> dict:
    """Parse Gemini's JSON while tolerating a fenced response from older models."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("The document could not be read as structured evidence. Please try a clearer image.") from exc
    if not isinstance(value, dict):
        raise ValueError("The document could not be read as structured evidence. Please try a clearer image.")
    return value


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("The document returned an invalid text value. Please try a clearer image.")
    value = value.strip()
    return value or None


def _optional_balance(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("The document returned an invalid balance. Please try a clearer image.")
    try:
        balance = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("The document returned an invalid balance. Please try a clearer image.") from exc
    if balance < 0:
        raise ValueError("The document returned an invalid balance. Please try a clearer image.")
    return balance


def _optional_date(value: object) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("The document returned an invalid date. Please try a clearer image.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("The document returned an invalid date. Please try a clearer image.") from exc


def extract(image_bytes: bytes, mime_type: str) -> ExtractedEvidence:
    """Extract candidate evidence from an image through the shared Vertex client.

    The returned object deliberately remains a candidate. Persistence and conversion
    to case facts happen only in the console's explicit confirmation route.
    """
    if not image_bytes:
        raise ValueError("The uploaded image is empty.")
    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Upload a JPEG, PNG, or WebP image.")

    # Keep the module importable for local deterministic tests when the optional
    # Vertex SDK is not installed. Cloud dependencies are required only on use.
    from google.genai import types
    from agents.shared.vertex import generate

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    contents = [types.Content(role="user", parts=[image_part])]
    response = generate(contents=contents, system_instruction=extraction_prompt())
    payload = _json_object((response.text or "").strip())
    return ExtractedEvidence(
        account_holder=_optional_text(payload.get("account_holder")),
        institution=_optional_text(payload.get("institution")),
        closing_balance_gbp=_optional_balance(payload.get("closing_balance_gbp")),
        closing_date=_optional_date(payload.get("closing_date")),
    )
