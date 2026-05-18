import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

interface Task {
  id: number
  title: string
  estimated_effort: number
  actual_effort: number
  status: string
  pbi_id: number
}

interface PBIGroup {
  pbi_id: number
  pbi_title: string
  pbi_priority: string
  pbi_status: string
  sprint_id: number
  all_done: boolean
  tasks: Task[]
}

const STATUS_OPTIONS = ['Not Started', 'In Progress', 'Done']

const statusStyle: Record<string, string> = {
  'Not Started': 'bg-gray-100 text-gray-600',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Done': 'bg-green-100 text-green-700',
}

const priorityStyle: Record<string, string> = {
  H: 'text-red-600 font-bold',
  M: 'text-yellow-600 font-bold',
  L: 'text-green-600 font-bold',
}

export default function TasksPage() {
  const [groups, setGroups] = useState<PBIGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [addingTo, setAddingTo] = useState<number | null>(null)
  const [newTitle, setNewTitle] = useState('')
  const [newEffort, setNewEffort] = useState('')
  const [loggingFor, setLoggingFor] = useState<number | null>(null)
  const [logHours, setLogHours] = useState('')
  const [logDate, setLogDate] = useState(new Date().toISOString().split('T')[0])
  const [error, setError] = useState('')
  const { state, dispatch } = useAuth()
  const navigate = useNavigate()

  const fetchTasks = () => {
    api.get('/tasks/by-pbi')
      .then(res => setGroups(res.data))
      .catch(() => dispatch({ type: 'LOGOUT' }))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!state.isAuthenticated) { navigate('/login'); return }
    fetchTasks()
  }, [])

  const handleStatusChange = async (taskId: number, status: string) => {
    try {
      await api.post('/tasks/' + taskId + '/status', { status })
      fetchTasks()
    } catch {
      setError('Failed to update status')
    }
  }

  const handleAddTask = async (pbiId: number) => {
    if (!newTitle.trim() || !newEffort) return
    try {
      await api.post('/tasks/', {
        title: newTitle.trim(),
        estimated_effort: parseFloat(newEffort),
        pbi_id: pbiId,
      })
      setNewTitle('')
      setNewEffort('')
      setAddingTo(null)
      fetchTasks()
    } catch {
      setError('Failed to add task')
    }
  }

  const handleLogEffort = async (taskId: number) => {
    if (!logHours || !logDate) return
    try {
      await api.post('/tasks/' + taskId + '/log-effort', {
        hours_spent: parseFloat(logHours),
        date: logDate,
      })
      setLogHours('')
      setLoggingFor(null)
      fetchTasks()
    } catch {
      setError('Failed to log effort')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gray-900 text-white px-6 py-3 flex justify-between items-center">
        <span className="font-bold text-lg">ScrumManager</span>
        <div className="flex items-center gap-4 text-sm">
          <button onClick={() => navigate('/backlog')} className="hover:text-gray-300">Backlog</button>
          <button onClick={() => navigate('/sprint')} className="hover:text-gray-300">Sprints</button>
          <button onClick={() => navigate('/tasks')} className="hover:text-gray-300 text-white">Tasks</button>
          <span className="text-gray-400">{state.role}</span>
          <button onClick={() => { dispatch({ type: 'LOGOUT' }); navigate('/login') }}
            className="bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded transition">
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Tasks</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm mb-4">
            {error}
            <button onClick={() => setError('')} className="ml-3 underline">dismiss</button>
          </div>
        )}

        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : groups.length === 0 ? (
          <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
            No PBIs are currently in a sprint. Add PBIs to a sprint first.
          </div>
        ) : (
          <div className="space-y-6">
            {groups.map(group => (
              <div key={group.pbi_id} className="bg-white rounded-xl shadow overflow-hidden">
                <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100 bg-gray-50">
                  <div className="flex items-center gap-3">
                    {group.all_done && (
                      <span className="text-green-500 text-lg" title="All tasks complete">done</span>
                    )}
                    <span className="font-semibold text-gray-800">{group.pbi_title}</span>
                    <span className={"text-xs " + priorityStyle[group.pbi_priority]}>
                      {group.pbi_priority}
                    </span>
                    <span className="text-xs text-gray-400">Sprint #{group.sprint_id}</span>
                  </div>
                  {state.role !== 'client' && (
                    <button
                      onClick={() => { setAddingTo(group.pbi_id); setError('') }}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      + Add task
                    </button>
                  )}
                </div>

                <div className="divide-y divide-gray-50">
                  {group.tasks.length === 0 ? (
                    <p className="px-6 py-4 text-sm text-gray-400 italic">No tasks yet.</p>
                  ) : (
                    group.tasks.map(task => (
                      <div key={task.id} className="px-6 py-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">{task.title}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-gray-400">
                              {task.actual_effort}h / {task.estimated_effort}h
                            </span>
                            {state.role !== 'client' ? (
                              <select
                                value={task.status}
                                onChange={e => handleStatusChange(task.id, e.target.value)}
                                className={"text-xs px-2 py-1 rounded-full border-0 font-medium cursor-pointer focus:outline-none " + statusStyle[task.status]}
                              >
                                {STATUS_OPTIONS.map(s => (
                                  <option key={s} value={s}>{s}</option>
                                ))}
                              </select>
                            ) : (
                              <span className={"text-xs px-2 py-1 rounded-full font-medium " + statusStyle[task.status]}>
                                {task.status}
                              </span>
                            )}
                            {state.role !== 'client' && (
                              <button
                                onClick={() => { setLoggingFor(loggingFor === task.id ? null : task.id); setError('') }}
                                className="text-xs text-gray-400 hover:text-blue-600 transition"
                                title="Log effort"
                              >
                                log
                              </button>
                            )}
                          </div>
                        </div>

                        {loggingFor === task.id && (
                          <div className="mt-2 flex gap-2 items-center bg-blue-50 rounded-lg px-3 py-2">
                            <input
                              type="number"
                              value={logHours}
                              onChange={e => setLogHours(e.target.value)}
                              placeholder="Hours"
                              className="border border-gray-300 rounded px-2 py-1 text-xs w-20 focus:outline-none focus:ring-1 focus:ring-blue-400"
                            />
                            <input
                              type="date"
                              value={logDate}
                              onChange={e => setLogDate(e.target.value)}
                              className="border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-400"
                            />
                            <button
                              onClick={() => handleLogEffort(task.id)}
                              className="bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700 transition"
                            >
                              Log
                            </button>
                            <button
                              onClick={() => setLoggingFor(null)}
                              className="text-xs text-gray-400 hover:text-gray-600"
                            >
                              cancel
                            </button>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>

                {addingTo === group.pbi_id && (
                  <div className="px-6 py-4 bg-blue-50 border-t border-blue-100 flex gap-2 items-center">
                    <input
                      type="text"
                      value={newTitle}
                      onChange={e => setNewTitle(e.target.value)}
                      placeholder="Task title"
                      className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      value={newEffort}
                      onChange={e => setNewEffort(e.target.value)}
                      placeholder="Est. hours"
                      className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => handleAddTask(group.pbi_id)}
                      className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-blue-700 transition"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => { setAddingTo(null); setNewTitle(''); setNewEffort('') }}
                      className="text-sm text-gray-400 hover:text-gray-600"
                    >
                      cancel
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
