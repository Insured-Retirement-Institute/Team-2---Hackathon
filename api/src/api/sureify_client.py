import logging
import os

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from api.sureify_models import (
    ClientProfile,
    DisclosureItem,
    PolicyData,
    ProductOption,
    SuitabilityData,
    VisualizationProduct,
)


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class SureifyAuthConfig(BaseModel):
    base_url: str = Field(default_factory=lambda: _env("SUREIFY_BASE_URL", "https://hackathon-dev-api.sureify.com"))
    client_id: str = Field(default_factory=lambda: _env("SUREIFY_CLIENT_ID"))
    client_secret: str = Field(default_factory=lambda: _env("SUREIFY_CLIENT_SECRET"))
    token_url: str = Field(default_factory=lambda: _env("SUREIFY_TOKEN_URL", "https://hackathon-dev-sureify.auth.us-west-2.amazoncognito.com/oauth2/token"))
    scope: str = Field(default_factory=lambda: _env("SUREIFY_SCOPE", "hackathon-dev-EdgeApiM2M/edge"))


class SureifyClient:
    def __init__(self, config: SureifyAuthConfig) -> None:
        self._config = config
        self._access_token: str | None = None
        self._client = httpx.AsyncClient(base_url=config.base_url)

    async def __aenter__(self) -> "SureifyClient":
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def authenticate(self) -> str:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        logger.debug("POST %s (client_id=%s, scope=%s)", self._config.token_url, self._config.client_id, self._config.scope)
        logger.debug("AUTH request headers: %s", headers)
        async with httpx.AsyncClient() as auth_client:
            response = await auth_client.post(
                self._config.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                    "scope": self._config.scope,
                },
                headers=headers,
            )
        logger.debug("AUTH response: %d, headers: %s", response.status_code, dict(response.headers))
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        return self._access_token

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def _get(self, path: str, response_key: str) -> list[dict]:
        if not self._access_token:
            raise RuntimeError("SureifyClient not authenticated. Call authenticate() first or use as context manager.")
        url = f"{self._config.base_url}{path}"
        headers = self._headers()
        logger.debug("GET %s", url)
        logger.debug("GET request headers: %s", headers)
        response = await self._client.get(path, headers=headers)
        logger.debug("GET %s -> %d, response headers: %s", url, response.status_code, dict(response.headers))
        response.raise_for_status()
        return response.json()[response_key]

    async def get_policy_data(self) -> list[PolicyData]:
        data = await self._get("/puddle/policyData", "policyData")
        return [PolicyData(**item) for item in data]

    async def get_suitability_data(self) -> list[SuitabilityData]:
        data = await self._get("/puddle/suitabilityData", "suitabilityData")
        return [SuitabilityData(**item) for item in data]

    async def get_disclosure_items(self) -> list[DisclosureItem]:
        data = await self._get("/puddle/disclosureItem", "disclosureItems")
        return [DisclosureItem(**item) for item in data]

    async def get_product_options(self) -> list[ProductOption]:
        data = await self._get("/puddle/productOption", "productOptions")
        return [ProductOption(**item) for item in data]

    async def get_visualization_products(self) -> list[VisualizationProduct]:
        data = await self._get("/puddle/visualizationProduct", "visualizationProducts")
        return [VisualizationProduct(**item) for item in data]

    async def get_client_profiles(self) -> list[ClientProfile]:
        data = await self._get("/puddle/clientProfile", "clientProfiles")
        return [ClientProfile(**item) for item in data]
