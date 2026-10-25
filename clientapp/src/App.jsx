import { useEffect, useState } from 'react'
import api from './api'

const blankForm = { name: '', activity: '', hours: '' }

function App() {
  const [form, setForm] = useState(blankForm)
  const [activities, setActivities] = useState([])
  const [summary, setSummary] = useState({ total_entries: 0, total_hours: 0, most_active_user: null })
  const [errors, setErrors] = useState({})
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const [activityResponse, summaryResponse] = await Promise.all([
        api.get('/activities/'),
        api.get('/summary/'),
      ])
      setActivities(activityResponse.data.activities)
      setSummary(summaryResponse.data)
      setNotice('')
    } catch {
      setNotice('We couldn’t load the activity log. Check that the server is running, then try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setNotice('')

    const nextErrors = {}
    if (!form.name.trim()) nextErrors.name = 'Add the student’s name.'
    if (!form.activity.trim()) nextErrors.activity = 'Describe the activity.'
    if (!form.hours || Number(form.hours) <= 0) nextErrors.hours = 'Enter a number of hours greater than zero.'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    setSubmitting(true)
    try {
      await api.post('/activities/', { ...form, hours: Number(form.hours) })
      setForm(blankForm)
      setErrors({})
      setNotice('Your activity has been added.')
      await loadData()
    } catch (error) {
      setErrors(error.response?.data?.fields || {})
      setNotice(error.response?.data?.error || 'We couldn’t save that activity. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return <main className="page-shell">
    <header className="hero">
      <p className="eyebrow">STUDENT ACTIVITY TRACKER</p>
      <h1>Small steps add up.</h1>
      <p>Keep track of the time students spend learning, creating, and getting involved.</p>
    </header>

    <section className="summary-grid" aria-label="Activity summary">
      <SummaryCard label="Activities logged" value={summary.total_entries} />
      <SummaryCard label="Hours recorded" value={`${Number(summary.total_hours).toFixed(1)} h`} />
      <SummaryCard label="Most active student" value={summary.most_active_user || 'Not yet available'} />
    </section>

    <section className="content-grid">
      <section className="panel">
        <div className="section-heading"><p className="eyebrow">ADD TO THE LOG</p><h2>Record an activity</h2>
          <p className="section-copy">Add a student’s name, what they did, and how long it took.</p></div>
        <form onSubmit={handleSubmit}>
          <Field label="Student name" error={errors.name}>
            <input value={form.name} onChange={(event) => updateField('name', event.target.value)} placeholder="e.g. Asha Sharma" maxLength="100" required />
          </Field>
          <Field label="Activity" error={errors.activity}>
            <input value={form.activity} onChange={(event) => updateField('activity', event.target.value)} placeholder="e.g. Robotics club" maxLength="150" required />
          </Field>
          <Field label="Time spent (hours)" error={errors.hours}>
            <input type="number" min="0.01" max="9999.99" step="0.25" value={form.hours} onChange={(event) => updateField('hours', event.target.value)} placeholder="e.g. 1.5" required />
          </Field>
          <button className="primary-button" disabled={submitting}>
            {submitting ? 'Saving…' : 'Add activity'}
          </button>
        </form>
        {notice && <p className={`notice ${notice.includes('added') ? 'success' : 'error'}`} role="status">{notice}</p>}
      </section>

      <section className="panel" aria-labelledby="recent-heading">
        <div className="section-heading entries-heading">
          <div><p className="eyebrow">THE LATEST</p><h2 id="recent-heading">Recent activities</h2></div>
          <button className="text-button" onClick={loadData} disabled={loading}>Refresh</button>
        </div>
        {loading ? <p className="empty-state">Loading activities…</p>
          : activities.length === 0 ? <p className="empty-state">Nothing here yet. Add the first activity using the form.</p>
            : <div className="table-wrap"><table><thead><tr><th>Student</th><th>Activity</th><th>Hours</th></tr></thead>
              <tbody>{activities.map((item) => <tr key={item.id}><td>{item.name}</td><td>{item.activity}</td><td>{Number(item.hours).toFixed(1)} h</td></tr>)}</tbody>
            </table></div>}
      </section>
    </section>
  </main>
}

function Field({ label, error, children }) {
  return <label className="field"><span>{label}</span>{children}{error && <small>{error}</small>}</label>
}

function SummaryCard({ label, value }) {
  return <article className="summary-card"><p>{label}</p><strong>{value}</strong></article>
}

export default App
