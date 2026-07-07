import { useState, useEffect } from 'react'
import { uploadDocument, listDocuments, deleteDocument, reindexAll } from '../api.js'
import './AdminPanel.css'

export default function AdminPanel() {
  const [adminKey, setAdminKey] = useState(localStorage.getItem('jgu_admin_key') || '')
  const [docs, setDocs] = useState([])
  const [status, setStatus] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => { localStorage.setItem('jgu_admin_key', adminKey) }, [adminKey])

  async function refresh() {
    try {
      setDocs(await listDocuments(adminKey))
    } catch (e) {
      setStatus(e.message)
    }
  }

  useEffect(() => { if (adminKey) refresh() }, [adminKey])

  async function handleUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    setBusy(true)
    setStatus(`Uploading ${file.name}...`)
    try {
      const res = await uploadDocument(file, adminKey)
      setStatus(`Indexed "${res.filename}" — ${res.chunks_indexed} chunks.`)
      await refresh()
    } catch (err) {
      setStatus(err.message)
    } finally {
      setBusy(false)
      e.target.value = ''
    }
  }

  async function handleDelete(docId) {
    setBusy(true)
    try {
      await deleteDocument(docId, adminKey)
      setStatus('Document deleted.')
      await refresh()
    } catch (err) {
      setStatus(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleReindex() {
    setBusy(true)
    setStatus('Re-indexing all documents...')
    try {
      const res = await reindexAll(adminKey)
      setStatus(`Re-indexed ${res.documents_processed} documents (${res.total_chunks} chunks).`)
      await refresh()
    } catch (err) {
      setStatus(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="admin-panel">
      <h1>Manage Chatbot Knowledge</h1>
      <p className="admin-sub">Upload, remove, or re-index the official documents the AI Assistant answers from.</p>

      <label className="admin-field">
        Admin key
        <input type="password" value={adminKey} onChange={(e) => setAdminKey(e.target.value)} placeholder="X-Admin-Key" />
      </label>

      <div className="admin-actions">
        <label className="admin-upload-btn">
          Upload document (PDF / DOCX / TXT)
          <input type="file" accept=".pdf,.docx,.doc,.txt" onChange={handleUpload} disabled={busy || !adminKey} hidden />
        </label>
        <button onClick={handleReindex} disabled={busy || !adminKey}>Re-index all documents</button>
      </div>

      {status && <p className="admin-status">{status}</p>}

      <table className="admin-table">
        <thead>
          <tr><th>Filename</th><th>Chunks</th><th>Uploaded</th><th></th></tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.doc_id}>
              <td>{d.filename}</td>
              <td>{d.chunk_count}</td>
              <td>{new Date(d.uploaded_at).toLocaleString()}</td>
              <td><button className="admin-delete" onClick={() => handleDelete(d.doc_id)} disabled={busy}>Delete</button></td>
            </tr>
          ))}
          {docs.length === 0 && <tr><td colSpan={4}>No documents indexed yet.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
