import { NavLink } from 'react-router-dom'
import { getCapabilities, isDemoMode } from '../api'
import { useEffect, useState } from 'react'

type HeaderProps = {
  onLogout: () => void
}

export default function Header({ onLogout }: HeaderProps) {
  const [dataMode, setDataMode] = useState<'real' | 'demo' | null>(null)
  const [hasSeedData, setHasSeedData] = useState(false)

  useEffect(() => {
    if (isDemoMode) return
    getCapabilities()
      .then((result) => {
        setDataMode((result.mode as 'real' | 'demo') || null)
        setHasSeedData((result.capabilities || []).some((item) => item.id === 'demo_data' && item.status === 'warning'))
      })
      .catch(() => setHasSeedData(false))
  }, [])

  const navItems = [
    { to: '/discover', label: '选股评审', short: '评' },
    { to: '/track', label: '持仓跟踪', short: '持' },
    { to: '/query', label: '单股分析', short: '析' },
    { to: '/macro', label: '宏观分析', short: '宏' },
    { to: '/profile', label: '投资者画像', short: '像' },
  ]

  return (
    <header className="header">
      <div className="brand">
        <span className="brand-mark">JT</span>
        <div>
          <div className="brand-title">金通科技</div>
          <div className="brand-subtitle">AI 投资决策系统</div>
        </div>
      </div>
      <nav className="segment-nav" aria-label="主导航">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => `segment-link ${isActive ? 'active' : ''}`}>
            <span className="nav-glyph" aria-hidden="true">{item.short}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="nav-footer">
        {isDemoMode && <span className="demo-badge">界面演示模式</span>}
        {!isDemoMode && dataMode === 'real' && hasSeedData && <span className="demo-badge">样例数据需清理</span>}
        <button className="nav-action" onClick={onLogout} type="button">退出登录</button>
      </div>
    </header>
  )
}
