from __future__ import annotations

from typing import Any

import sqlalchemy as sa

from app.core.import_context import ImportContext
from app.importer.utils.normalization import is_empty
from app.models.customer import Customer
from app.models.customer_recipient import CustomerRecipient
from app.models.owner import Owner
from app.models.product import Product
from app.models.proposal_type import ProposalType
from app.models.team import Team


def _normalize_text(value: Any) -> str | None:
    if is_empty(value):
        return None
    text = str(value).strip()
    return text or None


def get_or_create_customer(
    ctx: ImportContext,
    main_contract_id: int | None,
    customer_reference: str | None = None,
) -> Customer | None:
    if is_empty(main_contract_id):
        return None
    contract_id = int(main_contract_id)
    if contract_id in ctx.customers:
        return ctx.customers[contract_id]

    customer = (
        ctx.session.execute(
            sa.select(Customer).distinct().where(Customer.main_contract_id == contract_id)
        )
        .scalars()
        .first()
    )
    if customer is None:
        customer = Customer(
            main_contract_id=contract_id,
            customer_reference=_normalize_text(customer_reference),
        )
        ctx.session.add(customer)

    ctx.customers[contract_id] = customer
    return customer


def get_or_create_customer_recipient(
    ctx: ImportContext,
    main_contract_id: int | None,
    recipient_email: str | None,
    recipient_name: str | None = None,
    cellphone: str | None = None,
) -> CustomerRecipient | None:
    if is_empty(main_contract_id) or is_empty(recipient_email):
        return None
    contract_id = int(main_contract_id)
    email = str(recipient_email).strip()
    if not email:
        return None

    key = (contract_id, email)
    if key in ctx.recipients:
        return ctx.recipients[key]

    recipient = (
        ctx.session.execute(
            sa.select(CustomerRecipient)
            .distinct()
            .where(
                CustomerRecipient.main_contract_id == contract_id,
                CustomerRecipient.recipient_email == email,
            )
        )
        .scalars()
        .first()
    )
    if recipient is None:
        name = _normalize_text(recipient_name)
        if name is None:
            return None
        recipient = CustomerRecipient(
            main_contract_id=contract_id,
            recipient_email=email,
            recipient_name=name,
            cellphone=_normalize_text(cellphone),
        )
        ctx.session.add(recipient)

    ctx.recipients[key] = recipient
    return recipient


def _get_or_create_named(
    ctx: ImportContext,
    cache: dict[str, Any],
    model: type,
    field_name: str,
    value: str | None,
):
    name = _normalize_text(value)
    if name is None:
        return None
    if name in cache:
        return cache[name]

    field = getattr(model, field_name)
    existing = (
        ctx.session.execute(sa.select(model).distinct().where(field == name))
        .scalars()
        .first()
    )
    if existing is None:
        existing = model(**{field_name: name})
        ctx.session.add(existing)

    cache[name] = existing
    return existing


def get_or_create_product(ctx: ImportContext, name: str | None) -> Product | None:
    return _get_or_create_named(ctx, ctx.products, Product, "product_name", name)


def get_or_create_proposal_type(ctx: ImportContext, name: str | None) -> ProposalType | None:
    return _get_or_create_named(ctx, ctx.proposal_types, ProposalType, "proposal_type_name", name)


def get_or_create_team(ctx: ImportContext, name: str | None) -> Team | None:
    return _get_or_create_named(ctx, ctx.teams, Team, "team_name", name)


def get_or_create_owner(ctx: ImportContext, name: str | None) -> Owner | None:
    return _get_or_create_named(ctx, ctx.owners, Owner, "owner_name", name)
