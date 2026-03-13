"""
RiskMind AI - Project Risk Analysis Assistant
=============================================
An AI-powered project risk management tool that analyzes project descriptions
and generates a structured PMBOK-style risk register.
"""

import json
import os
import re
from html import escape

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv()


BRAND_NAME = "RiskMind Prime"
BRAND_TAGLINE = "AI Risk Intelligence for Project Leaders"
BRAND_FAVICON = "🛡️"
BRAND_EXPORT_PREFIX = "riskmind_prime"


st.set_page_config(
    page_title=BRAND_NAME,
    page_icon=BRAND_FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --rm-bg-a: #f7f7ef;
    --rm-bg-b: #fff4e6;
    --rm-surface: #fffdf7;
    --rm-surface-2: #fff7eb;
    --rm-border: #f0dcc3;
    --rm-text: #1a1e23;
    --rm-muted: #4f4337;
    --rm-brand: #ea5b2f;
    --rm-brand-2: #0a7c8d;
    --rm-ok: #228b4e;
    --rm-warn: #dc8b00;
    --rm-high: #d84a1b;
    --rm-critical: #a32020;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: var(--rm-text);
}

.stApp {
    background:
        radial-gradient(1200px 520px at 88% -10%, rgba(234, 91, 47, 0.18), transparent 55%),
        radial-gradient(900px 420px at 4% -6%, rgba(10, 124, 141, 0.12), transparent 50%),
        linear-gradient(180deg, var(--rm-bg-a) 0%, var(--rm-bg-b) 100%);
}

#MainMenu, footer { visibility: hidden; }

header[data-testid="stHeader"] {
    background: rgba(255, 247, 235, 0.75) !important;
    backdrop-filter: blur(8px) !important;
    border-bottom: 1px solid rgba(240, 220, 195, 0.65) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fffdf6 0%, #fff6eb 100%) !important;
    border-right: 1px solid var(--rm-border) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: var(--rm-text) !important;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown * {
    color: var(--rm-text) !important;
    opacity: 1 !important;
}

section[data-testid="stSidebar"] table,
section[data-testid="stSidebar"] th,
section[data-testid="stSidebar"] td {
    color: var(--rm-text) !important;
    opacity: 1 !important;
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color: var(--rm-muted) !important;
}

h1, h2, h3, .stSubheader {
    font-family: 'Sora', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--rm-text) !important;
}

.rm-hero {
    position: relative;
    border: 1px solid var(--rm-border);
    border-radius: 22px;
    background: linear-gradient(130deg, rgba(255, 255, 255, 0.86), rgba(255, 244, 226, 0.95));
    box-shadow: 0 18px 50px rgba(111, 82, 37, 0.09);
    padding: 30px 34px;
    margin-top: 8px;
    margin-bottom: 18px;
    overflow: hidden;
    animation: rm-fade-in 500ms ease-out;
}

.rm-hero::after {
    content: "";
    position: absolute;
    right: -95px;
    top: -95px;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(10, 124, 141, 0.24) 0%, rgba(10, 124, 141, 0) 70%);
}

.rm-hero-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(1.7rem, 3vw, 2.4rem);
    font-weight: 800;
    margin: 0;
}

.rm-hero-subtitle {
    color: var(--rm-muted);
    margin-top: 8px;
    font-size: 0.96rem;
}

.rm-chip-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
}

.rm-chip {
    border: 1px solid var(--rm-border);
    background: rgba(255, 255, 255, 0.72);
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 0.77rem;
    color: var(--rm-muted);
}

