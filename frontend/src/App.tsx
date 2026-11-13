import { BannerCarousel } from './components/BannerCarousel'
import { Header } from './components/Header'
import { RightPanel } from './components/RightPanel'
import { Sidebar } from './components/Sidebar'
import { config } from './config'
import { useClientOffers } from './hooks/useClientOffers'

export default function App() {
  const { offers, status, error } = useClientOffers(config.clientId)
  const initialLoading = status === 'loading' && offers.length === 0
  const pollLabel = error
    ? 'Нет связи с API'
    : `Обновляется каждые ${Math.round(config.pollingIntervalMs / 1000)} секунды`

  return (
    <>
      <Header clientId={config.clientId} />

      <div className="no-layout">
        <Sidebar />

        <main className="no-main">
          <section>
            <div className="no-section-header">
              <h2 className="no-section-title">Персональные предложения</h2>
              <span
                className="no-poll-status"
                data-status={error ? 'error' : status}
                aria-live="polite"
              >
                {pollLabel}
              </span>
            </div>

            {error ? (
              <p className="no-alert" role="alert">
                Не удалось получить предложения ({error}). Повторяем попытки…
              </p>
            ) : null}

            {initialLoading ? (
              <p className="no-empty">Загрузка предложений…</p>
            ) : (
              <BannerCarousel offers={offers} />
            )}
          </section>

          <section>
            <h2 className="no-section-title">Мои финансы</h2>
            <div className="no-balance-grid">
              <div className="no-card">
                <h3 className="no-card__label">Остаток на счёте</h3>
                <div className="no-card__value">10 134,10 ₽</div>
              </div>
              <div className="no-card">
                <h3 className="no-card__label">Кешбэк и бонусы</h3>
                <div className="no-card__value">351 ₽</div>
              </div>
            </div>
          </section>
        </main>

        <RightPanel />
      </div>
    </>
  )
}
