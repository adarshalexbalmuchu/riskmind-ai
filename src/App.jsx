import { useState, useRef } from 'react'
import UploadZone        from './components/UploadZone.jsx'
import TextPreview       from './components/TextPreview.jsx'
import AnalysisStepper   from './components/AnalysisStepper.jsx'
import ResultsDashboard  from './components/ResultsDashboard.jsx'
import {
  generateScopeOfWork,
  generateWBS,
  generateRiskAnalysis,
  generateGanttData,
  generatePERTData,
} from './utils/claudeApi.js'

const EXAMPLE = `Project Title: E-Commerce Platform Relaunch

Our company plans to relaunch our e-commerce website within the next 4 months to
coincide with the holiday shopping season. The project involves migrating from our
legacy PHP system to a new React/Node.js stack, integrating three third-party payment
gateways (Stripe, PayPal, and a new regional provider), and redesigning the entire
UI/UX based on customer research.

The budget is $280,000. The team consists of 6 developers (2 contractors ending
in 6 weeks), 1 UX designer, and a part-time project manager handling two other
projects simultaneously.

The vendor providing the inventory module has not yet delivered API documentation.
Initial testing revealed compatibility issues between the payment gateway and
existing database schema. The team has no prior experience with the new stack
and training has not been scheduled.`

const EMPTY_STATUSES = { sow: 'idle', wbs: 'idle', risk: 'idle', gantt: 'idle', pert: 'idle' }

