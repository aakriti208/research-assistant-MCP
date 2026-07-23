"""arXiv Atom API client with rate limiting."""

import asyncio
import time
from typing import Any

import feedparser
import httpx

ARXIV_API_URL = "https://export.arxiv.org/api/query"
_last_call_time: float = 0.0
_RATE_LIMIT_SECONDS = 3.0


def _sort_by_param(sort_by: str) -> str:
    mapping = {
        "relevance": "relevance",
        "lastUpdatedDate": "lastUpdatedDate",
        "submittedDate": "submittedDate",
    }
    return mapping.get(sort_by, "relevance")


def _parse_entry(entry: Any) -> dict:
    arxiv_id = entry.get("id", "")
    if "/abs/" in arxiv_id:
        arxiv_id = arxiv_id.split("/abs/")[-1].strip()

    authors = [a.get("name", "") for a in entry.get("authors", [])]
    categories = [t.get("term", "") for t in entry.get("tags", [])]

    pdf_url = ""
    for link in entry.get("links", []):
        if link.get("type") == "application/pdf":
            pdf_url = link.get("href", "")
            break
    if not pdf_url:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

    return {
        "arxiv_id": arxiv_id,
        "title": entry.get("title", "").replace("\n", " ").strip(),
        "authors": authors,
        "abstract": entry.get("summary", "").replace("\n", " ").strip(),
        "published": entry.get("published", ""),
        "pdf_url": pdf_url,
        "categories": categories,
    }


async def _rate_limited_get(url: str, params: dict) -> httpx.Response:
    global _last_call_time
    elapsed = time.monotonic() - _last_call_time
    if elapsed < _RATE_LIMIT_SECONDS:
        await asyncio.sleep(_RATE_LIMIT_SECONDS - elapsed)
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(url, params=params)
    _last_call_time = time.monotonic()
    response.raise_for_status()
    return response


async def search_arxiv_api(
    query: str,
    max_results: int = 10,
    category: str | None = None,
    sort_by: str = "relevance",
) -> list[dict]:
    """Fetch papers from arXiv matching query; returns parsed list of dicts."""
    if category:
        search_query = f"cat:{category} AND all:{query}"
    else:
        search_query = f"all:{query}"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": _sort_by_param(sort_by),
        "sortOrder": "descending",
    }

    response = await _rate_limited_get(ARXIV_API_URL, params)
    feed = feedparser.parse(response.text)

    if feed.get("bozo") and not feed.entries:
        raise ValueError(f"Failed to parse arXiv response: {feed.get('bozo_exception')}")

    return [_parse_entry(e) for e in feed.entries]


async def get_paper_api(arxiv_id: str) -> dict:
    """Fetch a single paper's metadata by arXiv ID."""
    bare_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

    params = {
        "id_list": bare_id,
        "max_results": 1,
    }

    response = await _rate_limited_get(ARXIV_API_URL, params)
    feed = feedparser.parse(response.text)

    if not feed.entries:
        raise ValueError(f"No paper found for arXiv ID: {arxiv_id!r}")

    return _parse_entry(feed.entries[0])
