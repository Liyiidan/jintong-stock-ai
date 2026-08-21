import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Capability, DataStatus, getCapabilities, isDemoMode } from '../api'

type HomeProps = {
  authenticated: boolean
}

const modules = [
  {
    title: '智能评审与排名',
    desc: '将新闻、行情、宏观、财务和基本面评分汇总为可解释排名。',
    image: '/picture/windows1.jpg',
    meta: '总分 / 分项 / 建议',
  },
  {
    title: '单股深度分析',
    desc: '保留五专家证据、冲突信号、投资动作、仓位和风险说明。',
    image: '/picture/windows2.jpg',
    meta: '证据 / 仓位 / 风险',
  },
  {
    title: '持仓与交易跟踪',
    desc: '记录交易、持仓、止损止盈和交易信号，形成持续跟踪链路。',
    image: '/picture/windows3.jpg',
    meta: '交易 / 持仓 / 信号',
  },
  {
    title: '宏观环境分析',
    desc: '按国内宏观、市场风格、行业轮动和外部扰动输出结构化结论。',
    image: '/picture/windows6.jpg',
    meta: '风格 / 轮动 / 风险',
  },
]

export default function Home({ authenticated }: HomeProps) {
  const [capabilities, setCapabilities] = useState<Capability[]>([])
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null)

  useEffect(() => {
    let cancelled = false
    getCapabilities()
      .then((result) => {
        if (!cancelled) {
          setCapabilities(result.capabilities || [])
          setDataStatus(result.data_status || null)
        }
      })
      .catch(() => {
        if (!cancelled) setCapabilities([])
      })
    return () => {
      cancelled = true
    }
  }, [])

  const visibleCapabilities = capabilities.filter((item) =>
    ['core', 'demo_data', 'market_data', 'fallback_analysis', 'llm'].includes(item.id)
  )

  function capabilityState(status: Capability['status']): string {
    if (status === 'ready') return '可用'
    if (status === 'optional') return '可选'
    if (status === 'not_configured') return '未配置'
    if (status === 'not_installed') return '未安装'
    if (status === 'warning') return '需处理'
    return '不可用'
  }

  return (
    <section className="home-page">
      <header className="home-top">
        <Link className="home-wordmark" to="/home" aria-label="金通科技首页">
          <span className="home-logo">JT</span>
          <span>金通科技</span>
        </Link>
        <div className="home-cta">
          <span className="home-system-state"><i /> 系统界面</span>
          <Link className="home-btn dark" to={authenticated ? '/discover' : '/login'}>
            {authenticated ? '进入工作台' : '登录系统'}
          </Link>
        </div>
      </header>

      <div className="home-hero">
        <div className="home-hero-copy">
          <span className="eyebrow">LLM + MoE 多专家决策融合</span>
          <h1>金通科技</h1>
          <p>面向 A 股研究的多源数据分析与投资决策工作台。</p>
          <div className="hero-actions">
            <Link className="home-btn primary" to={authenticated ? '/discover' : '/login'}>
              {authenticated ? '查看最新评审' : '开始使用'}
            </Link>
            <a className="home-btn subtle" href="#modules">查看模块</a>
          </div>
        </div>
        <div className="hero-data-strip" aria-label="系统决策结构">
          <span><strong>5</strong>专家信号</span>
          <span><strong>2</strong>驱动维度</span>
          <span><strong>1</strong>融合决策</span>
        </div>
      </div>

      <section className="home-facts" aria-label="系统能力">
        <div><strong>可解释</strong><span>保留评分与证据</span></div>
        <div><strong>个性化</strong><span>结合投资者风险画像</span></div>
        <div><strong>全链路</strong><span>从选股到持仓跟踪</span></div>
      </section>

      {visibleCapabilities.length > 0 && (
        <section className="capability-panel" aria-label="当前运行能力">
          <div className="section-heading compact-heading">
            <span className="eyebrow">运行状态</span>
            <h2>{isDemoMode ? '演示环境' : '当前环境能力'}</h2>
          </div>
          <div className="capability-grid">
            {visibleCapabilities.map((item) => (
              <article className="capability-item" key={item.id}>
                <div className="capability-item-head">
                  <strong>{item.label}</strong>
                  <span className={`capability-state ${item.status}`}>{capabilityState(item.status)}</span>
                </div>
                <p>{item.message}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {dataStatus && (
        <section className="capability-panel data-status-panel" aria-label="数据状态">
          <div className="section-heading compact-heading">
            <span className="eyebrow">数据可追溯性</span>
            <h2>{dataStatus.mode === 'demo' ? '演示数据状态' : '真实数据状态'}</h2>
          </div>
          <div className="capability-grid">
            {dataStatus.datasets.map((dataset) => (
              <article className="capability-item" key={dataset.id}>
                <div className="capability-item-head">
                  <strong>{dataset.label}</strong>
                  <span className={`capability-state ${dataset.status === 'available' ? 'ready' : 'not_configured'}`}>
                    {dataset.status === 'available' ? '有记录' : '暂无记录'}
                  </span>
                </div>
                <p>
                  {dataset.row_count} 条 · 来源 {dataset.source} · 最后更新{' '}
                  {dataset.updated_at ? new Date(dataset.updated_at).toLocaleString() : '暂无'}
                </p>
              </article>
            ))}
          </div>
          {dataStatus.last_sync.status !== 'never' && (
            <p className="row-sub">
              最近同步：{dataStatus.last_sync.status}
              {dataStatus.last_sync.error_message ? `，${dataStatus.last_sync.error_message}` : ''}
            </p>
          )}
        </section>
      )}

      <section className="home-modules" id="modules">
        <div className="section-heading">
          <span className="eyebrow">核心能力</span>
          <h2>系统核心模块</h2>
        </div>
        <div className="module-list">
          {modules.map((item, index) => (
            <article className="module-row" key={item.title}>
              <span className="module-index">0{index + 1}</span>
              <div className="module-thumb"><img src={item.image} alt="" /></div>
              <div className="module-copy">
                <h3>{item.title}</h3>
                <p>{item.desc}</p>
              </div>
              <span className="module-meta">{item.meta}</span>
            </article>
          ))}
        </div>
      </section>

      <footer className="home-footer">
        <span>本系统仅供学术交流与科研使用，不构成投资建议。</span>
        <span>JinTong Technology</span>
      </footer>
    </section>
  )
}