div[data-testid="stMetric"] {
    background: linear-gradient(180deg, #fffef9, #fff7ea) !important;
    border: 1px solid var(--rm-border) !important;
    border-radius: 14px !important;
    padding: 16px 16px !important;
    box-shadow: 0 6px 20px rgba(98, 73, 30, 0.06);
}

div[data-testid="stMetric"] label {
    color: var(--rm-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600 !important;
    font-size: 0.71rem !important;
}

div[data-testid="stMetricValue"] {
    color: var(--rm-text) !important;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
}

textarea {
    border-radius: 14px !important;
    border: 1px solid var(--rm-border) !important;
    background: rgba(255, 255, 255, 0.86) !important;
    color: var(--rm-text) !important;
}

textarea::placeholder {
    color: #6a5f55 !important;
    opacity: 1 !important;
}

textarea:focus {
    border-color: rgba(10, 124, 141, 0.55) !important;
    box-shadow: 0 0 0 2px rgba(10, 124, 141, 0.12) !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, var(--rm-brand), #f2742a) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

button[kind="primary"] *,
button[kind="secondary"] * {
    color: inherit !important;
    opacity: 1 !important;
}

button[kind="secondary"] {
    background: #fffef9 !important;
    border-radius: 12px !important;
    border: 1px solid var(--rm-border) !important;
    color: var(--rm-text) !important;
}

.stButton > button:not([kind="primary"]) {
    background: #fffef9 !important;
    color: var(--rm-text) !important;
    border: 1px solid var(--rm-border) !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #fff8ed !important;
    border-color: #ddc3a2 !important;
    color: #161a1f !important;
}

button[data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    color: var(--rm-muted) !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--rm-brand) !important;
    font-weight: 700 !important;
    background: rgba(234, 91, 47, 0.1) !important;
}

section[data-testid="stFileUploader"] {
    border: 2px dashed rgba(10, 124, 141, 0.38) !important;
    border-radius: 14px !important;
    background: rgba(10, 124, 141, 0.04) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--rm-border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}

details {
    border: 1px solid var(--rm-border) !important;
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.75) !important;
}

details summary {
    color: var(--rm-text) !important;
    font-weight: 700 !important;
}

details [data-testid="stMarkdownContainer"],
details [data-testid="stMarkdownContainer"] p,
details [data-testid="stMarkdownContainer"] strong,
details [data-testid="stMarkdownContainer"] b {
    color: #1f2328 !important;
    opacity: 1 !important;
}

details [data-testid="stText"],
details [data-testid="stText"] *,
details [data-testid="stVerticalBlock"] p,
details [data-testid="stVerticalBlock"] span,
details [data-testid="stVerticalBlock"] li {
    color: #1f2328 !important;
    opacity: 1 !important;
}

details [data-testid="stCaptionContainer"],
details [data-testid="stCaptionContainer"] * {
    color: #3f3730 !important;
    opacity: 1 !important;
}

details [data-testid="stAlertContainer"] {
    background: #eef9f0 !important;
    border: 1px solid #b8e1bf !important;
}

details [data-testid="stAlertContainer"] p {
    color: #1f2328 !important;
}

@keyframes rm-fade-in {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 900px) {
    .rm-hero {
        padding: 22px;
    }

    .rm-chip-row {
        gap: 8px;
    }
}
</style>
"""


PRIORITY_COLOURS = {
    "Critical": "#A32020",
    "High": "#D84A1B",
    "Medium": "#DC8B00",
    "Low": "#228B4E",
}


CATEGORY_ICONS = {
    "Schedule Risk": "Calendar",
    "Cost Risk": "Budget",
    "Scope Creep Risk": "Scope",
    "Resource Risk": "People",
    "Vendor / Procurement Risk": "Vendor",
    "Technical Risk": "Technical",
    "Communication Risk": "Comms",
    "Stakeholder Risk": "Stakeholder",
    "Quality Risk": "Quality",
}


LEVEL_WEIGHTS = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
}


def normalize_level(value: str, *, allow_critical: bool = False) -> str:
    """Normalize model labels to supported values used by the UI."""
    cleaned = str(value or "").strip().lower()
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
    }
    normalized = mapping.get(cleaned, "Medium")
    if normalized == "Critical" and not allow_critical:
        return "High"
    return normalized


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


def init_state() -> None:
    """Initialize session state keys once."""
    if "project_input" not in st.session_state:
        st.session_state["project_input"] = ""
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None
    if "analysis_meta" not in st.session_state:
        st.session_state["analysis_meta"] = {}


def apply_styles() -> None:
    """Inject app-wide CSS tokens and components."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def get_groq_client() -> Groq:
    """Create a Groq client using GROQ_API_KEY from environment variables."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY was not found. Add it to .env before running analysis.")
        st.stop()
    return Groq(api_key=api_key)


def build_system_prompt() -> str:
    """Return strict JSON output instructions for the LLM risk analyst role."""
    return """You are a senior Project Risk Management Analyst with 15+ years of experience 
following PMBOK (Project Management Body of Knowledge) standards.

Your task is to analyze project descriptions, meeting notes, or scope documents and 
identify ALL potential project risks.

STRICT RULES:
1. Return ONLY valid JSON - no markdown fences, no extra text before or after.
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
    """Wrap user content for analysis with hard output constraints."""
    return f"""Analyze the following project description and produce the risk register JSON.

PROJECT DESCRIPTION:
\"\"\"
{project_text}
\"\"\"

Remember: Return ONLY the JSON object - nothing else."""


def parse_llm_response(raw_text: str) -> dict:
    """Parse model output as JSON and validate required structure."""
    cleaned = re.sub(r"```(?:json)?", "", raw_text, flags=re.IGNORECASE).strip()
    cleaned = cleaned.strip("`").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("The model response was not valid JSON.") from exc

    if "risks" not in data or not isinstance(data["risks"], list):
        raise ValueError("The model response JSON must contain a risks list.")

    return data


def call_groq_api(client: Groq, project_text: str, model: str) -> dict:
    """Call Groq chat completion and return validated JSON payload."""
    with st.spinner("Analyzing project risks. This may take a few seconds..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": build_user_prompt(project_text)},
            ],
            temperature=0.3,
            max_tokens=4096,
        )

    raw_text = (response.choices[0].message.content or "").strip()
    if not raw_text:
        raise ValueError("The model returned an empty response.")
    return parse_llm_response(raw_text)


