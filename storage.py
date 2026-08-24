"""Persist one demo case locally in development and in Firestore on Cloud Run.

The decision engine receives plain ``CaseFacts`` either way. Storage never
decides eligibility; it only preserves user-confirmed input and briefings.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent / "data"


class CaseStore:
    def __init__(self) -> None:
        self.cloud = bool(os.getenv("K_SERVICE")) or os.getenv("DOSSIER_STORAGE") == "firestore"
        self._client = None

    def _document(self, name: str):
        if self._client is None:
            from google.cloud import firestore
            self._client = firestore.Client()
        return self._client.collection("dossier_state").document(name)

    def load(self, name: str) -> dict[str, Any]:
        if self.cloud:
            snapshot = self._document(name).get()
            return snapshot.to_dict() or {} if snapshot.exists else {}
        path = DATA_DIR / f"{name}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def save(self, name: str, value: dict[str, Any]) -> None:
        if self.cloud:
            self._document(name).set(value)
            return
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
