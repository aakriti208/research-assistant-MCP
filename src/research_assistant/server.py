"""FastMCP Research Assistant Server."""

import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .arxiv import get_paper_api, search_arxiv_api
from .notes import (
    delete_note,
    get_note,
    list_notes,
    save_note,
    search_notes,
    update_note,
)
from .summarize import summarize_paper_api

load_dotenv()

mcp = FastMCP(
    name="research-assistant",
    instructions=(
        "A research assistant that can search arXiv papers, summarize them using Claude, "
        "and manage personal research notes."
    ),
)


# ---------------------------------------------------------------------------
# arXiv tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def search_arxiv(
    query: str,
    max_results: int = 10,
    category: str | None = None,
    sort_by: str = "relevance",
) -> list[dict]:
    """Search arXiv for papers matching a query.

    Args:
        query: Search terms (e.g. "attention is all you need").
        max_results: Number of results to return (1–50).
        category: Optional arXiv category filter (e.g. "cs.LG", "physics.hep-th").
        sort_by: Sort order — "relevance", "lastUpdatedDate", or "submittedDate".

    Returns:
        List of papers with arxiv_id, title, authors, abstract, published,
        pdf_url, and categories.
    """
    try:
        return await search_arxiv_api(query, max_results, category, sort_by)
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def get_paper(arxiv_id: str) -> dict:
    """Fetch metadata for a single arXiv paper by its ID.

    Args:
        arxiv_id: The arXiv paper ID (e.g. "2301.00001" or "2301.00001v2").

    Returns:
        Paper metadata: arxiv_id, title, authors, abstract, published,
        pdf_url, categories.
    """
    try:
        return await get_paper_api(arxiv_id)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def summarize_paper(arxiv_id: str, style: str = "concise") -> str:
    """Summarize an arXiv paper using Claude.

    Requires ANTHROPIC_API_KEY to be set in the environment.

    Args:
        arxiv_id: The arXiv paper ID (e.g. "2301.00001").
        style: Summary style — "concise" (3 sentences), "detailed"
               (methods/results/limitations), or "eli5" (plain language).

    Returns:
        A text summary of the paper's abstract.
    """
    return await summarize_paper_api(arxiv_id, style)


# ---------------------------------------------------------------------------
# Note tools
# ---------------------------------------------------------------------------


@mcp.tool()
def save_note_tool(
    title: str,
    content: str,
    arxiv_id: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Save a new research note to local storage.

    Args:
        title: Short descriptive title for the note.
        content: Full text content of the note.
        arxiv_id: Optional arXiv paper ID this note is about.
        tags: Optional list of tag strings for categorization.

    Returns:
        The created note with id, title, content, arxiv_id, tags,
        created_at, and updated_at.
    """
    try:
        return save_note(title, content, arxiv_id, tags)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_notes_tool(
    tag: str | None = None,
    arxiv_id: str | None = None,
) -> list[dict]:
    """List all saved research notes, with optional filters.

    Args:
        tag: Filter notes by this tag (exact match).
        arxiv_id: Filter notes linked to this arXiv paper ID.

    Returns:
        List of matching notes.
    """
    try:
        return list_notes(tag, arxiv_id)
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def search_notes_tool(query: str) -> list[dict]:
    """Search notes by keyword across title, content, and tags.

    Args:
        query: Case-insensitive search string.

    Returns:
        List of notes containing the query string.
    """
    try:
        return search_notes(query)
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def update_note_tool(
    note_id: str,
    content: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update the content and/or tags of an existing note.

    Args:
        note_id: UUID of the note to update.
        content: New content text (omit to keep existing).
        tags: New list of tags (omit to keep existing).

    Returns:
        The updated note.
    """
    try:
        return update_note(note_id, content, tags)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def delete_note_tool(note_id: str) -> dict:
    """Delete a note by its ID.

    Args:
        note_id: UUID of the note to delete.

    Returns:
        The deleted note.
    """
    try:
        return delete_note(note_id)
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("notes://all")
def resource_all_notes() -> str:
    """All saved research notes as a JSON array."""
    return json.dumps(list_notes(), indent=2, ensure_ascii=False)


@mcp.resource("notes://{note_id}")
def resource_single_note(note_id: str) -> str:
    """A single research note by ID, as JSON."""
    try:
        return json.dumps(get_note(note_id), indent=2, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