def calculate_priority_score(probability: str, impact: str) -> int:
    """Compute score in range 1-9 using Probability x Impact."""
    return LEVEL_WEIGHTS.get(probability, 1) * LEVEL_WEIGHTS.get(impact, 1)


def risks_to_dataframe(risks: list[dict]) -> pd.DataFrame:
    """Normalize risk records and convert to a sorted DataFrame."""
    rows = []
    for index, risk in enumerate(risks, start=1):
        probability = normalize_level(risk.get("probability", "Medium"))
        impact = normalize_level(risk.get("impact", "Medium"))
        priority = normalize_level(risk.get("priority", "Medium"), allow_critical=True)
        category = (risk.get("category") or "Uncategorized").strip()

        rows.append(
            {
                "#": index,
                "Risk Name": risk.get("risk_name", "Unknown"),
                "Category": f"{CATEGORY_ICONS.get(category, 'General')} · {category}",
                "Evidence": risk.get("evidence", "-"),
                "Probability": probability,
                "Impact": impact,
                "Priority": priority,
                "Score (P*I)": calculate_priority_score(probability, impact),
                "Recommendation": risk.get("recommendation", "-"),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("Score (P*I)", ascending=False).reset_index(drop=True)
    df["#"] = df.index + 1
    return df


def colour_priority(value: str) -> str:
    """Return CSS style for priority level cell."""
    colour = PRIORITY_COLOURS.get(value, "#9aa0a6")
    text = "#ffffff" if value in ("Critical", "High") else "#111111"
    return f"background-color: {colour}; color: {text}; font-weight: 700;"


def style_dataframe(df: pd.DataFrame) -> "pd.io.formats.style.Styler":
    """Apply visual styling to risk register table."""
    return (
        df.style.applymap(colour_priority, subset=["Priority"])
        .format({"Score (P*I)": "{:.0f}"})
        .set_properties(
            subset=["Risk Name", "Category", "Evidence", "Recommendation"],
            **{"text-align": "left"},
        )
        .set_properties(
            subset=["Probability", "Impact", "Priority", "Score (P*I)"],
            **{"text-align": "center", "font-weight": "600"},
        )
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#fff3df"),
                        ("color", "#2b2b2b"),
                        ("font-weight", "700"),
                        ("text-align", "left"),
                    ],
                }
            ]
        )
        .hide(axis="index")
    )


