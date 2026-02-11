"""
AI Agent — Generates realistic answers for form questions that don't
match any stored profile field, using the user's profile and bio.
"""
import json
import re
import os
from typing import Optional, Dict

from app.config import AI_MODE, OPENAI_API_KEY, OPENAI_BASE_URL, GROK_API_KEY, GROK_BASE_URL, GROK_MODEL


def _build_prompt(question: str, profile: Dict[str, str]) -> str:
    """Build a prompt for the AI to generate a realistic answer."""
    profile_summary = "\n".join(
        f"- {key.replace('_', ' ').title()}: {value}"
        for key, value in profile.items()
        if value and value.strip()
    )

    return f"""You are an AI assistant helping a student fill out a form.
Based on the student's profile below, generate a realistic, appropriate, and concise answer
for the given question. The answer must sound natural and be truthful based on the profile information.

STUDENT PROFILE:
{profile_summary}

FORM QUESTION: "{question}"

RULES:
1. Answer must be relevant to the question
2. Use information from the profile when possible
3. Keep answers concise (1-3 sentences for paragraph questions, short for text fields)
4. Do NOT invent specific dates, numbers, or certifications that aren't in the profile
5. Do NOT use any markdown or formatting, plain text only
6. Be realistic and safe — do not exaggerate or hallucinate

ANSWER:"""


def _generate_with_local_model(question: str, profile: Dict[str, str]) -> str:
    """Generate answer using local sentence-transformers and template-based approach."""
    # Extract profile info
    name = profile.get("full_name", "the student")
    skills = profile.get("skills", "")
    interests = profile.get("interests", "")
    bio = profile.get("bio", "")
    department = profile.get("department", "")
    college = profile.get("college_name", "")
    year = profile.get("year", "")

    q_lower = question.lower().strip()

    # Template-based generation for common patterns
    # Motivation / why questions
    if any(kw in q_lower for kw in ["why do you want", "motivation", "why are you", "why join", "reason for"]):
        parts = []
        if interests:
            parts.append(f"I am deeply interested in {interests}")
        if skills:
            parts.append(f"and have skills in {skills}")
        if department:
            parts.append(f"As a {department} student")
        if bio:
            parts.append(f"{bio[:200]}")
        answer = ". ".join(parts) if parts else f"I am passionate about learning and growing in this field."
        return answer.strip()

    # About yourself / introduction
    if any(kw in q_lower for kw in ["about yourself", "introduce yourself", "tell us about", "describe yourself", "brief about"]):
        parts = []
        if name:
            parts.append(f"I am {name}")
        if department and college:
            parts.append(f"a {department} student at {college}")
        elif department:
            parts.append(f"studying {department}")
        if year:
            parts.append(f"currently in {year}")
        if skills:
            parts.append(f"I have skills in {skills}")
        if interests:
            parts.append(f"and I am interested in {interests}")
        if bio:
            parts.append(bio[:200])
        return ". ".join(parts).strip() if parts else f"I am an enthusiastic student eager to learn and contribute."

    # Achievements / accomplishments
    if any(kw in q_lower for kw in ["achievement", "accomplishment", "proud of", "notable"]):
        parts = []
        if skills:
            parts.append(f"I have developed proficiency in {skills}")
        if department:
            parts.append(f"with a strong academic foundation in {department}")
        if bio and len(bio) > 50:
            parts.append(bio[:200])
        return ". ".join(parts).strip() if parts else "I have consistently worked on improving my skills and contributing to team projects."

    # Expectations / what do you expect
    if any(kw in q_lower for kw in ["expect", "expectation", "hope to", "looking forward", "what do you want to learn"]):
        parts = []
        if interests:
            parts.append(f"I look forward to exploring {interests}")
        parts.append("enhancing my practical skills")
        parts.append("networking with like-minded peers")
        return "I look forward to " + ", ".join(parts[1:]) + "." if len(parts) > 1 else parts[0]

    # Skills question
    if any(kw in q_lower for kw in ["skill", "technical skill", "tools", "technologies", "programming"]):
        return skills if skills else "Problem solving, teamwork, and communication skills."

    # Experience
    if any(kw in q_lower for kw in ["experience", "work experience", "internship", "project"]):
        parts = []
        if skills:
            parts.append(f"I have hands-on experience with {skills}")
        if department:
            parts.append(f"gained through my {department} studies")
        if bio:
            parts.append(bio[:200])
        return ". ".join(parts).strip() if parts else "I have experience through academic projects and self-learning."

    # Generic fallback — use bio and profile to construct answer
    fallback_parts = []
    if bio:
        fallback_parts.append(bio[:300])
    elif name and department:
        fallback_parts.append(f"As {name}, a {department} student, I would like to share that I am enthusiastic about this opportunity.")
    if skills:
        fallback_parts.append(f"My skills include {skills}.")
    if interests:
        fallback_parts.append(f"I am interested in {interests}.")

    if fallback_parts:
        return " ".join(fallback_parts).strip()

    return "I am an enthusiastic student eager to learn and grow."


def _generate_with_openai(question: str, profile: Dict[str, str]) -> str:
    """Generate answer using OpenAI-compatible API."""
    try:
        import httpx

        prompt = _build_prompt(question, profile)

        response = httpx.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.7,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[AI Agent] OpenAI API error: {e}")
        # Fallback to local generation
        return _generate_with_local_model(question, profile)


def _generate_with_grok(question: str, profile: Dict[str, str]) -> str:
    """Generate answer using Groq (Grok) API."""
    try:
        import httpx

        prompt = _build_prompt(question, profile)

        response = httpx.post(
            f"{GROK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.7,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[AI Agent] Grok API error: {e}")
        # Fallback to local generation
        return _generate_with_local_model(question, profile)


def generate_answer(question: str, profile_data: Dict[str, str]) -> str:
    """
    Generate an answer for a form question using the user's profile.
    
    Uses OpenAI API or Grok API if configured, otherwise falls back to local
    template-based generation with NLP understanding.
    """
    if AI_MODE == "grok" and GROK_API_KEY:
        return _generate_with_grok(question, profile_data)

    if AI_MODE == "openai" and OPENAI_API_KEY:
        return _generate_with_openai(question, profile_data)
    
    return _generate_with_local_model(question, profile_data)


def get_profile_as_dict(profile) -> Dict[str, str]:
    """Convert a UserProfile model instance to a flat dictionary."""
    return {
        "full_name": profile.full_name or "",
        "register_number": profile.register_number or "",
        "department": profile.department or "",
        "year": profile.year or "",
        "email": profile.email or "",
        "phone": profile.phone or "",
        "gender": profile.gender or "",
        "college_name": profile.college_name or "",
        "address": profile.address or "",
        "skills": profile.skills or "",
        "interests": profile.interests or "",
        "bio": profile.bio or "",
    }
