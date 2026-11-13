from app.models import Account, BannerTemplate, Client, Product

SALARY_TITLE = "Сохраните зарплату под 8%"
SALARY_SUBTITLE = "Отложите часть на накопительный счёт с ежемесячной капитализацией"
SALARY_GRADIENT = "linear-gradient(135deg, #7c3aed 0%, #db2777 100%)"
SALARY_ICON = "💰"
SALARY_ACTION_TEXT = "Открыть счёт"

PURCHASE_TITLE = "Накопите на крупную покупку"
PURCHASE_SUBTITLE = "Откройте накопительный счёт для ремонта или отпуска"
PURCHASE_GRADIENT = "linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)"
PURCHASE_ICON = "🏠"
PURCHASE_ACTION_TEXT = "Открыть счёт"

DEPOSIT_VIEW_TITLE = "Специальная ставка по вкладу"
DEPOSIT_VIEW_SUBTITLE = "Только до конца месяца — вклад под 8,5% годовых"
DEPOSIT_VIEW_GRADIENT = "linear-gradient(135deg, #ea580c 0%, #f59e0b 100%)"
DEPOSIT_VIEW_ICON = "📈"
DEPOSIT_VIEW_ACTION_TEXT = "Открыть вклад"

HIGH_BALANCE_TITLE = "Перенесите остаток на накоп. счёт"
HIGH_BALANCE_SUBTITLE = "Ваш текущий остаток может приносить доход"
HIGH_BALANCE_GRADIENT = "linear-gradient(135deg, #059669 0%, #10b981 100%)"
HIGH_BALANCE_ICON = "💳"
HIGH_BALANCE_ACTION_TEXT = "Перевести средства"

BANNER_SEEDS = (
    {
        "type": "salary",
        "title": SALARY_TITLE,
        "subtitle": SALARY_SUBTITLE,
        "background_color": SALARY_GRADIENT,
        "icon": SALARY_ICON,
        "action_text": SALARY_ACTION_TEXT,
        "product_code": "savings_account",
    },
    {
        "type": "purchase",
        "title": PURCHASE_TITLE,
        "subtitle": PURCHASE_SUBTITLE,
        "background_color": PURCHASE_GRADIENT,
        "icon": PURCHASE_ICON,
        "action_text": PURCHASE_ACTION_TEXT,
        "product_code": "savings_account",
    },
    {
        "type": "deposit_view",
        "title": DEPOSIT_VIEW_TITLE,
        "subtitle": DEPOSIT_VIEW_SUBTITLE,
        "background_color": DEPOSIT_VIEW_GRADIENT,
        "icon": DEPOSIT_VIEW_ICON,
        "action_text": DEPOSIT_VIEW_ACTION_TEXT,
        "product_code": "term_deposit",
    },
    {
        "type": "high_balance",
        "title": HIGH_BALANCE_TITLE,
        "subtitle": HIGH_BALANCE_SUBTITLE,
        "background_color": HIGH_BALANCE_GRADIENT,
        "icon": HIGH_BALANCE_ICON,
        "action_text": HIGH_BALANCE_ACTION_TEXT,
        "product_code": "savings_account",
    },
)


def seed_demo_data(db):
    savings_product = Product(
        code="savings_account",
        name="Накопительный счёт",
        category="savings",
        description="Счёт с ежемесячной капитализацией процентов",
        annual_rate=8.00,
        min_amount=1000,
    )
    deposit_product = Product(
        code="term_deposit",
        name="Вклад «Доходный»",
        category="deposit",
        description="Срочный вклад с повышенной ставкой",
        annual_rate=8.50,
        min_amount=50000,
        term_months=6,
    )
    first_client = Client(
        external_id="demo-client-1",
        full_name="Иван Петров",
        segment="mass",
        has_savings_account=False,
        active_deposits_count=0,
    )
    second_client = Client(
        external_id="demo-client-2",
        full_name="Мария Смирнова",
        segment="mass",
        has_savings_account=False,
        active_deposits_count=0,
    )
    db.add_all([savings_product, deposit_product, first_client, second_client])
    db.flush()

    products_by_code = {
        savings_product.code: savings_product,
        deposit_product.code: deposit_product,
    }

    first_account = Account(
        client_id=first_client.id,
        account_type="current",
        balance=150000,
        currency="RUB",
    )
    second_account = Account(
        client_id=second_client.id,
        account_type="current",
        balance=310000,
        currency="RUB",
    )

    templates_by_type = {}
    for banner in BANNER_SEEDS:
        template = BannerTemplate(
            type=banner["type"],
            title=banner["title"],
            subtitle=banner["subtitle"],
            background_color=banner["background_color"],
            icon=banner["icon"],
            action_text=banner["action_text"],
            product_id=products_by_code[banner["product_code"]].id,
        )
        templates_by_type[banner["type"]] = template

    db.add_all([first_account, second_account, *templates_by_type.values()])
    db.commit()

    return {
        "client_id": first_client.id,
        "client_ids": [first_client.id, second_client.id],
        "clients": [
            {"id": first_client.id, "full_name": first_client.full_name},
            {"id": second_client.id, "full_name": second_client.full_name},
        ],
        "account_id": first_account.id,
        "product_id": savings_product.id,
        "product_ids": {
            code: product.id for code, product in products_by_code.items()
        },
        "banner_template_id": templates_by_type["salary"].id,
        "banner_template_ids": {
            banner_type: template.id
            for banner_type, template in templates_by_type.items()
        },
    }