def render_header() -> None:
    """Render the top hero region."""
    st.markdown(
        f"""
        <div class="rm-hero">
            <h1 class="rm-hero-title">{BRAND_FAVICON} {BRAND_NAME}</h1>
            <p class="rm-hero-subtitle">{BRAND_TAGLINE}</p>
            <div class="rm-chip-row">
                <span class="rm-chip">PMBOK aligned</span>
                <span class="rm-chip">Structured JSON output</span>
                <span class="rm-chip">Executive-ready exports</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_card(summary: str) -> None:
    """Display summary card with escaped content."""
    safe_summary = escape(summary).replace("\n", "<br>")
    st.markdown(
        f"""
        <div style="
            border: 1px solid #f0dcc3;
            background: linear-gradient(120deg, rgba(255,255,255,0.95), rgba(255,247,234,0.92));
            border-radius: 16px;
            padding: 20px 22px;
            margin: 10px 0 18px 0;
        ">
            <div style="font-family:'Sora',sans-serif; font-weight:700; margin-bottom:8px; color:#20262d;">
                Project Summary
            </div>
            <div style="color:#3f3730; line-height:1.7; font-size:0.92rem;">
                {safe_summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame) -> None:
    """Render KPI cards for quick risk distribution scan."""
    total = len(df)
    critical = len(df[df["Priority"] == "Critical"])
    high = len(df[df["Priority"] == "High"])
    medium = len(df[df["Priority"] == "Medium"])
    avg_score = df["Score (P*I)"].mean() if total else 0

    col_1, col_2, col_3, col_4, col_5 = st.columns(5)
    col_1.metric("Total Risks", total)
    col_2.metric("Critical", critical)
    col_3.metric("High", high)
    col_4.metric("Medium", medium)
    col_5.metric("Avg Score", f"{avg_score:.1f}")


def render_risk_chart(df: pd.DataFrame) -> None:
    """Render a visually rich priority chart with colors by risk level."""
    chart_df = df[["Risk Name", "Priority", "Score (P*I)"]].sort_values("Score (P*I)", ascending=False)
    priority_order = ["Low", "Medium", "High", "Critical"]
    color_scale = alt.Scale(
        domain=priority_order,
        range=["#228B4E", "#DC8B00", "#D84A1B", "#A32020"],
    )

    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            y=alt.Y("Risk Name:N", sort="-x", title=None),
            x=alt.X("Score (P*I):Q", title="Priority Score (P x I)", scale=alt.Scale(domain=[0, 9.5])),
            color=alt.Color("Priority:N", scale=color_scale, legend=alt.Legend(orient="top", title="Priority")),
            tooltip=[
                alt.Tooltip("Risk Name:N"),
                alt.Tooltip("Priority:N"),
                alt.Tooltip("Score (P*I):Q"),
            ],
        )
        .properties(height=min(420, 45 * max(4, len(chart_df))))
    )

    st.altair_chart(chart, use_container_width=True)


def render_sidebar() -> str:
    """Render sidebar controls and return selected model value."""
    with st.sidebar:
        st.markdown(f"### {BRAND_FAVICON} {BRAND_NAME}")
        st.caption(BRAND_TAGLINE)
        st.divider()
        st.title("Settings")
        model = st.selectbox(
            "Model",
            options=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
            index=0,
            help=(
                "llama-3.1-8b-instant: faster analysis.\n\n"
                "llama-3.3-70b-versatile: slower but more nuanced output."
            ),
        )

        st.markdown("### Workflow")
        st.markdown(
            """
1. Add project text or upload files.
2. Run Analyze Project Risks.
3. Review risks, chart, and details.
4. Export risk register as CSV.
            """
        )

        st.markdown("### Score Matrix")
        st.markdown(
            """
| Score | Label |
|---|---|
| 9 | Critical |
| 6 | High |
| 3-4 | Medium |
| 1-2 | Low |
            """
        )

        st.divider()
        st.caption(f"{BRAND_NAME} | Version 2.0")

    return model


