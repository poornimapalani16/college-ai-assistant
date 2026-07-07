import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../api.js'
import './ChatWidget.css'

function getSessionId() {
  let id = sessionStorage.getItem('jgu_session_id')
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem('jgu_session_id', id)
  }
  return id
}

const ROLES = [
  { value: 'student', label: 'Student' },
  { value: 'parent', label: 'Parent' },
  { value: 'faculty', label: 'Faculty' },
]

const SUGGESTIONS = [
  'What is the fee for the BBA LLB programme?',
  'When does the Fall semester end?',
  'What documents do I need for admission?',
  'Tell me about hostel accommodation.',
]

export default function ChatWidget({ open, onOpen, onClose }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm the JGU AI Assistant. Ask me about admissions, fees, academics, hostel, or campus life — I answer from JGU's official documents." },
  ])
  const [input, setInput] = useState('')
  const [role, setRole] = useState('student')
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)
  const sessionId = useRef(getSessionId())

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages, open])

  async function handleSend(text) {
    const question = (text ?? input).trim()
    if (!question || loading) return

    setMessages((m) => [...m, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await sendChatMessage({ message: question, sessionId: sessionId.current, role })
      setMessages((m) => [...m, { role: 'assistant', content: res.answer, sources: res.sources }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: `Sorry, something went wrong: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <button className="chat-launcher" onClick={onOpen} aria-label="Open JGU AI Assistant">
        <span className="chat-launcher-dot" />
        Ask JGU Assistant
      </button>
    )
  }

  return (
    <div className="chat-panel" role="dialog" aria-label="JGU AI Assistant">
      <div className="chat-header">
        <div>
          <strong>JGU AI Assistant</strong>
          <span className="chat-header-sub">Answers grounded in official JGU documents</span>
        </div>
        <button className="chat-close" onClick={onClose} aria-label="Close chat">&times;</button>
      </div>

      <div className="chat-role-row">
        <span>I am a:</span>
        {ROLES.map((r) => (
          <button
            key={r.value}
            className={`chat-role-pill ${role === r.value ? 'active' : ''}`}
            onClick={() => setRole(r.value)}
          >
            {r.label}
          </button>
        ))}
      </div>

      <div className="chat-messages" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            <p>{m.content}</p>
            {m.sources && m.sources.length > 0 && (
              <div className="chat-sources">
                <span className="chat-sources-label">Sources</span>
                {m.sources.map((s, j) => (
                  <div key={j} className="chat-source-chip">
                    {s.document_name}{s.page != null ? `, p.${s.page + 1}` : ''}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant chat-typing">Thinking…</div>}
      </div>

      {messages.length <= 1 && (
        <div className="chat-suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => handleSend(s)}>{s}</button>
          ))}
        </div>
      )}

      <form
        className="chat-input-row"
        onSubmit={(e) => { e.preventDefault(); handleSend() }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about attendance, fees, syllabus, hostel..."
        />
        <button type="submit" disabled={loading || !input.trim()}>Send</button>
      </form>
    </div>
  )
}
