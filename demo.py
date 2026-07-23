"""
Research Assistant MCP — end-to-end demo script.
Run with: uv run python demo.py
"""

import asyncio
import os
import time

from dotenv import load_dotenv

load_dotenv()

# Use a temp dir so demo notes don't pollute the real notes file
os.environ["NOTES_DIR"] = "/tmp/research-assistant-demo"

from src.research_assistant.arxiv import get_paper_api, search_arxiv_api
from src.research_assistant.notes import list_notes, save_note
from src.research_assistant.summarize import summarize_paper_api

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"


def header(text: str) -> None:
    width = 60
    print(f"\n{CYAN}{BOLD}{'─' * width}{RESET}")
    print(f"{CYAN}{BOLD}  {text}{RESET}")
    print(f"{CYAN}{BOLD}{'─' * width}{RESET}\n")


def step(text: str) -> None:
    print(f"{YELLOW}▶ {text}{RESET}")
    time.sleep(0.4)


def result(label: str, value: str) -> None:
    print(f"  {BOLD}{label}:{RESET} {value}")


def divider() -> None:
    print(f"\n{DIM}{'·' * 60}{RESET}\n")


async def main() -> None:
    print(f"\n{BOLD}{CYAN}")
    print("  ██████╗ ███████╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗")
    print("  ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║")
    print("  ██████╔╝█████╗  ███████╗█████╗  ███████║██████╔╝██║     ███████║")
    print("  ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║")
    print("  ██║  ██║███████╗███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║")
    print("  ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝")
    print(f"  ASSISTANT MCP — Demo{RESET}\n")
    time.sleep(1)

    # ── 1. Search arXiv ──────────────────────────────────────────────────────
    header("1 · Search arXiv")
    query = "retrieval augmented generation"
    step(f'Searching arXiv for "{query}" ...')
    results = await search_arxiv_api(query, max_results=3, sort_by="relevance")
    print()
    for i, p in enumerate(results, 1):
        result(f"  {i}", p["title"])
        print(f"     {DIM}{p['arxiv_id']}  ·  {p['published'][:10]}  ·  {', '.join(p['authors'][:2])}{RESET}")
    time.sleep(0.5)

    # ── 2. Get paper ──────────────────────────────────────────────────────────
    divider()
    header("2 · Get Paper Details")
    target_id = "1706.03762"
    step(f"Fetching metadata for {target_id} (Attention Is All You Need) ...")
    paper = await get_paper_api(target_id)
    print()
    result("Title", paper["title"])
    result("Authors", ", ".join(paper["authors"][:3]))
    result("Published", paper["published"][:10])
    result("Categories", ", ".join(paper["categories"][:3]))
    result("PDF", paper["pdf_url"])
    time.sleep(0.5)

    # ── 3. Summarize ─────────────────────────────────────────────────────────
    divider()
    header("3 · Summarize Paper")
    step(f'Summarizing {target_id} in "concise" style via Claude ...')
    summary = await summarize_paper_api(target_id, style="concise")
    print()
    if summary.startswith("Error"):
        print(f"  {YELLOW}{summary}{RESET}")
    else:
        for line in summary.split(". "):
            print(f"  {line.strip()}.")
    time.sleep(0.5)

    # ── 4. Save note ──────────────────────────────────────────────────────────
    divider()
    header("4 · Save Note")
    step("Saving note with summary ...")
    note = save_note(
        title=paper["title"],
        content=summary if not summary.startswith("Error") else "Summary unavailable — add ANTHROPIC_API_KEY.",
        arxiv_id=target_id,
        tags=["transformers", "attention", "nlp"],
    )
    print()
    result("Note ID", note["id"])
    result("Title", note["title"])
    result("Tags", ", ".join(note["tags"]))
    result("Saved at", note["created_at"])
    time.sleep(0.5)

    # ── 5. List notes ─────────────────────────────────────────────────────────
    divider()
    header("5 · List Notes")
    step("Listing all saved notes ...")
    notes = list_notes()
    print()
    result("Total notes", str(len(notes)))
    for n in notes:
        print(f"  {DIM}[{n['id'][:8]}...]{RESET} {n['title']}")
    time.sleep(0.5)

    # ── 6. Export ─────────────────────────────────────────────────────────────
    divider()
    header("6 · Export Notes")
    export_dir = "/tmp/research-assistant-demo"
    for fmt in ("json", "markdown", "csv"):
        step(f"Exporting as {fmt.upper()} ...")
        from pathlib import Path
        import csv, io, json as _json

        dest = Path(export_dir) / f"notes.{('md' if fmt == 'markdown' else fmt)}"
        if fmt == "json":
            dest.write_text(_json.dumps(notes, indent=2, ensure_ascii=False))
        elif fmt == "markdown":
            lines = ["# Research Notes\n"]
            for n in notes:
                lines += [f"## {n['title']}", f"\n{n['content']}\n", "---\n"]
            dest.write_text("\n".join(lines))
        elif fmt == "csv":
            buf = io.StringIO()
            fields = ["id", "title", "arxiv_id", "tags", "content", "created_at", "updated_at"]
            w = csv.DictWriter(buf, fieldnames=fields)
            w.writeheader()
            for n in notes:
                w.writerow({**n, "tags": "|".join(n.get("tags", []))})
            dest.write_text(buf.getvalue())
        result("Saved", str(dest))
    time.sleep(0.5)

    # ── Done ──────────────────────────────────────────────────────────────────
    print(f"\n{GREEN}{BOLD}  ✓ Demo complete!{RESET}\n")
    print(f"  {DIM}All exported files are in {export_dir}/{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
