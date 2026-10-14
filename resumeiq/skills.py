"""Skill taxonomy and skill extraction."""
import re

# canonical skill -> aliases
SKILLS = {
    "Python": ["python"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "node.js", "nodejs"],
    "React": ["react", "react.js"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Git": ["git", "github", "version control"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "neural network", "neural networks", "cnn", "rnn"],
    "NLP": ["nlp", "natural language processing"],
    "LLM": ["llm", "llms", "large language model", "large language models", "generative ai", "genai"],
    "RAG": ["rag", "retrieval-augmented generation", "retrieval augmented generation"],
    "Prompt Engineering": ["prompt engineering", "prompting"],
    "Feature Engineering": ["feature engineering"],
    "Model Evaluation": ["model evaluation", "precision", "recall", "f1-score", "f1 score"],
    "Data Analysis": ["data analysis", "data analytics", "analytics"],
    "EDA": ["eda", "exploratory data analysis"],
    "Statistics": ["statistics", "statistical"],
    "Data Visualization": ["data visualization", "data visualisation", "dashboard", "dashboards"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "microsoft excel"],
    "NumPy": ["numpy"],
    "Pandas": ["pandas"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "OpenCV": ["opencv"],
    "OCR": ["ocr"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Streamlit": ["streamlit"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "REST API": ["rest api", "rest apis", "restful"],
    "Linux": ["linux"],
    "Data Structures": ["data structures", "algorithms", "dsa"],
    "Debugging": ["debugging", "troubleshooting"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Communication": ["communication"],
    "Team Collaboration": ["team collaboration", "teamwork", "collaboration"],
    "IT Support": ["it support", "technical support", "helpdesk", "help desk"],
    "ETL": ["etl", "data pipeline", "data pipelines"],
    "Vector Database": ["faiss", "chromadb", "pinecone", "vector database", "vector store"],
}


def _pattern(alias: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", re.IGNORECASE)


_PATTERNS = {
    skill: [_pattern(a) for a in aliases] for skill, aliases in SKILLS.items()
}


def extract_skills(text: str) -> set:
    found = set()
    for skill, patterns in _PATTERNS.items():
        if any(p.search(text) for p in patterns):
            found.add(skill)
    return found
