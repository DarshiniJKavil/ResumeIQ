from resumeiq.matcher import analyze
from resumeiq.skills import extract_skills

RESUME = """
Python with Data Science Intern, QSpiders
- Completed hands-on training in Python, SQL, Statistics, Machine Learning, NumPy, Pandas, Matplotlib, and Seaborn.
- Performed data preprocessing, exploratory data analysis (EDA), feature engineering, and model development on real datasets.
Projects
- Built phishing detection using OCR and speech-to-text with NLP techniques to classify malicious content.
- Developed rainfall prediction using KNN, Naive Bayes; evaluated with Accuracy, Precision, Recall and F1-score.
Skills: Python, SQL, Power BI, HTML, CSS, Git, Excel
"""

JD = """
We are hiring a Data Analyst.
- Strong Python and SQL skills for data analysis
- Experience building dashboards in Power BI or Tableau
- Knowledge of statistics and exploratory data analysis
- Familiarity with Docker and AWS is a plus
"""


def test_extract_skills_word_boundaries():
    assert "Java" not in extract_skills("I know JavaScript")
    assert "Python" in extract_skills("python, sql")


def test_matched_and_missing():
    r = analyze(RESUME, JD)
    assert "Python" in r.matched_skills
    assert "SQL" in r.matched_skills
    assert "Power BI" in r.matched_skills
    assert "Docker" in r.missing_skills
    assert "AWS" in r.missing_skills
    assert "Tableau" in r.missing_skills


def test_score_bounds_and_evidence():
    r = analyze(RESUME, JD)
    assert 0 <= r.overall_score <= 100
    assert r.evidence, "expected evidence lines"
    assert any(e.skill == "Python" for e in r.evidence)


def test_identical_text_scores_high():
    r = analyze(JD, JD)
    assert r.overall_score >= 90


HR_JD = """
HR Executive
- Source candidates through job portals and schedule interviews
- Handle payroll inputs, attendance and leave management
- Strong communication and interpersonal skills
- Proficiency in Microsoft Excel
- Good team collaboration skills
"""


def test_non_it_job_scores_low_and_is_flagged():
    r = analyze(RESUME, HR_JD)
    assert r.low_confidence
    assert r.overall_score < 40


def test_it_job_is_not_flagged():
    r = analyze(RESUME, JD)
    assert not r.low_confidence
