import streamlit as st
import anthropic
import json
import io
import re
import os
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import streamlit.components.v1 as components

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EduAI – Learn Anything",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #07090f;
    --surface:  #0d1120;
    --surface2: #131929;
    --gold:     #d4a853;
    --gold2:    #f0c878;
    --text:     #dce3f0;
    --muted:    #7a87a3;
    --accent:   #4f7ef5;
    --green:    #34c78a;
    --red:      #e05a5a;
    --border:   rgba(212,168,83,0.14);
    --border2:  rgba(255,255,255,0.07);
}

html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'Source Sans 3', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3,h4 { font-family: 'Playfair Display', serif !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] .stButton > button { width:100%; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #d4a853, #a87830) !important;
    color: #07090f !important; font-weight: 600 !important;
    border: none !important; border-radius: 7px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    letter-spacing: 0.02em !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover { background: linear-gradient(135deg, #f0c878, #d4a853) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 20px rgba(212,168,83,0.25) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 8px !important; padding: 4px !important; }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; border-radius: 6px !important; font-family: 'Source Sans 3', sans-serif !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: var(--gold) !important; background: var(--surface2) !important; }

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, var(--gold), #a87830) !important; }

/* Input / textarea */
.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; border-radius: 7px !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* Radio */
.stRadio label { color: var(--text) !important; }

/* Expander */
[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* Metric */
[data-testid="stMetric"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { color: var(--gold) !important; font-family: 'Playfair Display', serif !important; }

/* Alerts */
.stAlert { background: var(--surface) !important; border-radius: 8px !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: var(--surface) !important; border: 2px dashed rgba(212,168,83,0.3) !important; border-radius: 10px !important; }
[data-testid="stFileUploaderDropzoneInstructions"] { color: var(--muted) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Card */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin: 0.4rem 0;
    transition: all 0.18s ease;
}
.card:hover { border-color: rgba(212,168,83,0.4); background: var(--surface2); }
.card.done { border-left: 3px solid var(--green); }

/* Badge */
.badge {
    display: inline-block; padding: 3px 11px; border-radius: 20px;
    font-size: 12px; font-weight: 600; letter-spacing: 0.04em;
    font-family: 'JetBrains Mono', monospace;
}
.bg  { background: rgba(212,168,83,0.12); color: var(--gold); border: 1px solid rgba(212,168,83,0.28); }
.bb  { background: rgba(79,126,245,0.12); color: var(--accent); border: 1px solid rgba(79,126,245,0.28); }
.bgr { background: rgba(52,199,138,0.12); color: var(--green); border: 1px solid rgba(52,199,138,0.28); }
.br  { background: rgba(224,90,90,0.12); color: var(--red); border: 1px solid rgba(224,90,90,0.28); }

/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid rgba(212,168,83,0.4) !important;
}
.stDownloadButton > button:hover { background: rgba(212,168,83,0.1) !important; }

/* Selectbox */
.stSelectbox div[data-baseweb="select"] { background: var(--surface) !important; border-color: var(--border) !important; }

/* Code */
.stCode { background: var(--surface2) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ───────────────────────────────────────────────────────
def init():
    defaults = {
        'page': 'home',
        'pdf_text': None,
        'course': None,
        'cur_unit': 0,
        'unit_content': {},
        'exam_data': {},
        'unit_prog': {i: {'lecture': False, 'practice': False, 'score': None, 'summary': False} for i in range(15)},
        'exam_results': {},
        'cur_exam': None,
        'exam_ans': {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ── Anthropic Client ─────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = (
        st.secrets.get("ANTHROPIC_API_KEY", None)
        or os.environ.get("ANTHROPIC_API_KEY", "")
    )
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


# ── PDF Helpers ──────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    pages = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages.append(t)
    return "\n\n".join(pages)


def parse_json(text: str) -> dict:
    """Robustly extract JSON from model response."""
    # Try full parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find outermost {...}
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        return json.loads(m.group())
    raise ValueError("No JSON found in response")


# ── AI Calls ─────────────────────────────────────────────────────────────────
def ai_course_structure(pdf_text: str, client) -> dict:
    prompt = f"""You are an expert academic curriculum designer.

Analyze this textbook and design a comprehensive 15-unit course.

BOOK CONTENT (excerpt):
{pdf_text[:14000]}

Return ONLY valid JSON — no preamble, no markdown fences:
{{
  "title": "Course title",
  "subject": "Subject area",
  "description": "2-3 sentence course overview",
  "learning_outcomes": ["outcome 1", "outcome 2", "outcome 3", "outcome 4"],
  "units": [
    {{
      "unit_number": 1,
      "title": "Unit title",
      "description": "2-3 sentences describing what this unit covers",
      "topics": ["topic 1", "topic 2", "topic 3", "topic 4"]
    }}
  ]
}}
Include exactly 15 units. Make them progressive and cohesive."""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_json(resp.content[0].text)


def ai_unit_content(unit: dict, pdf_text: str, client) -> dict:
    n = unit['unit_number']
    L = len(pdf_text)
    chunk = pdf_text[int((n-1)/15*L): int(n/15*L)]

    prompt = f"""You are an expert lecturer creating teaching materials for:

Unit {n}: "{unit['title']}"
Description: {unit['description']}
Topics: {", ".join(unit['topics'])}

Relevant material:
{chunk[:7500]}

Return ONLY valid JSON:
{{
  "slides": [
    {{
      "slide_number": 1,
      "type": "title",
      "title": "Unit title slide",
      "bullets": ["subtitle or topics overview"],
      "formula": null,
      "narration": "Welcome to Unit {n}. In this lecture we will cover..."
    }},
    {{
      "slide_number": 2,
      "type": "concept",
      "title": "Concept title",
      "bullets": ["key point 1", "key point 2", "key point 3"],
      "formula": null,
      "narration": "Detailed spoken explanation of the concept (3-5 sentences, professor's voice)"
    }}
    // 12-15 slides total. Types: title|concept|example|proof|formula|summary
    // Include mathematical proofs and worked examples where appropriate
  ],
  "practice_questions": [
    {{
      "q_number": 1,
      "type": "mcq",
      "question": "Question text?",
      "options": ["A) Option one", "B) Option two", "C) Option three", "D) Option four"],
      "correct": "A",
      "explanation": "Why A is correct and others are not"
    }},
    {{
      "q_number": 6,
      "type": "open",
      "question": "Open-ended question requiring explanation?",
      "model_answer": "Comprehensive model answer"
    }}
    // Exactly 5 MCQ (q_number 1-5) and 2 open-ended (q_number 6-7)
  ],
  "summary": {{
    "key_concepts": ["concept 1", "concept 2", "concept 3", "concept 4", "concept 5"],
    "key_formulas": ["formula or theorem 1", "formula 2"],
    "important_points": ["point 1", "point 2", "point 3"],
    "connections": "How this unit connects to the wider course",
    "takeaway": "The single most important insight from this unit"
  }}
}}"""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=7000,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_json(resp.content[0].text)


def ai_exam(exam_type: str, course: dict, client) -> dict:
    units = course['units'][:7] if exam_type == 'midterm' else course['units']
    n_mcq = 20 if exam_type == 'midterm' else 30
    n_short = 4 if exam_type == 'midterm' else 6
    mins = 90 if exam_type == 'midterm' else 150
    title = "Mid-Term Examination" if exam_type == 'midterm' else "Final Examination"
    units_text = "\n".join(f"- Unit {u['unit_number']}: {u['title']}: {u['description']}" for u in units)

    prompt = f"""Create a rigorous {title} for this course.

Course: {course['title']}
Units covered:
{units_text}

Return ONLY valid JSON:
{{
  "title": "{title}",
  "course": "{course['title']}",
  "duration_minutes": {mins},
  "total_points": 100,
  "instructions": "Instructions for students",
  "sections": [
    {{
      "section_title": "Part A — Multiple Choice (50 points)",
      "section_type": "mcq",
      "questions": [
        {{
          "q_number": 1,
          "question": "Question text?",
          "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
          "correct": "B",
          "points": 2,
          "unit": 1
        }}
        // exactly {n_mcq} questions, 2 pts each
      ]
    }},
    {{
      "section_title": "Part B — Short Answer (30 points)",
      "section_type": "short_answer",
      "questions": [
        {{
          "q_number": {n_mcq+1},
          "question": "Short answer question requiring a paragraph?",
          "model_answer": "Model answer",
          "points": 7,
          "unit": 2
        }}
        // exactly {n_short} questions totalling 30 pts
      ]
    }},
    {{
      "section_title": "Part C — Extended Response (20 points)",
      "section_type": "extended",
      "questions": [
        {{
          "q_number": {n_mcq+n_short+1},
          "question": "Complex question requiring detailed analysis and synthesis",
          "model_answer": "Comprehensive model answer",
          "points": 20,
          "unit": 4
        }}
      ]
    }}
  ]
}}
Questions must test deep understanding, application and critical thinking — not mere recall."""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_json(resp.content[0].text)


# ── PDF Summary Generator ────────────────────────────────────────────────────
def build_summary_pdf(unit: dict, summary: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=2.2*cm, leftMargin=2.2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    S = lambda name, **kw: ParagraphStyle(name, parent=styles['Normal'], **kw)
    title_s   = S('T', fontSize=24, textColor=colors.HexColor('#c49640'),
                   fontName='Times-Bold', spaceAfter=10)
    label_s   = S('L', fontSize=10, textColor=colors.HexColor('#888888'),
                   fontName='Helvetica', spaceAfter=4)
    head_s    = S('H', fontSize=14, textColor=colors.HexColor('#c49640'),
                   fontName='Times-Bold', spaceBefore=16, spaceAfter=8)
    body_s    = S('B', fontSize=11, textColor=colors.HexColor('#1a1a2e'),
                   leading=17, spaceAfter=6)
    bullet_s  = S('BL', fontSize=11, textColor=colors.HexColor('#1a1a2e'),
                   leading=16, spaceAfter=4, leftIndent=18)
    italic_s  = S('I', fontSize=12, textColor=colors.HexColor('#333333'),
                   fontName='Times-Italic', leading=18, spaceAfter=6)

    gold = colors.HexColor('#c49640')
    story = []

    story.append(Paragraph(f"Unit {unit['unit_number']}", label_s))
    story.append(Spacer(1, 4))
    story.append(Paragraph(unit['title'], title_s))
    story.append(HRFlowable(width='100%', thickness=2, color=gold, spaceAfter=12))
    story.append(Paragraph(unit['description'], body_s))
    story.append(Spacer(1, 10))

    if summary.get('key_concepts'):
        story.append(Paragraph("Key Concepts", head_s))
        for c in summary['key_concepts']:
            story.append(Paragraph(f"• {c}", bullet_s))
        story.append(Spacer(1, 6))

    if summary.get('key_formulas'):
        story.append(Paragraph("Key Formulas & Theorems", head_s))
        for f in summary['key_formulas']:
            story.append(Paragraph(f"▸  {f}", bullet_s))
        story.append(Spacer(1, 6))

    if summary.get('important_points'):
        story.append(Paragraph("Important Points", head_s))
        for p in summary['important_points']:
            story.append(Paragraph(f"• {p}", bullet_s))
        story.append(Spacer(1, 6))

    if summary.get('connections'):
        story.append(Paragraph("Connections to the Course", head_s))
        story.append(Paragraph(summary['connections'], body_s))
        story.append(Spacer(1, 6))

    if summary.get('takeaway'):
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width='100%', thickness=1, color=gold))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Key Takeaway", head_s))
        story.append(Paragraph(summary['takeaway'], italic_s))

    doc.build(story)
    return buf.getvalue()


# ── Lecture Player HTML ──────────────────────────────────────────────────────
def lecture_player_html(slides: list, unit_title: str) -> str:
    data = json.dumps(slides, ensure_ascii=False)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;500;600&display=swap');
body{{background:#07090f;font-family:'Source Sans 3',sans-serif;color:#dce3f0;height:100vh;display:flex;flex-direction:column;overflow:hidden;padding:14px;gap:10px}}
.hdr{{display:flex;justify-content:space-between;align-items:center}}
.hdr-title{{font-size:12px;color:#7a87a3;text-transform:uppercase;letter-spacing:.08em}}
.counter{{font-size:12px;color:#d4a853;font-family:monospace;background:rgba(212,168,83,.1);padding:3px 11px;border-radius:20px;border:1px solid rgba(212,168,83,.25)}}
.pbar{{width:100%;height:3px;background:rgba(255,255,255,.07);border-radius:2px;overflow:hidden}}
.pfill{{height:100%;background:linear-gradient(90deg,#d4a853,#f0c878);border-radius:2px;transition:width .35s ease}}
.slide{{flex:1;background:#0d1120;border:1px solid rgba(212,168,83,.14);border-radius:12px;padding:28px 36px;overflow-y:auto;position:relative;min-height:0}}
.type-badge{{position:absolute;top:14px;right:14px;font-size:10px;padding:3px 10px;border-radius:12px;background:rgba(212,168,83,.1);color:#d4a853;border:1px solid rgba(212,168,83,.22);text-transform:uppercase;letter-spacing:.09em;font-weight:700}}
.stitle{{font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:#f0c878;margin-bottom:18px;line-height:1.3;padding-right:90px}}
.stitle.center{{text-align:center;font-size:30px;padding:0;margin-top:16px}}
.subtitle{{text-align:center;color:#7a87a3;font-size:15px;margin-top:8px;font-style:italic}}
.bigicon{{text-align:center;font-size:44px;margin-bottom:8px}}
.bullets{{display:flex;flex-direction:column;gap:8px}}
.bullet{{display:flex;gap:10px;align-items:flex-start;padding:9px 13px;background:rgba(255,255,255,.03);border-radius:7px;border-left:2px solid rgba(212,168,83,.28);font-size:14.5px;line-height:1.55;color:#c8d0e0;opacity:0;transform:translateX(-8px);animation:fi .35s ease forwards}}
.bicon{{color:#d4a853;font-size:13px;margin-top:2px;flex-shrink:0}}
.formula{{background:rgba(79,126,245,.08);border:1px solid rgba(79,126,245,.25);border-radius:9px;padding:14px 20px;margin-top:14px;font-family:'Courier New',monospace;font-size:15px;color:#a8c8f8;text-align:center;line-height:1.7;white-space:pre-wrap}}
@keyframes fi{{to{{opacity:1;transform:translateX(0)}}}}
.narrator{{background:#0d1120;border:1px solid rgba(212,168,83,.14);border-radius:9px;padding:12px 16px;display:flex;gap:11px;align-items:flex-start}}
.avi{{width:36px;height:36px;background:linear-gradient(135deg,#d4a853,#a87830);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;box-shadow:0 2px 10px rgba(212,168,83,.25)}}
.avi.sp{{animation:pulse 1.4s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{box-shadow:0 2px 10px rgba(212,168,83,.25)}}50%{{box-shadow:0 2px 20px rgba(212,168,83,.6)}}}}
.nar-label{{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#d4a853;font-weight:700;margin-bottom:3px}}
.nar-text{{font-size:13px;color:#7a87a3;line-height:1.6;font-style:italic}}
.ctrls{{display:flex;align-items:center;gap:10px}}
.btn{{padding:9px 18px;border-radius:7px;border:none;cursor:pointer;font-family:'Source Sans 3',sans-serif;font-size:13.5px;font-weight:600;transition:all .18s ease;white-space:nowrap}}
.btn-p{{background:linear-gradient(135deg,#d4a853,#a87830);color:#07090f}}
.btn-p:hover{{background:linear-gradient(135deg,#f0c878,#d4a853);transform:translateY(-1px)}}
.btn-s{{background:rgba(255,255,255,.06);color:#dce3f0;border:1px solid rgba(255,255,255,.1)}}
.btn-s:hover{{background:rgba(255,255,255,.11)}}
.btn-s:disabled{{opacity:.35;cursor:not-allowed}}
.btn-tts{{background:rgba(79,126,245,.13);color:#6b96ff;border:1px solid rgba(79,126,245,.28)}}
.btn-tts:hover{{background:rgba(79,126,245,.22)}}
.btn-tts.on{{background:rgba(79,126,245,.25);color:#90b4ff}}
.spacer{{flex:1}}
.slide-num-bar{{display:flex;gap:5px;align-items:center;justify-content:center;flex-wrap:wrap}}
.dot{{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.15);transition:background .2s ease;cursor:pointer}}
.dot.active{{background:#d4a853}}
.dot.done{{background:rgba(212,168,83,.4)}}
</style>
</head><body>
<div class="hdr">
  <div class="hdr-title">🎓 {unit_title}</div>
  <div class="counter" id="ctr">Slide 1 / 1</div>
</div>
<div class="pbar"><div class="pfill" id="pf" style="width:0%"></div></div>
<div class="slide" id="slide"></div>
<div class="narrator">
  <div class="avi" id="avi">🎓</div>
  <div style="flex:1;min-width:0">
    <div class="nar-label">Lecturer</div>
    <div class="nar-text" id="nar">Select a slide to begin.</div>
  </div>
</div>
<div class="ctrls">
  <button class="btn btn-s" id="bprev" onclick="go(-1)" disabled>◀ Prev</button>
  <button class="btn btn-s" id="bnext" onclick="go(1)">Next ▶</button>
  <div class="spacer"></div>
  <div class="slide-num-bar" id="dots"></div>
  <div class="spacer"></div>
  <button class="btn btn-tts" id="btts" onclick="tts()">🔊 Narrate</button>
</div>

<script>
const S={slides_json};
let i=0,speaking=false,synth=window.speechSynthesis;

function dots(){{
  const d=document.getElementById('dots');
  d.innerHTML=S.map((_,j)=>`<div class="dot ${{j===i?'active':j<i?'done':''}}" onclick="goTo(${{j}})"></div>`).join('');
}}

function render(){{
  const sl=S[i];
  document.getElementById('ctr').textContent=`Slide ${{i+1}} / ${{S.length}}`;
  document.getElementById('pf').style.width=`${{(i+1)/S.length*100}}%`;
  document.getElementById('bprev').disabled=i===0;
  document.getElementById('bnext').disabled=i===S.length-1;
  if(speaking){{synth.cancel();setSp(false);}}
  document.getElementById('nar').textContent=sl.narration||'';
  const c=document.getElementById('slide');
  let h='';
  if(sl.type==='title'){{
    h=`<div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;gap:14px;">
      <div class="bigicon">🎓</div>
      <h1 class="stitle center">${{sl.title}}</h1>
      <div class="subtitle">${{(sl.bullets||[]).join(' · ')}}</div>
    </div>`;
  }}else{{
    h=`<span class="type-badge">${{sl.type||'concept'}}</span>`;
    h+=`<h2 class="stitle">${{sl.title}}</h2>`;
    if(sl.bullets&&sl.bullets.length){{
      h+='<div class="bullets">';
      sl.bullets.forEach((b,k)=>{{h+=`<div class="bullet" style="animation-delay:${{k*.09}}s"><span class="bicon">▸</span><span>${{b}}</span></div>`;}});
      h+='</div>';
    }}
    if(sl.formula)h+=`<div class="formula">${{sl.formula}}</div>`;
  }}
  c.innerHTML=h;
  dots();
}}

function go(d){{
  const ni=i+d;
  if(ni>=0&&ni<S.length){{i=ni;render();}}
}}
function goTo(n){{i=n;render();}}

function setSp(v){{
  speaking=v;
  const b=document.getElementById('btts'),a=document.getElementById('avi');
  b.textContent=v?'⏹ Stop':'🔊 Narrate';
  b.className='btn btn-tts'+(v?' on':'');
  a.className='avi'+(v?' sp':'');
}}

function tts(){{
  if(speaking){{synth.cancel();setSp(false);return;}}
  const txt=S[i].narration||S[i].title;
  if(!txt)return;
  const u=new SpeechSynthesisUtterance(txt);
  u.rate=0.93;u.pitch=1.0;u.volume=1.0;
  const vs=synth.getVoices();
  const v=vs.find(x=>x.name.includes('Google')&&x.lang==='en-US')||vs.find(x=>x.lang==='en-US')||vs.find(x=>x.lang.startsWith('en'));
  if(v)u.voice=v;
  setSp(true);
  u.onend=()=>setSp(false);u.onerror=()=>setSp(false);
  synth.speak(u);
}}

document.addEventListener('keydown',e=>{{
  if(e.key==='ArrowRight'||e.key==='ArrowDown')go(1);
  if(e.key==='ArrowLeft'||e.key==='ArrowUp')go(-1);
  if(e.key===' '){{e.preventDefault();tts();}}
}});

synth.onvoiceschanged=()>{{}};
render();
</script>
</body></html>""".replace('{slides_json}', data)


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_home():
    c1, c2, c3 = st.columns([1, 2.2, 1])
    with c2:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 2.5rem">
            <div style="font-size:60px;margin-bottom:14px">🎓</div>
            <h1 style="font-family:'Playfair Display',serif;font-size:3.2rem;color:#f0c878;letter-spacing:-.01em">EduAI</h1>
            <p style="font-size:1.1rem;color:#7a87a3;margin:.5rem 0 2rem">Transform any textbook into a complete 15-unit AI-powered course</p>
            <div style="display:flex;gap:10px;justify-content:center;margin-bottom:2.5rem;flex-wrap:wrap">
                <span class="badge bg">🎬 AI Lectures</span>
                <span class="badge bb">✍️ Practice Questions</span>
                <span class="badge bgr">📊 Midterm &amp; Final Exams</span>
                <span class="badge bg">📄 PDF Summaries</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Drop your course textbook (PDF)", type=['pdf'])

        client = get_client()
        if not client:
            st.warning("⚠️ Set `ANTHROPIC_API_KEY` in environment variables or `.streamlit/secrets.toml` to continue.")

        if uploaded and client:
            st.markdown(f"<p style='color:#34c78a;text-align:center;font-size:.9rem'>✓ {uploaded.name} &nbsp;·&nbsp; {uploaded.size//1024} KB</p>", unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("🚀  Generate My Course", use_container_width=True):
                    with st.spinner("Reading PDF…"):
                        txt = extract_pdf_text(uploaded)
                        st.session_state.pdf_text = txt
                    with st.spinner("🤖 AI is designing your 15-unit course — ~30 seconds…"):
                        try:
                            course = ai_course_structure(txt, client)
                            st.session_state.course = course
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating course: {e}")

        # Feature showcase
        st.markdown("<br>", unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        for col, icon, label, desc in [
            (fc1, "🎬", "Video Lecture", "Slide-by-slide presentation with AI voice narration"),
            (fc2, "✍️", "Practice", "MCQ + open questions with instant feedback"),
            (fc3, "📋", "Exams", "Midterm (Unit 7) and Final (Unit 15) assessments"),
            (fc4, "📄", "Summary PDFs", "Downloadable unit summaries with key concepts"),
        ]:
            with col:
                st.markdown(f"""
                <div class="card" style="text-align:center">
                    <div style="font-size:1.8rem;margin-bottom:8px">{icon}</div>
                    <h3 style="font-family:'Playfair Display',serif;font-size:.95rem;color:#d4a853;margin-bottom:6px">{label}</h3>
                    <p style="color:#7a87a3;font-size:.82rem;line-height:1.5">{desc}</p>
                </div>""", unsafe_allow_html=True)


def page_dashboard():
    course = st.session_state.course
    prog = st.session_state.unit_prog
    completed = sum(1 for p in prog.values() if p['lecture'] and p['practice'])

    # Sidebar
    with st.sidebar:
        st.markdown(f"<h3 style='font-family:\"Playfair Display\",serif;color:#d4a853;font-size:1rem;margin-bottom:2px'>{course['title']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#7a87a3;font-size:.8rem;margin-bottom:12px'>{course.get('subject','')}</p>", unsafe_allow_html=True)
        st.metric("Units Complete", f"{completed} / 15")
        st.progress(completed / 15)
        st.markdown("<hr>", unsafe_allow_html=True)

        for i, u in enumerate(course['units']):
            done = prog[i]['lecture'] and prog[i]['practice']
            icon = "✅" if done else "▶"
            label = f"{icon} {i+1}. {u['title'][:22]}…" if len(u['title']) > 22 else f"{icon} {i+1}. {u['title']}"
            if st.button(label, key=f"snav{i}"):
                st.session_state.cur_unit = i
                st.session_state.page = 'unit'
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        can_mid = completed >= 7
        can_fin = completed >= 15

        if can_mid:
            mid_done = 'midterm' in st.session_state.exam_results
            if st.button(f"{'📋' if not mid_done else '✅'} Mid-Term Exam"):
                st.session_state.cur_exam = 'midterm'
                st.session_state.page = 'exam'
                st.rerun()
        else:
            st.markdown(f"<p style='color:#7a87a3;font-size:.8rem'>📋 Midterm unlocks after Unit 7 ({max(0,7-completed)} more)</p>", unsafe_allow_html=True)

        if can_fin:
            fin_done = 'final' in st.session_state.exam_results
            if st.button(f"{'🎓' if not fin_done else '✅'} Final Exam"):
                st.session_state.cur_exam = 'final'
                st.session_state.page = 'exam'
                st.rerun()
        else:
            st.markdown(f"<p style='color:#7a87a3;font-size:.8rem'>🎓 Final unlocks after all 15 units</p>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("🏠 Start New Course"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Main
    st.markdown(f"""
    <h1 style="font-family:'Playfair Display',serif;font-size:2.4rem;color:#f0c878">{course['title']}</h1>
    <p style="color:#7a87a3;margin-bottom:.3rem">{course.get('description','')}</p>""", unsafe_allow_html=True)

    with st.expander("📌 Learning Outcomes"):
        for o in course.get('learning_outcomes', []):
            st.markdown(f"• {o}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:\"Playfair Display\",serif;color:#d4a853;margin-bottom:1rem'>Course Units</h2>", unsafe_allow_html=True)

    for row in range(0, 15, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = row + j
            if idx >= 15:
                break
            u = course['units'][idx]
            p = prog[idx]
            done = p['lecture'] and p['practice']
            score_html = f"<span class='badge bgr' style='font-size:10px'>✓ {p['score']}%</span>" if p['score'] is not None else ""
            note = ""
            if idx == 6:
                note = "<div style='margin-top:8px'><span class='badge bb' style='font-size:10px'>📋 Midterm after this</span></div>"
            elif idx == 14:
                note = "<div style='margin-top:8px'><span class='badge bb' style='font-size:10px'>🎓 Final after this</span></div>"
            topics_html = "".join(f"<span style='font-size:.75rem;color:#7a87a3;display:block'>• {t}</span>" for t in u['topics'][:3])

            with col:
                st.markdown(f"""
                <div class="card {'done' if done else ''}">
                    <div style="display:flex;justify-content:space-between;margin-bottom:7px">
                        <span style="font-size:.75rem;color:#7a87a3;font-family:monospace">UNIT {u['unit_number']:02d}</span>
                        {'<span class="badge bgr" style="font-size:10px">Complete</span>' if done else '<span class="badge bg" style="font-size:10px">Not started</span>'}
                    </div>
                    <h3 style="font-family:'Playfair Display',serif;font-size:.95rem;color:#f0c878;margin-bottom:7px">{u['title']}</h3>
                    {topics_html}{note}
                </div>""", unsafe_allow_html=True)
                if st.button(f"{'Resume' if done else 'Start'} →", key=f"du{idx}", use_container_width=True):
                    st.session_state.cur_unit = idx
                    st.session_state.page = 'unit'
                    st.rerun()

        if row == 6:
            if completed >= 7:
                if st.button("📋 Take Mid-Term Exam", key="mid_btn", use_container_width=False):
                    st.session_state.cur_exam = 'midterm'
                    st.session_state.page = 'exam'
                    st.rerun()
            else:
                st.markdown("""<div style="background:rgba(79,126,245,.08);border:1px solid rgba(79,126,245,.25);border-radius:9px;padding:.9rem 1.4rem;margin:.5rem 0;display:flex;align-items:center;gap:12px">
                    <span style="font-size:1.5rem">📋</span>
                    <div><span style="color:#4f7ef5;font-family:'Playfair Display',serif;font-size:1rem">Mid-Term Examination</span>
                    <span style="color:#7a87a3;font-size:.82rem;display:block;margin-top:2px">Unlocks after completing Unit 7 · 90 min · 25 questions</span></div>
                </div>""", unsafe_allow_html=True)


def page_unit():
    course = st.session_state.course
    idx = st.session_state.cur_unit
    unit = course['units'][idx]
    client = get_client()

    with st.sidebar:
        if st.button("← Dashboard"):
            st.session_state.page = 'dashboard'; st.rerun()
        st.markdown(f"<div style='padding:.8rem 0'><div style='color:#7a87a3;font-size:.7rem;text-transform:uppercase'>Unit {unit['unit_number']}</div><h3 style='font-family:\"Playfair Display\",serif;color:#d4a853;font-size:.95rem;margin-top:3px'>{unit['title']}</h3></div>", unsafe_allow_html=True)
        p = st.session_state.unit_prog[idx]
        for lbl, done in [("🎬 Lecture", p['lecture']), ("✍️ Practice", p['practice']), ("📄 Summary", p['summary'])]:
            st.markdown(f"<p style='color:{'#34c78a' if done else '#7a87a3'};font-size:.88rem'>{'✅' if done else '○'} {lbl}</p>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        if idx > 0:
            if st.button("← Prev Unit"): st.session_state.cur_unit -= 1; st.rerun()
        if idx < 14:
            if st.button("Next Unit →"): st.session_state.cur_unit += 1; st.rerun()

    # Header
    st.markdown(f"""
    <div style="margin-bottom:1.4rem">
        <span style="color:#7a87a3;font-size:.8rem;text-transform:uppercase;letter-spacing:.1em">Unit {unit['unit_number']} of 15</span>
        <h1 style="font-family:'Playfair Display',serif;font-size:2.1rem;color:#f0c878;margin:.3rem 0 .5rem">{unit['title']}</h1>
        <p style="color:#7a87a3">{unit['description']}</p>
    </div>""", unsafe_allow_html=True)

    # Generate content on demand
    if idx not in st.session_state.unit_content:
        with st.spinner(f"🤖 Generating Unit {idx+1} content — ~20 seconds…"):
            try:
                content = ai_unit_content(unit, st.session_state.pdf_text, client)
                st.session_state.unit_content[idx] = content
            except Exception as e:
                st.error(f"Error: {e}"); return

    content = st.session_state.unit_content[idx]
    tab1, tab2, tab3 = st.tabs(["🎬  Lecture", "✍️  Practice", "📄  Summary"])

    # ── Tab 1: Lecture ──
    with tab1:
        slides = content.get('slides', [])
        if slides:
            components.html(lecture_player_html(slides, unit['title']), height=600, scrolling=False)
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                if not st.session_state.unit_prog[idx]['lecture']:
                    if st.button("✅  Mark Lecture Complete", use_container_width=True):
                        st.session_state.unit_prog[idx]['lecture'] = True
                        st.success("Lecture marked as complete!"); st.rerun()
                else:
                    st.markdown("<p style='text-align:center;color:#34c78a;font-size:.95rem'>✅ Lecture completed</p>", unsafe_allow_html=True)
        else:
            st.warning("No slides available for this unit.")

    # ── Tab 2: Practice ──
    with tab2:
        qs = content.get('practice_questions', [])
        st.markdown("<h3 style='font-family:\"Playfair Display\",serif;color:#d4a853'>Practice Questions</h3>", unsafe_allow_html=True)

        if not qs:
            st.warning("No practice questions available.")
        else:
            user_ans = {}
            for q in qs:
                qn = q.get('q_number', 0)
                qt = q.get('type', 'mcq')
                with st.expander(f"Q{qn}: {q.get('question','')[:70]}{'…' if len(q.get('question',''))>70 else ''}", expanded=True):
                    st.markdown(f"**{q.get('question','')}**")
                    if qt == 'mcq':
                        ans = st.radio("", q.get('options', []), key=f"pq_{idx}_{qn}", label_visibility='collapsed')
                        user_ans[qn] = {'type': 'mcq', 'ans': ans, 'correct': q.get('correct',''), 'expl': q.get('explanation','')}
                    else:
                        ans = st.text_area("Your answer:", key=f"pq_{idx}_{qn}_t", height=90)
                        if ans:
                            with st.expander("💡 Model Answer"):
                                st.markdown(q.get('model_answer', ''))

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("📊  Submit Answers", use_container_width=True):
                    mcqs = [q for q in qs if q.get('type') == 'mcq']
                    correct_count = 0
                    for q in mcqs:
                        qn = q.get('q_number', 0)
                        if qn in user_ans:
                            ua = user_ans[qn]['ans'] or ''
                            if ua.startswith(q.get('correct', '~~')):
                                correct_count += 1
                    pct = int(correct_count / len(mcqs) * 100) if mcqs else 0
                    st.session_state.unit_prog[idx]['practice'] = True
                    st.session_state.unit_prog[idx]['score'] = pct
                    if pct >= 70:
                        st.success(f"✅ {correct_count}/{len(mcqs)} correct — {pct}%")
                    else:
                        st.warning(f"⚠️ {correct_count}/{len(mcqs)} correct — {pct}% (review the lecture)")
                    for q in mcqs:
                        qn = q.get('q_number', 0)
                        if qn in user_ans:
                            ua = user_ans[qn]['ans'] or ''
                            ok = ua.startswith(q.get('correct', '~~'))
                            icon = "✅" if ok else "❌"
                            st.markdown(f"{icon} **Q{qn}:** {q.get('explanation','')}")

    # ── Tab 3: Summary ──
    with tab3:
        summary = content.get('summary', {})
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("<h3 style='font-family:\"Playfair Display\",serif;color:#d4a853'>Unit Summary</h3>", unsafe_allow_html=True)
            if summary.get('key_concepts'):
                st.markdown("**📚 Key Concepts**")
                for c in summary['key_concepts']:
                    st.markdown(f"• {c}")
                st.markdown("")
            if summary.get('key_formulas'):
                st.markdown("**📐 Key Formulas & Theorems**")
                for f in summary['key_formulas']:
                    st.code(f, language=None)
                st.markdown("")
            if summary.get('important_points'):
                st.markdown("**⭐ Important Points**")
                for pt in summary['important_points']:
                    st.markdown(f"• {pt}")
                st.markdown("")
            if summary.get('connections'):
                st.markdown(f"**🔗 Connections:** {summary['connections']}")
            if summary.get('takeaway'):
                st.info(f"💡 **Key Takeaway:** {summary['takeaway']}")

        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            pdf_bytes = build_summary_pdf(unit, summary)
            fname = f"Unit_{idx+1}_{unit['title'][:25].replace(' ','_')}.pdf"
            st.download_button(
                "📥 Download PDF Summary",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
                on_click=lambda: st.session_state.unit_prog.__setitem__(idx, {**st.session_state.unit_prog[idx], 'summary': True})
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Topics:**")
            for t in unit.get('topics', []):
                st.markdown(f"<span style='font-size:.82rem;color:#7a87a3'>• {t}</span>", unsafe_allow_html=True)


def page_exam():
    exam_type = st.session_state.cur_exam
    course = st.session_state.course
    client = get_client()

    with st.sidebar:
        if st.button("← Dashboard"):
            st.session_state.page = 'dashboard'; st.rerun()

    # Generate if needed
    if exam_type not in st.session_state.exam_data:
        lbl = "Mid-Term" if exam_type == 'midterm' else "Final"
        with st.spinner(f"🤖 Generating {lbl} Examination — ~30 seconds…"):
            try:
                exam = ai_exam(exam_type, course, client)
                st.session_state.exam_data[exam_type] = exam
                st.session_state.exam_ans[exam_type] = {}
            except Exception as e:
                st.error(f"Error: {e}"); return

    exam = st.session_state.exam_data[exam_type]

    # Already submitted?
    if exam_type in st.session_state.exam_results:
        show_results(exam_type, exam, st.session_state.exam_results[exam_type])
        return

    icon = "📋" if exam_type == 'midterm' else "🎓"
    st.markdown(f"""
    <div style="margin-bottom:1.8rem">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
            <span style="font-size:2rem">{icon}</span>
            <h1 style="font-family:'Playfair Display',serif;color:#f0c878;font-size:2rem">{exam.get('title','Exam')}</h1>
        </div>
        <div style="display:flex;gap:12px;margin-bottom:10px;flex-wrap:wrap">
            <span class="badge bg">⏱ {exam.get('duration_minutes',90)} min</span>
            <span class="badge bb">📊 {exam.get('total_points',100)} pts</span>
            <span class="badge bg">{course['title']}</span>
        </div>
        <p style="color:#7a87a3">{exam.get('instructions','Answer all questions.')}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    if exam_type not in st.session_state.exam_ans:
        st.session_state.exam_ans[exam_type] = {}

    for section in exam.get('sections', []):
        stype = section.get('section_type', 'mcq')
        st.markdown(f"<h2 style='font-family:\"Playfair Display\",serif;color:#d4a853;font-size:1.3rem;margin:1.5rem 0 .9rem'>{section.get('section_title','')}</h2>", unsafe_allow_html=True)

        for q in section.get('questions', []):
            qn = q.get('q_number', 0)
            st.markdown(f"**Q{qn}.** {q.get('question','')}  <span style='color:#7a87a3;font-size:.82rem'>({q.get('points',1)} pts)</span>", unsafe_allow_html=True)
            if stype == 'mcq':
                st.radio("", q.get('options', []), key=f"ex_{exam_type}_{qn}", label_visibility='collapsed')
            else:
                st.text_area("", key=f"ex_{exam_type}_{qn}_t", height=110, label_visibility='collapsed',
                             placeholder="Write your answer here…")
            st.markdown("---")

    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button(f"📤  Submit {exam.get('title','Exam')}", use_container_width=True):
            earned, total, details = 0, 0, []
            for section in exam.get('sections', []):
                stype = section.get('section_type', 'mcq')
                for q in section.get('questions', []):
                    qn = q.get('q_number', 0)
                    pts = q.get('points', 1)
                    total += pts
                    if stype == 'mcq':
                        ua = st.session_state.get(f"ex_{exam_type}_{qn}", '') or ''
                        ok = ua.startswith(q.get('correct', '~~'))
                        if ok: earned += pts
                        details.append({'qn': qn, 'ok': ok, 'pts': pts, 'unit': q.get('unit', '?')})
            pct = int(earned / total * 100) if total else 0
            st.session_state.exam_results[exam_type] = {'score': pct, 'earned': earned, 'total': total, 'details': details}
            st.rerun()


def show_results(exam_type: str, exam: dict, result: dict):
    score = result['score']
    grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'
    gc = {'A': '#34c78a', 'B': '#4f7ef5', 'C': '#d4a853', 'D': '#f09050', 'F': '#e05a5a'}[grade]
    emoji = '🏆' if score >= 90 else '🎯' if score >= 70 else '📚'

    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0">
        <div style="font-size:5rem;margin-bottom:14px">{emoji}</div>
        <h1 style="font-family:'Playfair Display',serif;color:#f0c878;font-size:2.4rem">{exam.get('title','Exam')} — Results</h1>
        <div style="font-size:4.5rem;font-weight:700;color:{gc};font-family:'Playfair Display',serif;margin:.4rem 0">{score}%</div>
        <div style="font-size:1.4rem;color:{gc}">Grade: {grade}</div>
        <div style="color:#7a87a3;margin-top:6px">{result['earned']} / {result['total']} MCQ points scored</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if score >= 70:
            st.success("✅ Passed — well done!")
        else:
            st.error("Need 70%+ to pass. Review the material and try again.")
    with c3:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'; st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family:\"Playfair Display\",serif;color:#d4a853'>Question Breakdown</h3>", unsafe_allow_html=True)
    for d in result.get('details', []):
        icon = "✅" if d['ok'] else "❌"
        st.markdown(f"{icon} &nbsp; **Q{d['qn']}** &nbsp; <span style='color:#7a87a3;font-size:.85rem'>{d['pts']} pts · Unit {d['unit']}</span>", unsafe_allow_html=True)


# ── Router ───────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == 'home':
    page_home()
elif page == 'dashboard':
    if st.session_state.course:
        page_dashboard()
    else:
        st.session_state.page = 'home'; st.rerun()
elif page == 'unit':
    if st.session_state.course:
        page_unit()
    else:
        st.session_state.page = 'home'; st.rerun()
elif page == 'exam':
    if st.session_state.course:
        page_exam()
    else:
        st.session_state.page = 'home'; st.rerun()
