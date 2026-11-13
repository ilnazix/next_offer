interface HeaderProps {
  clientId: number
  clientName?: string | null
}

export function Header({ clientId, clientName }: HeaderProps) {
  return (
    <header className="no-header">
      <div className="no-header__left">
        <div className="no-logo">next_offer</div>
        <input
          className="no-search"
          type="text"
          placeholder="Поиск по продуктам..."
          aria-label="Поиск по продуктам"
        />
      </div>
      <div className="no-header__right">
        <span className="no-client-label">
          {clientName ?? `Клиент #${clientId}`}
        </span>
        <div className="no-avatar" aria-hidden="true">
          К
        </div>
      </div>
    </header>
  )
}
