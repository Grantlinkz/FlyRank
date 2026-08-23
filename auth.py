import os
import sys
import site

# Ensure user site-packages are included in Python path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    site.addsitedir(user_site)

from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastapi import Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ginezhzilpglcybjgsjy.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Security scheme for OpenAPI / Swagger UI Bearer Authorization padlock
security_scheme = HTTPBearer(auto_error=False)

class AuthException(Exception):
    """Custom authentication exception carrying status code and clean JSON error message."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)):
    """FastAPI security dependency extracting and verifying Bearer JWT via Supabase Auth."""
    if not credentials or not credentials.credentials:
        raise AuthException(401, "Access token required")
        
    token = credentials.credentials.strip()
    if not token:
        raise AuthException(401, "Access token required")
        
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise AuthException(401, "Invalid or expired token")
        return user_response.user
    except AuthException:
        raise
    except Exception:
        raise AuthException(401, "Invalid or expired token")

try:
    from supabase_auth.errors import AuthApiError, AuthError
except ImportError:
    AuthApiError = Exception
    AuthError = Exception

def logout_user(token: str) -> None:
    """Perform request-bound logout operation using the presented bearer token."""
    clean_token = token.strip() if token else ""
    if not clean_token:
        raise AuthException(401, "Access token required")
        
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    if hasattr(client.auth, "_headers"):
        client.auth._headers["Authorization"] = f"Bearer {clean_token}"
    try:
        client.auth.sign_out()
    except AuthException:
        raise
    except (AuthApiError, AuthError):
        raise AuthException(401, "Invalid or expired token")
    except Exception:
        raise AuthException(500, "Upstream authentication service error")


