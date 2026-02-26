from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from api.sureify_client import SureifyAuthConfig, SureifyClient
from api.sureify_models import (
    Application,
    Case,
    Commission,
    CommissionStatement,
    Document,
    FinancialActivity,
    FundAllocation,
    Keycard,
    Note,
    Persona,
    Person,
    Company,
    Trust,
    Estate,
    Charity,
    Policy,
    Product,
    QuoteIllustrationBase,
    Requirement,
    Rider,
    User,
)

router = APIRouter(prefix="/passthrough", tags=["passthrough"])

Contact = Person | Company | Trust | Estate | Charity
Quote = QuoteIllustrationBase


async def get_sureify_client() -> AsyncGenerator[SureifyClient, None]:
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyClientDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/applications")
async def get_applications(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Application]:
    return await client.get_applications(user_id, persona, keycard)


@router.get("/cases")
async def get_cases(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Case]:
    return await client.get_cases(user_id, persona, keycard)


@router.get("/commissions")
async def get_commissions(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Commission]:
    return await client.get_commissions(user_id, persona, keycard)


@router.get("/commission-statements")
async def get_commission_statements(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[CommissionStatement]:
    return await client.get_commission_statements(user_id, persona, keycard)


@router.get("/contacts")
async def get_contacts(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Contact]:
    return await client.get_contacts(user_id, persona, keycard)


@router.get("/documents")
async def get_documents(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Document]:
    return await client.get_documents(user_id, persona, keycard)


@router.get("/documents/{document_id}")
async def get_document_by_id(
    document_id: str,
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> Response:
    content = await client.get_document_by_id(document_id, user_id, persona, keycard)
    return Response(content=content, media_type="application/octet-stream")


@router.get("/financial-activities")
async def get_financial_activities(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[FinancialActivity]:
    return await client.get_financial_activities(user_id, persona, keycard)


@router.get("/fund-allocations")
async def get_fund_allocations(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[FundAllocation]:
    return await client.get_fund_allocations(user_id, persona, keycard)


@router.get("/keycards")
async def get_keycards(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Keycard]:
    return await client.get_keycards(user_id, persona, keycard)


@router.get("/notes")
async def get_notes(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Note]:
    return await client.get_notes(user_id, persona, keycard)


@router.get("/payment-methods")
async def get_payment_methods(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_payment_methods(user_id, persona, keycard)


@router.get("/policies")
async def get_policies(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Policy]:
    return await client.get_policies(user_id, persona, keycard)


@router.get("/products")
async def get_products(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Product]:
    return await client.get_products(user_id, persona, keycard)


@router.get("/qualifications")
async def get_qualifications(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_qualifications(user_id, persona, keycard)


@router.get("/quotes")
async def get_quotes(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Quote]:
    return await client.get_quotes(user_id, persona, keycard)


@router.get("/requirements")
async def get_requirements(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Requirement]:
    return await client.get_requirements(user_id, persona, keycard)


@router.get("/riders")
async def get_riders(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[Rider]:
    return await client.get_riders(user_id, persona, keycard)


@router.get("/roles")
async def get_roles(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_roles(user_id, persona, keycard)


@router.get("/profiles")
async def get_profiles(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_profiles(user_id, persona, keycard)


@router.get("/users")
async def get_users(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[User]:
    return await client.get_users(user_id, persona, keycard)


# --- Puddle Data API (suitabilityData, disclosureItem, productOption, visualizationProduct, clientProfile) ---


@router.get("/suitability-data")
async def get_suitability_data(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_suitability_data(user_id, persona, keycard)


@router.get("/disclosure-items")
async def get_disclosure_items(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_disclosure_items(user_id, persona, keycard)


@router.get("/product-options")
async def get_product_options(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_product_options(user_id, persona, keycard)


@router.get("/visualization-products")
async def get_visualization_products(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_visualization_products(user_id, persona, keycard)


@router.get("/client-profiles")
async def get_client_profiles(
    client: SureifyClientDep,
    user_id: Annotated[str | None, Query()] = None,
    persona: Annotated[Persona | None, Query()] = None,
    keycard: Annotated[str | None, Query()] = None,
) -> list[dict]:
    return await client.get_client_profiles(user_id, persona, keycard)
