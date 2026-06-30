"""
Vocabulary illustration generation for Picture Words.
Default: Pollinations.ai (free, no API key). Optional: OpenAI DALL·E 2 via existing key.
"""

from __future__ import annotations

import base64
import hashlib
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import streamlit as st

from config import IMAGE_PROVIDER, OPENAI_API_KEY
PICTURE_WORD_LIMIT = int(os.getenv("PICTURE_WORD_LIMIT", "10"))
IMAGE_SIZE = 512


def images_enabled() -> bool:
    return IMAGE_PROVIDER not in ("off", "none", "false", "0")


def education_image_prompt(term: str, description: str, topic: str = "") -> str:
    """Child-friendly prompt tuned for textbook-style vocabulary illustrations."""
    scene = (description or f"a clear diagram showing {term}").strip()
    topic_bit = f" for the lesson topic '{topic}'" if topic else ""
    return (
        f"Simple colourful educational illustration{topic_bit}, cartoon style, "
        f"clean white background, child-friendly school textbook art, "
        f"showing the concept '{term}': {scene}. "
        f"No text, no labels, no watermark."
    )


def pollinations_image_url(prompt: str, width: int = IMAGE_SIZE, height: int = IMAGE_SIZE) -> str:
    encoded = urllib.parse.quote(prompt, safe="")
    seed = int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16) % 1_000_000
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&seed={seed}&model=flux"
    )


def _fetch_url_bytes(url: str, timeout: float = 45.0) -> bytes | None:
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            content_type = (response.headers.get("content-type") or "").lower()
            if response.status_code == 200 and content_type.startswith("image"):
                return response.content
    except Exception:
        pass
    return None


def _openai_image_bytes(prompt: str) -> bytes | None:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        result = client.images.generate(
            model="dall-e-2",
            prompt=prompt[:1000],
            size="512x512",
            n=1,
            response_format="url",
        )
        url = result.data[0].url
        return _fetch_url_bytes(url, timeout=60.0) if url else None
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_picture_word_image(term: str, description: str, topic: str, provider: str) -> bytes | None:
    """Fetch one vocabulary illustration (cached 24 h per term + description)."""
    if provider in ("off", "none", "false", "0"):
        return None
    prompt = education_image_prompt(term, description, topic)
    if provider == "openai":
        data = _openai_image_bytes(prompt)
        if data:
            return data
    url = pollinations_image_url(prompt)
    return _fetch_url_bytes(url)


def picture_word_image_url(term: str, description: str, topic: str) -> str:
    """Public URL for HTML export (Pollinations — works without pre-fetch)."""
    prompt = education_image_prompt(term, description, topic)
    return pollinations_image_url(prompt)


def picture_word_image_data_uri(term: str, description: str, topic: str) -> str | None:
    """Base64 data URI for offline HTML export when bytes are available."""
    if not images_enabled():
        return None
    data = get_picture_word_image(term, description, topic, IMAGE_PROVIDER)
    if not data:
        return None
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def batch_load_picture_word_images(
    rows: list[dict],
    topic: str,
    *,
    limit: int | None = None,
) -> dict[str, bytes]:
    """Load illustrations in parallel for Picture Words grid."""
    if not images_enabled():
        return {}
    cap = limit if limit is not None else PICTURE_WORD_LIMIT
    targets = [row for row in rows[:cap] if row.get("term")]
    results: dict[str, bytes] = {}

    def _load(row: dict) -> tuple[str, bytes | None]:
        term = str(row.get("term", "")).strip()
        desc = str(row.get("draw_this") or row.get("visual") or row.get("image_prompt") or "")
        return term, get_picture_word_image(term, desc, topic, IMAGE_PROVIDER)

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_load, row): row for row in targets}
        for future in as_completed(futures):
            term, data = future.result()
            if term and data:
                results[term] = data
    return results
