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
    base_url: str = Field(
        default_factory=lambda: _env(
            "SUREIFY_BASE_URL", "https://hackathon-dev-api.sureify.com"
        )
    )
    client_id: str = Field(default_factory=lambda: _env("SUREIFY_CLIENT_ID"))
    client_secret: str = Field(default_factory=lambda: _env("SUREIFY_CLIENT_SECRET"))
    token_url: str = Field(
        default_factory=lambda: _env(
            "SUREIFY_TOKEN_URL",
            "https://hackathon-dev-sureify.auth.us-west-2.amazoncognito.com/oauth2/token",
        )
    )
    scope: str = Field(
        default_factory=lambda: _env("SUREIFY_SCOPE", "hackathon-dev-EdgeApiM2M/edge")
    )
    bearer_token: str = Field(default_factory=lambda: _env("SUREIFY_BEARER_TOKEN"))


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
        if self._config.bearer_token:
            self._access_token = self._config.bearer_token.strip()
            return self._access_token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        logger.debug(
            "POST %s (client_id=%s, scope=%s)",
            self._config.token_url,
            self._config.client_id,
            self._config.scope,
        )
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
        logger.debug(
            "AUTH response: %d, headers: %s",
            response.status_code,
            dict(response.headers),
        )
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        return self._access_token

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}", "UserID": "1001"}

    async def _get(self, path: str, response_key: str) -> list[dict]:
        if not self._access_token:
            raise RuntimeError(
                "SureifyClient not authenticated. Call authenticate() first or use as context manager."
            )
        url = f"{self._config.base_url}{path}"
        headers = self._headers()
        logger.debug("GET %s", url)
        logger.debug("GET request headers: %s", headers)
        response = await self._client.get(path, headers=headers)
        logger.debug(
            "GET %s -> %d, response headers: %s",
            url,
            response.status_code,
            dict(response.headers),
        )
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

    async def get_documents(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Document]:
        data = await self._get("/puddle/documents", user_id, persona, keycard)
        return [Document(**item) for item in data]

    async def get_document_by_id(
        self,
        document_id: str,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> bytes:
        params = {}
        if persona:
            params["persona"] = persona.value
        if keycard:
            params["keycard"] = keycard
        response = await self._client.get(
            f"/puddle/documents/{document_id}",
            headers=self._headers(user_id),
            params=params if params else None,
        )
        response.raise_for_status()
        return response.content

    async def get_financial_activities(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[FinancialActivity]:
        data = await self._get("/puddle/financialActivities", user_id, persona, keycard)
        return [FinancialActivity(**item) for item in data]

    async def get_fund_allocations(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[FundAllocation]:
        data = await self._get("/puddle/fundAllocations", user_id, persona, keycard)
        return [FundAllocation(**item) for item in data]

    async def get_keycards(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Keycard]:
        data = await self._get("/puddle/keycards", user_id, persona, keycard)
        return [Keycard(**item) for item in data]

    async def get_notes(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Note]:
        data = await self._get("/puddle/notes", user_id, persona, keycard)
        return [Note(**item) for item in data]

    async def get_payment_methods(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[dict]:
        return await self._get("/puddle/paymentMethods", user_id, persona, keycard)

    async def get_policies(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[Policy] | list[dict]:
        """GET /puddle/policyData. Puddle Data API requires persona=agent and UserID header."""
        data = await self._get("/puddle/policyData", user_id, persona, keycard)
        if isinstance(data, dict) and "policyData" in data:
            return data["policyData"]
        return [Policy(**item) for item in data]

    async def get_products(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Product]:
        data = await self._get("/puddle/products", user_id, persona, keycard)
        return [Product(**item) for item in data]

    async def get_qualifications(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[dict]:
        return await self._get("/puddle/qualifications", user_id, persona, keycard)

    async def get_quotes(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Quote]:
        data = await self._get("/puddle/quotes", user_id, persona, keycard)
        return [QuoteIllustrationBase(**item) for item in data]

    async def get_requirements(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Requirement]:
        data = await self._get("/puddle/requirements", user_id, persona, keycard)
        return [Requirement(**item) for item in data]

    async def get_riders(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Rider]:
        data = await self._get("/puddle/riders", user_id, persona, keycard)
        return [Rider(**item) for item in data]

    async def get_roles(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[dict]:
        return await self._get("/puddle/roles", user_id, persona, keycard)

    async def get_profiles(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[dict]:
        return await self._get("/puddle/profiles", user_id, persona, keycard)

    async def get_users(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[User]:
        data = await self._get("/puddle/users", user_id, persona, keycard)
        return [User(**item) for item in data]

    # --- Puddle Data API (OpenAPI 1.0.0: suitabilityData, disclosureItem, productOption, visualizationProduct, clientProfile) ---

    async def get_suitability_data(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[dict]:
        data = await self._get("/puddle/suitabilityData", user_id, persona, keycard)
        if isinstance(data, dict) and "suitabilityData" in data:
            return data["suitabilityData"]
        return data if isinstance(data, list) else []

    async def get_disclosure_items(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[dict]:
        data = await self._get("/puddle/disclosureItem", user_id, persona, keycard)
        if isinstance(data, dict) and "disclosureItems" in data:
            return data["disclosureItems"]
        return data if isinstance(data, list) else []

    async def get_product_options(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[dict]:
        data = await self._get("/puddle/productOption", user_id, persona, keycard)
        if isinstance(data, dict) and "productOptions" in data:
            return data["productOptions"]
        return data if isinstance(data, list) else []

    async def get_visualization_products(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[dict]:
        data = await self._get("/puddle/visualizationProduct", user_id, persona, keycard)
        if isinstance(data, dict) and "visualizationProducts" in data:
            return data["visualizationProducts"]
        return data if isinstance(data, list) else []

    async def get_client_profiles(
        self,
        user_id: str | None = None,
        persona: Persona | None = Persona.agent,
        keycard: str | None = None,
    ) -> list[dict]:
        data = await self._get("/puddle/clientProfile", user_id, persona, keycard)
        if isinstance(data, dict) and "clientProfiles" in data:
            return data["clientProfiles"]
        return data if isinstance(data, list) else []


def _parse_contact(data: dict) -> Contact:
    contact_type = data.get("type") or data.get("contactType")
    if contact_type == "Person":
        return Person(**data)
    if contact_type == "Company":
        return Company(**data)
    if contact_type == "Trust":
        return Trust(**data)
    if contact_type == "Estate":
        return Estate(**data)
    if contact_type == "Charity":
        return Charity(**data)
    return Person(**data)


def get_applications(client: SureifyClient, **kwargs) -> list[Application]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_applications(**kwargs))


def get_cases(client: SureifyClient, **kwargs) -> list[Case]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_cases(**kwargs))


def get_commissions(client: SureifyClient, **kwargs) -> list[Commission]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_commissions(**kwargs))


def get_commission_statements(client: SureifyClient, **kwargs) -> list[CommissionStatement]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_commission_statements(**kwargs))


def get_contacts(client: SureifyClient, **kwargs) -> list[Contact]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_contacts(**kwargs))


def get_documents(client: SureifyClient, **kwargs) -> list[Document]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_documents(**kwargs))


def get_document_by_id(client: SureifyClient, document_id: str, **kwargs) -> bytes:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(
        client.get_document_by_id(document_id, **kwargs)
    )


def get_financial_activities(client: SureifyClient, **kwargs) -> list[FinancialActivity]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_financial_activities(**kwargs))


def get_fund_allocations(client: SureifyClient, **kwargs) -> list[FundAllocation]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_fund_allocations(**kwargs))


def get_keycards(client: SureifyClient, **kwargs) -> list[Keycard]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_keycards(**kwargs))


def get_notes(client: SureifyClient, **kwargs) -> list[Note]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_notes(**kwargs))


def get_payment_methods(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_payment_methods(**kwargs))


def get_policies(client: SureifyClient, **kwargs) -> list[Policy]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_policies(**kwargs))


def get_products(client: SureifyClient, **kwargs) -> list[Product]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_products(**kwargs))


def get_qualifications(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_qualifications(**kwargs))


def get_quotes(client: SureifyClient, **kwargs) -> list[Quote]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_quotes(**kwargs))


def get_requirements(client: SureifyClient, **kwargs) -> list[Requirement]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_requirements(**kwargs))


def get_riders(client: SureifyClient, **kwargs) -> list[Rider]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_riders(**kwargs))


def get_roles(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_roles(**kwargs))


def get_profiles(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_profiles(**kwargs))


def get_users(client: SureifyClient, **kwargs) -> list[User]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_users(**kwargs))


def get_suitability_data(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_suitability_data(**kwargs))


def get_disclosure_items(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_disclosure_items(**kwargs))


def get_product_options(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_product_options(**kwargs))


def get_visualization_products(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_visualization_products(**kwargs))


def get_client_profiles(client: SureifyClient, **kwargs) -> list[dict]:
    import asyncio
    return asyncio.get_event_loop().run_until_complete(client.get_client_profiles(**kwargs))
