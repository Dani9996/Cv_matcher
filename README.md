# CV Matching Agent

A local AI agent that reads your CV, compares it to a job description,
scores the match, and tells you exactly how to rewrite your CV to get the job.

**100% free — runs on your Mac with no API keys, no subscriptions.**

---

## How it works

1. You paste your CV and a job description into the app
2. A local AI model (Ollama) extracts structured data from both
3. The agent computes a skill-by-skill match score
4. The AI then generates personalised advice: what to rewrite, what to add,
   how to frame your existing experience to fit the role

---

## Setup — step by step

### Step 1 — Install Ollama

Ollama lets you run AI models locally on your Mac for free.

1. Go to https://ollama.com and click **Download for Mac**
2. Open the downloaded `.dmg` file and drag Ollama to your Applications folder
3. Open Ollama from Applications — you'll see a small icon appear in your menu bar

That's it. Ollama now runs silently in the background.

---

### Step 2 — Download an AI model

Open **Terminal** (press Cmd+Space, type "Terminal", press Enter) and run:

```bash
ollama pull llama3.2
```

This downloads the Llama 3.2 model (~2 GB). It only needs to happen once.

**If you have a GPU (Apple Silicon — M1/M2/M3/M4 chip):**
Llama 3.2 will use your GPU automatically and run fast (10–20 seconds per analysis).

**If you have an Intel Mac (CPU only):**
Use the smaller Phi-3 model instead — it's faster on CPU:
```bash
ollama pull phi3
```

Then select "phi3" in the model dropdown inside the app.

---

### Step 3 — Install Python dependencies

In Terminal, navigate to this project folder:

```bash
cd path/to/cv_agent
```

(Replace `path/to/cv_agent` with the actual folder path — e.g. `cd ~/Downloads/cv_agent`)

Then install the required packages:

```bash
pip3 install -r requirements.txt
```

If you get a "pip3 not found" error, install Python first from https://python.org/downloads

---

### Step 4 — Run the app

```bash
python3 app.py
```

Your browser will open automatically at **http://127.0.0.1:7860**

---

## Using the app

1. **Paste your CV** in the left text box (or replace the example text)
2. **Paste the job description** in the right text box
3. **Choose your model** from the dropdown (llama3.2 recommended)
4. Click **Analyse match →**
5. Wait 15–40 seconds while the local AI processes everything
6. Read your results:
   - **Parsed CV** — what the AI understood about you
   - **Parsed Job** — what the job requires
   - **Match Score** — % match with colour-coded skill breakdown
   - **Advice** — exact, personalised tips to adapt your CV

---

## Troubleshooting

**"Cannot connect to Ollama"**
Ollama is not running. Open the Ollama app from your Applications folder,
or run `ollama serve` in a Terminal window.

**The analysis is very slow**
Try a smaller model. In the dropdown, select `phi3` instead of `llama3.2`.

**"pip3 not found"**
You need Python. Download it from https://python.org/downloads
After installing, try again.

**The model gives bad JSON**
This can happen occasionally. Just click Analyse again — it usually works
on the second attempt.

---

## Available models (free, all via Ollama)

| Model | Size | Best for |
|-------|------|---------|
| llama3.2 | ~2 GB | Best quality, Apple Silicon |
| mistral | ~4 GB | Very good quality |
| phi3 | ~2 GB | Fastest on Intel/CPU |
| gemma2 | ~5 GB | Google's model, high quality |

Install any of them with: `ollama pull MODEL_NAME`

---

## Project structure

```
cv_agent/
├── app.py          ← Gradio web interface
├── agent.py        ← AI agent logic (parsing, matching, advice)
├── requirements.txt
└── README.md
```
