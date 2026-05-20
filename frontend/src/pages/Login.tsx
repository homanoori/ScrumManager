import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { dispatch } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await api.post('/auth/login', { username, password })
      dispatch({ type: 'LOGIN', token: response.data.access_token, role: response.data.role, username })
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid username or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0d0f14', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ background: '#131720', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: '16px', padding: '40px', width: '100%', maxWidth: '380px' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
            <svg width="20" height="20" viewBox="0 0 12 12" fill="white">
              <path d="M2 2h3v3H2zM7 2h3v3H7zM2 7h3v3H2zM7 7h3v3H7z"/>
            </svg>
          </div>
          <div style={{ color: '#f1f5f9', fontSize: '18px', fontWeight: 500 }}>ScrumManager</div>
          <div style={{ color: '#4b5563', fontSize: '13px', marginTop: '4px' }}>Sign in to continue</div>
        </div>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.1)', border: '0.5px solid rgba(239,68,68,0.3)', color: '#fca5a5', padding: '10px 14px', borderRadius: '8px', fontSize: '12px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Username</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              style={{ width: '100%', background: '#0d0f14', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '9px 12px', fontSize: '13px', color: '#f1f5f9', outline: 'none', boxSizing: 'border-box' }}
              onFocus={e => e.target.style.borderColor = '#6366f1'}
              onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#64748b', marginBottom: '6px' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              style={{ width: '100%', background: '#0d0f14', border: '0.5px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '9px 12px', fontSize: '13px', color: '#f1f5f9', outline: 'none', boxSizing: 'border-box' }}
              onFocus={e => e.target.style.borderColor = '#6366f1'}
              onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.08)'}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{ background: loading ? '#4f46e5' : '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', padding: '10px', fontSize: '13px', fontWeight: 500, cursor: loading ? 'not-allowed' : 'pointer', marginTop: '4px', opacity: loading ? 0.7 : 1, transition: 'all 0.15s' }}
          >
            {loading ? 'Signing in...' : 'Sign in →'}
          </button>
        </form>

        <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '0.5px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: '11px', color: '#374151', marginBottom: '6px' }}>Demo credentials</div>
          <div style={{ fontSize: '11px', color: '#4b5563', lineHeight: '1.8' }}>
            alice / password123 — developer<br/>
            carol / password123 — client
          </div>
        </div>
      </div>
    </div>
  )
}
