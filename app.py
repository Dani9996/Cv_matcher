"""
CV Matching Agent — Gradio web app
Run with: python3 app.py
"""

import gradio as gr
import pypdf
import docx as python_docx
from agent import run_analysis

# ── file extraction ───────────────────────────────────────────────────────────

def extract_text_from_file(filepath: str) -> str:
    """Extract plain text from a PDF or DOCX file."""
    if filepath is None:
        return ""
    lower = filepath.lower()
    if lower.endswith(".pdf"):
        reader = pypdf.PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if lower.endswith(".docx"):
        doc = python_docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    with open(filepath, "r", errors="ignore") as f:
        return f.read().strip()

# ── colour helpers ────────────────────────────────────────────────────────────

def score_colour(score: int) -> str:
    if score >= 75: return "#27500A"
    if score >= 45: return "#633806"
    return "#501313"

def score_bg(score: int) -> str:
    if score >= 75: return "#EAF3DE"
    if score >= 45: return "#FAEEDA"
    return "#FCEBEB"

def score_label(score: int) -> str:
    if score >= 75: return "✓ Ottima corrispondenza"
    if score >= 45: return "~ Corrispondenza parziale — riformulabile"
    return "✗ Lacune significative"

def pill(text: str, bg: str, fg: str) -> str:
    return (
        f'<span style="display:inline-block;margin:3px 3px 3px 0;'
        f'padding:4px 10px;border-radius:20px;font-size:12px;'
        f'background:{bg};color:{fg}">{text}</span>'
    )

# ── result renderer ───────────────────────────────────────────────────────────

