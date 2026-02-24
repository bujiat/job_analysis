"""
Snippet generation and query-term highlighting for search results.

"""
import re
import html


def _strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace so snippet/description is plain text."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_snippet(text: str, query: str, max_len: int = 160) -> str:
    """
    Extract a short window from text that contains query words, then wrap those words in <mark>.

    - Query words: extracted by simple regex (alphanumeric), used for finding and highlighting.
    - Window: first occurrence of any query word, then up to max_len chars; HTML-escaped.
    - Highlight: each query word in the window is wrapped in <mark> (case-insensitive, preserves original case).
    - Input text is stripped of HTML tags so the snippet shows plain text only.
    """
    if not text or not isinstance(text, str):
        return ""
    text = _strip_html(text)
    if not text:
        return ""

    # re.findall(pattern, string): returns all non-overlapping matches of the regex as a list of strings.
    words = re.findall(r"[a-zA-Z0-9]+", query)
    words = [w for w in words if len(w) > 1]
    if not words:
        return _escape_and_truncate(text, max_len)

    # First occurrence of any query word (case-insensitive)
    lower_text = text.lower()
    first_pos = -1
    for w in words:
        pos = lower_text.find(w.lower())
        if pos != -1 and (first_pos == -1 or pos < first_pos):
            first_pos = pos

    if first_pos == -1:
        return _escape_and_truncate(text[:max_len], max_len)

    # Window: around first hit, then cap length
    half = max_len // 2
    start = max(0, first_pos - half)
    end = min(len(text), start + max_len)
    window = text[start:end]
    if start > 0:
        window = "…" + window
    if end < len(text):
        window = window + "…"

    # html.escape(s): turns <, >, &, " into &lt; etc. so the snippet is safe to insert into HTML (no XSS).
    window = html.escape(window)
    for w in words:
        if len(w) < 2:
            continue
        # re.escape(w): escapes regex metacharacters in w so we match the literal string. re.compile(..., re.IGNORECASE): build pattern for case-insensitive match. m.group(0): the whole matched substring (so we keep original case). pattern.sub(repl, window): replace each match with repl(match).
        pattern = re.compile(re.escape(w), re.IGNORECASE)

        def repl(m):
            return "<mark>" + m.group(0) + "</mark>"

        window = pattern.sub(repl, window)

    return window


def _escape_and_truncate(s: str, max_len: int) -> str:
    s = s[:max_len]
    if len(s) == max_len:
        s = s + "…"
    return html.escape(s)
