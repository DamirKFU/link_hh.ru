from fastapi import APIRouter
from httpx_oauth.clients.google import GoogleOAuth2

from backend.core.config import settings

router = APIRouter(prefix="/auth")

google_oauth_client = GoogleOAuth2(
    settings.google.client_id.get_secret_value(),
    settings.google.secret.get_secret_value(),
)
