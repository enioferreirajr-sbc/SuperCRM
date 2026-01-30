from __future__ import annotations

from typing import Iterable

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_recipient import CustomerRecipient


def insert_customers(session: Session, customers: dict[int, dict]) -> int:
    if not customers:
        return 0
    customer_ids = list(customers.keys())
    existing = set(
        session.execute(
            sa.select(Customer.main_contract_id).where(
                Customer.main_contract_id.in_(customer_ids)
            )
        )
        .scalars()
        .all()
    )
    inserted = 0
    for customer_id, data in customers.items():
        if customer_id in existing:
            continue
        session.add(
            Customer(
                main_contract_id=data["main_contract_id"],
                customer_reference=data.get("customer_reference"),
            )
        )
        inserted += 1
    return inserted


def insert_customer_recipients(
    session: Session, recipients: dict[tuple[int, str], dict]
) -> int:
    if not recipients:
        return 0

    keys = list(recipients.keys())
    incoming_rows = [
        sa.select(
            sa.literal(key[0]).label("main_contract_id"),
            sa.literal(key[1]).label("recipient_email"),
        )
        for key in keys
    ]
    if len(incoming_rows) == 1:
        incoming = incoming_rows[0].subquery()
    else:
        incoming = sa.union_all(*incoming_rows).subquery()

    existing = set(
        session.execute(
            sa.select(
                CustomerRecipient.main_contract_id,
                CustomerRecipient.recipient_email,
            ).select_from(
                CustomerRecipient.__table__.join(
                    incoming,
                    sa.and_(
                        CustomerRecipient.main_contract_id == incoming.c.main_contract_id,
                        CustomerRecipient.recipient_email == incoming.c.recipient_email,
                    ),
                )
            )
        ).all()
    )

    inserted = 0
    for key, data in recipients.items():
        if key in existing:
            continue
        session.add(
            CustomerRecipient(
                main_contract_id=data["main_contract_id"],
                recipient_email=data["recipient_email"],
                recipient_name=data.get("recipient_name"),
                cellphone=data.get("cellphone"),
            )
        )
        inserted += 1
    return inserted


def insert_named_values(
    session: Session,
    model: type,
    field_name: str,
    values: Iterable[str],
) -> int:
    values_set = {value for value in values if value is not None and str(value).strip()}
    if not values_set:
        return 0
    field = getattr(model, field_name)
    existing = set(
        session.execute(sa.select(field).where(field.in_(values_set))).scalars().all()
    )
    inserted = 0
    for value in values_set:
        if value in existing:
            continue
        session.add(model(**{field_name: value}))
        inserted += 1
    return inserted
