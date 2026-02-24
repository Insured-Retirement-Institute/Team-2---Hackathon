import os
from typing import TypeVar

import httpx
from pydantic import BaseModel, Field

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
    Person,
    Company,
    Trust,
    Estate,
    Charity,
    Persona,
    Policy,
    Product,
    QuoteIllustrationBase,
    Requirement,
    Rider,
    User,
)

T = TypeVar("T", bound=BaseModel)

Contact = Person | Company | Trust | Estate | Charity
Quote = QuoteIllustrationBase
Profile = Person | Company
Role = Person | Company


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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def authenticate(self) -> str:
        async with httpx.AsyncClient() as auth_client:
            response = await auth_client.post(
                self._config.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                    "scope": self._config.scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        response.raise_for_status()
        data = response.json()
        self._access_token = data["access_token"]
        return self._access_token

    @property
    def access_token(self) -> str | None:
        return self._access_token

    def _headers(self, user_id: str | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self._access_token}"}
        if user_id:
            headers["UserID"] = user_id
        return headers

    async def _get(
        self,
        path: str,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[dict]:
        params = {}
        if persona:
            params["persona"] = persona.value
        if keycard:
            params["keycard"] = keycard
        response = await self._client.get(
            path,
            headers=self._headers(user_id),
            params=params if params else None,
        )
        response.raise_for_status()
        return response.json()

    async def get_applications(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Application]:
        data = await self._get("/puddle/applications", user_id, persona, keycard)
        return [Application(**item) for item in data]

    async def get_cases(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Case]:
        data = await self._get("/puddle/cases", user_id, persona, keycard)
        return [Case(**item) for item in data]

    async def get_commissions(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Commission]:
        data = await self._get("/puddle/commissions", user_id, persona, keycard)
        return [Commission(**item) for item in data]

    async def get_commission_statements(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[CommissionStatement]:
        data = await self._get("/puddle/commissionStatements", user_id, persona, keycard)
        return [CommissionStatement(**item) for item in data]

    async def get_contacts(
        self,
        user_id: str | None = None,
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Contact]:
        data = await self._get("/puddle/contacts", user_id, persona, keycard)
        return [_parse_contact(item) for item in data]

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
        persona: Persona | None = None,
        keycard: str | None = None,
    ) -> list[Policy]:
        data = await self._get("/puddle/policies", user_id, persona, keycard)
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
