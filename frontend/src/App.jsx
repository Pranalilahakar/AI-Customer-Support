
import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API = '/api'

const STATUSES = [
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'waiting_for_customer', label: 'Waiting for customer' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

const PRIORITIES = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
]

async function request(path, options = {}, token = '') {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(', ')
      : typeof detail === 'string'
        ? detail
        : `Request failed with status ${response.status}.`

    const error = new Error(message)
    error.status = response.status
    throw error
  }

  return data
}

function formatStatus(status) {
  return (status || '').replaceAll('_', ' ')
}

function formatCategory(category) {
  return (category || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)

  return Number.isNaN(date.getTime())
    ? '—'
    : date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
}

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem('support_token') || ''
  )
  const [user, setUser] = useState(null)
  const [tickets, setTickets] = useState([])
  const [agents, setAgents] = useState([])

  const [view, setView] = useState('dashboard')
  const [authMode, setAuthMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [ticketLoading, setTicketLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [showCreate, setShowCreate] = useState(false)
  const [activeTicket, setActiveTicket] = useState(null)
  const [comments, setComments] = useState([])
  const [commentBody, setCommentBody] = useState('')
  const [commentLoading, setCommentLoading] = useState(false)
  const [assignmentByTicket, setAssignmentByTicket] = useState({})
  const [busyTicketId, setBusyTicketId] = useState(null)

  const [authForm, setAuthForm] = useState({
    full_name: '',
    email: '',
    password: '',
  })

  const [ticketForm, setTicketForm] = useState({
    title: '',
    description: '',
    category: 'Technical Support',
    priority: 'medium',
  })

  // AI category suggestion state
  const [categoryLoading, setCategoryLoading] = useState(false)
  const [categorySuggestion, setCategorySuggestion] = useState(null)
  const [categoryError, setCategoryError] = useState('')

  const clearMessages = useCallback(() => {
    setError('')
    setNotice('')
  }, [])

  const resetCategorySuggestion = useCallback(() => {
    setCategorySuggestion(null)
    setCategoryError('')
  }, [])

  const resetTicketForm = useCallback(() => {
    setTicketForm({
      title: '',
      description: '',
      category: 'Technical Support',
      priority: 'medium',
    })
    resetCategorySuggestion()
  }, [resetCategorySuggestion])

  const logout = useCallback(() => {
    localStorage.removeItem('support_token')
    setToken('')
    setUser(null)
    setTickets([])
    setAgents([])
    setView('dashboard')
    setActiveTicket(null)
    setComments([])
    clearMessages()
  }, [clearMessages])

  const loadTickets = useCallback(async (activeToken, role) => {
    setTicketLoading(true)

    try {
      let path = '/tickets/my-tickets'

      if (role === 'admin') {
        path = '/tickets/admin/all'
      } else if (role === 'agent') {
        path = '/tickets/assigned-to-me'
      }

      const data = await request(path, {}, activeToken)
      setTickets(Array.isArray(data) ? data : [])
    } finally {
      setTicketLoading(false)
    }
  }, [])

  const loadAgents = useCallback(async (activeToken) => {
    const data = await request('/tickets/agents', {}, activeToken)
    setAgents(Array.isArray(data) ? data : [])
  }, [])

  const initialize = useCallback(
    async (activeToken) => {
      if (!activeToken) return

      setLoading(true)
      clearMessages()

      try {
        // Only authentication failure should end the user's session.
        let currentUser

        try {
          currentUser = await request('/auth/me', {}, activeToken)
        } catch (authError) {
          if (
            authError.status === 401 ||
            authError.status === 403
          ) {
            logout()
          } else {
            setError(authError.message)
          }
          return
        }

        setUser(currentUser)

        // Ticket or agent loading failures should not automatically log out.
        const results = await Promise.allSettled([
          loadTickets(activeToken, currentUser.role),
          currentUser.role === 'admin'
            ? loadAgents(activeToken)
            : Promise.resolve([]),
        ])

        if (results[1].status === 'rejected') {
          setAgents([])

          if (currentUser.role === 'admin') {
            setError(
              `Could not load agents: ${results[1].reason.message}`
            )
          }
        } else if (currentUser.role !== 'admin') {
          setAgents([])
        }

        if (results[0].status === 'rejected') {
          setError(
            `Could not load tickets: ${results[0].reason.message}`
          )
        }
      } finally {
        setLoading(false)
      }
    },
    [clearMessages, loadAgents, loadTickets, logout]
  )

  useEffect(() => {
    if (token) {
      initialize(token)
    }
  }, [token, initialize])

  async function handleAuth(event) {
    event.preventDefault()
    setLoading(true)
    clearMessages()

    try {
      if (authMode === 'register') {
        await request('/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            full_name: authForm.full_name.trim(),
            email: authForm.email.trim(),
            password: authForm.password,
          }),
        })
      }

      const result = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: authForm.email.trim(),
          password: authForm.password,
        }),
      })

      localStorage.setItem('support_token', result.access_token)
      setToken(result.access_token)

      setAuthForm((previous) => ({
        ...previous,
        password: '',
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function refreshTickets() {
    if (!token || !user) return

    clearMessages()

    try {
      await loadTickets(token, user.role)

      if (user.role === 'admin') {
        try {
          await loadAgents(token)
        } catch (err) {
          setError(
            `Tickets refreshed, but agents could not load: ${err.message}`
          )
          return
        }
      }

      setNotice('Workspace refreshed successfully.')
    } catch (err) {
      setError(`Could not refresh tickets: ${err.message}`)
    }
  }

  // AI: predict a category from the ticket title and description.
  async function suggestCategory() {
    const title = ticketForm.title.trim()
    const description = ticketForm.description.trim()

    if (title.length < 3) {
      setCategoryError(
        'Enter a title with at least 3 characters.'
      )
      setCategorySuggestion(null)
      return
    }

    if (description.length < 10) {
      setCategoryError(
        'Enter a description with at least 10 characters.'
      )
      setCategorySuggestion(null)
      return
    }

    setCategoryLoading(true)
    setCategoryError('')
    setCategorySuggestion(null)

    try {
      const result = await request('/ai/predict-category', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
        }),
      })

      setCategorySuggestion(result)
    } catch (err) {
      setCategoryError(
        `Could not suggest a category: ${err.message}`
      )
    } finally {
      setCategoryLoading(false)
    }
  }

  async function createTicket(event) {
    event.preventDefault()

    if (loading) return

    clearMessages()
    setLoading(true)

    try {
      await request(
        '/tickets/',
        {
          method: 'POST',
          body: JSON.stringify({
            title: ticketForm.title.trim(),
            description: ticketForm.description.trim(),
            category: ticketForm.category.trim() || null,
            priority: ticketForm.priority,
          }),
        },
        token
      )

      resetTicketForm()
      setShowCreate(false)
      setView('tickets')
      setNotice('Your ticket was created successfully.')

      await loadTickets(token, user.role)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function changeStatus(ticket, newStatus) {
    if (!newStatus || newStatus === ticket.status) return

    clearMessages()
    setBusyTicketId(ticket.id)

    try {
      await request(
        `/tickets/${ticket.id}/status`,
        {
          method: 'PATCH',
          body: JSON.stringify({
            status: newStatus,
          }),
        },
        token
      )

      setNotice(
        `Ticket #${ticket.id} updated to ${formatStatus(newStatus)}.`
      )

      await loadTickets(token, user.role)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyTicketId(null)
    }
  }

  async function assignTicket(ticket) {
    if (user?.role !== 'admin') return

    const agentId = Number(assignmentByTicket[ticket.id])

    if (!Number.isInteger(agentId) || agentId <= 0) {
      setError('Please select an agent before assigning this ticket.')
      return
    }

    clearMessages()
    setBusyTicketId(ticket.id)

    try {
      await request(
        `/tickets/${ticket.id}/assign`,
        {
          method: 'POST',
          body: JSON.stringify({
            assigned_to: agentId,
          }),
        },
        token
      )

      const selectedAgent = agents.find(
        (agent) => agent.id === agentId
      )

      setNotice(
        `Ticket #${ticket.id} assigned to ${
          selectedAgent?.full_name || `agent #${agentId}`
        }.`
      )

      await loadTickets(token, user.role)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyTicketId(null)
    }
  }

  async function openComments(ticket) {
    clearMessages()
    setActiveTicket(ticket)
    setComments([])
    setCommentBody('')
    setCommentLoading(true)

    try {
      const data = await request(
        `/tickets/${ticket.id}/comments`,
        {},
        token
      )

      setComments(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(`Could not load comments: ${err.message}`)
    } finally {
      setCommentLoading(false)
    }
  }

  async function addComment(event) {
    event.preventDefault()

    if (!activeTicket || !commentBody.trim()) {
      setError('Please enter a comment.')
      return
    }

    clearMessages()
    setCommentLoading(true)

    try {
      const newComment = await request(
        `/tickets/${activeTicket.id}/comments`,
        {
          method: 'POST',
          body: JSON.stringify({
            body: commentBody.trim(),
          }),
        },
        token
      )

      setComments((previous) => [...previous, newComment])
      setCommentBody('')
      setNotice(`Comment added to ticket #${activeTicket.id}.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setCommentLoading(false)
    }
  }

  const visibleTickets = tickets.filter((ticket) => {
    const query = search.trim().toLowerCase()

    const matchesSearch =
      String(ticket.id).includes(query) ||
      (ticket.title || '').toLowerCase().includes(query) ||
      (ticket.description || '').toLowerCase().includes(query) ||
      (ticket.category || '').toLowerCase().includes(query)

    const matchesFilter =
      filter === 'all' || ticket.status === filter

    return matchesSearch && matchesFilter
  })

  const stats = {
    total: tickets.length,
    open: tickets.filter((ticket) => ticket.status === 'open').length,
    progress: tickets.filter(
      (ticket) => ticket.status === 'in_progress'
    ).length,
    resolved: tickets.filter(
      (ticket) => ['resolved', 'closed'].includes(ticket.status)
    ).length,
  }

  if (!token || !user) {
    return (
      <main className="auth-page">
        <section className="auth-brand">
          <div className="brand-mark">S</div>
          <span className="brand-name">SupportDesk</span>

          <div className="auth-hero">
            <span className="eyebrow">
              CUSTOMER SUPPORT, SIMPLIFIED
            </span>

            <h1>Every issue deserves a better answer.</h1>

            <p>
              One workspace for support tickets, team workflows, and
              customer conversations.
            </p>

            <div className="hero-points">
              <span>✓ Organized ticket management</span>
              <span>✓ Role-based team workflows</span>
              <span>✓ AI-powered category suggestions</span>
            </div>
          </div>

          <span className="auth-footer">
            AI Customer Support &amp; Ticket Management
          </span>
        </section>

        <section className="auth-panel">
          <form className="auth-card" onSubmit={handleAuth}>
            <span className="eyebrow">WELCOME TO SUPPORTDESK</span>

            <h2>
              {authMode === 'login'
                ? 'Sign in to your account'
                : 'Create your account'}
            </h2>

            <p className="muted">
              {authMode === 'login'
                ? 'Enter your details to access your workspace.'
                : 'Registration creates a customer account.'}
            </p>

            {authMode === 'register' && (
              <label>
                Full name
                <input
                  required
                  minLength={2}
                  maxLength={100}
                  autoComplete="name"
                  value={authForm.full_name}
                  onChange={(event) =>
                    setAuthForm({
                      ...authForm,
                      full_name: event.target.value,
                    })
                  }
                  placeholder="Your full name"
                />
              </label>
            )}

            <label>
              Email address
              <input
                required
                type="email"
                autoComplete="email"
                value={authForm.email}
                onChange={(event) =>
                  setAuthForm({
                    ...authForm,
                    email: event.target.value,
                  })
                }
                placeholder="you@example.com"
              />
            </label>

            <label>
              Password
              <input
                required
                minLength={authMode === 'register' ? 8 : undefined}
                type="password"
                autoComplete={
                  authMode === 'login'
                    ? 'current-password'
                    : 'new-password'
                }
                value={authForm.password}
                onChange={(event) =>
                  setAuthForm({
                    ...authForm,
                    password: event.target.value,
                  })
                }
                placeholder="Enter your password"
              />
            </label>

            {error && <div className="alert error">{error}</div>}

            <button
              className="primary-button full-width"
              disabled={loading}
              type="submit"
            >
              {loading
                ? 'Please wait…'
                : authMode === 'login'
                  ? 'Sign in →'
                  : 'Create account →'}
            </button>

            <p className="switch-auth">
              {authMode === 'login'
                ? 'New to SupportDesk?'
                : 'Already have an account?'}{' '}
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  setAuthMode(
                    authMode === 'login' ? 'register' : 'login'
                  )
                  clearMessages()
                }}
              >
                {authMode === 'login' ? 'Create account' : 'Sign in'}
              </button>
            </p>
          </form>
        </section>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <span>SupportDesk</span>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <button
          className={`nav-item ${view === 'dashboard' ? 'active' : ''}`}
          onClick={() => setView('dashboard')}
        >
          <span>▦</span> Dashboard
        </button>

        <button
          className={`nav-item ${view === 'tickets' ? 'active' : ''}`}
          onClick={() => setView('tickets')}
        >
          <span>▤</span>
          {user.role === 'agent'
            ? 'Assigned tickets'
            : user.role === 'admin'
              ? 'All tickets'
              : 'My tickets'}
          <span className="nav-count">{tickets.length}</span>
        </button>

        <button
          className="nav-item"
          onClick={() => {
            clearMessages()
            resetCategorySuggestion()
            setShowCreate(true)
          }}
        >
          <span>＋</span> Create ticket
        </button>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">✦</div>
            <strong>Support, made smarter</strong>
            <p>
              Get AI-powered category suggestions when creating tickets.
            </p>
          </div>

          <div className="profile">
            <div className="avatar">
              {user.full_name?.charAt(0).toUpperCase()}
            </div>

            <div className="profile-details">
              <strong>{user.full_name}</strong>
              <span>{user.role}</span>
            </div>

            <button
              className="icon-button"
              title="Sign out"
              aria-label="Sign out"
              onClick={logout}
            >
              ↪
            </button>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong>
              {view === 'dashboard' ? 'Overview' : 'Tickets'}
            </strong>
          </div>

          <div className="topbar-actions">
            <span className="role-chip">{user.role}</span>

            <button
              className="primary-button"
              onClick={() => {
                clearMessages()
                resetCategorySuggestion()
                setShowCreate(true)
              }}
            >
              ＋ New ticket
            </button>
          </div>
        </header>

        <section className="content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">YOUR SUPPORT WORKSPACE</span>

              <h1>
                {view === 'dashboard'
                  ? `Good to see you, ${user.full_name.split(' ')[0]}`
                  : user.role === 'admin'
                    ? 'All tickets'
                    : user.role === 'agent'
                      ? 'Assigned tickets'
                      : 'My tickets'}
              </h1>

              <p className="muted">
                {user.role === 'agent'
                  ? 'Review and manage tickets assigned to you.'
                  : user.role === 'admin'
                    ? 'Review customer requests, update statuses, and assign agents.'
                    : 'Track your support requests and keep conversations moving.'}
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={refreshTickets}
              disabled={loading || ticketLoading}
            >
              ↻ Refresh
            </button>
          </div>

          {error && <div className="alert error">{error}</div>}
          {notice && <div className="alert success">{notice}</div>}

          <div className="stats-grid">
            <StatCard
              label="Visible tickets"
              value={stats.total}
              icon="▤"
              tone="purple"
            />
            <StatCard
              label="Open"
              value={stats.open}
              icon="◷"
              tone="blue"
            />
            <StatCard
              label="In progress"
              value={stats.progress}
              icon="↗"
              tone="orange"
            />
            <StatCard
              label="Resolved / closed"
              value={stats.resolved}
              icon="✓"
              tone="green"
            />
          </div>

          {view === 'dashboard' && (
            <section className="welcome-banner">
              <div>
                <span className="eyebrow">SUPPORT OVERVIEW</span>
                <h2>Stay on top of every conversation.</h2>
                <p>
                  Create requests, track progress, and keep ticket discussions
                  in one place.
                </p>

                <button
                  className="banner-button"
                  onClick={() => {
                    clearMessages()
                    resetCategorySuggestion()
                    setShowCreate(true)
                  }}
                >
                  Create a ticket <span>→</span>
                </button>
              </div>

              <div className="banner-art" aria-hidden="true">
                <div className="art-orbit orbit-one" />
                <div className="art-orbit orbit-two" />
                <div className="art-card">
                  <span>✓</span>
                  <div>
                    <strong>Ticket workflow</strong>
                    <small>Organized support</small>
                  </div>
                </div>
                <div className="art-star">✦</div>
              </div>
            </section>
          )}

          <section className="ticket-section">
            <div className="section-heading">
              <div>
                <h2>
                  {user.role === 'admin'
                    ? 'All tickets'
                    : user.role === 'agent'
                      ? 'Assigned tickets'
                      : 'Recent tickets'}
                </h2>

                <p className="muted">
                  Search and filter the tickets available to your account.
                </p>
              </div>

              <button
                className="secondary-button"
                onClick={() => setView('tickets')}
              >
                View all →
              </button>
            </div>

            <div className="ticket-toolbar">
              <div className="search-box">
                <span>⌕</span>
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search tickets..."
                  aria-label="Search tickets"
                />
              </div>

              <select
                value={filter}
                onChange={(event) => setFilter(event.target.value)}
                aria-label="Filter tickets by status"
              >
                <option value="all">All statuses</option>
                {STATUSES.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="ticket-table-wrap">
              <table className="ticket-table">
                <thead>
                  <tr>
                    <th>Ticket</th>
                    {user.role === 'admin' && <th>Assignment</th>}
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleTickets.length > 0 ? (
                    visibleTickets.map((ticket) => (
                      <tr key={ticket.id}>
                        <td>
                          <div className="ticket-title">
                            <span className="ticket-icon">#</span>
                            <div>
                              <strong>{ticket.title}</strong>
                              <small>
                                Ticket #{ticket.id} ·{' '}
                                {ticket.category || 'Uncategorized'}
                              </small>
                            </div>
                          </div>
                        </td>

                        {user.role === 'admin' && (
                          <td>
                            <div className="assignment-control">
                              <select
                                aria-label={`Choose agent for ticket ${ticket.id}`}
                                value={
                                  assignmentByTicket[ticket.id] ??
                                  ticket.assigned_to ??
                                  ''
                                }
                                onChange={(event) =>
                                  setAssignmentByTicket((previous) => ({
                                    ...previous,
                                    [ticket.id]: event.target.value,
                                  }))
                                }
                              >
                                <option value="">Unassigned</option>
                                {agents.map((agent) => (
                                  <option key={agent.id} value={agent.id}>
                                    {agent.full_name} (#{agent.id})
                                  </option>
                                ))}
                              </select>

                              <button
                                type="button"
                                disabled={
                                  busyTicketId === ticket.id ||
                                  (!assignmentByTicket[ticket.id] &&
                                    !ticket.assigned_to)
                                }
                                onClick={() => assignTicket(ticket)}
                              >
                                Assign
                              </button>
                            </div>
                          </td>
                        )}

                        <td>
                          <span
                            className={`priority priority-${ticket.priority}`}
                          >
                            {ticket.priority}
                          </span>
                        </td>

                        <td>
                          <span
                            className={`status status-${ticket.status}`}
                          >
                            {formatStatus(ticket.status)}
                          </span>
                        </td>

                        <td className="date-cell">
                          {formatDate(ticket.created_at)}
                        </td>

                        <td>
                          <div className="row-actions">
                            <button
                              type="button"
                              onClick={() => openComments(ticket)}
                            >
                              Comments
                            </button>

                            {(user.role === 'admin' ||
                              user.role === 'agent') && (
                              <select
                                aria-label={`Update ticket ${ticket.id} status`}
                                value={ticket.status}
                                disabled={busyTicketId === ticket.id}
                                onChange={(event) =>
                                  changeStatus(ticket, event.target.value)
                                }
                              >
                                {STATUSES.map((status) => (
                                  <option
                                    key={status.value}
                                    value={status.value}
                                  >
                                    {status.label}
                                  </option>
                                ))}
                              </select>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={user.role === 'admin' ? 6 : 5}>
                        <div className="empty-state">
                          <span>▤</span>
                          <strong>
                            {ticketLoading
                              ? 'Loading tickets…'
                              : 'No tickets found'}
                          </strong>
                          <p>
                            {ticketLoading
                              ? 'Please wait while tickets load.'
                              : 'Try another filter or create a new support ticket.'}
                          </p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="table-footer">
              Showing {visibleTickets.length} of {tickets.length} visible
              tickets
            </div>
          </section>
        </section>
      </main>

      {showCreate && (
        <div
          className="modal-backdrop"
          onClick={() => {
            setShowCreate(false)
            resetCategorySuggestion()
          }}
        >
          <section
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-ticket-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <div>
                <span className="eyebrow">SUPPORT REQUEST</span>
                <h2 id="create-ticket-title">Create a ticket</h2>
              </div>

              <button
                type="button"
                className="icon-button"
                aria-label="Close create ticket form"
                onClick={() => {
                  setShowCreate(false)
                  resetCategorySuggestion()
                }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={createTicket}>
              <label>
                Ticket title
                <input
                  required
                  minLength={3}
                  maxLength={200}
                  value={ticketForm.title}
                  onChange={(event) => {
                    setTicketForm((previous) => ({
                      ...previous,
                      title: event.target.value,
                    }))
                    resetCategorySuggestion()
                  }}
                  placeholder="Briefly describe the issue"
                />
              </label>

              <label>
                Description
                <textarea
                  required
                  minLength={10}
                  rows={4}
                  value={ticketForm.description}
                  onChange={(event) => {
                    setTicketForm((previous) => ({
                      ...previous,
                      description: event.target.value,
                    }))
                    resetCategorySuggestion()
                  }}
                  placeholder="Explain what happened and what you need help with"
                />
              </label>

              <div className="form-row">
                <label className="category-field">
                  Category

                  <input
                    maxLength={100}
                    value={ticketForm.category}
                    onChange={(event) =>
                      setTicketForm((previous) => ({
                        ...previous,
                        category: event.target.value,
                      }))
                    }
                    placeholder="Enter a category"
                  />

                  <button
                    type="button"
                    className="secondary-button suggest-category-button"
                    onClick={suggestCategory}
                    disabled={categoryLoading || loading}
                  >
                    {categoryLoading
                      ? 'Predicting...'
                      : 'Suggest Category ✨'}
                  </button>

                  {categoryError && (
                    <div className="alert error category-message">
                      {categoryError}
                    </div>
                  )}

                  {categorySuggestion && (
                    <div className="category-suggestion">
                      <p>
                        <strong>AI suggestion:</strong>{' '}
                        {formatCategory(categorySuggestion.category)}
                      </p>

                      <p className="muted">
                        Confidence:{' '}
                        {(
                          categorySuggestion.confidence * 100
                        ).toFixed(1)}
                        %
                      </p>

                      <button
                        type="button"
                        className="text-button"
                        onClick={() => {
                          setTicketForm((previous) => ({
                            ...previous,
                            category: categorySuggestion.category,
                          }))
                          resetCategorySuggestion()
                        }}
                      >
                        Use this suggestion
                      </button>
                    </div>
                  )}
                </label>

                <label>
                  Priority

                  <select
                    value={ticketForm.priority}
                    onChange={(event) =>
                      setTicketForm((previous) => ({
                        ...previous,
                        priority: event.target.value,
                      }))
                    }
                  >
                    {PRIORITIES.map((priority) => (
                      <option key={priority.value} value={priority.value}>
                        {priority.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {error && <div className="alert error">{error}</div>}

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setShowCreate(false)
                    resetCategorySuggestion()
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={loading || categoryLoading}
                >
                  {loading ? 'Submitting…' : 'Submit ticket →'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}

      {activeTicket && (
        <div
          className="modal-backdrop"
          onClick={() => setActiveTicket(null)}
        >
          <section
            className="modal-card comments-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="comments-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <div>
                <span className="eyebrow">
                  TICKET #{activeTicket.id}
                </span>
                <h2 id="comments-title">Conversation</h2>
                <p className="muted">{activeTicket.title}</p>
              </div>

              <button
                type="button"
                className="icon-button"
                aria-label="Close comments"
                onClick={() => setActiveTicket(null)}
              >
                ✕
              </button>
            </div>

            <div className="comments-list">
              {commentLoading && comments.length === 0 ? (
                <p className="muted">Loading conversation…</p>
              ) : comments.length === 0 ? (
                <div className="empty-state">
                  <strong>No comments yet</strong>
                  <p>
                    Start the conversation by adding a comment below.
                  </p>
                </div>
              ) : (
                comments.map((comment) => (
                  <article className="comment-item" key={comment.id}>
                    <div className="comment-avatar">
                      {(comment.author_name || `U${comment.user_id}`)
                        .charAt(0)
                        .toUpperCase()}
                    </div>

                    <div className="comment-content">
                      <div className="comment-meta">
                        <strong>
                          {comment.author_name ||
                            `User ${comment.user_id}`}
                        </strong>
                        <span>{formatDate(comment.created_at)}</span>
                      </div>

                      <p>{comment.body}</p>
                    </div>
                  </article>
                ))
              )}
            </div>

            <form className="comment-form" onSubmit={addComment}>
              <label>
                Add a comment
                <textarea
                  required
                  minLength={1}
                  maxLength={5000}
                  rows={3}
                  value={commentBody}
                  onChange={(event) =>
                    setCommentBody(event.target.value)
                  }
                  placeholder="Write your message…"
                />
              </label>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setActiveTicket(null)}
                >
                  Close
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={commentLoading || !commentBody.trim()}
                >
                  {commentLoading ? 'Sending…' : 'Send comment →'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, icon, tone }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${tone}`}>{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <span className="stat-decoration">↗</span>
    </div>
  )
}

export default App
