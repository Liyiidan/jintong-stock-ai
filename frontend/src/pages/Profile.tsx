import { useEffect, useMemo, useState } from 'react'
import { getProfile, getQuestionnaireTemplate, isDemoMode, updateProfile } from '../api'

type QuestionnaireTemplate = {
  required_order?: string[]
  questions?: Record<
    string,
    {
      title?: string
      type?: string
      min?: number
      options?: Record<string, string>
    }
  >
}

type QuestionnaireAnswers = {
  disposable_funds: number
  loss_aversion: string
  risk_comfort: string
  time_horizon: string
  financial_literacy: string
}

const defaultAnswers: QuestionnaireAnswers = {
  disposable_funds: 0,
  loss_aversion: '2',
  risk_comfort: '2',
  time_horizon: '2',
  financial_literacy: '2',
}

const riskLabels: Record<string, string> = { low: '低', medium: '中', high: '高' }
const styleLabels: Record<string, string> = { stable: '稳健', balanced: '均衡', aggressive: '进取' }
const personaLabels: Record<string, string> = {
  conservative: '保守型',
  balanced_growth: '均衡成长型',
  aggressive_growth: '进取成长型',
}

function formatMoney(value: unknown): string {
  const amount = Number(value)
  return Number.isFinite(amount) ? `¥${new Intl.NumberFormat('zh-CN').format(amount)}` : '-'
}

function formatPercent(value: unknown): string {
  const amount = Number(value)
  return Number.isFinite(amount) ? `${(amount * 100).toFixed(0)}%` : '-'
}

