"""
RiskMind AI – Project Risk Analysis Assistant
==============================================
A beginner-friendly AI-powered project risk management tool.
Uses Groq API (LLaMA models) to analyze project descriptions and
generate a structured risk register following PMBOK-style reasoning.

Author:  AI Software Engineering Assignment
Version: 1.0.0
"""

import os
import json
import re
import streamlit as st
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# ── Load environment variables from .env file ─────────────────────────────────
load_dotenv()

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RiskMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS injection ──────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Inter font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Hide default Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: rgba(14,17,23,0.85) !important;
    backdrop-filter: blur(12px) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1119 0%, #161927 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.15) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    color: #b0b8c8 !important;
    font-size: 0.88rem !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(99,102,241,0.06)) !important;
    border: 1px solid rgba(124,58,237,0.18) !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(124,58,237,0.12);
}
div[data-testid="stMetric"] label {
    color: #8b92a5 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f0f2f6 !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: #8b92a5 !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 24px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #a78bfa !important;
    background: rgba(124,58,237,0.06) !important;
}

/* ── Primary button ── */
button[kind="primary"], .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7C3AED, #6366F1) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em;
    padding: 12px 24px !important;
    transition: all 0.25s ease !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(124,58,237,0.35) !important;
    transform: translateY(-1px);
}

/* ── Text area ── */
textarea {
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-radius: 12px !important;
    background: rgba(14,17,23,0.6) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease !important;
}
textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
}

/* ── File uploader ── */
section[data-testid="stFileUploader"] {
    border: 2px dashed rgba(124,58,237,0.25) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    background: rgba(124,58,237,0.03) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(124,58,237,0.12) !important;
}

/* ── Expander ── */
details {
    border: 1px solid rgba(124,58,237,0.12) !important;
    border-radius: 14px !important;
    background: rgba(14,17,23,0.4) !important;
}
details summary {
    font-weight: 600 !important;
    color: #c4b5fd !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    border-radius: 12px !important;
    color: #a78bfa !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(124,58,237,0.1) !important;
    border-color: #7C3AED !important;
}

/* ── Dividers ── */
hr {
    border-color: rgba(124,58,237,0.1) !important;
    margin: 2rem 0 !important;
}

/* ── Subheaders ── */
.stSubheader, h2, h3 {
    color: #e2e0f0 !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.25); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.45); }
</style>
""", unsafe_allow_html=True)

# ── Colour / style constants ───────────────────────────────────────────────────
PRIORITY_COLOURS = {
    "Critical": "#EF4444",
    "High":     "#F97316",
    "Medium":   "#EAB308",
    "Low":      "#22C55E",
}

CATEGORY_ICONS = {
    "Schedule Risk":             "🗓️",
    "Cost Risk":                 "💰",
    "Scope Creep Risk":          "📐",
    "Resource Risk":             "👥",
    "Vendor / Procurement Risk": "🤝",
    "Technical Risk":            "⚙️",
    "Communication Risk":        "💬",
    "Stakeholder Risk":          "🏢",
    "Quality Risk":              "✅",
}

# ── Numeric weights for probability / impact ───────────────────────────────────
LEVEL_WEIGHTS = {"Low": 1, "Medium": 2, "High": 3}


# ════════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════

def get_groq_client() -> Groq:
    """Initialise and return a Groq client using the API key from .env or secrets."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error(
            "⚠️  **GROQ_API_KEY not found.**  "
            "Add it to your `.env` file or set it as an environment variable."
        )
        st.stop()
    return Groq(api_key=api_key)


def build_system_prompt() -> str:
    """
    Return the system prompt that instructs the LLM to act as a
    PMBOK-style Project Risk Management Analyst.
    """
    return """You are a senior Project Risk Management Analyst with 15+ years of experience 
following PMBOK (Project Management Body of Knowledge) standards.

Your task is to analyze project descriptions, meeting notes, or scope documents and 
identify ALL potential project risks.

STRICT RULES:
1. Return ONLY valid JSON — no markdown fences, no extra text before or after.
2. Classify every risk into exactly ONE of these categories:
   - Schedule Risk
   - Cost Risk
   - Scope Creep Risk
   - Resource Risk
   - Vendor / Procurement Risk
   - Technical Risk
   - Communication Risk
   - Stakeholder Risk
   - Quality Risk
3. Rate Probability, Impact, and Priority as: Low | Medium | High
   (Priority may also be Critical for the most severe risks)
4. Evidence must be a direct quote or close paraphrase from the input text.
5. Recommendation must be a concrete, actionable mitigation strategy.
6. Identify a minimum of 5 risks; more if the text warrants it.

JSON SCHEMA (return exactly this structure):
{
  "project_summary": "<2-3 sentence summary of the project>",
  "risks": [
    {
      "risk_name": "<short descriptive name>",
      "category": "<one of the 9 categories above>",
      "evidence": "<quote or paraphrase from the input>",
      "probability": "<Low|Medium|High>",
      "impact": "<Low|Medium|High>",
      "priority": "<Low|Medium|High|Critical>",
      "recommendation": "<specific mitigation action>"
    }
  ]
}"""


