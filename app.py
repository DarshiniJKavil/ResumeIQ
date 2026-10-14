from pathlib import Path

import streamlit as st

from resumeiq.highlight import annotate, chips, count_mentions, flat
from resumeiq.llm import get_suggestions, llm_available, rule_based_tips
from resumeiq.matcher import analyze
from resumeiq.parser import extract_text
from resumeiq.report import build_report

BASE = Path(__file__).parent
SAMPLES = {
    "AI/ML engineer": "ai_ml_engineer.txt",
    "Data analyst": "data_analyst.txt",
    "Marketing executive": "marketing_executive.txt",
    "HR executive": "hr_executive.txt",
}

st.set_page_config(page_title="ResumeIQ", page_icon="🖍️", layout="wide")
st.markdown(f"<style>{(BASE / 'resumeiq' / 'style.css').read_text()}</style>", unsafe_allow_html=True)

st.session_state.setdefault("resume_text", "")
st.session_state.setdefault("jd_text", "")


def load_sample(filename: str):
    st.session_state.jd_text = (BASE / "samples" / filename).read_text()


def ring_color(score: int) -> str:
    return "#0F5C4D" if score >= 75 else "#B7791F" if score >= 50 else "#D13B3B"


def verdict_for(score: int):
    if score >= 75:
        return "Strong match", "Your resume covers most of what this job asks for. Apply, and tailor your summary to its wording."
    if score >= 50:
        return "Close, with some gaps", "Add the missing skills you genuinely have. For the rest, a small project is the fastest proof."
    return "Not a match yet", "The job asks for skills your resume does not show. Start with the ones it mentions most."


