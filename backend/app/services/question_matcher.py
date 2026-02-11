"""
Smart Question Matcher — Maps form questions to user profile fields.
Supports fallback to simple matching if heavy ML libraries are missing (Lite mode).
"""
import re
from typing import Optional, Tuple, Dict, List

# Try imports for heavy ML features
try:
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_ML = True
except ImportError:
    HAS_ML = False

# Lazy-loaded model
_model = None
_field_embeddings = None
_field_descriptions = None


def _get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            _model = None
    return _model


# Description phrases for each profile field (used for embedding comparison)
FIELD_DESCRIPTIONS: Dict[str, List[str]] = {
    "full_name": [
        "full name", "your name", "name of the student", "participant name",
        "first name last name", "what is your name", "enter your name",
    ],
    "register_number": [
        "register number", "registration number", "roll number", "roll no",
        "reg no", "student id", "enrollment number", "admission number",
        "student number", "id number",
    ],
    "department": [
        "department", "branch", "stream", "field of study",
        "specialization", "major", "course", "programme",
        "which department", "your branch",
    ],
    "year": [
        "year of study", "current year", "academic year", "semester",
        "which year", "year", "batch", "graduating year",
    ],
    "email": [
        "email", "email address", "e-mail", "mail id",
        "your email", "email id", "contact email",
    ],
    "phone": [
        "phone number", "mobile number", "contact number", "phone",
        "mobile", "cell number", "whatsapp number", "telephone",
        "contact no",
    ],
    "gender": [
        "gender", "sex", "male or female", "your gender",
    ],
    "college_name": [
        "college name", "university", "institution", "school name",
        "college", "institute", "institution name", "university name",
        "name of your college",
    ],
    "address": [
        "address", "residential address", "home address", "current address",
        "city", "location", "where do you live",
    ],
    "skills": [
        "skills", "technical skills", "key skills", "skill set",
        "programming languages", "technologies", "tools known",
        "what skills do you have",
    ],
    "interests": [
        "interests", "hobbies", "areas of interest", "what are your interests",
        "hobbies and interests", "passion", "what excites you",
    ],
    "bio": [
        "about yourself", "tell us about yourself", "brief introduction",
        "self introduction", "describe yourself", "bio", "about you",
        "introduce yourself",
    ],
}


def _get_field_embeddings():
    """Compute and cache embeddings for all field descriptions."""
    global _field_embeddings, _field_descriptions
    model = _get_model()
    if model is None:
        return None, None
        
    if _field_embeddings is None:
        _field_descriptions = {}
        all_texts = []
        for field_name, descriptions in FIELD_DESCRIPTIONS.items():
            for desc in descriptions:
                _field_descriptions[len(all_texts)] = field_name
                all_texts.append(desc)
        _field_embeddings = model.encode(all_texts, normalize_embeddings=True)
    return _field_embeddings, _field_descriptions


def _simple_match(question: str) -> Optional[str]:
    """Fallback simple string matching logic."""
    q = question.lower()
    for field, keywords in FIELD_DESCRIPTIONS.items():
        if any(kw in q for kw in keywords):
            return field
    return None


def match_question_to_field(question: str, threshold: float = 0.45) -> Tuple[Optional[str], float]:
    """Match a form question using embeddings or simple fallback."""
    model = _get_model()
    
    # Fallback to simple matching if ML libraries are missing
    if not HAS_ML or model is None:
        matched = _simple_match(question)
        return matched, 1.0 if matched else 0.0

    embeddings, field_map = _get_field_embeddings()
    if embeddings is None:
        matched = _simple_match(question)
        return matched, 0.9 if matched else 0.0

    # Clean question
    clean_q = re.sub(r'[*\n\r]+', ' ', question).strip().lower()
    if not clean_q:
        return None, 0.0

    # Encode question
    q_embedding = model.encode([clean_q], normalize_embeddings=True)

    # Compute similarities
    similarities = cosine_similarity(q_embedding, embeddings)[0]

    # Find best match
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])
    best_field = field_map[best_idx]

    if best_score >= threshold:
        return best_field, best_score
    return None, best_score


def match_question_batch(questions: List[str], threshold: float = 0.45) -> List[Tuple[Optional[str], float]]:
    """Match multiple questions (Lite optimized)."""
    model = _get_model()
    
    if not HAS_ML or model is None:
        return [match_question_to_field(q, threshold) for q in questions]

    embeddings, field_map = _get_field_embeddings()
    if embeddings is None:
        return [match_question_to_field(q, threshold) for q in questions]

    # Clean questions
    clean_questions = [re.sub(r'[*\n\r]+', ' ', q).strip().lower() for q in questions]
    if not clean_questions:
        return []

    # Encode all questions
    q_embeddings = model.encode(clean_questions, normalize_embeddings=True)

    # Compute similarities
    sims = cosine_similarity(q_embeddings, embeddings)

    results = []
    for i in range(len(questions)):
        best_idx = int(np.argmax(sims[i]))
        best_score = float(sims[i][best_idx])
        best_field = field_map[best_idx]
        if best_score >= threshold:
            results.append((best_field, best_score))
        else:
            results.append((None, best_score))

    return results