def render_results(result: dict) -> tuple:
    cv     = result["cv"]
    job    = result["job"]
    match  = result["match"]
    advice = result["advice"]
    score  = match["score"]

    # Parsed CV
    exp_rows = "".join(
        f'<tr><td style="padding:3px 12px 3px 0;color:#555;font-size:13px">{e.get("role","")}</td>'
        f'<td style="padding:3px 0;font-size:13px;color:#888">{e.get("company","")} · {e.get("years","")}</td></tr>'
        for e in cv.get("experience", [])
    )
    skills_html = "".join(pill(s, "#E6F1FB", "#185FA5") for s in cv.get("skills", []))
    cv_html = f"""
<div style="font-family:system-ui,sans-serif;line-height:1.6;padding:4px">
  <p style="font-size:20px;font-weight:500;margin:0 0 2px">{cv.get('name','—')}</p>
  <p style="font-size:13px;color:#666;margin:0 0 12px">{cv.get('title','—')} &nbsp;·&nbsp; {cv.get('years_experience','?')} anni esp.</p>
  <p style="font-size:13px;color:#444;margin:0 0 14px">{cv.get('summary','')}</p>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">Competenze</p>
  <div style="margin-bottom:14px">{skills_html or '<span style="color:#aaa;font-size:13px">Nessuna trovata</span>'}</div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">Esperienza</p>
  <table style="border-collapse:collapse">{exp_rows}</table>
</div>"""

    # Parsed Job
    req_pills  = "".join(pill(s, "#EAF3DE", "#27500A") for s in job.get("required_skills", []))
    nice_pills = "".join(pill(s, "#FAEEDA", "#633806") for s in job.get("nice_to_have_skills", []))
    job_html = f"""
<div style="font-family:system-ui,sans-serif;line-height:1.6;padding:4px">
  <p style="font-size:20px;font-weight:500;margin:0 0 2px">{job.get('title','—')}</p>
  <p style="font-size:13px;color:#666;margin:0 0 14px">{job.get('company','') or 'Azienda non specificata'} &nbsp;·&nbsp; {job.get('industry','')}</p>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">Competenze richieste</p>
  <div style="margin-bottom:14px">{req_pills or '<span style="color:#aaa;font-size:13px">Nessuna specificata</span>'}</div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">Preferenziali</p>
  <div style="margin-bottom:14px">{nice_pills or '<span style="color:#aaa;font-size:13px">Nessuna</span>'}</div>
  <p style="font-size:13px;color:#555">Esperienza richiesta: <strong>{job.get('years_experience_required','?')} anni</strong></p>
</div>"""

    # Match score
    bar_colour = "#27500A" if score >= 75 else ("#E89B2B" if score >= 45 else "#A32D2D")
    exp_note = ""
    if not match["experience_ok"]:
        exp_note = f'<p style="font-size:12px;color:#A32D2D;margin:8px 0 0">⚠ Hai {match["cv_years"]} anni di esperienza; il ruolo ne richiede {match["job_years"]}.</p>'

    matched_pills = "".join(pill(s, "#EAF3DE", "#27500A") for s in match["matched"])
    partial_pills = "".join(pill(s, "#FAEEDA", "#633806") for s in match["partial"])
    missing_pills = "".join(pill(s, "#FCEBEB", "#A32D2D") for s in match["missing_required"])
    nice_m_pills  = "".join(pill(s, "#E6F1FB", "#185FA5") for s in match["nice_matched"])

    match_html = f"""
<div style="font-family:system-ui,sans-serif;line-height:1.6;padding:4px">
  <div style="background:{score_bg(score)};border-radius:10px;padding:16px 20px;margin-bottom:16px">
    <p style="font-size:38px;font-weight:500;color:{score_colour(score)};margin:0 0 2px">{score}%</p>
    <p style="font-size:13px;color:{score_colour(score)};margin:0 0 10px">{score_label(score)}</p>
    <div style="background:rgba(0,0,0,0.08);border-radius:4px;height:6px;overflow:hidden">
      <div style="width:{score}%;height:100%;background:{bar_colour};border-radius:4px"></div>
    </div>
    {exp_note}
  </div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">✓ Match forti</p>
  <div style="margin-bottom:12px">{matched_pills or '<span style="font-size:13px;color:#aaa">Nessuno trovato</span>'}</div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">~ Parziali / riformulabili</p>
  <div style="margin-bottom:12px">{partial_pills or '<span style="font-size:13px;color:#aaa">Nessuno</span>'}</div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">✗ Mancanti (richiesti)</p>
  <div style="margin-bottom:12px">{missing_pills or '<span style="font-size:13px;color:#aaa">Nessuno — ottimo!</span>'}</div>
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em">Preferenziali che hai</p>
  <div>{nice_m_pills or '<span style="font-size:13px;color:#aaa">Nessuno</span>'}</div>
</div>"""

    # Advice
    lines = [l.strip() for l in advice.strip().splitlines() if l.strip()]
    items = "".join(
        f'<div style="display:flex;gap:10px;padding:10px 0;border-bottom:0.5px solid #eee">'
        f'<span style="color:#185FA5;font-size:14px;margin-top:2px;flex-shrink:0">→</span>'
        f'<p style="font-size:13px;color:#333;margin:0;line-height:1.6">{l}</p></div>'
        for l in lines
    )
    advice_html = f"""
<div style="font-family:system-ui,sans-serif;padding:4px">
  <p style="font-size:11px;font-weight:500;color:#999;margin:0 0 12px;text-transform:uppercase;letter-spacing:.05em">Come adattare il tuo CV</p>
  {items}
</div>"""

    return cv_html, job_html, match_html, advice_html

# ── main handler ──────────────────────────────────────────────────────────────

def analyse(cv_file, cv_text: str, job_text: str, model: str) -> tuple:
    empty = ('<p style="color:#aaa;font-size:13px;font-family:system-ui">In attesa dell\'analisi…</p>',) * 4

    # File takes priority over pasted text
    final_cv = ""
    if cv_file is not None:
        try:
            final_cv = extract_text_from_file(cv_file)
        except Exception as e:
            return (f'<p style="color:#c00;font-size:13px">Errore nel file: {e}</p>', *empty[1:])

    if not final_cv.strip():
        final_cv = cv_text.strip()

    if not final_cv:
        return ('<p style="color:#c00;font-size:13px;font-family:system-ui">Carica un file o incolla il testo del CV.</p>', *empty[1:])
    if not job_text.strip():
        return ('<p style="color:#c00;font-size:13px;font-family:system-ui">Incolla la descrizione del lavoro.</p>', *empty[1:])

    try:
        result = run_analysis(final_cv, job_text.strip(), model)
    except Exception as e:
        return (f'<p style="color:#c00;font-size:13px;font-family:system-ui">Errore: {e}</p>', *empty[1:])

    return render_results(result)

