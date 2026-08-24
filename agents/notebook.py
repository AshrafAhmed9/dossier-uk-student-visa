"""Durable, correctable case notes; facts and preferences are different data.

The UI can prove collaboration because a factual correction changes the
assessment, while a preference correction changes only the question style.
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class NoteKind(StrEnum):
    FACT = "fact"
    INFERENCE = "inference"
    PREFERENCE = "preference"


@dataclass
class Note:
    key: str
    value: Any
    kind: NoteKind
    provenance: str
    derived_from: str | None = None
    corrected_at: str | None = None


@dataclass
class Notebook:
    notes: dict[str, Note] = field(default_factory=dict)

    def set(self, key: str, value: Any, kind: NoteKind, provenance: str, derived_from: str | None = None) -> Note:
        note = Note(key, value, kind, provenance, derived_from)
        self.notes[key] = note
        return note

    def correct(self, key: str, value: Any) -> Note:
        note = self.notes[key]
        note.value = value
        note.corrected_at = datetime.now(timezone.utc).isoformat()
        return note

    def value(self, key: str, default=None):
        return self.notes.get(key, Note(key, default, NoteKind.FACT, "missing")).value

    def serialize(self) -> list[dict]:
        return [asdict(note) for note in self.notes.values()]
