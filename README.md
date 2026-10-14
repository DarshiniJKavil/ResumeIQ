# ResumeIQ 📄

**AI Resume vs. Job Description Analyzer.** Upload a resume and paste a job description to get a match score, skill gaps, evidence lines from the resume, and improvement suggestions.

> Live demo: _add your Streamlit / Hugging Face link here_

![screenshot](docs/screenshot.png)

## Features
- Parses resumes from **PDF, DOCX or TXT**
- Extracts skills against a taxonomy of 50+ skills with aliases (e.g. `sklearn` → Scikit-learn)
- **Match score** = 65% skill coverage + 35% TF-IDF semantic similarity
- **RAG-style evidence retrieval**: for each matched skill, retrieves the most relevant resume line so every claim is backed by the resume
- Flags job requirements the resume does not support
- **Optional Claude-powered rewrite suggestions**, grounded in resume facts only (no invented experience)
- Works without any API key (rule-based mode)

### Interactive UI
- **Marked-up text**: your resume and the job description side by side, with shared skills highlighted and missing skills underlined in red
- **What-if simulator**: pick missing skills and see the estimated score change instantly
- **Fix these first**: missing skills ranked by how often the job description mentions them
- One-click sample job descriptions (AI/ML, data analyst, marketing, HR)
- Downloadable markdown report
- Reliability warning when a job description has too few recognized technical skills

## Architecture

```
Resume (PDF/DOCX/TXT) ──► parser ──► clean text ──┐
                                                  ├─► skill extractor ─► matched / missing / extra
Job description ─────────────────────────────────┘
                                                  ├─► TF-IDF similarity ─► semantic score
                                                  └─► chunk + retrieve ──► evidence lines
                                                            │
                                  (optional) Claude API ◄───┘ grounded rewrite suggestions
                                                            ▼
                                                    Streamlit UI
```

## Tech stack
Python, Streamlit, scikit-learn (TF-IDF, cosine similarity), pypdf, python-docx, Anthropic API (optional)

## Run locally
```bash
git clone <your-repo-url>
cd ResumeIQ
pip install -r requirements.txt
streamlit run app.py
```
Optional AI suggestions:
```bash
export ANTHROPIC_API_KEY=your_key_here   # Windows: set ANTHROPIC_API_KEY=your_key_here
```

## Run tests
```bash
python -m pytest -q
```

## Deploy free
1. Push to GitHub
2. Go to Streamlit Community Cloud → New app → select repo → main file `app.py`
3. Add `ANTHROPIC_API_KEY` under Secrets (optional)

## Evaluation (fill this in, recruiters love numbers)
Test the matcher on 10-20 resume/JD pairs you label yourself (good / partial / poor fit).

| Metric | Result |
|---|---|
| Pairs tested | _e.g. 20_ |
| Skill extraction precision | _e.g. 92%_ |
| Skill extraction recall | _e.g. 88%_ |
| Score agrees with manual label | _e.g. 80%_ |

## Limitations
- Skill extraction uses a fixed taxonomy focused on IT, data and AI; skills outside it (e.g. marketing, HR) are not detected, and the app warns when a job description has fewer than 3 recognized technical skills
- Generic skills (communication, teamwork, problem solving) count for 25% of a technical skill, and a job ad is treated as asking for at least 5 weighted skills, so generic overlap cannot produce a high score
- TF-IDF similarity is lexical, not deep semantic (upgrade path: sentence-transformers + FAISS)
- Score is a guide, not a hiring decision
- PDFs with complex layouts or scanned images may extract poorly (OCR not included)

## Roadmap
- [ ] Swap TF-IDF for sentence-transformers embeddings + FAISS
- [ ] Add OCR for scanned resumes (reuse your phishing project's OCR pipeline)
- [ ] Export a tailored resume as DOCX
- [ ] Batch mode: rank many resumes for one JD

## Author
Darshini J · [LinkedIn](https://linkedin.com/in/darshini-j-0103b3288)