# ── UI layout ─────────────────────────────────────────────────────────────────

css = """
footer { display: none !important; }
.gr-button-primary { background: #185FA5 !important; border-color: #185FA5 !important; }
textarea { font-size: 13px !important; line-height: 1.6 !important; }
"""

with gr.Blocks(css=css, title="CV Matching Agent") as demo:

    gr.HTML("""
    <div style="padding:20px 0 16px;border-bottom:1px solid #eee;margin-bottom:24px">
      <h1 style="font-size:22px;font-weight:500;margin:0 0 4px;font-family:system-ui">CV Matching Agent</h1>
      <p style="font-size:14px;color:#888;margin:0;font-family:system-ui">
        Carica il tuo CV (PDF/DOCX) o incollalo, aggiungi l'offerta di lavoro — l'agente analizza il match e ti dice come adattare il CV. Gira al 100% in locale, gratis.
      </p>
    </div>
    """)

    with gr.Row():
        with gr.Column():
            gr.HTML('<p style="font-size:13px;font-weight:500;margin:0 0 8px;font-family:system-ui">📄 Il tuo CV</p>')
            cv_file = gr.File(
                label="Carica PDF o DOCX",
                file_types=[".pdf", ".docx", ".txt"],
                file_count="single",
                type="filepath",
            )
            cv_text = gr.Textbox(
                label="Oppure incolla il testo del CV qui sotto",
                placeholder="Nome, competenze, esperienze lavorative, istruzione…",
                lines=9,
            )

        with gr.Column():
            gr.HTML('<p style="font-size:13px;font-weight:500;margin:0 0 8px;font-family:system-ui">💼 Offerta di lavoro</p>')
            job_text = gr.Textbox(
                label="Incolla qui l'annuncio di lavoro",
                placeholder="Titolo, requisiti, competenze richieste, responsabilità…",
                lines=15,
            )

    with gr.Row():
        model_choice = gr.Dropdown(
            label="Modello Ollama",
            choices=["llama3.2", "mistral", "phi3", "gemma2", "llama3"],
            value="llama3.2",
            scale=1,
        )
        analyse_btn = gr.Button("Analizza il match →", variant="primary", scale=3)

    gr.HTML("""
    <div style="font-family:system-ui;font-size:12px;color:#999;margin:8px 0 20px;
                padding:10px 14px;background:#f7f7f7;border-radius:8px;border-left:3px solid #ddd">
      ⏱ L'analisi richiede 20–60 secondi sul tuo Mac con Apple Silicon.<br>
      Assicurati che Ollama sia aperto (icona nella barra del menu) oppure esegui <code>ollama serve</code> nel Terminale.
    </div>
    """)

    gr.HTML("<hr style='border:none;border-top:1px solid #eee;margin:0 0 20px'>")
    gr.HTML('<p style="font-size:14px;font-weight:500;margin:0 0 16px;font-family:system-ui">Risultati</p>')

    with gr.Row():
        cv_out  = gr.HTML(label="CV analizzato")
        job_out = gr.HTML(label="Offerta analizzata")

    with gr.Row():
        match_out  = gr.HTML(label="Punteggio match")
        advice_out = gr.HTML(label="Consigli personalizzati")

    analyse_btn.click(
        fn=analyse,
        inputs=[cv_file, cv_text, job_text, model_choice],
        outputs=[cv_out, job_out, match_out, advice_out],
    )

if __name__ == "__main__":
    print("\n✓ CV Matching Agent avviato")
    print("  Apri il browser su: http://127.0.0.1:7860\n")
    demo.launch(inbrowser=True)
