import stripe
import os

stripe.api_key = os.getenv("STRIPE_API_KEY")

def create_stripe_price(payment):
    """Создает цену в страйпе."""

    amount = payment.amount

    return stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product_data={"name": "Course_purchase"},
    )

def create_stripe_session(price):
    """Создает сессию на оплату в страйпе."""

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")