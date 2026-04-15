import { useState } from 'react'

const PILLS = [
  { icon: '💬', label: 'Plain-English answers' },
  { icon: '📋', label: 'Document-grounded' },
  { icon: '⚡', label: 'Instant responses' },
]

export default function LoginPage({ onLogin }) {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields.')
      return
    }

    setLoading(true)
    // Simulate a short auth delay — swap this for a real fetch() call later
    await new Promise(r => setTimeout(r, 700))
    setLoading(false)
    onLogin({ email, password })
  }

  return (
    <div className="relative flex h-full w-full overflow-hidden">
      {/* ── Background image + overlay ── */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/car.jpg')" }}
      />
      <div className="absolute inset-0 bg-[#08080f]/55" />

      {/* ── Left hero ── */}
      <div className="relative z-10 flex flex-1 flex-col justify-end px-14 pb-16 pr-16">
        {/* Wordmark */}
        <p className="mb-9 text-sm font-bold tracking-wide text-white/80">
          DriveFinance AI
        </p>

        {/* Headline */}
        <h1 className="mb-5 text-5xl font-bold leading-tight tracking-tight text-white">
          Smart answers for
          <br />
          <span className="text-brand-400">your auto loan</span>
        </h1>

        {/* Sub-copy */}
        <p className="mb-10 max-w-sm text-[15px] leading-relaxed text-white/50">
          Get instant, accurate answers about financing rates, eligibility,
          fees, and refinancing — powered by your official finance documents.
        </p>

        {/* Pills */}
        <div className="flex flex-wrap gap-3">
          {PILLS.map(p => (
            <span
              key={p.label}
              className="flex items-center gap-2 rounded-[9px] border border-white/[0.14] bg-white/[0.07] px-4 py-2 text-[13px] text-white/70"
            >
              {p.icon}&nbsp;{p.label}
            </span>
          ))}
        </div>
      </div>

      {/* ── Right sign-in panel ── */}
      <div className="relative z-10 flex w-[440px] flex-shrink-0 flex-col justify-center border-l border-white/[0.06] bg-surface-800 px-11 py-14">
        <h2 className="mb-1 text-2xl font-bold tracking-tight text-[#ececec]">
          Welcome back
        </h2>
        <p className="mb-8 text-[13px] leading-relaxed text-surface-100/40">
          Sign in to access your automotive finance assistant
        </p>

        <form onSubmit={handleSubmit} noValidate>
          {/* Email */}
          <label className="mb-1.5 block text-[11px] font-medium uppercase tracking-widest text-surface-100/50">
            Email address
          </label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="mb-4 w-full rounded-[9px] border border-surface-400 bg-surface-700 px-3.5 py-[11px] text-sm text-[#ececec] placeholder-surface-300/40 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
          />

          {/* Password */}
          <label className="mb-1.5 block text-[11px] font-medium uppercase tracking-widest text-surface-100/50">
            Password
          </label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="mb-1 w-full rounded-[9px] border border-surface-400 bg-surface-700 px-3.5 py-[11px] text-sm text-[#ececec] placeholder-surface-300/40 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
          />

          {/* Inline error */}
          <div className="mb-5 h-4">
            {error && (
              <p className="text-[12px] text-red-400">{error}</p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-[10px] bg-brand-500 py-3 text-[15px] font-semibold text-white transition hover:bg-brand-600 disabled:opacity-60"
          >
            {loading ? (
              <>
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Signing in…
              </>
            ) : (
              'Sign In →'
            )}
          </button>
        </form>

        <p className="mt-5 text-center text-[12px] text-surface-100/30">
          Don't have an account?{' '}
          <button className="text-brand-400 hover:underline">
            Create one
          </button>
        </p>
      </div>
    </div>
  )
}
