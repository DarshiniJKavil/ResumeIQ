"""Optional LLM layer: grounded rewrite suggestions using the Anthropic API.

Set ANTHROPIC_API_KEY to enable. The app works without it (rule-based mode).
"""
import os

MODEL = os.getenv("RESUMEIQ_MODEL", "claude-sonnet-5-5")

SYSTEM = (
    "You are a careful resume coach. Use ONLY facts present in the resume text. "
    "Never invent experience, tools, or numbers. If a skill from the job description "
    "is missing from the resume, say it is a gap instead of claiming it."
)


def llm_available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def build_prompt(resume_text: str, jd_text: str, result) -> str:
    return f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

ANALYSIS (computed by the app):
- Match score: {result.overall_score}/100
- Matched skills: {", ".join(result.matched_skills) or "none"}
- Missing skills: {", ".join(result.missing_skills) or "none"}

Give:
1. Three rewritten resume bullets (using only real resume facts) that better target this job.
2. A 2-3 sentence tailored professional summary.
3. Two project ideas that would close the biggest skill gaps.
Keep it concise and use markdown."""


def get_suggestions(resume_text: str, jd_text: str, result) -> str:
    import anthropic

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=900,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(resume_text, jd_text, result)}],
    )
    return "".join(block.text for block in msg.content if block.type == "text")


def rule_based_tips(result) -> list:
    """Fallback suggestions when no API key is set."""
    tips = []
    for skill in result.missing_skills[:6]:
        tips.append(
            f"**{skill}** is in the job description but not in your resume. "
            f"If you have used it, add it to a project or skills line; if not, build a small project with it."
        )
    for req in result.weak_requirements[:3]:
        tips.append(f"Your resume has no strong evidence for: _{req}_")
    if not tips:
        tips.append("Your resume covers the key skills in this job description. Add measurable results to your bullets.")
    return tips
