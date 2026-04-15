import { useState, useEffect } from 'react'
import LoginPage from './components/LoginPage'
import ChatPage from './components/ChatPage'

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [visible, setVisible] = useState(false)

  // Trigger fade-in on mount
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 20)
    return () => clearTimeout(t)
  }, [isLoggedIn])

  function handleLogin(credentials) {
    // TODO: Replace with real auth call
    setVisible(false)
    setTimeout(() => {
      setIsLoggedIn(true)
    }, 300)
  }

  function handleLogout() {
    setVisible(false)
    setTimeout(() => {
      setIsLoggedIn(false)
    }, 300)
  }

  return (
    <div
      className="h-full transition-all duration-300"
      style={{ opacity: visible ? 1 : 0 }}
    >
      {isLoggedIn ? (
        <ChatPage onLogout={handleLogout} />
      ) : (
        <LoginPage onLogin={handleLogin} />
      )}
    </div>
  )
}
