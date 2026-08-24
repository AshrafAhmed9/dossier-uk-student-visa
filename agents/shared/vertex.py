"""Optional Vertex client for interview phrasing and document extraction only.

The assessment engine never imports this module. CRUCIBLE-style retries are
kept separate so unavailable billing/API access cannot affect eligibility.
"""
import os
import time
from google import genai
from google.genai import errors as genai_errors, types

PROJECT_ID = os.environ.get("DOSSIER_PROJECT", "dossier-visa-copilot-2026")
LOCATION = "global"
FLASH_MODEL = "gemini-3.5-flash"
PRO_MODEL = "gemini-3.1-pro-preview"
_client = None


class DailyQuotaExhausted(RuntimeError):
    pass


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    return _client


def call_with_retry(fn, max_attempts=4, base_delay=3):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except genai_errors.ClientError as exc:
            if "RESOURCE_EXHAUSTED" in str(exc) and "PerDay" in str(exc):
                raise DailyQuotaExhausted(str(exc)) from exc
            if attempt == max_attempts:
                raise
            time.sleep(base_delay * attempt)
        except genai_errors.ServerError:
            if attempt == max_attempts:
                raise
            time.sleep(base_delay * attempt)


def generate(contents, system_instruction: str, model: str = FLASH_MODEL):
    return call_with_retry(lambda: get_client().models.generate_content(
        model=model, contents=contents, config=types.GenerateContentConfig(system_instruction=system_instruction)
    ))