export default function App() {
  const [text, setText]             = useState('')
  const [fileName, setFileName]     = useState('')
  const [analysisData, setAnalysis] = useState(null)
  const [statuses, setStatuses]     = useState(EMPTY_STATUSES)
  const [analyzing, setAnalyzing]   = useState(false)
  const [errors, setErrors]         = useState({})
  const abortRef                    = useRef(null)

  function setStatus(key, val) {
    setStatuses(s => ({ ...s, [key]: val }))
  }

  function setError(key, msg) {
    setErrors(e => ({ ...e, [key]: msg }))
    setStatus(key, 'error')
  }

  async function runStep(key, fn, signal) {
    setStatus(key, 'running')
    try {
      const result = await fn(text, signal)
      setStatus(key, 'done')
      setAnalysis(prev => ({ ...prev, [key]: result }))
      return result
    } catch (e) {
      if (e.name === 'AbortError') throw e
      setError(key, e.message)
      return null
    }
  }

  async function handleAnalyze() {
    if (!text.trim()) return
    abortRef.current = new AbortController()
    const { signal } = abortRef.current

    setAnalyzing(true)
    setErrors({})
    setAnalysis(null)
    setStatuses(EMPTY_STATUSES)

    try {
      await runStep('sow',   generateScopeOfWork,  signal)
      await runStep('wbs',   generateWBS,           signal)
      await runStep('risk',  generateRiskAnalysis,  signal)
      await runStep('gantt', generateGanttData,     signal)
      await runStep('pert',  generatePERTData,      signal)
    } catch (e) {
      if (e.name !== 'AbortError') console.error(e)
    } finally {
      setAnalyzing(false)
    }
  }

  async function retryStep(key) {
    const fns = { sow: generateScopeOfWork, wbs: generateWBS,
      risk: generateRiskAnalysis, gantt: generateGanttData, pert: generatePERTData }
    abortRef.current = new AbortController()
    setErrors(e => { const n = { ...e }; delete n[key]; return n })
    await runStep(key, fns[key], abortRef.current.signal)
  }

  function handleStop() {
    abortRef.current?.abort()
    setAnalyzing(false)
  }

  const showResults  = analysisData !== null
  const showStepper  = analyzing
  const hasAnyError  = Object.keys(errors).length > 0

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        background: 'rgba(255,247,235,0.75)', backdropFilter: 'blur(8px)',
        borderBottom: '1px solid rgba(240,220,195,0.65)',
        padding: '0 24px', height: 56,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        position: 'sticky', top: 0, zIndex: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 22 }}>🛡️</span>
          <span style={{ fontFamily: 'Sora, sans-serif', fontWeight: 800, fontSize: '1.05rem',
            letterSpacing: '-0.02em' }}>RiskMind AI</span>
          <span style={{ fontSize: '0.72rem', color: 'var(--rm-muted)',
            background: 'rgba(10,124,141,0.10)', borderRadius: 999,
            padding: '2px 9px', marginLeft: 4 }}>Project Analyzer</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['PMBOK aligned', 'Claude AI', '5 Deliverables'].map(chip => (
            <span key={chip} style={{
              fontSize: '0.72rem', color: 'var(--rm-muted)',
              border: '1px solid var(--rm-border)', borderRadius: 999,
              padding: '3px 10px', background: 'rgba(255,255,255,0.72)',
            }}>{chip}</span>
          ))}
        </div>
      </header>

      <main style={{ flex: 1, maxWidth: 1100, margin: '0 auto', width: '100%', padding: '28px 24px 80px' }}>

        {/* Hero */}
        <div style={{
          position: 'relative', border: '1px solid var(--rm-border)', borderRadius: 22,
          background: 'linear-gradient(130deg, rgba(255,255,255,0.86), rgba(255,244,226,0.95))',
          boxShadow: '0 18px 50px rgba(111,82,37,0.09)',
          padding: '30px 34px', marginBottom: 24, overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', right: -95, top: -95, width: 240, height: 240,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(10,124,141,0.24) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />
          <h1 style={{ fontFamily: 'Sora, sans-serif', fontWeight: 800,
            fontSize: 'clamp(1.6rem, 3vw, 2.2rem)', margin: 0 }}>
            AI-Powered Project Analyzer
          </h1>
          <p style={{ margin: '8px 0 0', color: 'var(--rm-muted)', fontSize: '0.94rem' }}>
            Upload a project document and generate 5 PM deliverables in minutes.
          </p>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 14 }}>
            {['Scope of Work','Work Breakdown','Risk Register','Gantt Chart','PERT Analysis'].map(t => (
              <span key={t} style={{
                border: '1px solid var(--rm-border)', background: 'rgba(255,255,255,0.72)',
                borderRadius: 999, padding: '4px 12px', fontSize: '0.76rem', color: 'var(--rm-muted)',
              }}>{t}</span>
            ))}
          </div>
        </div>

        {/* Upload + input area */}
        {!showResults && !analyzing && (
          <div className="rm-fade-in" style={{
            border: '1px solid var(--rm-border)', borderRadius: 16,
            background: 'rgba(255,253,247,0.95)', padding: 28, marginBottom: 20,
          }}>
            <h2 style={{ fontFamily: 'Sora, sans-serif', fontWeight: 700, fontSize: '1rem',
              margin: '0 0 16px' }}>Project Input</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {/* Upload */}
              <div>
                <p style={{ margin: '0 0 8px', fontSize: '0.83rem', color: 'var(--rm-muted)' }}>
                  Upload a file (PDF, DOCX, TXT)
                </p>
                <UploadZone onExtracted={(t, n) => { setText(t); setFileName(n) }} />
              </div>
              {/* Paste */}
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <p style={{ margin: 0, fontSize: '0.83rem', color: 'var(--rm-muted)' }}>
                    Or paste project text
                  </p>
                  <button
                    onClick={() => { setText(EXAMPLE); setFileName('') }}
                    style={{
                      background: 'none', border: '1px solid var(--rm-border)',
                      borderRadius: 8, padding: '2px 10px', fontSize: '0.76rem',
                      cursor: 'pointer', color: 'var(--rm-muted)',
                    }}>
                    Load example
                  </button>
                </div>
                <textarea
                  value={text}
                  onChange={e => { setText(e.target.value); setFileName('') }}
                  placeholder="Paste your project description, scope document, or meeting notes here…"
                  style={{
                    flex: 1, minHeight: 160, padding: 12, fontSize: '0.85rem',
                    borderRadius: 14, border: '1px solid var(--rm-border)',
                    background: 'rgba(255,255,255,0.86)', resize: 'vertical',
                    fontFamily: 'IBM Plex Sans, sans-serif', color: 'var(--rm-text)',
                    outline: 'none',
                  }}
                />
                {text && (
                  <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: 'var(--rm-muted)' }}>
                    {text.trim().split(/\s+/).length.toLocaleString()} words · {text.length.toLocaleString()} chars
                  </p>
                )}
              </div>
            </div>

            {text && <TextPreview text={text} fileName={fileName} />}

            <div style={{ marginTop: 20, display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={handleAnalyze}
                disabled={!text.trim()}
                style={{
                  padding: '12px 32px', borderRadius: 12, border: 'none',
                  background: text.trim()
                    ? 'linear-gradient(135deg, var(--rm-brand), #f2742a)'
                    : 'var(--rm-border)',
                  color: text.trim() ? '#fff' : 'var(--rm-muted)',
                  fontFamily: 'Sora, sans-serif', fontWeight: 700, fontSize: '0.95rem',
                  cursor: text.trim() ? 'pointer' : 'not-allowed',
                  boxShadow: text.trim() ? '0 4px 18px rgba(234,91,47,0.3)' : 'none',
                  transition: 'all 0.2s',
                }}
              >
                🔍 Analyze Project
              </button>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!text && !showResults && !analyzing && (
          <div className="rm-fade-in" style={{ textAlign: 'center', padding: '48px 24px', color: 'var(--rm-muted)' }}>
            <div style={{ fontSize: 52, marginBottom: 12 }}>📁</div>
            <p style={{ fontFamily: 'Sora, sans-serif', fontWeight: 600, fontSize: '1.05rem', color: 'var(--rm-text)' }}>
              Upload a project document to get started
            </p>
            <p style={{ fontSize: '0.88rem' }}>
              Supports PDF, DOCX, and TXT files — or paste your text directly.
            </p>
          </div>
        )}

        {/* Stepper */}
        {analyzing && (
          <div className="rm-fade-in">
            <AnalysisStepper statuses={statuses} />
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <button onClick={handleStop} style={{
                padding: '8px 20px', borderRadius: 10,
                border: '1px solid var(--rm-border)', background: 'rgba(255,254,249,0.9)',
                color: 'var(--rm-muted)', cursor: 'pointer', fontSize: '0.85rem',
              }}>
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Error retry buttons */}
        {hasAnyError && !analyzing && (
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
            {Object.entries(errors).map(([key, msg]) => (
              <div key={key} style={{
                border: '1px solid rgba(163,32,32,0.3)', borderRadius: 12,
                background: 'rgba(163,32,32,0.06)', padding: '10px 16px',
                display: 'flex', alignItems: 'center', gap: 12,
              }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--rm-critical)' }}>
                  ✕ {key.toUpperCase()}: {msg}
                </span>
                <button onClick={() => retryStep(key)} style={{
                  padding: '4px 12px', borderRadius: 8, border: '1px solid rgba(163,32,32,0.4)',
                  background: 'none', color: 'var(--rm-critical)', cursor: 'pointer',
                  fontSize: '0.78rem', fontWeight: 600,
                }}>
                  Retry
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Results + reset */}
        {showResults && (
          <div className="rm-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h2 style={{ fontFamily: 'Sora, sans-serif', fontWeight: 700, fontSize: '1.05rem', margin: 0 }}>
                Analysis Results
              </h2>
              <button
                onClick={() => { setAnalysis(null); setStatuses(EMPTY_STATUSES); setErrors({}) }}
                style={{
                  padding: '6px 16px', borderRadius: 10, border: '1px solid var(--rm-border)',
                  background: 'rgba(255,254,249,0.9)', color: 'var(--rm-muted)',
                  cursor: 'pointer', fontSize: '0.82rem',
                }}
              >
                ← New Analysis
              </button>
            </div>
            <ResultsDashboard analysisData={analysisData} statuses={statuses} />
          </div>
        )}
      </main>
    </div>
  )
}
