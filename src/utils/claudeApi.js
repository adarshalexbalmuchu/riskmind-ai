/**
 * Anthropic Claude API calls for the 5 PM analysis deliverables.
 *
 * WARNING: For production, move these calls to a backend proxy.
 * Never expose API keys in a public-facing frontend.
 */

const API_URL = 'https://api.anthropic.com/v1/messages'
const MODEL   = 'claude-3-5-sonnet-20241022'

// Truncate document to avoid exceeding token limits
const MAX_TEXT_CHARS = 12000

const SYSTEM_PROMPT = `You are an expert project manager and business analyst.
Analyze the provided project document and respond ONLY with valid JSON.
Do not include markdown, code fences, or explanations — only raw JSON.`

async function callClaude(userPrompt, signal) {
  const apiKey = (import.meta.env.VITE_ANTHROPIC_API_KEY || '').trim()

  if (!apiKey) {
    throw new Error('API key not found. Set VITE_ANTHROPIC_API_KEY in your environment.')
  }

  const body = {
    model: MODEL,
    max_tokens: 2048,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: userPrompt }],
  }

  console.log('[Claude] Sending request, model:', MODEL, 'prompt length:', userPrompt.length)

  const res = await fetch(API_URL, {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    const errText = await res.text()
    console.error('[Claude] API error', res.status, errText)
    let detail = errText
    try {
      const parsed = JSON.parse(errText)
      detail = parsed?.error?.message ?? parsed?.message ?? errText
    } catch {}
    throw new Error(`[${res.status}] ${detail}`)
  }

  const data = await res.json()
  const raw  = data.content?.[0]?.text ?? ''
  const cleaned = raw
    .replace(/^```(?:json)?\s*/m, '')
    .replace(/\s*```$/m, '')
    .trim()

  try {
    return JSON.parse(cleaned)
  } catch {
    console.error('[Claude] JSON parse failed. Raw response:', raw.slice(0, 500))
    throw new Error(`Response was not valid JSON: ${raw.slice(0, 200)}`)
  }
}

function truncate(text) {
  return text.length > MAX_TEXT_CHARS
    ? text.slice(0, MAX_TEXT_CHARS) + '\n[...truncated for length]'
    : text
}

export async function generateScopeOfWork(text, signal) {
  const doc = truncate(text)
  const prompt = `Generate a Scope of Work (SoW) for this project in this exact JSON format:
{
  "project_name": "string",
  "overview": "string",
  "objectives": ["string"],
  "deliverables": ["string"],
  "exclusions": ["string"],
  "assumptions": ["string"],
  "constraints": ["string"]
}
PROJECT DOCUMENT:
${doc}`
  return callClaude(prompt, signal)
}

export async function generateWBS(text, signal) {
  const doc = truncate(text)
  const prompt = `Generate a hierarchical Work Breakdown Structure (WBS) for this project in this exact JSON format:
{
  "project_name": "string",
  "wbs": [
    {
      "id": "1",
      "name": "Phase Name",
      "level": 1,
      "children": [
        { "id": "1.1", "name": "Task Name", "level": 2, "duration_days": 5, "children": [] }
      ]
    }
  ]
}
Include at least 3 top-level phases with 3-5 sub-tasks each.
PROJECT DOCUMENT:
${doc}`
  return callClaude(prompt, signal)
}

export async function generateRiskAnalysis(text, signal) {
  const doc = truncate(text)
  const prompt = `Identify and analyze project risks for this project in this exact JSON format:
{
  "risks": [
    {
      "id": "R1",
      "category": "Technical",
      "title": "string",
      "description": "string",
      "probability": "High",
      "impact": "High",
      "risk_score": 9,
      "mitigation": "string",
      "contingency": "string",
      "owner": "string"
    }
  ]
}
Categories must be one of: Technical, Financial, Resource, Schedule, External.
Probability and Impact must be: Low, Medium, or High.
Identify at least 6 risks.
PROJECT DOCUMENT:
${doc}`
  return callClaude(prompt, signal)
}

export async function generateGanttData(text, signal) {
  const doc = truncate(text)
  const today = new Date().toISOString().split('T')[0]
  const prompt = `Generate Gantt chart task data for this project in this exact JSON format:
{
  "tasks": [
    {
      "id": "T1",
      "name": "string",
      "phase": "string",
      "start_day": 0,
      "end_day": 10,
      "duration_days": 10,
      "dependencies": [],
      "assigned_to": "string"
    }
  ],
  "total_duration_days": 90,
  "start_date": "${today}"
}
Use ${today} as the project start date. All day values must be integers.
PROJECT DOCUMENT:
${doc}`
  return callClaude(prompt, signal)
}

export async function generatePERTData(text, signal) {
  const doc = truncate(text)
  const prompt = `Generate PERT network analysis for this project in this exact JSON format:
{
  "nodes": [
    {
      "id": "N1",
      "name": "string",
      "optimistic_days": 3,
      "most_likely_days": 5,
      "pessimistic_days": 10,
      "expected_time": 5.5,
      "variance": 1.36,
      "is_critical": true
    }
  ],
  "critical_path": ["N1"],
  "critical_path_duration": 45,
  "edges": [
    { "from": "N1", "to": "N2" }
  ]
}
PROJECT DOCUMENT:
${doc}`
  return callClaude(prompt, signal)
}
