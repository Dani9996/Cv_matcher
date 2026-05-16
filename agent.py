"""
CV Matching Agent — core logic
Una sola chiamata al modello per velocità massima.
"""

import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def _ask_ollama(prompt: str, model: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,      # più deterministico = più veloce
            "num_predict": 1200,     # limita la lunghezza della risposta
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Ollama non risponde. Aprilo dall'icona nel menu bar oppure esegui 'ollama serve' nel Terminale."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout: il modello ha impiegato troppo. Prova phi3 che è più veloce.")
    except Exception as e:
        raise RuntimeError(f"Errore Ollama: {e}")


def _extract_json_block(text: str, key: str) -> dict | list:
    """Estrae un blocco JSON marcato con ===KEY_START=== ... ===KEY_END==="""
    pattern = rf"==={key}_START===(.*?)==={key}_END==="
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return {} if key != "ADVICE" else ""
    raw = match.group(1).strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _extract_advice_block(text: str) -> str:
    pattern = r"===ADVICE_START===(.*?)===ADVICE_END==="
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        # fallback: return everything after the last JSON block
        return text.split("===")[-1].strip()
    return match.group(1).strip()


def compute_skill_match(cv_data: dict, job_data: dict) -> dict:
    """Confronto competenze — nessuna chiamata LLM, pura logica Python."""
    cv_skills_lower = {s.lower() for s in cv_data.get("skills", [])}
    required    = job_data.get("required_skills", [])
    nice_to_have = job_data.get("nice_to_have_skills", [])

    matched, partial, missing = [], [], []
    for skill in required:
        sl = skill.lower()
        if sl in cv_skills_lower:
            matched.append(skill)
        elif any(sl in cs or cs in sl for cs in cv_skills_lower):
            partial.append(skill)
        else:
            missing.append(skill)

    nice_matched, nice_missing = [], []
    for skill in nice_to_have:
        sl = skill.lower()
        if sl in cv_skills_lower or any(sl in cs or cs in sl for cs in cv_skills_lower):
            nice_matched.append(skill)
        else:
            nice_missing.append(skill)

    total_possible = len(required) * 2 + len(nice_to_have) * 0.5
    earned = len(matched) * 2 + len(partial) * 1 + len(nice_matched) * 0.5
    score = round((earned / total_possible * 100) if total_possible > 0 else 50)
    score = min(score, 100)

    cv_years  = cv_data.get("years_experience", 0) or 0
    job_years = job_data.get("years_experience_required", 0) or 0

    return {
        "score": score,
        "matched": matched,
        "partial": partial,
        "missing_required": missing,
        "nice_matched": nice_matched,
        "nice_missing": nice_missing,
        "experience_ok": cv_years >= job_years if job_years > 0 else True,
        "cv_years": cv_years,
        "job_years": job_years,
    }


def run_analysis(cv_text: str, job_text: str, model: str = "llama3.2") -> dict:
    """
    Pipeline completa in UNA sola chiamata LLM.
    Il modello restituisce CV strutturato, job strutturato e consigli
    tutto insieme, delimitati da marker speciali.
    """
    if not cv_text.strip():
        raise ValueError("Incolla il testo del CV.")
    if not job_text.strip():
        raise ValueError("Incolla la descrizione del lavoro.")

    prompt = f"""You are a CV analysis expert. Analyze the CV and job description below.
Respond with EXACTLY this structure — no extra text before or after:

===CV_START===
{{
  "name": "...",
  "title": "...",
  "years_experience": 0,
  "skills": ["skill1", "skill2"],
  "education": ["degree1"],
  "experience": [{{"role": "...", "company": "...", "years": "..."}}],
  "summary": "Two sentences about this person."
}}
===CV_END===

===JOB_START===
{{
  "title": "...",
  "company": "...",
  "required_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill3"],
  "years_experience_required": 0,
  "education_required": "...",
  "industry": "..."
}}
===JOB_END===

===ADVICE_START===
Write 4 specific, actionable tips telling this candidate EXACTLY how to rewrite or reframe their CV for this job. Mention actual skills, roles and companies from their CV. Be concrete — no generic advice.
1. ...
2. ...
3. ...
4. ...
===ADVICE_END===

CV:
{cv_text[:3000]}

JOB DESCRIPTION:
{job_text[:2000]}"""

    raw = _ask_ollama(prompt, model)

    cv_data  = _extract_json_block(raw, "CV")
    job_data = _extract_json_block(raw, "JOB")
    advice   = _extract_advice_block(raw)

    # Fallback defaults so the UI never crashes
    cv_data.setdefault("name", "—")
    cv_data.setdefault("title", "—")
    cv_data.setdefault("years_experience", 0)
    cv_data.setdefault("skills", [])
    cv_data.setdefault("education", [])
    cv_data.setdefault("experience", [])
    cv_data.setdefault("summary", "")

    job_data.setdefault("title", "—")
    job_data.setdefault("company", "")
    job_data.setdefault("required_skills", [])
    job_data.setdefault("nice_to_have_skills", [])
    job_data.setdefault("years_experience_required", 0)
    job_data.setdefault("industry", "")

    match = compute_skill_match(cv_data, job_data)

    return {
        "cv": cv_data,
        "job": job_data,
        "match": match,
        "advice": advice or "Analisi completata — riprova se i consigli non appaiono.",
    }
