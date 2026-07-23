"""Anthropic LLM-based paper summarization."""

import os

import anthropic

from .arxiv import get_paper_api

_STYLE_PROMPTS = {
    "concise": (
        "Summarize the following research paper abstract in exactly 3 sentences. "
        "Focus on: what problem is solved, the method used, and the key result."
    ),
    "detailed": (
        "Provide a detailed summary of the following research paper abstract covering: "
        "1) Problem and motivation, 2) Methods and approach, 3) Key results, "
        "4) Limitations and future work. Use clear section headers."
    ),
    "eli5": (
        "Explain the following research paper abstract as if explaining to a curious "
        "12-year-old with no technical background. Use simple language, analogies, "
        "and avoid jargon."
    ),
}


async def summarize_paper_api(arxiv_id: str, style: str = "concise") -> str:
    """Fetch a paper's abstract and summarize it using Claude or other LLMs."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return (
            "Error: ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or environment to use summarize_paper."
        )

    if style not in _STYLE_PROMPTS:
        return (
            f"Error: Unknown style {style!r}. "
            f"Valid options: {', '.join(_STYLE_PROMPTS)}"
        )

    try:
        paper = await get_paper_api(arxiv_id)
    except Exception as e:
        return f"Error fetching paper {arxiv_id!r}: {e}"

    abstract = paper.get("abstract", "").strip()
    if not abstract:
        return f"Error: No abstract available for paper {arxiv_id!r}."

    title = paper.get("title", arxiv_id)
    system_prompt = _STYLE_PROMPTS[style]
    user_message = f"Title: {title}\n\nAbstract:\n{abstract}"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except anthropic.AuthenticationError:
        return "Error: Invalid ANTHROPIC_API_KEY. Please check your API key."
    except anthropic.APIError as e:
        return f"Error calling Anthropic API: {e}"