export default function Profile() {
  const [profile, setProfile] = useState<any>(null)
  const [template, setTemplate] = useState<QuestionnaireTemplate | null>(null)
  const [status, setStatus] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [currentPassword, setCurrentPassword] = useState<string>('')

  const [assets, setAssets] = useState<string>('0')
  const [income, setIncome] = useState<string>('0')
  const [riskLevel, setRiskLevel] = useState<string>('medium')
  const [horizon, setHorizon] = useState<string>('long')
  const [style, setStyle] = useState<string>('balanced')
  const [answers, setAnswers] = useState<QuestionnaireAnswers>(defaultAnswers)

  useEffect(() => {
    let cancelled = false

    async function init() {
      try {
        const [profileResp, templateResp] = await Promise.all([getProfile(), getQuestionnaireTemplate()])
        if (cancelled) return
        setProfile(profileResp)
        setTemplate(templateResp as QuestionnaireTemplate)

        const qa = (profileResp?.questionnaire_answers || {}) as Record<string, unknown>
        setAssets(String(profileResp?.assets ?? 0))
        setIncome(String(profileResp?.income ?? 0))
        setRiskLevel(profileResp?.risk_level || 'medium')
        setHorizon(profileResp?.investment_horizon || 'long')
        setStyle(profileResp?.style || 'balanced')
        setAnswers({
          disposable_funds: Number(qa.disposable_funds ?? profileResp?.disposable_funds ?? 0),
          loss_aversion: String(qa.loss_aversion ?? '2'),
          risk_comfort: String(qa.risk_comfort ?? '2'),
          time_horizon: String(qa.time_horizon ?? '2'),
          financial_literacy: String(qa.financial_literacy ?? '2'),
        })
      } catch (err: unknown) {
        if (cancelled) return
        setStatus((err as Error).message)
      }
    }

    void init()
    return () => {
      cancelled = true
    }
  }, [])

  const scoring = useMemo(() => profile?.questionnaire_answers?.scoring || null, [profile])

  function updateAnswer<K extends keyof QuestionnaireAnswers>(key: K, value: QuestionnaireAnswers[K]) {
    setAnswers((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setStatus('')
    if (!isDemoMode && !currentPassword.trim()) {
      setStatus('更新画像需要输入当前密码。')
      return
    }
    if (!Number.isFinite(answers.disposable_funds) || answers.disposable_funds <= 0) {
      setStatus('可支配资金必须大于 0。')
      return
    }

    setLoading(true)
    try {
      const payload = {
        assets: Number(assets || 0),
        income: Number(income || 0),
        risk_level: riskLevel,
        investment_horizon: horizon,
        style,
        questionnaire_answers: {
          disposable_funds: Number(answers.disposable_funds),
          loss_aversion: Number(answers.loss_aversion),
          risk_comfort: Number(answers.risk_comfort),
          time_horizon: Number(answers.time_horizon),
          financial_literacy: Number(answers.financial_literacy),
        },
        ...(!isDemoMode ? { current_password: currentPassword } : {}),
      }
      const updated = await updateProfile(payload)
      setProfile(updated)
      setCurrentPassword('')
      setStatus(isDemoMode ? '演示画像已在当前会话更新。' : '画像与问卷已更新。')
    } catch (err: unknown) {
      setStatus((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (!profile) {
    return <div className="paper">正在加载画像...</div>
  }

  const q = template?.questions || {}

  return (
    <section className="screen">
      <div className="paper">
        <div className="paper-header">
          <div>
            <h2>个人投资者画像</h2>
            <p>资金情况、风险承受能力与投资偏好。</p>
          </div>
          <div className="profile-tags">
            <span>{riskLabels[profile.risk_level] || profile.risk_level}风险</span>
            <span>{styleLabels[profile.style] || profile.style}风格</span>
            <span>{personaLabels[profile.persona] || profile.persona}</span>
          </div>
        </div>

        {isDemoMode && (
          <div className="demo-profile-note">当前为演示快照，修改仅保留在本次页面会话中。</div>
        )}

        <form onSubmit={handleSave} className="form-grid">
          {!isDemoMode && (
            <label>
              当前密码（保存必填）
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="请输入当前密码"
                required
              />
            </label>
          )}

          <label>
            总资产（人民币）
            <input type="number" min={0} value={assets} onChange={(e) => setAssets(e.target.value)} />
          </label>

          <label>
            年收入（人民币）
            <input type="number" min={0} value={income} onChange={(e) => setIncome(e.target.value)} />
          </label>

          <label>
            风险等级
            <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </label>

          <label>
            投资期限
            <select value={horizon} onChange={(e) => setHorizon(e.target.value)}>
              <option value="short">短期</option>
              <option value="medium">中期</option>
              <option value="long">长期</option>
            </select>
          </label>

          <label>
            投资风格
            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              <option value="stable">稳健</option>
              <option value="balanced">均衡</option>
              <option value="aggressive">进取</option>
            </select>
          </label>

          <div className="paper-header with-top-line profile-subtitle">
            <h3>风险问卷</h3>
          </div>

          <label>
            {q.disposable_funds?.title || '可支配资金（人民币）'}
            <input
              type="number"
              min={0}
              value={answers.disposable_funds}
              onChange={(e) => updateAnswer('disposable_funds', Number(e.target.value || 0))}
            />
          </label>

          <label>
            {q.loss_aversion?.title || '亏损厌恶'}
            <select value={answers.loss_aversion} onChange={(e) => updateAnswer('loss_aversion', e.target.value)}>
              {Object.entries(q.loss_aversion?.options || {}).map(([value, label]) => (
                <option key={value} value={value}>
                  {value} - {label}
                </option>
              ))}
            </select>
          </label>

          <label>
            {q.risk_comfort?.title || '风险承受偏好'}
            <select value={answers.risk_comfort} onChange={(e) => updateAnswer('risk_comfort', e.target.value)}>
              {Object.entries(q.risk_comfort?.options || {}).map(([value, label]) => (
                <option key={value} value={value}>
                  {value} - {label}
                </option>
              ))}
            </select>
          </label>

          <label>
            {q.time_horizon?.title || '投资期限'}
            <select value={answers.time_horizon} onChange={(e) => updateAnswer('time_horizon', e.target.value)}>
              {Object.entries(q.time_horizon?.options || {}).map(([value, label]) => (
                <option key={value} value={value}>
                  {value} - {label}
                </option>
              ))}
            </select>
          </label>

          <label>
            {q.financial_literacy?.title || '金融知识水平'}
            <select
              value={answers.financial_literacy}
              onChange={(e) => updateAnswer('financial_literacy', e.target.value)}
            >
              {Object.entries(q.financial_literacy?.options || {}).map(([value, label]) => (
                <option key={value} value={value}>
                  {value} - {label}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" className="btn solid" disabled={loading}>
            {loading ? '保存中...' : '保存画像'}
          </button>
        </form>

        {scoring && (
          <div className="profile-score-panel">
            <h3>问卷评分</h3>
            <div className="profile-score-grid">
              <div><span>风险敏感指数</span><strong>{scoring.risk_sensitivity_index}</strong></div>
              <div><span>资金分层</span><strong>{scoring.funds_bucket}</strong></div>
              <div><span>建议单笔预算</span><strong>{formatMoney(scoring.suggested_order_budget)}</strong></div>
              <div><span>风险预算</span><strong>{formatPercent(scoring.risk_budget)}</strong></div>
              <div><span>单票最大仓位</span><strong>{formatPercent(scoring.max_single_position)}</strong></div>
            </div>
          </div>
        )}

        {status && <div className="inline-status">{status}</div>}
      </div>
    </section>
  )
}
