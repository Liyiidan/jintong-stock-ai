import { useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import {
  AUTH_EXPIRED_EVENT,
  clearSession,
  getCurrentUser,
  getToken,
  isDemoMode,
  setUserId,
} from './api'
import Discover from './pages/Discover'
import Home from './pages/Home'
import Login from './pages/Login'
import MacroStandalone from './pages/MacroStandalone'
import Profile from './pages/Profile'
import QueryStocks from './pages/QueryStocks'
import StockDetail from './pages/StockDetail'
import TrackStocks from './pages/TrackStocks'

export default function App() {
  const [ready, setReady] = useState(false)
  const [authenticated, setAuthenticated] = useState(false)
  const [status, setStatus] = useState('')
  const location = useLocation()

  useEffect(() => {
    async function init() {
      if (isDemoMode) {
        setUserId('1')
        setAuthenticated(true)
        setReady(true)
        return
      }
      const token = getToken()
      if (!token) {
        setAuthenticated(false)
        setReady(true)
        return
      }

      try {
        const me = await getCurrentUser()
        setUserId(String(me.id))
        setAuthenticated(true)
      } catch {
        clearSession()
        setAuthenticated(false)
      } finally {
        setReady(true)
      }
    }

    init()
  }, [])

  useEffect(() => {
    function handleExpiredSession() {
      clearSession()
      setAuthenticated(false)
      setStatus('登录已过期，请重新登录。')
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleExpiredSession)
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleExpiredSession)
  }, [])

  const showHeader = useMemo(() => {
    if (!authenticated) {
      return false
    }
    return ['/discover', '/track', '/query', '/stock', '/profile', '/macro'].some((path) =>
      location.pathname.startsWith(path)
    )
  }, [authenticated, location.pathname])

  function handleLoginSuccess(userId: string) {
    setUserId(userId)
    setAuthenticated(true)
    setStatus('')
  }

  function handleLogout() {
    clearSession()
    setAuthenticated(false)
    setStatus('')
  }

  if (!ready) {
    return <div className="boot-screen">正在初始化会话...</div>
  }

  return (
    <div className={`app ${showHeader ? 'app-shell' : ''}`}>
      {showHeader && <Header onLogout={handleLogout} />}
      {status && <div className="global-status">{status}</div>}
      <main className="main-stage">
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<Home authenticated={authenticated} />} />
          <Route
            path="/login"
            element={
              authenticated ? (
                <Navigate to="/discover" replace />
              ) : (
                <Login onLoginSuccess={handleLoginSuccess} onStatus={setStatus} />
              )
            }
          />

          <Route
            path="/discover"
            element={authenticated ? <Discover /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/track"
            element={authenticated ? <TrackStocks /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/query"
            element={authenticated ? <QueryStocks /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/macro"
            element={authenticated ? <MacroStandalone /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/profile"
            element={authenticated ? <Profile /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/stock/:symbol"
            element={authenticated ? <StockDetail /> : <Navigate to="/login" replace />}
          />

          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </main>
    </div>
  )
}
