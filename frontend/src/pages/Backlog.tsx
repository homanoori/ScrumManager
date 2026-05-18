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

export default function Backlog() {
  const [pbis, setPbis] = useState<PBI[]>([])
  const [loading, setLoading] = useState(true)
  const [sortField, setSortField] = useState<keyof PBI>('id')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const { state, dispatch } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!state.isAuthenticated) {
      navigate('/login')
      return
    }
    api.get('/pbis/?per_page=100')
      .then(res => setPbis(res.data.pbis))
      .catch(() => dispatch({ type: 'LOGOUT' }))
      .finally(() => setLoading(false))
  }, [])

  const handleSort = (field: keyof PBI) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const sorted = [...pbis].sort((a, b) => {
    const aVal = a[sortField] ?? ''
    const bVal = b[sortField] ?? ''
    if (aVal < bVal) return sortDir === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDir === 'asc' ? 1 : -1
    return 0
  })

  const priorityColor: Record<string, string> = {
    H: 'text-red-600 font-bold',
    M: 'text-yellow-600 font-bold',
    L: 'text-green-600 font-bold',
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gray-900 text-white px-6 py-3 flex justify-between items-center">
        <span className="font-bold text-lg">⚡ ScrumManager</span>
        <div className="flex items-center gap-4 text-sm">
          <button onClick={() => navigate('/sprint')} className="hover:text-gray-300">Sprints</button>
          <button onClick={() => navigate('/tasks')} className="hover:text-gray-300">Tasks</button>
          <span className="text-gray-400">{state.role}</span>
          <button
            onClick={() => { dispatch({ type: 'LOGOUT' }); navigate('/login') }}
            className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded transition"
          >
            Logout
          </button>
        </div>
      </nav>
      <div className="max-w-5xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Product Backlog</h1>
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <div className="bg-white rounded-xl shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800 text-white">
                <tr>
                  {(['id', 'title', 'priority', 'effort', 'status'] as (keyof PBI)[]).map(field => (
                    <th
                      key={field}
                      onClick={() => handleSort(field)}
                      className="px-4 py-3 text-left cursor-pointer hover:bg-gray-700 uppercase text-xs tracking-wide"
                    >
                      {field} {sortField === field ? (sortDir === 'asc' ? '↑' : '↓') : ''}
                    </th>
                  ))}
                  <th className="px-4 py-3 text-left uppercase text-xs tracking-wide">Sprint</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((pbi, i) => (
                  <tr key={pbi.id} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3">{pbi.id}</td>
                    <td className="px-4 py-3 font-medium">{pbi.title}</td>
                    <td className={`px-4 py-3 ${priorityColor[pbi.priority]}`}>{pbi.priority}</td>
                    <td className="px-4 py-3">{pbi.effort}h</td>
                    <td className="px-4 py-3">{pbi.status}</td>
                    <td className="px-4 py-3">{pbi.sprint_id ? `Sprint ${pbi.sprint_id}` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}