/**
 * Anthropic Claude API calls for the 5 PM analysis deliverables.
 *
 * WARNING: For production, move these calls to a backend proxy.
 * Never expose API keys in a public-facing frontend.
 */

const API_URL = 'https://api.anthropic.com/v1/messages'
const MODEL = 'claude-3-5-sonnet-20241022'

const SYSTEM_PROMPT = `You are an expert project manager and business analyst.
Analyze the provided project document and respond ONLY with valid JSON.
Do not include markdown, code fences, or explanations — only raw JSON.`

async function callClaude(userPrompt, signal) {
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('VITE_ANTHROPIC_API_KEY is not set in .env')

  const res = await fetch(API_URL, {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 4096,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    let detail = err
    try { detail = JSON.parse(err)?.error?.message ?? err } catch {}
    throw new Error(`Claude API ${res.status}: ${detail}`)
  }

  const data = await res.json()
  const raw = data.content?.[0]?.text ?? ''
  // Strip accidental markdown fences
  const cleaned = raw.replace(/^```(?:json)?/m, '').replace(/```$/m, '').trim()
  try {
    return JSON.parse(cleaned)
  } catch {
    throw new Error(`Failed to parse Claude response as JSON:\n${raw.slice(0, 300)}`)
  }
}

export async function generateScopeOfWork(text, signal) {
  const prompt = `Given this project document, generate a Scope of Work (SoW) in this exact JSON format:
{
  "project_name": "string",
  "overview": "string (2-3 sentences)",
  "objectives": ["string"],
  "deliverables": ["string"],
  "exclusions": ["string"],
  "assumptions": ["string"],
  "constraints": ["string"]
}
Document: ${text}`
  return callClaude(prompt, signal)
}

export async function generateWBS(text, signal) {
  const prompt = `Given this project document, generate a hierarchical WBS in this exact JSON format:
{
  "project_name": "string",
  "wbs": [
    {
      "id": "1",
      "name": "Phase/Deliverable Name",
      "level": 1,
      "children": [
        {
          "id": "1.1",
          "name": "Task Name",
          "level": 2,
          "duration_days": 5,
          "children": []
        }
      ]
    }
  ]
}
Include at least 3 top-level phases with 3-5 sub-tasks each.
Document: ${text}`
  return callClaude(prompt, signal)
}

export async function generateRiskAnalysis(text, signal) {
  const prompt = `Given this project document, identify and analyze project risks in this exact JSON format:
{
  "risks": [
    {
      "id": "R1",
      "category": "Technical | Financial | Resource | Schedule | External",
      "title": "string",
      "description": "string",
      "probability": "Low | Medium | High",
      "impact": "Low | Medium | High",
      "risk_score": 6,
      "mitigation": "string",
      "contingency": "string",
      "owner": "string"
    }
  ]
}
Identify at least 6 risks across different categories.
Document: ${text}`
  return callClaude(prompt, signal)
}

export async function generateGanttData(text, signal) {
  const today = new Date().toISOString().split('T')[0]
  const prompt = `Given this project document, generate Gantt chart task data in this exact JSON format:
{
  "tasks": [
    {
      "id": "string",
      "name": "string",
      "phase": "string",
      "start_day": 0,
      "end_day": 5,
      "duration_days": 5,
      "dependencies": [],
      "assigned_to": "string"
    }
  ],
  "total_duration_days": 90,
  "start_date": "${today}"
}
Use ${today} as project start. Ensure logical sequencing with start_day/end_day as integers.
Document: ${text}`
  return callClaude(prompt, signal)
}

export async function generatePERTData(text, signal) {
  const prompt = `Given this project document, generate PERT network analysis in this exact JSON format:
{
  "nodes": [
    {
      "id": "string",
      "name": "string",
      "optimistic_days": 3,
      "most_likely_days": 5,
      "pessimistic_days": 10,
      "expected_time": 5.5,
      "variance": 1.36,
      "is_critical": true
    }
  ],
  "critical_path": ["node_id"],
  "critical_path_duration": 45,
  "edges": [
    { "from": "node_id", "to": "node_id" }
  ]
}
Document: ${text}`
  return callClaude(prompt, signal)
}
