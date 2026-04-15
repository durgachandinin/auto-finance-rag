import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'

const SUGGESTED = [
  'APR for 750 credit score, new car?',
  'Minimum down payment needed?',
  'What is the late payment fee?',
  'Can I pay off my loan early?',
  'Do I need GAP insurance?',
  'How does refinancing work?',
  'What documents do I need?',
]

const TOPICS = [
  'Loan rates & APR',
  'Credit eligibility',
  'Down payments',
  'Fees & closing costs',
  'Refinancing',
  'Early payoff',
  'GAP insurance',
  'Required documents',
]

// ── Mock API — replace with real fetch('/api/chat', ...) when backend is ready ──
async function mockApiCall(question, history) {
  await new Promise(r => setTimeout(r, 1200 + Math.random() * 600))

  const responses = {
    apr: 'For a 750 credit score on a new vehicle, you can typically qualify for our Tier 1 rates. Current APR ranges from 5.49% to 6.99% for 60-month terms, depending on the loan amount and your complete credit profile.',
    down: 'The minimum required down payment is 10% of the vehicle purchase price for financed loans. However, we recommend 20% or more to reduce your monthly payment and minimize interest charges over the loan term.',
    fee: 'Late payments incur a fee of $35 or 5% of the unpaid installment, whichever is greater, after a 10-day grace period. Repeated late payments may also affect your credit score and future rate eligibility.',
    early: 'Yes — you can pay off your auto loan early at any time with no prepayment penalty. Simply contact us to request a payoff quote, which is valid for 10 business days.',
    gap: 'GAP insurance covers the difference between your loan balance and the vehicle\'s actual cash value if your car is totaled or stolen. It is optional but strongly recommended for loans exceeding 80% of the vehicle\'s value.',
    refi: 'Refinancing replaces your current loan with a new one, ideally at a lower rate. To qualify, your account must be current, the vehicle must be under 100,000 miles, and the remaining balance must be at least $5,000.',
    docs: 'You will need: a valid government-issued ID, proof of income (recent pay stubs or tax returns), proof of residence, vehicle title or purchase agreement, and insurance information.',
  }

  const q = question.toLowerCase()
  if (q.includes('apr') || q.includes('rate') || q.includes('credit score')) return responses.apr
  if (q.includes('down')) return responses.down
  if (q.includes('late') || q.includes('fee') || q.includes('penalty')) return responses.fee
  if (q.includes('early') || q.includes('pay off') || q.includes('payoff')) return responses.early
  if (q.includes('gap')) return responses.gap
  if (q.includes('refinanc') || q.includes('refi')) return responses.refi
  if (q.includes('document') || q.includes('need to') || q.includes('require')) return responses.docs

  return `Thank you for your question about "${question}". Based on the automotive finance documents, I can confirm that our lending policies are designed to be transparent and competitive. For the most accurate answer to your specific situation, I recommend reviewing your loan agreement or speaking with one of our finance specialists. Is there anything else I can help clarify?`
}

