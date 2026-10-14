"""Helpers for the front end: marked-up text, mention counts, chips."""
import html
import re

from .skills import SKILLS, _PATTERNS


def count_mentions(text: str, skill: str) -> int:
    return sum(len(p.findall(text)) for p in _PATTERNS.get(skill, []))


def annotate(text: str, hit=frozenset(), miss=frozenset()) -> str:
    """Return HTML where skills in `hit` get a highlighter mark and skills in `miss` a red wavy underline."""
    escaped = html.escape(text)
    alias_map = {}
    for skill in set(hit) | set(miss):
        cls = "hit" if skill in hit else "miss"
        for alias in SKILLS.get(skill, []):
            alias_map[alias.lower()] = (skill, cls)
    if alias_map:
        aliases = sorted(alias_map, key=len, reverse=True)
        pattern = re.compile(
            r"(?<![A-Za-z0-9])(" + "|".join(re.escape(a) for a in aliases) + r")(?![A-Za-z0-9])",
            re.IGNORECASE,
        )

        def repl(m):
            skill, cls = alias_map[m.group(1).lower()]
            return f'<mark class="{cls}" title="{skill}">{m.group(1)}</mark>'

        escaped = pattern.sub(repl, escaped)
    return escaped.replace("\n", "<br>")


def chips(skills, kind: str, counts=None) -> str:
    if not skills:
        return ""
    out = []
    for s in skills:
        extra = f"<em>x{counts[s]}</em>" if counts and counts.get(s) else ""
        out.append(f'<span class="chip {kind}">{html.escape(s)}{extra}</span>')
    return "".join(out)


def flat(s: str) -> str:
    """Strip leading indentation so Streamlit's markdown doesn't treat HTML as a code block."""
    return "\n".join(line.strip() for line in s.splitlines())
