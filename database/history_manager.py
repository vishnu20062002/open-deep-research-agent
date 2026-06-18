"""
History Manager
---------------
Manages research session history using Streamlit session state.
Provides add, retrieve, and clear operations for research records.
"""

from datetime import datetime
import streamlit as st


def init_history():
    """Initialize history list in session state if not present."""
    if "research_history" not in st.session_state:
        st.session_state.research_history = []


def add_to_history(subject: str, input_type: str, mode: str, report: dict):
    """
    Add a completed research session to history.

    Args:
        subject: Topic or URL researched
        input_type: 'topic' or 'url'
        mode: 'Short Summary' or 'Detailed Research Report'
        report: The generated report dict
    """
    init_history()
    entry = {
        "id": len(st.session_state.research_history) + 1,
        "subject": subject[:80] + ("..." if len(subject) > 80 else ""),
        "input_type": input_type,
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "report": report,
        "word_count": report.get("word_count", 0),
    }
    st.session_state.research_history.insert(0, entry)  # newest first


def get_history() -> list:
    """Return the full history list."""
    init_history()
    return st.session_state.research_history


def clear_history():
    """Clear all history entries."""
    st.session_state.research_history = []


def get_entry_by_id(entry_id: int) -> dict | None:
    """Retrieve a single history entry by its ID."""
    for entry in get_history():
        if entry["id"] == entry_id:
            return entry
    return None
