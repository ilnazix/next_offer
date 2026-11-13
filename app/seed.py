from app.models import Account, BannerTemplate, Client, Offer, Product

SALARY_TITLE = "Сохраните зарплату под 8%"
SALARY_SUBTITLE = "Отложите часть на накопительный счёт с ежемесячной капитализацией"
SALARY_GRADIENT = "linear-gradient(135deg, #7c3aed 0%, #db2777 100%)"
SALARY_ICON = "💰"
SALARY_ACTION_TEXT = "Открыть счёт"


def seed_demo_data(db):
    client = Client(
        external_id="demo-client-1",
        full_name="Иван Петров",
        segment="mass",
        has_savings_account=False,
        active_deposits_count=0,
    )
    product = Product(
        code="savings_account",
        name="Накопительный счёт",
        category="savings",
        description="Счёт с ежемесячной капитализацией процентов",
        annual_rate=8.00,
        min_amount=1000,
    )
    db.add_all([client, product])
    db.flush()

    account = Account(
        client_id=client.id,
        account_type="current",
        balance=150000,
        currency="RUB",
    )
    template = BannerTemplate(
        type="salary",
        title=SALARY_TITLE,
        subtitle=SALARY_SUBTITLE,
        background_color=SALARY_GRADIENT,
        icon=SALARY_ICON,
        action_text=SALARY_ACTION_TEXT,
        product_id=product.id,
    )
    db.add_all([account, template])
    db.commit()

    return {
        "client_id": client.id,
        "account_id": account.id,
        "product_id": product.id,
        "banner_template_id": template.id,
    }
