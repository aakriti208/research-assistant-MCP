# Research Assistant MCP

A Python MCP server that gives Claude (and any MCP-compatible client) tools to search arXiv papers, summarize them using Claude AI, and manage persistent research notes.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)

[![asciicast](https://asciinema.org/a/G8fxQJAaVFUe9iq1.svg)](https://asciinema.org/a/G8fxQJAaVFUe9iq1)

---

## Why This Exists

Keeping up with research is hard. arXiv publishes hundreds of papers daily, and the typical workflow is fragmented — search in a browser, open PDFs, copy-paste abstracts into notes, summarize manually, lose track of what you read.

This MCP server fixes that by bringing the entire workflow into your AI assistant:

- **Search** arXiv without leaving Claude
- **Summarize** papers instantly at whatever depth you need
- **Save notes** linked to papers, tagged and searchable
- **Export** everything to Markdown, JSON, or CSV for use in Obsidian, Notion, or a spreadsheet

No browser switching, no copy-pasting, no lost context.

---

## Future Enhancements

- **Semantic search** — embed notes and papers with a vector DB (e.g. ChromaDB) for similarity-based retrieval instead of substring search
- **PDF ingestion** — download and parse full paper PDFs for richer, section-aware summaries beyond the abstract
- **Citation graph** — fetch references from Semantic Scholar API and let Claude explore related work
- **Daily digest** — scheduled tool that searches a saved list of topics and summarizes new papers published that day
- **Groq / local LLM support** — swap in a different LLM provider via an env var for offline or cost-free summarization
- **Multi-user notes** — replace `notes.json` with SQLite for concurrent access and better query performance
- **Obsidian sync** — export notes directly into an Obsidian vault with frontmatter metadata

---

## Architecture

```
┌─────────────────────┐         stdio          ┌──────────────────────────┐
│   Claude Desktop    │ ◄────────────────────► │  Research Assistant MCP  │
│   / MCP Inspector   │                        │       (FastMCP)          │
└─────────────────────┘                        └──────────┬───────────────┘
                                                          │
                               ┌──────────────────────────┼───────────────────┐
                               │                          │                   │
                        ┌──────▼──────┐         ┌────────▼──────┐   ┌────────▼──────┐
                        │  arXiv API  │         │ Anthropic API │   │  notes.json   │
                        │  (Atom/RSS) │         │   (Claude)    │   │ (local file)  │
                        └─────────────┘         └───────────────┘   └───────────────┘
```

---

## Features

| Tool | Description |
|------|-------------|
| `search_arxiv` | Search arXiv by keyword, category, and sort order |
| `get_paper` | Fetch full metadata for a paper by arXiv ID |
| `summarize_paper` | Summarize a paper via Claude (concise / detailed / eli5) |
| `summarize_and_save` | Summarize a paper and save it as a note in one step |
| `save_note_tool` | Save a research note with optional tags and arXiv link |
| `list_notes_tool` | List all notes, optionally filtered by tag or arXiv ID |
| `search_notes_tool` | Full-text search across title, content, and tags |
| `update_note_tool` | Update content or tags on an existing note |
| `delete_note_tool` | Delete a note by ID |
| `export_notes` | Export all notes to JSON, Markdown, or CSV |

**Resources:**

| URI | Description |
|-----|-------------|
| `notes://all` | All notes as a JSON array |
| `notes://{note_id}` | Single note by UUID |

---

## Quick Start

**Requirements:** Python 3.10+, [`uv`](https://docs.astral.sh/uv/)

```bash
git clone <repo-url>
cd research-assistant-MCP

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Install dependencies
uv sync
```

---

## Usage

### MCP Inspector (for testing)

```bash
PYTHONPATH=src uv run mcp dev src/research_assistant/server.py
```

Open the URL printed in the terminal. Use the **Tools** tab to call any tool interactively.

### Run the demo script

```bash
uv run python demo.py
```

Walks through: search → get paper → summarize → save note → export.

---

## Claude Desktop Setup

Add the following to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "research-assistant": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/absolute/path/to/research-assistant-MCP",
        "run",
        "research-assistant"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here",
        "NOTES_DIR": ""
      }
    }
  }
}
```

Replace `/path/to/uv` (find it with `which uv`) and `/absolute/path/to/research-assistant-MCP` with the actual paths on your machine.

Fully quit Claude Desktop (Cmd+Q) and reopen it. You should see the tools available in new conversations.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Required for `summarize_paper` and `summarize_and_save` |
| `NOTES_DIR` | `~/.research-assistant/` | Directory where `notes.json` is stored |

---

## Project Structure

```
research-assistant-MCP/
├── pyproject.toml                   # Dependencies and script entrypoint
├── .env.example                     # Environment variable template
├── demo.py                          # End-to-end demo script
├── demo.cast                        # Recorded terminal demo (asciinema)
└── src/research_assistant/
    ├── __init__.py
    ├── server.py                    # FastMCP instance and all tool definitions
    ├── arxiv.py                     # arXiv Atom API client with rate limiting
    ├── summarize.py                 # Anthropic Claude summarization
    └── notes.py                     # JSON file persistence with atomic writes
```

---

## Summarization Styles

The `summarize_paper` and `summarize_and_save` tools support three styles:

| Style | Description |
|-------|-------------|
| `concise` | 3 sentences: problem, method, result |
| `detailed` | Sections: motivation, methods, results, limitations |
| `eli5` | Plain language explanation for non-experts |

---

## Case Study — The Problem This Solves

### Before

Researching a topic like *"retrieval augmented generation"* used to look like this:

1. Open Google Scholar or arXiv in a browser
2. Search, scan titles, click a paper
3. Read the abstract in a new tab
4. Open another paper in another tab
5. Mentally (or manually) compare the two
6. Copy-paste key points into a notes app
7. Repeat for 10+ papers
8. Lose track of which paper said what

A single research session could mean **20+ tabs, 45+ minutes**, and notes scattered across different apps — with no clear link between a note and the paper it came from.

### After

With Research Assistant MCP, the same session inside Claude Desktop looks like this:

1. `search_arxiv("retrieval augmented generation", max_results=5)` — get 5 papers instantly
2. `summarize_and_save("2005.11401", style="concise")` — summarize and save in one call
3. `summarize_and_save("2312.10997", style="concise")` — do the same for the next paper
4. `search_notes("retrieval")` — pull up all saved summaries side by side
5. `export_notes(format="markdown")` — drop everything into Obsidian

**Same research, a fraction of the time, everything in one place.**

---

## Notes Export Formats

The `export_notes` tool supports:

| Format | Output |
|--------|--------|
| `json` | Pretty-printed JSON array |
| `markdown` | One `##` section per note, suitable for Obsidian or Notion |
| `csv` | Spreadsheet-friendly, tags joined with `\|` |

By default exports to `~/research-exports/`. Set `output_path` to override.