export default function ChatPage({ onLogout }) {
  const [messages, setMessages]     = useState([])
  const [input, setInput]           = useState('')
  const [isLoading, setIsLoading]   = useState(false)
  const [conversations, setConversations] = useState([])
  const messagesEndRef = useRef(null)
  const inputRef       = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  async function sendMessage(text) {
    const question = text.trim()
    if (!question || isLoading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question, id: Date.now() }])
    setIsLoading(true)

    try {
      // Swap mockApiCall for a real API call:
      // const res  = await fetch('/api/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ question, history: messages }) })
      // const data = await res.json()
      // const answer = data.answer
      const answer = await mockApiCall(question, messages)
      setMessages(prev => [...prev, { role: 'assistant', content: answer, id: Date.now() + 1 }])
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.', id: Date.now() + 1 },
      ])
    } finally {
      setIsLoading(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  function startNewChat() {
    if (messages.length > 0) {
      const title = messages.find(m => m.role === 'user')?.content.slice(0, 48) ?? 'Conversation'
      setConversations(prev => [{ title, messages }, ...prev].slice(0, 20))
    }
    setMessages([])
  }

  function loadConversation(conv) {
    setMessages(conv.messages)
  }

  return (
    <div className="flex h-full bg-surface-500">
      {/* ── Sidebar ── */}
      <aside className="flex w-64 flex-shrink-0 flex-col border-r border-surface-400 bg-surface-600">
        {/* Logo */}
        <div className="flex items-center gap-2.5 border-b border-surface-400 px-4 py-[18px]">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-brand-500 to-brand-400 text-[11px] font-bold text-white">
            DF
          </div>
          <span className="text-sm font-semibold text-[#ececec]">DriveFinance AI</span>
        </div>

        {/* New chat button */}
        <div className="p-3">
          <button
            onClick={startNewChat}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-[13px] text-surface-100/60 transition hover:bg-surface-400 hover:text-[#ececec]"
          >
            <svg className="h-4 w-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New conversation
          </button>
        </div>

        {/* Recent conversations */}
        {conversations.length > 0 && (
          <div className="px-3">
            <p className="mb-1.5 px-2 text-[10px] font-medium uppercase tracking-widest text-surface-300/50">
              Recent
            </p>
            {conversations.map((conv, i) => (
              <button
                key={i}
                onClick={() => loadConversation(conv)}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-[12px] text-surface-100/50 transition hover:bg-surface-400 hover:text-[#ececec]"
              >
                <span className="h-1 w-1 flex-shrink-0 rounded-full bg-surface-300/40" />
                <span className="truncate">{conv.title}</span>
              </button>
            ))}
          </div>
        )}

        {/* Topics */}
        <div className="mt-4 px-3">
          <p className="mb-1.5 px-2 text-[10px] font-medium uppercase tracking-widest text-surface-300/50">
            Topics
          </p>
          {TOPICS.map(t => (
            <div
              key={t}
              className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-[12px] text-surface-100/40"
            >
              <span className="h-1 w-1 flex-shrink-0 rounded-full bg-surface-300/30" />
              {t}
            </div>
          ))}
        </div>

        {/* Suggested questions */}
        <div className="mt-4 px-3">
          <p className="mb-1.5 px-2 text-[10px] font-medium uppercase tracking-widest text-surface-300/50">
            Common questions
          </p>
          {SUGGESTED.map(q => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-left text-[12px] text-surface-100/50 transition hover:bg-surface-400 hover:text-[#ececec]"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Bottom user row */}
        <div className="mt-auto border-t border-surface-400 p-3">
          <div className="flex items-center gap-2.5 rounded-lg px-2 py-2">
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-400 text-[11px] font-semibold text-white">
              U
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[13px] font-medium text-[#ececec]">My Account</p>
              <p className="text-[11px] text-surface-100/40">Finance Assistant</p>
            </div>
            <button
              onClick={onLogout}
              title="Sign out"
              className="text-surface-100/30 transition hover:text-surface-100/70"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h6a2 2 0 012 2v1" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main chat area ── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-surface-400 bg-surface-500 px-7 py-3.5">
          <div>
            <p className="text-[15px] font-semibold text-[#ececec]">Automotive Finance Assistant</p>
            <p className="text-[11px] text-surface-300/50">Powered by your finance documents</p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-brand-500/25 bg-brand-500/10 px-3 py-1.5 text-[11px] text-brand-400">
            <span className="h-[5px] w-[5px] animate-blink rounded-full bg-brand-500" />
            AI Online
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-[10%] py-10">
          {messages.length === 0 && !isLoading ? (
            <div className="flex h-full flex-col items-center justify-center text-center animate-fadein">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-400 text-lg font-bold text-white">
                DF
              </div>
              <h2 className="mb-2 text-xl font-semibold text-[#ececec]">How can I help you today?</h2>
              <p className="max-w-sm text-[14px] leading-relaxed text-surface-300/50">
                Ask about loan rates, down payments, fees,
                <br />
                refinancing, or any finance question.
              </p>

              {/* Quick-start chips */}
              <div className="mt-8 flex flex-wrap justify-center gap-2">
                {SUGGESTED.slice(0, 4).map(q => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="rounded-lg border border-surface-400 bg-surface-600 px-3.5 py-2 text-[13px] text-surface-100/60 transition hover:border-brand-500/40 hover:bg-surface-500 hover:text-[#ececec]"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {messages.map((msg, i) => (
                <MessageBubble key={msg.id} message={msg} isLast={i === messages.length - 1 && !isLoading} />
              ))}

              {/* Loading dots */}
              {isLoading && (
                <div className="flex items-start gap-3.5 py-3 animate-fadein">
                  <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-400 text-[11px] font-bold text-white">
                    DF
                  </div>
                  <div className="flex items-center gap-1.5 pt-2.5">
                    <span className="h-2 w-2 animate-tdot1 rounded-full bg-brand-500" />
                    <span className="h-2 w-2 animate-tdot2 rounded-full bg-brand-500" />
                    <span className="h-2 w-2 animate-tdot3 rounded-full bg-brand-500" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <p className="pb-1 text-center text-[11px] text-surface-300/20">
          Answers grounded in official finance documents · DriveFinance AI © 2025
        </p>

        {/* Input bar */}
        <div className="border-t border-surface-400 bg-surface-500 px-[10%] py-4">
          <div className="flex items-end gap-3 rounded-[13px] border border-surface-400 bg-surface-600 px-4 py-3 transition focus-within:border-brand-500/50 focus-within:ring-2 focus-within:ring-brand-500/10">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={e => {
                setInput(e.target.value)
                // Auto-grow
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
              }}
              onKeyDown={handleKeyDown}
              placeholder="Message DriveFinance AI…"
              className="flex-1 resize-none bg-transparent text-sm leading-relaxed text-[#ececec] placeholder-surface-300/30 outline-none"
              style={{ maxHeight: '160px', overflowY: 'auto' }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || isLoading}
              className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-brand-500 text-white transition hover:bg-brand-600 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <svg className="h-4 w-4 translate-x-[1px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-center text-[11px] text-surface-300/25">
            Press <kbd className="rounded bg-surface-400 px-1 text-[10px]">Enter</kbd> to send
            &nbsp;·&nbsp;
            <kbd className="rounded bg-surface-400 px-1 text-[10px]">Shift+Enter</kbd> for new line
          </p>
        </div>
      </div>
    </div>
  )
}
