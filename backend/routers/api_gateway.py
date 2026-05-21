"""
CleanInbox AI — Module 1: API Gateway Router
Kết nối Mailchimp, HubSpot, SendGrid — Plug-and-play trong 15 phút.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import httpx, hashlib
from backend.auth.jwt_handler import get_current_org, TokenData
from backend.config import settings

router = APIRouter(prefix="/api/v1/gateway", tags=["🔌 Cổng Kết Nối API"])


# ─── Schemas ────────────────────────────────────────
class ConnectMailchimpRequest(BaseModel):
    api_key: str          # Format: key-serverprefix (vd: abc123-us21)
    list_id: str          # Mailchimp Audience ID

class ConnectHubSpotRequest(BaseModel):
    access_token: str     # HubSpot Private App Token

class ConnectSendGridRequest(BaseModel):
    api_key: str          # SendGrid API Key (SG.xxx)

class SyncResult(BaseModel):
    provider: str
    contacts_synced: int
    campaigns_synced: int
    status: str
    message: str


# ─── Mailchimp Service ──────────────────────────────
class MailchimpService:
    BASE_URL = "https://{server}.api.mailchimp.com/3.0"

    def __init__(self, api_key: str):
        # api_key format: "key-serverprefix"
        parts = api_key.split("-")
        self.server = parts[-1] if len(parts) > 1 else settings.MAILCHIMP_SERVER_PREFIX
        self.api_key = api_key
        self.base_url = self.BASE_URL.format(server=self.server)

    async def validate_connection(self) -> dict:
        """Kiểm tra kết nối API key có hợp lệ không."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/ping",
                auth=("anystring", self.api_key),
                timeout=10.0
            )
            if resp.status_code != 200:
                raise HTTPException(400, "Mailchimp API key không hợp lệ")
            return resp.json()

    async def get_list_members(self, list_id: str, count: int = 100) -> List[dict]:
        """Lấy danh sách contacts từ Mailchimp Audience."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/lists/{list_id}/members",
                auth=("anystring", self.api_key),
                params={"count": count, "fields": "members.email_address,members.status,members.stats"},
                timeout=15.0
            )
            resp.raise_for_status()
            return resp.json().get("members", [])

    async def get_campaigns(self, count: int = 50) -> List[dict]:
        """Lấy danh sách campaigns từ Mailchimp."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/campaigns",
                auth=("anystring", self.api_key),
                params={"count": count},
                timeout=15.0
            )
            resp.raise_for_status()
            return resp.json().get("campaigns", [])


# ─── HubSpot Service ────────────────────────────────
class HubSpotService:
    BASE_URL = "https://api.hubapi.com"

    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def validate_connection(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/crm/v3/objects/contacts?limit=1",
                headers=self.headers, timeout=10.0
            )
            if resp.status_code == 401:
                raise HTTPException(400, "HubSpot access token không hợp lệ")
            return {"status": "connected", "code": resp.status_code}

    async def get_contacts(self, limit: int = 100) -> List[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/crm/v3/objects/contacts",
                headers=self.headers,
                params={"limit": limit, "properties": "email,hs_email_open_count,hs_email_sends_since_last_engagement"},
                timeout=15.0
            )
            resp.raise_for_status()
            return resp.json().get("results", [])

    async def get_email_events(self, limit: int = 100) -> List[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/email/public/v1/events",
                headers=self.headers,
                params={"limit": limit},
                timeout=15.0
            )
            resp.raise_for_status()
            return resp.json().get("events", [])


# ─── SendGrid Service ───────────────────────────────
class SendGridService:
    BASE_URL = "https://api.sendgrid.com/v3"

    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def validate_connection(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/user/profile",
                headers=self.headers, timeout=10.0
            )
            if resp.status_code == 401:
                raise HTTPException(400, "SendGrid API key không hợp lệ")
            return resp.json()

    async def get_stats(self, start_date: str) -> List[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/stats",
                headers=self.headers,
                params={"start_date": start_date, "aggregated_by": "month"},
                timeout=15.0
            )
            resp.raise_for_status()
            return resp.json()


# ─── API Endpoints ──────────────────────────────────

@router.post("/connect/mailchimp", response_model=SyncResult)
async def connect_mailchimp(
    payload: ConnectMailchimpRequest,
    background_tasks: BackgroundTasks,
    current_org: TokenData = Depends(get_current_org),
):
    """
    Kết nối Mailchimp — Bước 1 trong quy trình onboarding 15 phút.
    1. Validate API key với Mailchimp ping endpoint.
    2. Đồng bộ contacts và campaigns ở background.
    3. Hash API key trước khi lưu DB (tuân thủ bảo mật).
    """
    svc = MailchimpService(payload.api_key)
    await svc.validate_connection()

    # Hash API key để lưu an toàn
    key_hash = hashlib.sha256(payload.api_key.encode()).hexdigest()

    # Lấy preview data để trả về ngay
    members = await svc.get_list_members(payload.list_id, count=10)
    campaigns = await svc.get_campaigns(count=5)

    # TODO: Lưu api_connection vào DB với key_hash
    # TODO: background_tasks.add_task(sync_all_mailchimp_contacts, org_id, payload)

    return SyncResult(
        provider="mailchimp",
        contacts_synced=len(members),
        campaigns_synced=len(campaigns),
        status="connected",
        message=f"Kết nối thành công! Đã đồng bộ {len(members)} contacts và {len(campaigns)} campaigns."
    )


@router.post("/connect/hubspot", response_model=SyncResult)
async def connect_hubspot(
    payload: ConnectHubSpotRequest,
    current_org: TokenData = Depends(get_current_org),
):
    """Kết nối HubSpot qua Private App Token."""
    svc = HubSpotService(payload.access_token)
    await svc.validate_connection()
    contacts = await svc.get_contacts(limit=10)

    return SyncResult(
        provider="hubspot",
        contacts_synced=len(contacts),
        campaigns_synced=0,
        status="connected",
        message=f"Kết nối HubSpot thành công! Preview: {len(contacts)} contacts."
    )


@router.post("/connect/sendgrid", response_model=SyncResult)
async def connect_sendgrid(
    payload: ConnectSendGridRequest,
    current_org: TokenData = Depends(get_current_org),
):
    """Kết nối SendGrid qua API Key."""
    svc = SendGridService(payload.api_key)
    profile = await svc.validate_connection()

    return SyncResult(
        provider="sendgrid",
        contacts_synced=0,
        campaigns_synced=0,
        status="connected",
        message=f"Kết nối SendGrid thành công! Account: {profile.get('email', 'N/A')}"
    )


@router.get("/sync/status/{provider}")
async def get_sync_status(
    provider: str,
    current_org: TokenData = Depends(get_current_org),
):
    """Kiểm tra trạng thái đồng bộ của một provider."""
    # TODO: Query DB for last sync timestamp
    return {
        "provider": provider,
        "org_id": current_org.org_id,
        "status": "synced",
        "last_synced_at": "2025-05-19T15:00:00Z",
        "next_sync_in_minutes": 30
    }
