# research-assistant-MCP

A lightweight Research Assistant MCP Server built with Python that extends AI assistants with tools for searching arXiv, summarizing research papers using LLMs, and managing persistent research notes through the Model Context Protocol.

## Setup

**Requirements:** Python 3.10+, [`uv`](https://docs.astral.sh/uv/)

```bash
git clone <repo>
cd research-assistant-MCP
cp .env.example .env        # add your ANTHROPIC_API_KEY
uv sync
```

## Running

```bash
uv run research-assistant
```

## Claude Desktop configuration

Add this to your `claude_desktop_config.json` (usually at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "research-assistant": {
      "command": "uv",
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

Replace `/absolute/path/to/research-assistant-MCP` with the actual path on your machine.

## Tools

| Tool | Description |
|------|-------------|
| `search_arxiv` | Search arXiv by keyword, category, and sort order |
| `get_paper` | Fetch metadata for a single paper by arXiv ID |
| `summarize_paper` | Summarize a paper via Claude (concise / detailed / eli5) |
| `save_note_tool` | Save a research note with optional tags and arXiv link |
| `list_notes_tool` | List notes, optionally filtered by tag or arXiv ID |
| `search_notes_tool` | Full-text search across title, content, and tags |
| `update_note_tool` | Update content or tags on an existing note |
| `delete_note_tool` | Delete a note by ID |

## Resources

| URI | Description |
|-----|-------------|
| `notes://all` | All notes as a JSON array |
| `notes://{note_id}` | Single note by UUID |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Required for `summarize_paper` |
| `NOTES_DIR` | `~/.research-assistant/` | Directory for `notes.json` |
