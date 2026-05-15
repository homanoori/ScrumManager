import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

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

interface ProposedPBI {
  id: number
  title: string
  priority: string
  effort: number
}

export default function SprintPage() {
  const [sprints, setSprints] = useState<Sprint[]>([])
  const [sprintPbis, setSprintPbis] = useState<PBI[]>([])
  const [capacity, setCapacity] = useState('')
  const [proposed, setProposed] = useState<ProposedPBI[]>([])
  const [proposalError, setProposalError] = useState('')
  const [loading, setLoading] = useState(true)
  const { state, dispatch } = useAuth()
  const navigate = useNavigate()

  const fetchData = () => {
    Promise.all([
      api.get('/sprints/?per_page=100'),
      api.get('/pbis/?per_page=100'),
    ]).then(([sprintRes, pbiRes]) => {
      setSprints(sprintRes.data.sprints)
      setSprintPbis(pbiRes.data.pbis.filter((p: PBI) => p.sprint_id !== null))
    }).catch(() => dispatch({ type: 'LOGOUT' }))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!state.isAuthenticated) { navigate('/login'); return }
    fetchData()
  }, [])

  const handlePropose = async () => {
    setProposalError('')
    setProposed([])
    try {
      const res = await api.post('/sprints/propose', { capacity: parseFloat(capacity) })
      if (res.data.error) {
        setProposalError(res.data.error)
      } else {
        setProposed(res.data.proposed)
      }
    } catch {
      setProposalError('Failed to propose sprint')
    }
  }

  const handleCreate = async () => {
    try {
      await api.post('/sprints/create', {
        capacity: parseFloat(capacity),
        pbi_ids: proposed.map(p => p.id),
      })
      setProposed([])
      setCapacity('')
      fetchData()
    } catch {
      setProposalError('Failed to create sprint')
    }
  }

  const handleStatus = async (sprintId: number) => {
    try {
      await api.post(`/sprints/${sprintId}/status`)
      fetchData()
    } catch {
      alert('Failed to update sprint status')
    }
  }

  const priorityColor: Record<string, string> = {
    H: 'text-red-600 font-bold',
    M: 'text-yellow-600 font-bold',
    L: 'text-green-600 font-bold',
  }

  const statusColor: Record<string, string> = {
    Planned: 'bg-gray-100 text-gray-700',
    Active: 'bg-blue-100 text-blue-700',
    Complete: 'bg-green-100 text-green-700',
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gray-900 text-white px-6 py-3 flex justify-between items-center">
        <span className="font-bold text-lg">⚡ ScrumManager</span>
        <div className="flex items-center gap-4 text-sm">
          <button onClick={() => navigate('/backlog')} className="hover:text-gray-300">Backlog</button>
          <button onClick={() => navigate('/sprint')} className="hover:text-gray-300">Sprints</button>
          <span className="text-gray-400">{state.role}</span>
          <button onClick={() => { dispatch({ type: 'LOGOUT' }); navigate('/login') }}
            className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded transition">
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Sprint Backlog</h1>

        {loading ? <p className="text-gray-500">Loading...</p> : (
          <>
            {/* Sprint cards */}
            {sprints.map(sprint => (
              <div key={sprint.id} className="bg-white rounded-xl shadow mb-4 p-6">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h2 className="text-lg font-bold">Sprint #{sprint.id}</h2>
                    <p className="text-sm text-gray-500">Capacity: {sprint.capacity}h</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor[sprint.status]}`}>
                      {sprint.status}
                    </span>
                    {sprint.status !== 'Complete' && (
                      <button onClick={() => handleStatus(sprint.id)}
                        className="bg-blue-600 text-white text-sm px-3 py-1 rounded hover:bg-blue-700 transition">
                        {sprint.status === 'Planned' ? 'Start Sprint' : 'Complete Sprint'}
                      </button>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  {sprintPbis.filter(p => p.sprint_id === sprint.id).map(pbi => (
                    <div key={pbi.id} className="flex justify-between items-center bg-gray-50 rounded px-4 py-2 text-sm">
                      <span className="font-medium">{pbi.title}</span>
                      <div className="flex gap-4 text-gray-500">
                        <span className={priorityColor[pbi.priority]}>{pbi.priority}</span>
                        <span>{pbi.effort}h</span>
                        <span>{pbi.status}</span>
                        {sprint.status === 'Active' && (
                          <span className="text-gray-400">🔒 Locked</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Propose new sprint */}
            {state.role !== 'client' && (
              <div className="bg-white rounded-xl shadow p-6 mt-6">
                <h2 className="text-lg font-bold mb-4">Propose New Sprint</h2>
                <div className="flex gap-3 mb-4">
                  <input
                    type="number"
                    value={capacity}
                    onChange={e => setCapacity(e.target.value)}
                    placeholder="Capacity (hours)"
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button onClick={handlePropose}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition">
                    Propose
                  </button>
                </div>

                {proposalError && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm mb-4">
                    {proposalError}
                  </div>
                )}

                {proposed.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2 text-sm text-gray-700">Proposed Items:</h3>
                    <div className="space-y-2 mb-4">
                      {proposed.map(pbi => (
                        <div key={pbi.id} className="flex justify-between items-center bg-blue-50 rounded px-4 py-2 text-sm">
                          <span>{pbi.title}</span>
                          <div className="flex gap-3 text-gray-500">
                            <span className={priorityColor[pbi.priority]}>{pbi.priority}</span>
                            <span>{pbi.effort}h</span>
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Total: <strong>{proposed.reduce((s, p) => s + p.effort, 0)}h</strong> / {capacity}h
                    </p>
                    <button onClick={handleCreate}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition">
                      Confirm — Create Sprint
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}