def build_user_prompt(project_text: str) -> str:
    """Wrap the user's project text in a clear instruction prompt."""
    return f"""Analyze the following project description and produce the risk register JSON.

PROJECT DESCRIPTION:
\"\"\"
{project_text}
\"\"\"

Remember: Return ONLY the JSON object — nothing else."""


def call_groq_api(client: Groq, project_text: str, model: str) -> dict:
    """
    Send the project description to the Groq API and return the parsed JSON response.

    Parameters
    ----------
    client       : Groq client instance
    project_text : raw user input
    model        : Groq model identifier string

    Returns
    -------
    dict  – parsed risk register data
    """
    with st.spinner("🤖 Analysing project risks — this may take a few seconds…"):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user",   "content": build_user_prompt(project_text)},
            ],
            temperature=0.3,   # Lower = more consistent, structured output
            max_tokens=4096,
        )

    raw_text = response.choices[0].message.content.strip()
    return parse_llm_response(raw_text)


def parse_llm_response(raw_text: str) -> dict:
    """
    Safely parse the LLM's raw text response into a Python dict.
    Handles common formatting quirks (e.g. stray markdown fences).

    Parameters
    ----------
    raw_text : str  – the raw string from the LLM

    Returns
    -------
    dict – validated risk data

    Raises
    ------
    ValueError if JSON cannot be parsed
    """
    # Strip markdown code fences if the model accidentally adds them
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$",          "", cleaned,  flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Could not parse LLM response as JSON.\n\nRaw response:\n{raw_text}"
        ) from exc

    # Basic validation
    if "risks" not in data or not isinstance(data["risks"], list):
        raise ValueError("Response JSON is missing the 'risks' array.")

    return data


def calculate_priority_score(probability: str, impact: str) -> int:
    """
    Compute a numeric priority score: Probability × Impact (1–9 scale).

    Parameters
    ----------
    probability : str  – "Low" | "Medium" | "High"
    impact      : str  – "Low" | "Medium" | "High"

    Returns
    -------
    int  – score between 1 and 9
    """
    p = LEVEL_WEIGHTS.get(probability, 1)
    i = LEVEL_WEIGHTS.get(impact, 1)
    return p * i


def risks_to_dataframe(risks: list[dict]) -> pd.DataFrame:
    """
    Convert the list of risk dicts to a clean Pandas DataFrame,
    adding a numeric priority score column.

    Parameters
    ----------
    risks : list of risk dicts from the LLM

    Returns
    -------
    pd.DataFrame
    """
    rows = []
    for idx, risk in enumerate(risks, start=1):
        prob    = risk.get("probability", "Medium")
        impact  = risk.get("impact",      "Medium")
        score   = calculate_priority_score(prob, impact)
        cat     = risk.get("category", "")
        icon    = CATEGORY_ICONS.get(cat, "⚠️")

        rows.append({
            "#":             idx,
            "Risk Name":     risk.get("risk_name",     "Unknown"),
            "Category":      f"{icon} {cat}",
            "Evidence":      risk.get("evidence",      "—"),
            "Probability":   prob,
            "Impact":        impact,
            "Priority":      risk.get("priority",      "Medium"),
            "Score (P×I)":   score,
            "Recommendation": risk.get("recommendation", "—"),
        })

    df = pd.DataFrame(rows)
    # Sort by score descending so highest risks appear first
    df = df.sort_values("Score (P×I)", ascending=False).reset_index(drop=True)
    df["#"] = df.index + 1   # Re-number after sort
    return df


def colour_priority(val: str) -> str:
    """Return a CSS background-color style string based on priority label."""
    colour = PRIORITY_COLOURS.get(val, "#CCCCCC")
    text   = "#FFFFFF" if val in ("Critical", "High") else "#000000"
    return f"background-color: {colour}; color: {text}; font-weight: bold; border-radius: 4px;"


