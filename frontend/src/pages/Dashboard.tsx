import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Layout from '../components/Layout'
import api from '../api/client'

interface Stats {
  open_pbis: number
  tasks_done: number
  tasks_total: number
  effort_logged: number
  active_sprint_id: number | null
  active_sprint_capacity: number
  velocity: number
}

interface PBI {
  id: number
  title: string
  priority: string
  effort: number
  status: string
  sprint_id: number | null
}

interface Sprint {
  id: number
  capacity: number
  status: string
}

const priorityColor: Record<string, string> = {
  H: '#ef4444', M: '#f59e0b', L: '#22c55e'
}

const chipStyle = (type: string) => {
  const map: Record<string, { bg: string; color: string }> = {
    H: { bg: 'rgba(239,68,68,0.15)', color: '#fca5a5' },
    M: { bg: 'rgba(245,158,11,0.15)', color: '#fcd34d' },
    L: { bg: 'rgba(34,197,94,0.15)', color: '#86efac' },
    Active: { bg: 'rgba(99,102,241,0.2)', color: '#a5b4fc' },
    Planned: { bg: 'rgba(255,255,255,0.06)', color: '#64748b' },
    Complete: { bg: 'rgba(34,197,94,0.15)', color: '#86efac' },
  }
  return map[type] || { bg: 'rgba(255,255,255,0.06)', color: '#64748b' }
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [pbis, setPbis] = useState<PBI[]>([])
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [loading, setLoading] = useState(true)
  const { state, dispatch } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!state.isAuthenticated) { navigate('/login'); return }
    Promise.all([
      api.get('/stats/'),
      api.get('/pbis/?per_page=5'),
      api.get('/sprints/?per_page=10'),
    ]).then(([statsRes, pbiRes, sprintRes]) => {
      setStats(statsRes.data)
      setPbis(pbiRes.data.pbis)
      setSprints(sprintRes.data.sprints)
    }).catch(() => dispatch({ type: 'LOGOUT' }))
      .finally(() => setLoading(false))
  }, [])

  const activeSprint = sprints.find(s => s.status === 'Active')

  const kpis = stats ? [
    { label: 'Open PBIs', value: stats.open_pbis, sub: `${sprints.filter(s => s.status === 'Active').length} active sprint`, subColor: '#818cf8' },
    { label: 'Tasks done', value: `${stats.tasks_done} / ${stats.tasks_total}`, sub: stats.tasks_total > 0 ? `${Math.round((stats.tasks_done / stats.tasks_total) * 100)}% complete` : '0% complete', subColor: '#34d399' },
    { label: 'Effort logged', value: `${stats.effort_logged}h`, sub: activeSprint ? `of ${activeSprint.capacity}h capacity` : 'no active sprint', subColor: '#f59e0b' },
    { label: 'Velocity', value: `${stats.velocity}h`, sub: 'last completed sprint', subColor: '#34d399' },
  ] : []

  return (
    <Layout>
      <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>

        {/* Page header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ color: '#f1f5f9', fontSize: '18px', fontWeight: 500 }}>Dashboard</div>
            <div style={{ color: '#4b5563', fontSize: '12px', marginTop: '3px' }}>
              {activeSprint ? `Sprint ${activeSprint.id} is active` : 'No active sprint'}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => navigate('/backlog')}
              style={{ fontSize: '12px', padding: '7px 14px', borderRadius: '8px', border: '0.5px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.05)', color: '#94a3b8', cursor: 'pointer', fontWeight: 500 }}
            >
              View backlog
            </button>
            <button
              onClick={() => navigate('/sprint')}
              style={{ fontSize: '12px', padding: '7px 14px', borderRadius: '8px', border: 'none', background: '#6366f1', color: '#fff', cursor: 'pointer', fontWeight: 500 }}
            >
              Plan sprint →
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ color: '#374151', fontSize: '13px' }}>Loading...</div>
        ) : (
          <>
            {/* KPI cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '10px' }}>
              {kpis.map((k, i) => (
                <div key={i} style={{ background: '#131720', border: '0.5px solid rgba(255,255,255,0.06)', borderRadius: '10px', padding: '14px 16px', cursor: 'pointer', transition: 'border-color 0.15s' }}
                  onMouseEnter={e => (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(99,102,241,0.4)'}
                  onMouseLeave={e => (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.06)'}
                >
                  <div style={{ fontSize: '10px', color: '#4b5563', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>{k.label}</div>
                  <div style={{ fontSize: '20px', fontWeight: 500, color: '#f1f5f9' }}>{k.value}</div>
                  <div style={{ fontSize: '11px', marginTop: '3px', color: k.subColor }}>{k.sub}</div>
                </div>
              ))}
            </div>

            {/* Two column */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>

              {/* Backlog preview */}
              <div style={{ background: '#131720', border: '0.5px solid rgba(255,255,255,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
                <div style={{ padding: '12px 16px', borderBottom: '0.5px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 500, color: '#e2e8f0' }}>Product backlog</span>
                  <button onClick={() => navigate('/backlog')} style={{ fontSize: '11px', color: '#6366f1', background: 'none', border: 'none', cursor: 'pointer' }}>See all →</button>
                </div>
                {pbis.map(pbi => (
                  <div key={pbi.id}
                    style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 16px', borderBottom: '0.5px solid rgba(255,255,255,0.04)', cursor: 'pointer', transition: 'background 0.1s' }}
                    onMouseEnter={e => (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.03)'}
                    onMouseLeave={e => (e.currentTarget as HTMLDivElement).style.background = 'transparent'}
                  >
                    <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: priorityColor[pbi.priority], flexShrink: 0 }}></div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1', flex: 1 }}>{pbi.title}</div>
                    <span style={{ fontSize: '10px', padding: '2px 7px', borderRadius: '10px', fontWeight: 500, background: chipStyle(pbi.priority).bg, color: chipStyle(pbi.priority).color }}>
                      {pbi.priority}
                    </span>
                    <div style={{ width: '48px', height: '3px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ height: '3px', borderRadius: '2px', background: priorityColor[pbi.priority], width: `${Math.min((pbi.effort / 10) * 100, 100)}%` }}></div>
                    </div>
                    <span style={{ fontSize: '10px', color: '#374151', width: '28px', textAlign: 'right' }}>{pbi.effort}h</span>
                  </div>
                ))}
              </div>

              {/* Sprints preview */}
              <div style={{ background: '#131720', border: '0.5px solid rgba(255,255,255,0.06)', borderRadius: '12px', overflow: 'hidden' }}>
                <div style={{ padding: '12px 16px', borderBottom: '0.5px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '13px', fontWeight: 500, color: '#e2e8f0' }}>Sprints</span>
                  <button onClick={() => navigate('/sprint')} style={{ fontSize: '11px', color: '#6366f1', background: 'none', border: 'none', cursor: 'pointer' }}>Manage →</button>
                </div>
                {sprints.length === 0 ? (
                  <div style={{ padding: '24px 16px', color: '#374151', fontSize: '12px', textAlign: 'center' }}>No sprints yet</div>
                ) : sprints.map(sprint => {
                  const chip = chipStyle(sprint.status)
                  return (
                    <div key={sprint.id}
                      style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderBottom: '0.5px solid rgba(255,255,255,0.04)', cursor: 'pointer', transition: 'background 0.1s' }}
                      onMouseEnter={e => (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.03)'}
                      onMouseLeave={e => (e.currentTarget as HTMLDivElement).style.background = 'transparent'}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '12px', color: '#cbd5e1', fontWeight: 500 }}>Sprint #{sprint.id}</div>
                        <div style={{ fontSize: '11px', color: '#374151', marginTop: '2px' }}>{sprint.capacity}h capacity</div>
                      </div>
                      <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '10px', fontWeight: 500, background: chip.bg, color: chip.color }}>
                        {sprint.status}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}
