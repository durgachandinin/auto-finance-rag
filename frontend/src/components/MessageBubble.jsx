export default function MessageBubble({ message, isLast }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className={`flex justify-end py-1.5 ${isLast ? 'animate-fadein' : ''}`}>
        <div className="flex max-w-[70%] items-end gap-2.5">
          <div className="rounded-[14px] rounded-br-[4px] bg-surface-400 px-4 py-2.5 text-sm leading-relaxed text-[#ececec]">
            {message.content}
          </div>
          <div className="mb-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-surface-300 to-surface-400 text-[11px] font-semibold text-[#ececec]">
            U
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex items-start gap-3.5 py-1.5 ${isLast ? 'animate-fadein' : ''}`}>
      {/* Avatar */}
      <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-brand-400 text-[11px] font-bold text-white">
        DF
      </div>

      {/* Body */}
      <div className="max-w-[75%] flex-1">
        <p className="mb-1.5 text-[12px] font-semibold text-[#ececec]">DriveFinance AI</p>
        <p className="text-sm leading-[1.75] text-[#d0d0e8]">{message.content}</p>
      </div>
    </div>
  )
}
