from sqlalchemy.orm import Session

from app.models import Order


def create_order(
    db: Session,
    user_id: int,
    customer_name: str,
    item: str,
    quantity: int,
    amount: int,
):
    order = Order(
        user_id=user_id,
        customer_name=customer_name,
        item=item,
        quantity=quantity,
        amount=amount,
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order