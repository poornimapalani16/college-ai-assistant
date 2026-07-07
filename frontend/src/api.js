const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function sendChatMessage({ message, sessionId, role }) {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, role }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function getCollegeInfo() {
  const res = await fetch(`${API_BASE_URL}/api/college-info`)
  if (!res.ok) throw new Error('Failed to load college info')
  return res.json()
}

// --- Admin (module 3: manage chatbot knowledge) ---

export async function uploadDocument(file, adminKey) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE_URL}/api/admin/documents`, {
    method: 'POST',
    headers: { 'X-Admin-Key': adminKey },
    body: form,
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed')
  return res.json()
}

export async function listDocuments(adminKey) {
  const res = await fetch(`${API_BASE_URL}/api/admin/documents`, {
    headers: { 'X-Admin-Key': adminKey },
  })
  if (!res.ok) throw new Error('Failed to list documents')
  return res.json()
}

export async function deleteDocument(docId, adminKey) {
  const res = await fetch(`${API_BASE_URL}/api/admin/documents/${docId}`, {
    method: 'DELETE',
    headers: { 'X-Admin-Key': adminKey },
  })
  if (!res.ok) throw new Error('Delete failed')
  return res.json()
}

export async function reindexAll(adminKey) {
  const res = await fetch(`${API_BASE_URL}/api/admin/reindex`, {
    method: 'POST',
    headers: { 'X-Admin-Key': adminKey },
  })
  if (!res.ok) throw new Error('Re-index failed')
  return res.json()
}
