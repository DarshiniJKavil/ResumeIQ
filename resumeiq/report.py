"""Build a downloadable markdown report from an analysis."""
from datetime import date


def build_report(result, mentions: dict, tips: list) -> str:
    lines = [
        "# ResumeIQ report",
        f"Date: {date.today().isoformat()}",
        "",
        f"**Overall match: {result.overall_score}/100**  ",
        f"Skill coverage: {result.skill_score}%  ",
        f"Text similarity: {result.semantic_score}%",
        "",
        result.verdict,
        "",
        "## Skills on your resume that the job asks for",
        ", ".join(result.matched_skills) or "None",
        "",
        "## Skills the job asks for that are not on your resume",
    ]
    if result.missing_skills:
        for s in result.missing_skills:
            n = mentions.get(s, 0)
            lines.append(f"- {s} (mentioned {n}x in the job description)")
    else:
        lines.append("None")
    lines += ["", "## Where your resume backs up each matched skill"]
    for ev in result.evidence:
        lines.append(f"- **{ev.skill}**: {ev.resume_line}")
    lines += ["", "## What to do next"]
    lines += [f"- {t}" for t in tips]
    return "\n".join(lines) + "\n"
