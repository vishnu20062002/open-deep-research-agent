"""
Helpers
-------
Utility functions: URL validation, text truncation, PDF generation placeholder,
and formatting helpers used across the app.
"""

import re
from datetime import datetime


def is_valid_url(text: str) -> bool:
    """Return True if text looks like a valid HTTP/HTTPS URL."""
    pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    return bool(pattern.match(text.strip()))


def truncate(text: str, max_chars: int = 120) -> str:
    """Truncate text to max_chars with ellipsis."""
    return text[:max_chars] + "..." if len(text) > max_chars else text


def format_timestamp(dt: datetime | None = None) -> str:
    """Return a human-readable timestamp string."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%B %d, %Y – %H:%M")


def word_count_badge(count: int) -> str:
    """Return a label string for word count."""
    if count < 200:
        return f"~{count} words · Quick read"
    elif count < 600:
        return f"~{count} words · 3 min read"
    else:
        return f"~{count} words · {count // 200} min read"


def generate_pdf_placeholder(report_text: str) -> bytes:
    """
    PDF generation placeholder.
    Returns the report as UTF-8 bytes (real PDF library would go here).
    In production: use reportlab or fpdf2.
    """
    # Placeholder: encode as bytes — swap this for actual PDF generation
    return report_text.encode("utf-8")


def sanitize_filename(text: str) -> str:
    """Strip characters unsafe for filenames."""
    safe = re.sub(r'[^\w\s-]', '', text).strip()
    safe = re.sub(r'[\s]+', '_', safe)
    return safe[:50] or "research_report"
