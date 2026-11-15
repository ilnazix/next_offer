from dataclasses import dataclass

from app.models import Account, BannerTemplate, Client, Product


@dataclass(frozen=True)
class BannerSeed:
    type: str
    title: str
    subtitle: str
    background_color: str
    icon: str
    action_text: str
    product_code: str


BANNER_SEEDS: tuple[BannerSeed, ...] = (
    BannerSeed(
        type="salary",
        title="Сохраните зарплату под 8%",
        subtitle="Отложите часть на накопительный счёт с ежемесячной капитализацией",
        background_color="linear-gradient(135deg, #7c3aed 0%, #db2777 100%)",
        icon="💰",
        action_text="Открыть счёт",
        product_code="savings_account",
    ),
    BannerSeed(
        type="purchase",
        title="Накопите на крупную покупку",
        subtitle="Откройте накопительный счёт для ремонта или отпуска",
        background_color="linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)",
        icon="🏠",
        action_text="Открыть счёт",
        product_code="savings_account",
    ),
    BannerSeed(
        type="deposit_view",
        title="Специальная ставка по вкладу",
        subtitle="Только до конца месяца — вклад под 8,5% годовых",
        background_color="linear-gradient(135deg, #ea580c 0%, #f59e0b 100%)",
        icon="📈",
        action_text="Открыть вклад",
        product_code="term_deposit",
    ),
    BannerSeed(
        type="high_balance",
        title="Перенесите остаток на накоп. счёт",
        subtitle="Ваш текущий остаток может приносить доход",
        background_color="linear-gradient(135deg, #059669 0%, #10b981 100%)",
        icon="💳",
        action_text="Перевести средства",
        product_code="savings_account",
    ),
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
            type=banner.type,
            title=banner.title,
            subtitle=banner.subtitle,
            background_color=banner.background_color,
            icon=banner.icon,
            action_text=banner.action_text,
            product_id=products_by_code[banner.product_code].id,
        )
        templates_by_type[banner.type] = template

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