def render_input_area() -> str:
    """Render text and upload inputs, then return combined analysis text."""
    st.subheader("Project Input")
    tab_paste, tab_upload = st.tabs(["Paste Text", "Upload Files"])

    with tab_paste:
        col_left, col_right = st.columns([5, 1])
        with col_right:
            if st.button("Load Example", use_container_width=True):
                st.session_state["project_input"] = EXAMPLE_PROJECT

        with col_left:
            st.caption("Paste project scope, notes, or planning documents.")

        pasted_text = st.text_area(
            label="Project Description",
            key="project_input",
            height=250,
            placeholder="Paste your project description or notes here...",
            label_visibility="collapsed",
        )

        word_count = len((pasted_text or "").split())
        char_count = len(pasted_text or "")
        st.caption(f"Input length: {word_count} words, {char_count} characters")

    uploaded_text = ""
    with tab_upload:
        st.caption("Upload .txt, .md, .csv, .json, or .log files. Contents are merged for analysis.")
        uploaded_files = st.file_uploader(
            "Upload project files",
            type=["txt", "md", "csv", "json", "log"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files:
            chunks = []
            for file_obj in uploaded_files:
                try:
                    content = file_obj.read().decode("utf-8", errors="replace")
                    chunks.append(f"--- {file_obj.name} ---\n{content}")
                except Exception:
                    st.warning(f"Could not read {file_obj.name}. Skipped.")

            uploaded_text = "\n\n".join(chunks).strip()
            if uploaded_text:
                with st.expander("Preview Uploaded Content", expanded=False):
                    preview = uploaded_text[:3000]
                    suffix = "..." if len(uploaded_text) > 3000 else ""
                    st.text(preview + suffix)

    return uploaded_text if uploaded_text else (pasted_text or "").strip()


def run_analysis(project_text: str, model: str) -> None:
    """Execute AI analysis and persist normalized results in session state."""
    client = get_groq_client()
    payload = call_groq_api(client, project_text, model)
    risks = payload.get("risks", [])

    if not risks:
        st.warning("The model returned no risks. Try a more detailed project description.")
        return

    df = risks_to_dataframe(risks)
    st.session_state["analysis_result"] = {
        "summary": payload.get("project_summary", "No summary provided."),
        "df": df,
    }
    st.session_state["analysis_meta"] = {
        "model": model,
        "source_text": project_text,
    }


def render_risk_cards(df: pd.DataFrame) -> None:
    """Render detailed risks with robust native Streamlit components."""
    priority_icon = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
    }

    with st.expander("Detailed Risk Breakdown", expanded=False):
        for _, row in df.iterrows():
            priority = str(row["Priority"])
            with st.container(border=True):
                title_col, tag_col = st.columns([5, 2])
                with title_col:
                    st.markdown(f"**#{int(row['#'])} {str(row['Risk Name'])}**")
                with tag_col:
                    st.markdown(f"**{priority_icon.get(priority, '🟡')} {priority}**")

                st.caption(
                    f"{str(row['Category'])} | "
                    f"P: {str(row['Probability'])} | "
                    f"I: {str(row['Impact'])} | "
                    f"Score: {str(row['Score (P*I)'])}"
                )

                st.markdown("**Evidence**")
                st.write(str(row["Evidence"]))

                st.markdown("**Mitigation**")
                recommendation = str(row["Recommendation"])
                if priority == "Critical":
                    st.error(recommendation)
                elif priority == "High":
                    st.warning(recommendation)
                elif priority == "Medium":
                    st.info(recommendation)
                else:
                    st.success(recommendation)


def render_results(selected_model: str, project_text: str) -> None:
    """Render full analysis output if a stored result exists."""
    result = st.session_state.get("analysis_result")
    meta = st.session_state.get("analysis_meta", {})
    if not result:
        return

    stale_result = meta.get("source_text") and meta.get("source_text") != project_text
    if stale_result:
        st.warning("The displayed results are from a previous input. Run analysis again to refresh.")

    summary = result["summary"]
    df = result["df"]

    render_summary_card(summary)
    render_metrics(df)

    st.divider()
    st.subheader("Risk Register")
    st.caption(f"{len(df)} risks identified. Sorted by score using Probability x Impact.")
    st.dataframe(style_dataframe(df), use_container_width=True, height=min(100 + len(df) * 58, 640))

    st.divider()
    st.subheader("Risk Priority Chart")
    st.caption("Score distribution across identified risks.")
    render_risk_chart(df)

    st.divider()
    render_risk_cards(df)

    csv_data = df.to_csv(index=False).encode("utf-8")
    c1, c2 = st.columns([3, 1])
    with c2:
        st.download_button(
            label="Download Risk Register CSV",
            data=csv_data,
            file_name=f"{BRAND_EXPORT_PREFIX}_risk_register.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c1:
        st.caption(
            f"Analysis model: {meta.get('model', selected_model)} | Risk count: {len(df)}"
        )


def main() -> None:
    """Render complete Streamlit UI and orchestrate analysis flow."""
    init_state()
    apply_styles()

    selected_model = render_sidebar()
    render_header()

    project_text = render_input_area()

    analyze_clicked = st.button(
        "Analyze Project Risks",
        type="primary",
        use_container_width=True,
        disabled=not bool(project_text.strip()),
    )

    if not project_text.strip():
        st.info("Add project content in Paste Text or Upload Files, then run analysis.")

    if analyze_clicked:
        try:
            run_analysis(project_text.strip(), selected_model)
            st.success("Risk analysis complete.")
        except ValueError as exc:
            st.error(f"Parsing error: {exc}")
        except Exception as exc:
            st.error(f"API error: {exc}")

    render_results(selected_model, project_text.strip())


if __name__ == "__main__":
    main()
