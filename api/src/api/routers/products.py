"""
Products shelf endpoint - returns available products for comparison.
"""
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.sureify_client import SureifyClient, SureifyAuthConfig
from api.sureify_models import ProductOption

router = APIRouter(prefix="/products", tags=["Products"])


async def get_sureify_client() -> AsyncGenerator[SureifyClient, None]:
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/shelf", response_model=list[ProductOption])
async def get_product_shelf(
    sureify: SureifyDep,
    carrier: Annotated[str | None, Query()] = None,
):
    """
    Get product shelf - all available products for comparison.

    Used by the UI's Product Shelf modal in the Compare tab.
    Users can browse and select products to compare against current policy.
    """
    products = await sureify.get_product_options()

    if carrier:
        products = [
            p for p in products
            if p.carrier and carrier.lower() in p.carrier.lower()
        ]

    return products