def style_dataframe(df: pd.DataFrame) -> "pd.io.formats.style.Styler":
    """Apply conditional colouring to the Priority column."""
    return (
        df.style
          .applymap(colour_priority, subset=["Priority"])
          .set_properties(**{"text-align": "left"})
          .set_table_styles([
              {"selector": "thead th",
               "props": [("background-color", "#1E1E2E"), ("color", "white"),
                         ("font-weight", "bold"), ("text-align", "left")]},
          ])
          .hide(axis="index")
    )


def render_summary_card(summary: str) -> None:
    """Render the project summary as a styled card."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(124,58,237,0.06), rgba(99,102,241,0.04));
            border: 1px solid rgba(124,58,237,0.15);
            border-radius: 16px;
            padding: 24px 28px;
            margin: 8px 0 24px 0;
            color: #cbd5e1;
            font-size: 0.92rem;
            line-height: 1.7;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute; top: 0; left: 0; width: 4px; height: 100%;
                background: linear-gradient(180deg, #7C3AED, #6366F1);
                border-radius: 16px 0 0 16px;
            "></div>
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <span style="
                    background: rgba(124,58,237,0.12); border-radius:10px;
                    padding: 6px 10px; font-size: 1.1rem;
                ">📋</span>
                <span style="color:#c4b5fd; font-weight:600; font-size:0.95rem; letter-spacing:0.02em;">Project Summary</span>
            </div>
            {summary}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame) -> None:
    """Display quick-glance KPI metrics above the risk table."""
    total    = len(df)
    critical = len(df[df["Priority"] == "Critical"])
    high     = len(df[df["Priority"] == "High"])
    medium   = len(df[df["Priority"] == "Medium"])
    avg_score = df["Score (P×I)"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Risks",    total)
    c2.metric("Critical",       critical)
    c3.metric("High",           high)
    c4.metric("Medium",         medium)
    c5.metric("Avg Score",      f"{avg_score:.1f}")


def render_risk_chart(df: pd.DataFrame) -> None:
    """Render a horizontal bar chart of risk scores."""
    chart_data = (
        df[["Risk Name", "Score (P×I)"]]
        .set_index("Risk Name")
        .sort_values("Score (P×I)")
    )
    st.bar_chart(chart_data, color="#7C3AED", height=320)


# ════════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> str:
    """Render the sidebar and return the selected model name."""
    with st.sidebar:
        st.image(
            "https://img.icons8.com/color/96/artificial-intelligence.png",
            width=64,
        )
        st.title("⚙️ Settings")
        st.divider()

        model = st.selectbox(
            "🤖 LLM Model",
            options=[
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
            ],
            index=0,
            help=(
                "**llama-3.1-8b-instant** – faster, lighter model (default).\n\n"
                "**llama-3.3-70b-versatile** – slower but more nuanced analysis."
            ),
        )

        st.divider()
        st.markdown("### 📘 How to use")
        st.markdown(
            """
1. Paste a **project description**, meeting notes, or scope document.
2. Click **Analyse Project Risks**.
3. Review the AI-generated **risk register**.
4. Download as **CSV** if needed.
            """
        )

        st.divider()
        st.markdown("### 🎯 Risk Priority Score")
        st.markdown(
            """
| Score | Label     |
|-------|-----------|
| 9     | 🔴 Critical |
| 6     | 🟠 High     |
| 3–4   | 🟡 Medium   |
| 1–2   | 🟢 Low      |

Score = **Probability × Impact** (each 1–3)
            """
        )

        st.divider()
        st.caption("RiskMind AI v1.0 · Powered by Groq + LLaMA")

    return model


# ════════════════════════════════════════════════════════════════════════════════
#  EXAMPLE PROJECT DESCRIPTIONS
# ════════════════════════════════════════════════════════════════════════════════

EXAMPLE_PROJECT = """Project Title: E-Commerce Platform Relaunch

Our company plans to relaunch our e-commerce website within the next 4 months to 
coincide with the holiday shopping season. The project involves migrating from our 
legacy PHP system to a new React/Node.js stack, integrating three third-party payment 
gateways (Stripe, PayPal, and a new regional provider), and redesigning the entire 
UI/UX based on customer research.

The budget is $280,000. However, the finance team has flagged that a 15% budget 
reduction may be required due to broader company cost-cutting measures. The project 
team consists of 6 developers (2 of whom are contractors ending their contracts in 
6 weeks), 1 UX designer, and a part-time project manager who is also managing two 
other projects simultaneously.

