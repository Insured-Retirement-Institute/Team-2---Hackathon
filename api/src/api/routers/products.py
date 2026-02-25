"""
Products shelf endpoint - returns available products for comparison.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from api.sureify_client import SureifyClient, SureifyAuthConfig, Product, Persona

router = APIRouter(prefix="/api/products", tags=["Products"])


class ProductShelfItem(BaseModel):
    """Product item for the product shelf"""
    id: str
    name: str
    productCode: str | None = None
    carrier: str | None = None
    type: str | None = None


async def get_sureify_client():
    """Dependency to get authenticated Sureify client"""
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/shelf", response_model=list[Product])
async def get_product_shelf(
    sureify: SureifyDep,
    carrier: Annotated[str | None, Query()] = None,
    product_type: Annotated[str | None, Query(alias="type")] = None,
):
    """
    Get product shelf - all available products for comparison.

    Used by the UI's Product Shelf modal in the Compare tab.
    Users can browse and select products to compare against current policy.
    """
    # Fetch all products from Sureify
    products = await sureify.get_products(
        user_id="1003",  # Use default user for product catalog
        persona=Persona.agent
    )

    # Apply filters if provided
    filtered_products = products

    if carrier:
        filtered_products = [
            p for p in filtered_products
            if p.carrierCode and carrier.lower() in str(p.carrierCode).lower()
        ]

    if product_type:
        filtered_products = [
            p for p in filtered_products
            if p.productType and product_type.lower() in str(p.productType).lower()
        ]

    return filtered_products