# ---------- header ----------
st.markdown(
    flat(
        """
        <div class="hero">
        <h1>ResumeIQ</h1>
        <p>Paste a job description and see which of its skills your resume already shows,
        which ones it can't find, and what to fix first.</p>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

# ---------- inputs ----------
left, right = st.columns(2, gap="large")

with left:
    st.markdown("#### Your resume")
    upload = st.file_uploader("Upload a PDF, DOCX or TXT file", type=["pdf", "docx", "txt"], key="resume_file")
    if upload is not None:
        signature = (upload.name, upload.size)
        if st.session_state.get("_upload_sig") != signature:
            st.session_state.resume_text = extract_text(upload.getvalue(), upload.name)
            st.session_state._upload_sig = signature
    st.text_area("Resume text", key="resume_text", height=280, placeholder="Upload a file above, or paste your resume here.")

with right:
    st.markdown("#### Job description")
    st.caption("Nothing to paste yet? Load a sample:")
    cols = st.columns(len(SAMPLES))
    for col, (label, fname) in zip(cols, SAMPLES.items()):
        col.button(label, key=f"sample_{fname}", on_click=load_sample, args=(fname,), use_container_width=True)
    st.text_area("Job description text", key="jd_text", height=280, placeholder="Paste the full job description here.")

go = st.button("Analyze resume", type="primary")

if go:
    resume_text, jd_text = st.session_state.resume_text, st.session_state.jd_text
    if len(resume_text.split()) < 30:
        st.warning("Your resume text is too short. Upload your resume file or paste at least a few lines.")
    elif len(jd_text.split()) < 15:
        st.warning("The job description is too short. Paste the full posting, or load a sample.")
    else:
        result = analyze(resume_text, jd_text)
        mentions = {s: count_mentions(jd_text, s) for s in result.missing_skills + result.matched_skills}
        st.session_state.analysis = {"result": result, "resume": resume_text, "jd": jd_text, "mentions": mentions}
        st.session_state.ai_text = ""
        st.session_state.pop("whatif", None)

# ---------- results ----------
data = st.session_state.get("analysis")
if data:
    result, resume_text, jd_text, mentions = data["result"], data["resume"], data["jd"], data["mentions"]
    tips = rule_based_tips(result)
    total_jd_skills = len(result.matched_skills) + len(result.missing_skills)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_overview, tab_marked, tab_skills, tab_improve = st.tabs(["Overview", "Marked-up text", "Skills", "Improve"])

    # ----- Overview -----
    with tab_overview:
        c1, c2 = st.columns([1, 2], gap="large")
        title, sub = verdict_for(result.overall_score)
        with c1:
            st.markdown(
                flat(
                    f"""
                    <div class="ring" style="--p:{result.overall_score};--c:{ring_color(result.overall_score)}">
                    <div class="ring-in"><span class="num">{result.overall_score}</span><span class="of">out of 100</span></div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(f'<p class="verdict">{title}</p><p class="sub">{sub}</p>', unsafe_allow_html=True)
            st.markdown(
                flat(
                    f"""
                    <div class="stat"><span>Skills from the job that are on your resume</span><b>{len(result.matched_skills)} of {total_jd_skills}</b></div>
                    <div class="stat"><span>Skill coverage</span><b>{result.skill_score}%</b></div>
                    <div class="stat"><span>Wording similarity to the job description</span><b>{result.semantic_score}%</b></div>
                    """
                ),
                unsafe_allow_html=True,
            )

        if result.low_confidence:
            st.warning(
                f"ResumeIQ found only {result.tech_skills_in_jd} technical skill"
                f"{'' if result.tech_skills_in_jd == 1 else 's'} in this job description, so the score is not reliable. "
                "It recognizes IT, data and AI skills best. For other fields, read the Marked-up text tab instead."
            )

        st.markdown('<h4 class="section">Fix these first</h4>', unsafe_allow_html=True)
        ranked = sorted(result.missing_skills, key=lambda s: (-mentions.get(s, 0), s))[:3]
        if ranked:
            for s in ranked:
                n = mentions.get(s, 0)
                st.markdown(
                    f'<div class="todo"><b>{s}</b><small>The job description mentions it {n} time{"s" if n != 1 else ""}. '
                    f"Add it if you have used it, or build something small with it.</small></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.success("No missing skills. Next, add numbers to your bullets, such as accuracy, dataset size or users.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "Download report",
            data=build_report(result, mentions, tips),
            file_name="resumeiq_report.md",
            mime="text/markdown",
        )

    # ----- Marked-up text -----
    with tab_marked:
        st.markdown(
            '<p class="legend"><mark class="hit">Highlighted</mark> skills appear in both. '
            '<mark class="miss">Underlined</mark> skills are in the job description but not on your resume.</p>',
            unsafe_allow_html=True,
        )
        m1, m2 = st.columns(2, gap="large")
        with m1:
            st.markdown("#### Your resume")
            st.markdown(
                f'<div class="paper">{annotate(resume_text, hit=set(result.matched_skills))}</div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown("#### Job description")
            st.markdown(
                f'<div class="paper">{annotate(jd_text, hit=set(result.matched_skills), miss=set(result.missing_skills))}</div>',
                unsafe_allow_html=True,
            )

    # ----- Skills -----
    with tab_skills:
        st.markdown('<h4 class="section">On your resume and in the job description</h4>', unsafe_allow_html=True)
        st.markdown(chips(result.matched_skills, "hit") or "None found.", unsafe_allow_html=True)

        st.markdown('<h4 class="section">In the job description, not on your resume</h4>', unsafe_allow_html=True)
        st.caption("The number is how many times the job description mentions the skill.")
        st.markdown(chips(result.missing_skills, "miss", mentions) or "None. You cover every skill it lists.", unsafe_allow_html=True)

        st.markdown('<h4 class="section">On your resume, not asked for here</h4>', unsafe_allow_html=True)
        st.markdown(chips(result.extra_skills, "extra") or "None.", unsafe_allow_html=True)

        if result.missing_skills and total_jd_skills:
            st.markdown('<h4 class="section">What if you add skills?</h4>', unsafe_allow_html=True)
            chosen = st.multiselect(
                "Pick skills you have or plan to learn",
                options=result.missing_skills,
                key="whatif",
            )
            gain = round(65 * len(chosen) / total_jd_skills)
            new_score = min(100, result.overall_score + gain)
            st.metric("Estimated match score", f"{new_score}", delta=f"{new_score - result.overall_score} points" if chosen else None)

        if result.evidence:
            with st.expander("Where your resume backs up each matched skill"):
                for ev in result.evidence:
                    st.markdown(f"**{ev.skill}**: {ev.resume_line}")

    # ----- Improve -----
    with tab_improve:
        if llm_available():
            st.markdown("Claude can rewrite your bullets for this job using only facts from your resume.")
            if st.button("Write tailored suggestions", key="ai_btn"):
                with st.spinner("Writing suggestions..."):
                    try:
                        st.session_state.ai_text = get_suggestions(resume_text, jd_text, result)
                    except Exception as e:
                        st.session_state.ai_text = ""
                        st.error(f"The AI request failed: {e}")
            if st.session_state.get("ai_text"):
                st.markdown(st.session_state.ai_text)
        else:
            st.info("Set the ANTHROPIC_API_KEY environment variable to get tailored bullet rewrites. The checks below work without it.")

        st.markdown('<h4 class="section">Checks from your analysis</h4>', unsafe_allow_html=True)
        for t in tips:
            st.markdown(f"- {t}")

    st.caption("The score is a guide: 65% skill coverage plus 35% wording similarity. It is not a hiring decision.")
