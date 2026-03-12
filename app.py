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

# ── Colour / style constants ───────────────────────────────────────────────────
PRIORITY_COLOURS = {
    "Critical": "#FF4B4B",
    "High":     "#FF8C00",
    "Medium":   "#FFC300",
    "Low":      "#28A745",
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
            background: linear-gradient(135deg, #1E1E2E, #2D2D44);
            border-left: 4px solid #7C3AED;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 20px;
            color: #E0E0E0;
            font-size: 0.95rem;
            line-height: 1.6;
        ">
            <strong style="color:#A78BFA; font-size:1rem;">📋 Project Summary</strong><br><br>
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
    avg_score = df["Score (P×I)"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔢 Total Risks",       total)
    c2.metric("🔴 Critical Risks",    critical)
    c3.metric("🟠 High Risks",        high)
    c4.metric("📊 Avg Priority Score", f"{avg_score:.1f} / 9")


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
        <div style="text-align:center; padding: 10px 0 4px 0;">
            <h1 style="font-size:2.4rem; margin-bottom:4px;">
                🧠 RiskMind AI
            </h1>
            <p style="color:#9CA3AF; font-size:1.05rem; margin:0;">
                Project Risk Analysis Assistant · Powered by Groq &amp; LLaMA
            </p>
        </div>
        <hr style="border-color:#374151; margin: 12px 0 24px 0;">
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
    st.subheader("📊 Risk Register")
    st.caption(
        f"Identified **{len(df)} risks**, sorted by priority score (highest first). "
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
    st.subheader("📈 Risk Priority Chart")
    st.caption("Horizontal bars show the P×I score for each identified risk.")
    render_risk_chart(df)

    st.divider()

    # ── Detailed risk cards ───────────────────────────────────────────────────
    with st.expander("🔎 Detailed Risk Cards", expanded=False):
        for _, row in df.iterrows():
            priority_colour = PRIORITY_COLOURS.get(row["Priority"], "#888")
            st.markdown(
                f"""
                <div style="
                    border-left: 4px solid {priority_colour};
                    background: #1E1E2E;
                    border-radius: 6px;
                    padding: 14px 18px;
                    margin-bottom: 12px;
                ">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="font-size:1rem; color:#E0E0E0;">
                            {row['#']}. {row['Risk Name']}
                        </strong>
                        <span style="
                            background:{priority_colour};
                            color:{'white' if row['Priority'] in ('Critical','High') else 'black'};
                            padding: 2px 10px;
                            border-radius: 12px;
                            font-size: 0.8rem;
                            font-weight: bold;
                        ">{row['Priority']}</span>
                    </div>
                    <div style="color:#9CA3AF; font-size:0.85rem; margin: 4px 0 10px 0;">
                        {row['Category']} &nbsp;|&nbsp; 
                        P: <strong>{row['Probability']}</strong> &nbsp;·&nbsp; 
                        I: <strong>{row['Impact']}</strong> &nbsp;·&nbsp;
                        Score: <strong>{row['Score (P×I)']}</strong>
                    </div>
                    <div style="color:#CBD5E1; font-size:0.88rem; margin-bottom:8px;">
                        <em>📎 Evidence:</em> {row['Evidence']}
                    </div>
                    <div style="color:#A7F3D0; font-size:0.88rem;">
                        <strong>✅ Mitigation:</strong> {row['Recommendation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── CSV download ──────────────────────────────────────────────────────────
    st.subheader("💾 Export Risk Register")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Risk Register as CSV",
        data=csv_data,
        file_name="riskmind_risk_register.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        f"✅ Analysis complete · Model used: `{selected_model}` · "
        f"{len(df)} risks identified"
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
