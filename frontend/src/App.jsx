import { useState } from 'react'
import LandingPage from './components/LandingPage.jsx'
import ChatWidget from './components/ChatWidget.jsx'
import AdminPanel from './components/AdminPanel.jsx'

export default function App() {
  const [chatOpen, setChatOpen] = useState(false)

  // Visit #admin to reach the "Manage chatbot knowledge" module (PRD: Admin user stories)
  if (typeof window !== 'undefined' && window.location.hash === '#admin') {
    return <AdminPanel />
  }

  return (
    <>
      <LandingPage onAskAssistant={() => setChatOpen(true)} />
      <ChatWidget open={chatOpen} onOpen={() => setChatOpen(true)} onClose={() => setChatOpen(false)} />
    </>
  )
}
