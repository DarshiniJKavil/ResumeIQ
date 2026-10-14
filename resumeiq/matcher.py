"""Core matching logic: skill gap, semantic similarity, evidence retrieval, scoring."""
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .parser import split_chunks
from .skills import extract_skills


# Generic skills appear in almost every job ad, so they count for less than technical ones.
SOFT_SKILLS = {"Communication", "Team Collaboration", "Problem Solving"}
SOFT_WEIGHT = 0.25
# A job ad is treated as asking for at least this much weighted skill, so an ad that only
# matches a couple of generic skills (e.g. a non-IT role) cannot reach a high score.
MIN_TOTAL_WEIGHT = 5.0
# Fewer technical skills than this recognized in the job description = unreliable score.
MIN_TECH_SKILLS = 3


def _weight(skill: str) -> float:
    return SOFT_WEIGHT if skill in SOFT_SKILLS else 1.0


@dataclass
class Evidence:
    skill: str
    resume_line: str
    score: float


@dataclass
class MatchResult:
    overall_score: int
    skill_score: int
    semantic_score: int
    matched_skills: list = field(default_factory=list)
    missing_skills: list = field(default_factory=list)
    extra_skills: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    weak_requirements: list = field(default_factory=list)
    verdict: str = ""
    low_confidence: bool = False
    tech_skills_in_jd: int = 0


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between full resume and JD (0-1)."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vec.fit_transform([resume_text, jd_text])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def retrieve_evidence(resume_text: str, queries: list, top_k: int = 1, min_score: float = 0.08):
    """RAG-style retrieval: for each JD requirement, find the best-matching resume chunk.

    Returns (evidence list, list of queries with no supporting chunk).
    """
    chunks = split_chunks(resume_text)
    if not chunks or not queries:
        return [], list(queries)

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit(chunks + queries)
    chunk_m = vec.transform(chunks)
    evidence, weak = [], []
    for q in queries:
        sims = cosine_similarity(vec.transform([q]), chunk_m)[0]
        order = sims.argsort()[::-1][:top_k]
        best = order[0]
        if sims[best] >= min_score:
            evidence.append(Evidence(skill="", resume_line=chunks[best], score=float(sims[best])))
        else:
            weak.append(q)
    return evidence, weak


def jd_requirements(jd_text: str):
    """Pick JD lines that look like requirements (bullets / sentences with enough words)."""
    lines = []
    for raw in jd_text.splitlines():
        line = raw.strip(" -•●\t")
        if 4 <= len(line.split()) <= 40:
            lines.append(line)
    return lines


def analyze(resume_text: str, jd_text: str) -> MatchResult:
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    matched_weight = sum(_weight(s) for s in matched)
    total_weight = sum(_weight(s) for s in jd_skills)
    skill_ratio = matched_weight / max(total_weight, MIN_TOTAL_WEIGHT) if jd_skills else 0.0
    tech_in_jd = sum(1 for s in jd_skills if s not in SOFT_SKILLS)
    sem = semantic_similarity(resume_text, jd_text)

    # Weighted blend: hard skills matter most; semantic score is scaled because
    # TF-IDF similarity between two different documents is naturally low.
    sem_scaled = min(1.0, sem * 2.5)
    overall = 0.65 * skill_ratio + 0.35 * sem_scaled

    # Evidence: one best resume line per matched skill
    evidence = []
    for skill in matched:
        ev, _ = retrieve_evidence(resume_text, [skill])
        if ev:
            ev[0].skill = skill
            evidence.append(ev[0])

    # Requirements from the JD that the resume doesn't back up
    reqs = [r for r in jd_requirements(jd_text) if extract_skills(r)]
    _, weak = retrieve_evidence(resume_text, reqs, min_score=0.12)

    pct = round(overall * 100)
    if pct >= 75:
        verdict = "Strong match - apply with confidence."
    elif pct >= 50:
        verdict = "Moderate match - close the skill gaps and tailor your resume."
    else:
        verdict = "Low match - significant gaps; consider building projects in the missing skills."

    return MatchResult(
        overall_score=pct,
        skill_score=round(skill_ratio * 100),
        semantic_score=round(sem_scaled * 100),
        matched_skills=matched,
        missing_skills=missing,
        extra_skills=extra,
        evidence=evidence,
        weak_requirements=weak,
        verdict=verdict,
        low_confidence=tech_in_jd < MIN_TECH_SKILLS,
        tech_skills_in_jd=tech_in_jd,
    )
