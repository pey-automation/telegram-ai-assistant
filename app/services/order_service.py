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


def get_orders(
    db: Session,
    user_id: int,
):
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .all()
    )


def get_order(
    db: Session,
    user_id: int,
    order_id: int,
):
    return (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .first()
    )