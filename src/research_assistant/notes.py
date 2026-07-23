"""JSON-file persistence for research notes."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _notes_path() -> Path:
    notes_dir = os.environ.get("NOTES_DIR", "").strip()
    if notes_dir:
        base = Path(notes_dir)
    else:
        base = Path.home() / ".research-assistant"
    base.mkdir(parents=True, exist_ok=True)
    return base / "notes.json"


def _load_notes() -> list[dict]:
    path = _notes_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_notes(notes: list[dict]) -> None:
    path = _notes_path()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_note(
    title: str,
    content: str,
    arxiv_id: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Create a new note and persist it."""
    notes = _load_notes()
    note = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "arxiv_id": arxiv_id,
        "tags": tags or [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    notes.append(note)
    _save_notes(notes)
    return note


def list_notes(
    tag: str | None = None,
    arxiv_id: str | None = None,
) -> list[dict]:
    """Return all notes, optionally filtered by tag or arxiv_id."""
    notes = _load_notes()
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    if arxiv_id:
        notes = [n for n in notes if n.get("arxiv_id") == arxiv_id]
    return notes


def search_notes(query: str) -> list[dict]:
    """Case-insensitive substring search over title, content, and tags."""
    q = query.lower()
    results = []
    for note in _load_notes():
        searchable = " ".join([
            note.get("title", ""),
            note.get("content", ""),
            " ".join(note.get("tags", [])),
        ]).lower()
        if q in searchable:
            results.append(note)
    return results


def update_note(
    note_id: str,
    content: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update content and/or tags on an existing note."""
    notes = _load_notes()
    for note in notes:
        if note["id"] == note_id:
            if content is not None:
                note["content"] = content
            if tags is not None:
                note["tags"] = tags
            note["updated_at"] = _now()
            _save_notes(notes)
            return note
    raise ValueError(f"Note not found: {note_id!r}")


def delete_note(note_id: str) -> dict:
    """Delete a note by ID and return the deleted note."""
    notes = _load_notes()
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            deleted = notes.pop(i)
            _save_notes(notes)
            return deleted
    raise ValueError(f"Note not found: {note_id!r}")


def get_note(note_id: str) -> dict:
    """Fetch a single note by ID."""
    for note in _load_notes():
        if note["id"] == note_id:
            return note
    raise ValueError(f"Note not found: {note_id!r}")
