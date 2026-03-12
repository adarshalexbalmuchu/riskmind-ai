# 🧠 RiskMind AI – Project Risk Analysis Assistant

> An AI-powered project risk management tool built with **Python**, **Streamlit**, and the **Groq API**.  
> Designed as a clean, beginner-friendly prototype for university AI assignments.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Quick Start](#quick-start)
6. [Configuration](#configuration)
7. [Running the App](#running-the-app)
8. [Example Input](#example-input)
9. [How It Works](#how-it-works)
10. [Risk Categories](#risk-categories)
11. [Troubleshooting](#troubleshooting)

---

## Overview

RiskMind AI allows a user to paste any **project description**, **meeting notes**, or **scope document** and instantly receive a structured **PMBOK-style Risk Register** — powered by a large language model running on Groq's ultra-fast inference infrastructure.

The system:
- **Identifies** potential project risks hidden in free-form text
- **Classifies** each risk into one of 9 standard categories
- **Scores** risks using a Probability × Impact matrix (1–9 scale)
- **Recommends** concrete mitigation strategies for each risk
- **Exports** the full risk register as a downloadable CSV

---

## Features

| Feature | Description |
|---|---|
| 🤖 AI Risk Identification | LLaMA 3 model identifies risks from unstructured text |
| 🗂️ Risk Register Table | Sortable, colour-coded risk table with all PMBOK fields |
| 📊 Priority Score | Numeric P×I score (1–9) calculated for each risk |
| 📈 Visual Chart | Bar chart of all risk scores for quick overview |
| 🔎 Detailed Cards | Expandable cards with full risk details and evidence |
| 💾 CSV Export | Download the complete risk register as a CSV file |
| 🔁 Model Switching | Toggle between llama-3.1-8b-instant and llama-3.3-70b-versatile |

---

## Tech Stack

| Component | Technology |
|---|---|
| **UI Framework** | [Streamlit](https://streamlit.io/) |
| **LLM Inference** | [Groq API](https://groq.com/) |
| **Language Models** | Meta LLaMA 3.1 8B / LLaMA 3.3 70B |
| **Data Handling** | [Pandas](https://pandas.pydata.org/) |
| **Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| **Language** | Python 3.10+ |

---

## Project Structure

```
riskmind-ai/
│
├── app.py              ← Main Streamlit application (all logic here)
├── requirements.txt    ← Python dependencies
├── .env.example        ← Template for your API key (copy → .env)
└── README.md           ← This file
```

---

## Quick Start

### 1. Clone / Download the project

```bash
# If using git:
git clone https://github.com/your-username/riskmind-ai.git
cd riskmind-ai

# Or just download the zip and cd into the folder
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Activate on macOS / Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API Key

```bash
# Copy the example file
cp .env.example .env

# Open .env in any text editor and replace the placeholder:
# GROQ_API_KEY=your_groq_api_key_here
```

> 🔑 **Get a free API key** at [https://console.groq.com/keys](https://console.groq.com/keys) — no credit card required.

---

## Configuration

The only required configuration is your **Groq API key**.

Open the `.env` file and set:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

No other configuration is needed.

---

## Running the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Example Input

Paste the following into the text area to test the system:

```
Project Title: E-Commerce Platform Relaunch

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
```

> 💡 This example is also built into the app — click the **📄 Load Example** button!

---

## How It Works

```
User Input (project text)
        │
        ▼
┌─────────────────────┐
│   Streamlit UI      │  ← User pastes text, clicks "Analyse"
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Prompt Engineering │  ← System prompt: PMBOK analyst persona
│                     │  ← User prompt: wraps project description
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Groq API          │  ← LLaMA 3 model analyses the text
│   (LLM Inference)   │  ← Returns structured JSON
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   JSON Parser       │  ← Validates and cleans the response
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Pandas DataFrame   │  ← Adds P×I score, sorts by priority
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Streamlit Display  │  ← Renders metrics, table, chart, cards
│  + CSV Download     │
└─────────────────────┘
```

---

## Risk Categories

The system classifies risks into these 9 standard PMBOK categories:

| Icon | Category | Examples |
|---|---|---|
| 🗓️ | **Schedule Risk** | Tight deadlines, missing milestones |
| 💰 | **Cost Risk** | Budget overruns, funding cuts |
| 📐 | **Scope Creep Risk** | Undefined requirements, feature additions |
| 👥 | **Resource Risk** | Staff shortages, contractor departures |
| 🤝 | **Vendor / Procurement Risk** | Third-party delays, missing deliverables |
| ⚙️ | **Technical Risk** | Tech stack issues, integration failures |
| 💬 | **Communication Risk** | Informal channels, lack of PM tools |
| 🏢 | **Stakeholder Risk** | Unclear expectations, disengaged sponsors |
| ✅ | **Quality Risk** | No testing plan, lack of QA processes |

---

## Priority Score Matrix

| | Low Impact (1) | Medium Impact (2) | High Impact (3) |
|---|---|---|---|
| **Low Probability (1)** | 1 🟢 Low | 2 🟢 Low | 3 🟡 Medium |
| **Medium Probability (2)** | 2 🟢 Low | 4 🟡 Medium | 6 🟠 High |
| **High Probability (3)** | 3 🟡 Medium | 6 🟠 High | 9 🔴 Critical |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `GROQ_API_KEY not found` | Make sure `.env` exists with a valid key |
| `JSON parsing error` | Try the 70B model (more reliable structured output) |
| App won't start | Run `pip install -r requirements.txt` again |
| Blank output | Ensure your project description has enough detail (>3 sentences) |

---

## Assignment Notes

This project demonstrates:
- **Prompt Engineering** — structured system prompts with PMBOK domain framing
- **LLM Integration** — Groq API with model selection and temperature control
- **JSON Handling** — safe parsing with fallback cleaning
- **Data Processing** — Pandas for transformation and scoring
- **UI Design** — multi-section Streamlit app with visualisations
- **Software Engineering** — modular, documented, beginner-readable code

---

*Built with ❤️ using Python, Streamlit, and Groq*
