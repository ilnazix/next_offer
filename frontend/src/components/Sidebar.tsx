const NAV_ITEMS = [
  'Главная',
  'Счета и карты',
  'Переводы',
  'История',
  'Предложения',
  'Настройки',
]

export function Sidebar() {
  return (
    <nav className="no-sidebar" aria-label="Основная навигация">
      {NAV_ITEMS.map((item) => (
        <div
          key={item}
          className={
            item === 'Главная'
              ? 'no-nav-item no-nav-item--active'
              : 'no-nav-item'
          }
        >
          {item}
        </div>
      ))}
    </nav>
  )
}
