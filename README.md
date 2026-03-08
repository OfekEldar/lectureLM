# 🎓 EduAI — AI-Powered Course Learning Platform

Transform any textbook PDF into a complete 15-unit interactive course with AI lectures, practice questions, exams, and PDF summaries.

---

## Features

| Feature | Details |
|---|---|
| **15 Teaching Units** | AI automatically divides your book into 15 logical, progressive units |
| **AI Lecture Player** | Slide-by-slide presentation with voice narration (Web Speech API) |
| **Practice Questions** | 5 MCQ + 2 open-ended questions per unit with instant feedback |
| **PDF Unit Summaries** | Downloadable summaries with key concepts, formulas, and takeaways |
| **Mid-Term Exam** | 25-question exam covering Units 1–7, unlocks after Unit 7 |
| **Final Exam** | 40-question comprehensive exam, unlocks after all 15 units |
| **Progress Tracking** | Visual progress dashboard across all units |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

**Option A — Streamlit secrets (recommended):**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your key
```

**Option B — Environment variable:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## How It Works

```
Upload PDF
    │
    ▼
Claude analyzes the book
    │
    ▼
Generates 15-unit course structure
    │
    ├──► Unit 1 ──► Lecture (slides + narration)
    │              ──► Practice (MCQ + open-ended)
    │              ──► PDF Summary
    │
    ├──► Units 2–7 (same)
    │
    ├──► 📋 MID-TERM EXAM (after Unit 7)
    │
    ├──► Units 8–15 (same)
    │
    └──► 🎓 FINAL EXAM (after Unit 15)
```

### Content generation
- **Course structure** is generated once when the PDF is uploaded (~30 seconds)
- **Unit content** (slides, questions, summary) is generated on first visit to each unit (~20 seconds)
- **Exams** are generated on first access (~30 seconds)
- All generated content is cached in session state — no re-generation on re-visits

---

## Lecture Player

The lecture player is a custom HTML/JavaScript component embedded in Streamlit:

- **Navigation**: Click Prev/Next buttons, dot navigation, or use arrow keys
- **Voice narration**: Click "🔊 Narrate" to hear the AI-generated narration (uses browser's Web Speech API)
- **Keyboard shortcuts**: `←/→` navigate slides, `Space` toggles narration
- **Slide types**: title, concept, example, proof, formula, summary — each with unique styling

---

## Exam System

| Exam | Unlocks | Questions | Time | Points |
|---|---|---|---|---|
| Mid-Term | After completing Unit 7 | 25 (MCQ) + short answer + essay | 90 min | 100 |
| Final | After completing all 15 units | 30 (MCQ) + short answer + essay | 150 min | 100 |

Grading scale: A ≥ 90 · B ≥ 80 · C ≥ 70 · D ≥ 60 · F < 60

---

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add `ANTHROPIC_API_KEY` in the Secrets section

---

## Tech Stack

- **Frontend**: Streamlit + custom HTML/CSS/JS components
- **AI**: Anthropic Claude (claude-sonnet-4-20250514)
- **PDF reading**: pypdf
- **PDF generation**: ReportLab
- **Voice**: Browser Web Speech API (no external TTS service needed)
