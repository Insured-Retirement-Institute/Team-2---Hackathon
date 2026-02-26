from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends

from api.sureify_client import SureifyAuthConfig, SureifyClient
from api.sureify_models import (
    ClientProfile,
    PolicyData,
    ProductOption,
)

router = APIRouter(prefix="/passthrough", tags=["passthrough"])


async def get_sureify_client() -> AsyncGenerator[SureifyClient, None]:
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyClientDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/policy-data")
async def get_policy_data(client: SureifyClientDep) -> list[PolicyData]:
    return await client.get_policy_data()


@router.get("/suitability-data")
async def get_suitability_data(client: SureifyClientDep) -> list[dict]:
    return await client.get_suitability_data()


@router.get("/disclosure-items")
async def get_disclosure_items(client: SureifyClientDep) -> list[dict]:
    return await client.get_disclosure_items()


@router.get("/product-options")
async def get_product_options(client: SureifyClientDep) -> list[ProductOption]:
    return await client.get_product_options()


@router.get("/visualization-products")
async def get_visualization_products(client: SureifyClientDep) -> list[dict]:
    return await client.get_visualization_products()


@router.get("/client-profiles")
async def get_client_profiles(client: SureifyClientDep) -> list[ClientProfile]:
    return await client.get_client_profiles()