Key stakeholders include the CEO (who has requested several last-minute feature 
additions), the Head of Marketing (whose requirements are still being finalised), 
and an external vendor providing the new inventory management module. The vendor 
has not yet delivered the API documentation required for integration.

Initial testing has revealed compatibility issues between the new payment gateway 
and our existing customer database schema. The team has no prior experience with the 
new tech stack and training has not yet been scheduled. There are no formal change 
control procedures in place, and team communication is currently handled via 
informal email chains with no project management tool in use.
"""


# ════════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Entry point – renders the full Streamlit application."""

    # ── Sidebar ──────────────────────────────────────────────────────────────
    selected_model = render_sidebar()

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; padding: 24px 0 8px 0;">
            <div style="
                display:inline-flex; align-items:center; justify-content:center;
                width:64px; height:64px; border-radius:18px;
                background: linear-gradient(135deg, #7C3AED, #6366F1);
                margin-bottom: 16px;
                box-shadow: 0 8px 32px rgba(124,58,237,0.25);
            ">
                <span style="font-size:2rem;">🧠</span>
            </div>
            <h1 style="
                font-size:2.2rem; margin:0 0 6px 0; font-weight:700;
                background: linear-gradient(135deg, #f0f2f6, #c4b5fd);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.02em;
            ">
                RiskMind AI
            </h1>
            <p style="color:#6b7280; font-size:0.9rem; margin:0; font-weight:400; letter-spacing:0.02em;">
                AI-powered project risk analysis
            </p>
        </div>
        <div style="
            width:80px; height:3px; margin:20px auto 28px auto;
            background: linear-gradient(90deg, #7C3AED, #6366F1);
            border-radius: 4px;
        "></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input section ─────────────────────────────────────────────────────────
    st.subheader("📝 Project Description")

    tab_paste, tab_upload = st.tabs(["✏️ Paste Text", "📁 Upload Files"])

    with tab_paste:
        col_input, col_example = st.columns([5, 1])
        with col_example:
            if st.button("📄 Load Example", help="Fill in a sample project description"):
                st.session_state["project_input"] = EXAMPLE_PROJECT

        with col_input:
            st.caption("Paste your project description, meeting notes, or scope document below.")

        pasted_text = st.text_area(
            label="Project Description",
            key="project_input",
            height=240,
            placeholder=(
                "Paste your project description, meeting notes, or scope document here…\n\n"
                "Tip: Use the '📄 Load Example' button on the right to see a demo."
            ),
            label_visibility="collapsed",
        )

    with tab_upload:
        st.caption(
            "Upload one or more text files (.txt, .md, .csv, .log, .json). "
            "Their contents will be combined for analysis."
        )
        uploaded_files = st.file_uploader(
            "Upload project documents",
            type=["txt", "md", "csv", "log", "json"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        uploaded_text = ""
        if uploaded_files:
            file_contents = []
            for uf in uploaded_files:
                try:
                    content = uf.read().decode("utf-8", errors="replace")
                    file_contents.append(f"--- {uf.name} ---\n{content}")
                except Exception:
                    st.warning(f"⚠️ Could not read **{uf.name}** — skipped.")
            uploaded_text = "\n\n".join(file_contents)
            if uploaded_text.strip():
                with st.expander("📄 Preview uploaded content", expanded=False):
                    st.text(uploaded_text[:3000] + ("…" if len(uploaded_text) > 3000 else ""))

    # Combine: uploaded files take priority; pasted text used as fallback
    project_text = uploaded_text.strip() if uploaded_text and uploaded_text.strip() else (pasted_text or "").strip()

    # ── Analyse button ────────────────────────────────────────────────────────
    analyse_clicked = st.button(
        "🔍 Analyse Project Risks",
        type="primary",
        use_container_width=True,
        disabled=not bool(project_text),
    )

    if not project_text:
        st.info("ℹ️  Paste a project description or upload files above, then click **Analyse Project Risks**.")
        return

    if not analyse_clicked:
        return

    # ── API call ──────────────────────────────────────────────────────────────
    client = get_groq_client()

    try:
        data = call_groq_api(client, project_text.strip(), selected_model)
    except ValueError as exc:
        st.error(f"❌ **Parsing Error:** {exc}")
        return
    except Exception as exc:
        st.error(f"❌ **API Error:** {exc}")
        return

    # ── Extract results ───────────────────────────────────────────────────────
    summary = data.get("project_summary", "No summary provided.")
    risks   = data.get("risks", [])

    if not risks:
        st.warning("⚠️  The model returned no risks. Try a more detailed project description.")
        return

    df = risks_to_dataframe(risks)

    # ── Project summary ───────────────────────────────────────────────────────
    render_summary_card(summary)

    # ── KPI metrics ───────────────────────────────────────────────────────────
    render_metrics(df)

    st.divider()

    # ── Risk register table ───────────────────────────────────────────────────
    st.subheader("Risk Register")
    st.caption(
        f"**{len(df)} risks** identified, sorted by priority score. "
        "Score = Probability × Impact (max 9)."
    )

    # Styled table
    st.dataframe(
        style_dataframe(df),
        use_container_width=True,
        height=min(100 + len(df) * 58, 620),  # Dynamic height, capped at 620px
    )

    st.divider()

    # ── Risk score bar chart ──────────────────────────────────────────────────
    st.subheader("Risk Priority Chart")
    st.caption("Score distribution across all identified risks.")
    render_risk_chart(df)

    st.divider()

    # ── Detailed risk cards ───────────────────────────────────────────────────
    with st.expander("Detailed Risk Breakdown", expanded=False):
        for _, row in df.iterrows():
            priority_colour = PRIORITY_COLOURS.get(row["Priority"], "#888")
            text_col = '#fff' if row['Priority'] in ('Critical', 'High') else '#000'
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(30,30,46,0.8), rgba(22,25,39,0.9));
                    border: 1px solid rgba(124,58,237,0.1);
                    border-radius: 16px;
                    padding: 20px 24px;
                    margin-bottom: 14px;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position:absolute; top:0; left:0; width:4px; height:100%;
                        background:{priority_colour};
                        border-radius:16px 0 0 16px;
                    "></div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="
                                background:rgba(124,58,237,0.1); border-radius:10px;
                                padding:6px 11px; font-size:0.82rem; font-weight:700; color:#a78bfa;
                            ">{row['#']}</span>
                            <strong style="font-size:0.98rem; color:#f0f2f6; font-weight:600;">
                                {row['Risk Name']}
                            </strong>
                        </div>
                        <span style="
                            background:{priority_colour};
                            color:{text_col};
                            padding: 4px 14px;
                            border-radius: 20px;
                            font-size: 0.72rem;
                            font-weight: 700;
                            letter-spacing: 0.04em;
                            text-transform: uppercase;
                        ">{row['Priority']}</span>
                    </div>
                    <div style="
                        display:flex; gap:16px; flex-wrap:wrap;
                        color:#8b92a5; font-size:0.8rem; margin-bottom:14px;
                        padding: 8px 14px;
                        background: rgba(0,0,0,0.15); border-radius:10px;
                    ">
                        <span>{row['Category']}</span>
                        <span>P: <b style='color:#c4b5fd'>{row['Probability']}</b></span>
                        <span>I: <b style='color:#c4b5fd'>{row['Impact']}</b></span>
                        <span>Score: <b style='color:#c4b5fd'>{row['Score (P×I)']}</b></span>
                    </div>
                    <div style="color:#94a3b8; font-size:0.86rem; margin-bottom:10px; line-height:1.6;">
                        <span style="color:#8b92a5; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">Evidence</span><br>
                        {row['Evidence']}
                    </div>
                    <div style="
                        color:#86efac; font-size:0.86rem; line-height:1.6;
                        padding:10px 14px; background:rgba(34,197,94,0.06);
                        border-radius:10px; border:1px solid rgba(34,197,94,0.1);
                    ">
                        <span style="font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#4ade80;">Mitigation</span><br>
                        {row['Recommendation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── CSV download ──────────────────────────────────────────────────────────
    csv_data = df.to_csv(index=False).encode("utf-8")
    dl_col1, dl_col2 = st.columns([3, 1])
    with dl_col2:
        st.download_button(
            label="⬇  Download CSV",
            data=csv_data,
            file_name="riskmind_risk_register.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl_col1:
        st.markdown(
            f"""
            <div style="
                display:flex; align-items:center; gap:12px;
                padding:12px 0; color:#6b7280; font-size:0.82rem;
            ">
                <span style="
                    background:rgba(34,197,94,0.1); color:#4ade80;
                    border-radius:20px; padding:4px 12px;
                    font-weight:600; font-size:0.75rem;
                ">✓ Complete</span>
                <span>Model: <b style="color:#a78bfa">{selected_model}</b></span>
                <span>•</span>
                <span><b style="color:#e2e0f0">{len(df)}</b> risks identified</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
