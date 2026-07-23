# Research Assistant MCP

A Python MCP server that gives Claude (and any MCP-compatible client) tools to search arXiv papers, summarize them using Claude AI, and manage persistent research notes.

[![asciicast](https://asciinema.org/a/G8fxQJAaVFUe9iq1.svg)](https://asciinema.org/a/G8fxQJAaVFUe9iq1)

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

## Notes Export Formats

The `export_notes` tool supports:

| Format | Output |
|--------|--------|
| `json` | Pretty-printed JSON array |
| `markdown` | One `##` section per note, suitable for Obsidian or Notion |
| `csv` | Spreadsheet-friendly, tags joined with `\|` |

By default exports to `~/research-exports/`. Set `output_path` to override.
