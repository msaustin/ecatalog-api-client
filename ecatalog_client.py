import requests
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import json
from datetime import datetime, timedelta
import time
import hashlib
import base64
import secrets
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import os


class ItemDivision(BaseModel):
    Active: bool


class ItemDivisions(BaseModel):
    FL: Optional[ItemDivision] = None
    SE: Optional[ItemDivision] = None
    TX: Optional[ItemDivision] = None


class ItemAttributes(BaseModel):
    Color: Optional[List[str]] = None
    Decor: Optional[List[str]] = None
    Finish: Optional[List[str]] = None
    Features: Optional[List[str]] = None
    Material: Optional[List[str]] = None
    Movement: Optional[List[str]] = None
    PieceCount: Optional[List[str]] = None
    Shape: Optional[List[str]] = None
    Size: Optional[List[str]] = None
    Style: Optional[List[str]] = None
    Theme: Optional[List[str]] = None
    Team: Optional[List[str]] = None


class PackageProduct(BaseModel):
    Sku: str
    Quantity: int


class ItemPackageProducts(BaseModel):
    FL: Optional[List[PackageProduct]] = None
    SE: Optional[List[PackageProduct]] = None
    TX: Optional[List[PackageProduct]] = None


class Item(BaseModel):
    Sku: str
    Site: str
    Category: str
    Collection: str
    Brand: Optional[str] = ""
    RTGAlias: str
    Title: str
    AdvertisingCopy: str
    Image: str
    AdditionalNotes: Optional[str] = ""
    Dimensions: str
    GenericName: str
    Attributes: Optional[ItemAttributes] = None
    DeliveryType: str
    DeliverySubType: Optional[str] = ""
    ShippingCode: Optional[str] = ""
    SingleItemRoom: Optional[bool] = False
    GroupKey: Optional[str] = ""
    GroupKeyModifier: Optional[str] = ""
    Divisions: ItemDivisions
    PackageProducts: Optional[ItemPackageProducts] = None


class ItemNew(BaseModel):
    Sku: str
    Site: str
    Category: str
    Collection: str
    Brand: Optional[str] = ""
    PDMDescription: str
    Title: str
    AdvertisingCopy: str
    Image: str
    AdditionalNotes: Optional[str] = ""
    Dimensions: str
    GenericName: str
    Attributes: Optional[ItemAttributes] = None
    DeliveryType: str
    DeliverySubType: Optional[str] = ""
    ShippingCode: Optional[str] = ""
    SingleItemRoom: Optional[bool] = False
    GroupKey: Optional[str] = ""
    GroupKeyModifier: Optional[str] = ""
    Divisions: ItemDivisions


class ItemPartialUpdate(BaseModel):
    RTGAlias: Optional[str] = None
    Title: Optional[str] = None
    AdvertisingCopy: Optional[str] = None
    Image: Optional[str] = None
    AdditionalNotes: Optional[str] = None
    Dimensions: Optional[str] = None
    GenericName: Optional[str] = None
    DeliveryType: Optional[str] = None
    DeliverySubType: Optional[str] = None
    ShippingCode: Optional[str] = None
    SingleItemRoom: Optional[bool] = None
    GroupKey: Optional[str] = None
    GroupKeyModifier: Optional[str] = None


class ItemDeleteRequest(BaseModel):
    Site: str
    Division: Optional[str] = None
    DeleteImportData: bool = False


class RoomItem(BaseModel):
    Sku: str
    Quantity: int


class RoomItems(BaseModel):
    FL: Optional[List[RoomItem]] = None
    SE: Optional[List[RoomItem]] = None
    TX: Optional[List[RoomItem]] = None


class SwapRoomItemsRequest(BaseModel):
    RoomSku: str
    SwapOutRoomItems: List[RoomItem]
    SwapInRoomItems: List[RoomItem]
    Divisions: List[str]


class RoomAttributes(BaseModel):
    Color: Optional[List[str]] = []
    Decor: Optional[List[str]] = []
    Finish: Optional[List[str]] = []
    Features: Optional[List[str]] = []
    Material: Optional[List[str]] = []
    Movement: Optional[List[str]] = []
    PieceCount: Optional[List[str]] = []
    Shape: Optional[List[str]] = []
    Size: Optional[List[str]] = []
    Style: Optional[List[str]] = []
    Theme: Optional[List[str]] = []


class Room(BaseModel):
    Sku: str
    Site: str
    Category: str
    Collection: str
    Brand: Optional[str] = ""
    RTGAlias: Optional[str] = ""
    Title: Optional[str] = ""
    AdvertisingCopy: Optional[str] = ""
    Image: Optional[str] = ""
    AdditionalNotes: Optional[str] = ""
    Attributes: Optional[RoomAttributes] = None
    DeliveryType: Optional[str] = ""
    GroupKey: Optional[str] = ""
    GroupKeyModifier: Optional[str] = ""
    ShippingCode: Optional[str] = ""
    Divisions: ItemDivisions
    PackageProducts: ItemPackageProducts
    RoomItems: RoomItems


class SkuLookupResponse(BaseModel):
    sku: str
    site: str
    type: str
    divisions: Dict[str, Any]
    exists: bool


class SkuSubstitutionRequest(BaseModel):
    Site: str
    ReplacedSkus: List[str] = Field(alias="Replaced Skus")
    SubstitutedSkus: List[str] = Field(alias="Substituted Skus")
    Divisions: List[str]
    PackageSkus: Optional[List[str]] = Field(alias="Package Skus", default=None)


class OAuthConfig(BaseModel):
    client_id: str
    client_secret: Optional[str] = None  # Required for M2M, not needed for PKCE
    authorization_url: Optional[str] = None  # Not needed for M2M
    token_url: str
    redirect_uri: str = "http://localhost:8080/callback"
    scope: Optional[str] = None
    use_pkce: bool = True
    use_m2m: bool = False  # Machine-to-Machine authentication
    auto_open_browser: bool = True  # Automatically open browser
    callback_port: int = 8080  # Port for local callback server


class PKCEChallenge(BaseModel):
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    expires_at: Optional[datetime] = None  # When token expires

    def is_expired(self) -> bool:
        """Check if token is expired (with 1 minute buffer)"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at - timedelta(minutes=1)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenResponse":
        """Create from dictionary (JSON deserialization)"""
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""

    def __init__(self, *args, **kwargs):
        self.authorization_code = None
        self.error = None
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET request to callback URL"""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if 'code' in query_params:
            # Successfully received authorization code
            self.server.authorization_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html><body>
                    <h2>Authorization Successful!</h2>
                    <p>You can close this window and return to the CLI.</p>
                </body></html>
            ''')
        elif 'error' in query_params:
            # Authorization failed
            self.server.error = query_params['error'][0]
            error_description = query_params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'''
                <html><body>
                    <h2>Authorization Failed</h2>
                    <p>Error: {self.server.error}</p>
                    <p>Description: {error_description}</p>
                </body></html>
            '''.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html><body>
                    <h2>Invalid Request</h2>
                    <p>No authorization code received.</p>
                </body></html>
            ''')

    def log_message(self, format, *args):
        # Suppress log messages
        pass


class ECatalogAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", access_token: Optional[str] = None, oauth_config: Optional[OAuthConfig] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # OAuth configuration
        self.oauth_config = oauth_config
        self.current_token: Optional[TokenResponse] = None
        self.token_expires_at: Optional[datetime] = None

        # Set initial token if provided
        if access_token:
            self.set_access_token(access_token)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Token storage
        self.token_cache_dir = Path.home() / ".ecatalog" / "tokens"
        self.token_cache_dir.mkdir(parents=True, exist_ok=True)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        # Ensure we have a valid token if OAuth is configured
        if self.oauth_config and self.current_token:
            self.ensure_valid_token()

        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.info(f"{method} {url} - Status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e} - {response.text}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {e}")
            raise

    def set_access_token(self, token: str):
        """Set the access token for authentication"""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def _generate_pkce_challenge(self) -> PKCEChallenge:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')

        return PKCEChallenge(
            code_verifier=code_verifier,
            code_challenge=code_challenge
        )

    def get_authorization_url(self) -> tuple[str, PKCEChallenge]:
        """Generate authorization URL for OAuth flow with PKCE"""
        if not self.oauth_config:
            raise ValueError("OAuth configuration not provided")

        pkce_challenge = self._generate_pkce_challenge()

        params = {
            'client_id': self.oauth_config.client_id,
            'response_type': 'code',
            'redirect_uri': self.oauth_config.redirect_uri,
        }

        if self.oauth_config.scope:
            params['scope'] = self.oauth_config.scope

        if self.oauth_config.use_pkce:
            params.update({
                'code_challenge': pkce_challenge.code_challenge,
                'code_challenge_method': pkce_challenge.code_challenge_method
            })

        auth_url = f"{self.oauth_config.authorization_url}?{urllib.parse.urlencode(params)}"
        return auth_url, pkce_challenge

    def exchange_code_for_token(self, authorization_code: str, pkce_challenge: PKCEChallenge) -> TokenResponse:
        """Exchange authorization code for access token using PKCE"""
        if not self.oauth_config:
            raise ValueError("OAuth configuration not provided")

        token_data = {
            'grant_type': 'authorization_code',
            'client_id': self.oauth_config.client_id,
            'code': authorization_code,
            'redirect_uri': self.oauth_config.redirect_uri,
        }

        if self.oauth_config.use_pkce:
            token_data['code_verifier'] = pkce_challenge.code_verifier
        else:
            token_data['client_secret'] = self.oauth_config.client_secret

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(
                self.oauth_config.token_url,
                data=token_data,
                headers=headers
            )
            response.raise_for_status()
            token_response = TokenResponse(**response.json())

            # Store token and set expiration
            self.current_token = token_response
            if token_response.expires_in:
                token_response.expires_at = datetime.now() + timedelta(seconds=token_response.expires_in)
                self.token_expires_at = token_response.expires_at

            # Save token to cache
            self.save_token(token_response)

            # Set the token for future requests
            self.set_access_token(token_response.access_token)

            self.logger.info("OAuth token obtained successfully")
            return token_response

        except requests.exceptions.HTTPError as e:
            error_details = ""
            try:
                if response.content:
                    error_data = response.json()
                    error_details = f" - {error_data}"
            except:
                error_details = f" - {response.text}"

            self.logger.error(f"Token exchange failed: {e}{error_details}")
            raise Exception(f"OAuth token exchange failed: {e}{error_details}")
        except Exception as e:
            self.logger.error(f"Token exchange error: {e}")
            raise

    def refresh_token(self) -> Optional[TokenResponse]:
        """Refresh the access token using refresh token"""
        if not self.current_token or not self.current_token.refresh_token:
            self.logger.error("No refresh token available")
            return None

        if not self.oauth_config:
            raise ValueError("OAuth configuration not provided")

        token_data = {
            'grant_type': 'refresh_token',
            'client_id': self.oauth_config.client_id,
            'refresh_token': self.current_token.refresh_token,
        }

        if not self.oauth_config.use_pkce and self.oauth_config.client_secret:
            token_data['client_secret'] = self.oauth_config.client_secret

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(
                self.oauth_config.token_url,
                data=token_data,
                headers=headers
            )
            response.raise_for_status()
            token_response = TokenResponse(**response.json())

            # Update stored token
            self.current_token = token_response
            if token_response.expires_in:
                token_response.expires_at = datetime.now() + timedelta(seconds=token_response.expires_in)
                self.token_expires_at = token_response.expires_at

            # Save refreshed token to cache
            self.save_token(token_response)

            # Update the token for future requests
            self.set_access_token(token_response.access_token)

            self.logger.info("Token refreshed successfully")
            return token_response

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Token refresh failed: {e}")
            return None

    def is_token_expired(self) -> bool:
        """Check if the current token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.now() >= self.token_expires_at - timedelta(minutes=1)  # Refresh 1 minute early

    def ensure_valid_token(self):
        """Ensure we have a valid token, refresh if needed"""
        if self.is_token_expired():
            self.logger.info("Token expired, attempting to refresh")
            if not self.refresh_token():
                raise Exception("Unable to refresh token, re-authentication required")

    def _get_token_cache_path(self) -> Path:
        """Get the path for token cache file"""
        if not self.oauth_config:
            raise ValueError("OAuth configuration required for token caching")

        # Use client_id and base_url to create unique token file
        safe_url = self.base_url.replace("://", "_").replace("/", "_").replace(":", "_")
        filename = f"{self.oauth_config.client_id}_{safe_url}.json"
        return self.token_cache_dir / filename

    def save_token(self, token: TokenResponse):
        """Save token to cache file"""
        try:
            cache_path = self._get_token_cache_path()

            # Calculate expiration time if not set
            if not token.expires_at and token.expires_in:
                token.expires_at = datetime.now() + timedelta(seconds=token.expires_in)

            with open(cache_path, 'w') as f:
                json.dump(token.to_dict(), f, indent=2)

            # Set restrictive permissions (only user can read/write)
            os.chmod(cache_path, 0o600)

            self.logger.info(f"Token saved to {cache_path}")
        except Exception as e:
            self.logger.warning(f"Failed to save token: {e}")

    def load_token(self) -> Optional[TokenResponse]:
        """Load token from cache file"""
        try:
            cache_path = self._get_token_cache_path()

            if not cache_path.exists():
                self.logger.debug("No cached token found")
                return None

            with open(cache_path, 'r') as f:
                token_data = json.load(f)

            token = TokenResponse.from_dict(token_data)

            if token.is_expired():
                self.logger.info("Cached token is expired")
                # Try to refresh if we have a refresh token
                if token.refresh_token:
                    self.current_token = token
                    refreshed = self.refresh_token()
                    if refreshed:
                        self.logger.info("Token refreshed successfully")
                        return refreshed

                # Remove expired token
                cache_path.unlink()
                return None

            self.logger.info("Loaded valid token from cache")
            return token

        except Exception as e:
            self.logger.warning(f"Failed to load token: {e}")
            return None

    def clear_token_cache(self):
        """Clear cached token"""
        try:
            cache_path = self._get_token_cache_path()
            if cache_path.exists():
                cache_path.unlink()
                self.logger.info("Token cache cleared")
        except Exception as e:
            self.logger.warning(f"Failed to clear token cache: {e}")

    def authenticate_m2m(self, force_reauth: bool = False) -> TokenResponse:
        """Authenticate using Machine-to-Machine (client credentials) flow"""
        if not self.oauth_config:
            raise ValueError("OAuth configuration not provided")

        if not self.oauth_config.client_secret:
            raise ValueError("Client secret required for M2M authentication")

        # Try to load cached token first (unless forced to reauth)
        if not force_reauth:
            cached_token = self.load_token()
            if cached_token:
                self.current_token = cached_token
                self.set_access_token(cached_token.access_token)
                return cached_token

        # Request token using client credentials
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.oauth_config.client_id,
            'client_secret': self.oauth_config.client_secret,
        }

        if self.oauth_config.scope:
            token_data['scope'] = self.oauth_config.scope

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(
                self.oauth_config.token_url,
                data=token_data,
                headers=headers
            )
            response.raise_for_status()
            token_response = TokenResponse(**response.json())

            # Store token and set expiration
            self.current_token = token_response
            if token_response.expires_in:
                token_response.expires_at = datetime.now() + timedelta(seconds=token_response.expires_in)
                self.token_expires_at = token_response.expires_at

            # Save token to cache
            self.save_token(token_response)

            # Set the token for future requests
            self.set_access_token(token_response.access_token)

            self.logger.info("M2M OAuth token obtained successfully")
            return token_response

        except requests.exceptions.HTTPError as e:
            error_details = ""
            try:
                if response.content:
                    error_data = response.json()
                    error_details = f" - {error_data}"
            except:
                error_details = f" - {response.text}"

            self.logger.error(f"M2M token request failed: {e}{error_details}")
            raise Exception(f"M2M OAuth token request failed: {e}{error_details}")
        except Exception as e:
            self.logger.error(f"M2M token request error: {e}")
            raise

    def authenticate_with_browser(self, timeout: int = 300, force_reauth: bool = False) -> TokenResponse:
        """Complete OAuth flow automatically using local callback server and browser"""
        if not self.oauth_config:
            raise ValueError("OAuth configuration not provided")

        # Try to load cached token first (unless forced to reauth)
        if not force_reauth:
            cached_token = self.load_token()
            if cached_token:
                self.current_token = cached_token
                self.set_access_token(cached_token.access_token)
                return cached_token

        # Generate PKCE challenge
        pkce_challenge = self._generate_pkce_challenge()

        # Update redirect URI to use local server
        original_redirect = self.oauth_config.redirect_uri
        self.oauth_config.redirect_uri = f"http://127.0.0.1:{self.oauth_config.callback_port}/callback"

        try:
            # Get authorization URL
            auth_url, _ = self.get_authorization_url()

            # Start local callback server
            server = HTTPServer(('127.0.0.1', self.oauth_config.callback_port), CallbackHandler)
            server.authorization_code = None
            server.error = None

            # Start server in background thread
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self.logger.info(f"Started local callback server on port {self.oauth_config.callback_port}")

            # Open browser automatically if configured
            if self.oauth_config.auto_open_browser:
                self.logger.info("Opening browser for authorization...")
                webbrowser.open(auth_url)
            else:
                self.logger.info(f"Please visit: {auth_url}")

            # Wait for authorization code or timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if server.authorization_code:
                    # Got authorization code, exchange for token
                    server.shutdown()
                    token = self.exchange_code_for_token(server.authorization_code, pkce_challenge)
                    self.logger.info("OAuth authentication completed successfully")
                    return token

                if server.error:
                    server.shutdown()
                    raise Exception(f"OAuth authorization failed: {server.error}")

                time.sleep(0.5)

            # Timeout
            server.shutdown()
            raise Exception(f"OAuth authentication timed out after {timeout} seconds")

        finally:
            # Restore original redirect URI
            self.oauth_config.redirect_uri = original_redirect

    # SKU Lookup Operations
    def lookup_sku(self, sku: str) -> Optional[SkuLookupResponse]:
        """Look up SKU type, site, and division availability"""
        response = self._make_request('GET', f'/sku/{sku}/lookup')
        data = self._handle_response(response)

        try:
            return SkuLookupResponse(**data)
        except Exception as e:
            self.logger.error(f"Invalid SKU lookup data: {e}")
            return None

    # Item Operations
    def get_item(self, sku: str) -> Optional[Item]:
        """Get item by SKU"""
        response = self._make_request('GET', f'/item/{sku}')
        data = self._handle_response(response)

        try:
            return Item(**data)
        except Exception as e:
            self.logger.error(f"Invalid item data: {e}")
            return None

    def create_item(self, item: ItemNew) -> Optional[Dict]:
        """Create a new item - returns response data with work request ID if successful"""
        item_data = item.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request('POST', '/item', json=item_data)

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            return None

    def update_item(self, sku: str, item_update: ItemPartialUpdate) -> Optional[Dict]:
        """Partially update an item by SKU"""
        update_data = item_update.model_dump(exclude_none=True)
        response = self._make_request('PATCH', f'/item/{sku}', json=update_data)
        return self._handle_response(response)

    def delete_item(self, sku: str, delete_request: ItemDeleteRequest) -> Optional[Dict]:
        """Delete an item by SKU"""
        delete_data = delete_request.model_dump(exclude_none=True)
        response = self._make_request('DELETE', f'/item/{sku}', json=delete_data)
        return self._handle_response(response)

    # Room Operations
    def get_room(self, sku: str) -> Optional[Room]:
        """Get room by SKU"""
        response = self._make_request('GET', f'/room/{sku}')
        data = self._handle_response(response)

        try:
            return Room(**data)
        except Exception as e:
            self.logger.error(f"Invalid room data: {e}")
            return None

    def create_room(self, room: Room) -> bool:
        """Create a new room"""
        room_data = room.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request('POST', '/room', json=room_data)

        try:
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError:
            return False

    def update_room(self, sku: str, room_update: Dict) -> Optional[Dict]:
        """Partially update a room by SKU"""
        response = self._make_request('PATCH', f'/room/{sku}', json=room_update)
        return self._handle_response(response)

    def delete_room(self, sku: str, delete_request: ItemDeleteRequest) -> Optional[Dict]:
        """Delete a room by SKU"""
        delete_data = delete_request.model_dump(exclude_none=True)
        response = self._make_request('DELETE', f'/room/{sku}', json=delete_data)
        return self._handle_response(response)

    def swap_room_items(self, swap_request: SwapRoomItemsRequest) -> Optional[Dict]:
        """Swap items in a room"""
        request_data = swap_request.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request('POST', '/room/swap-items', json=request_data)
        return self._handle_response(response)

    # SKU Substitution Operations
    def prevalidate_sku_substitution(self, substitution_request: SkuSubstitutionRequest) -> Optional[Dict]:
        """Prevalidate a SKU substitution request"""
        request_data = substitution_request.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request('POST', '/sku/substitution/prevalidate', json=request_data)
        return self._handle_response(response)

    def submit_sku_substitution(self, substitution_request: SkuSubstitutionRequest) -> Optional[Dict]:
        """Submit a SKU substitution request"""
        request_data = substitution_request.model_dump(by_alias=True, exclude_none=True)
        response = self._make_request('POST', '/sku/substitution', json=request_data)
        return self._handle_response(response)

    # Work Request Operations
    def get_workrequest(self, workrequest_id: int) -> Optional[Dict]:
        """Get work request by ID"""
        response = self._make_request('GET', f'/workrequests/{workrequest_id}')
        return self._handle_response(response)

    def list_workrequests(self, status: Optional[str] = None, route_name: Optional[str] = None) -> Optional[List[Dict]]:
        """List work requests with optional filtering"""
        params = {}
        if status:
            params['status'] = status
        if route_name:
            params['route_name'] = route_name

        response = self._make_request('GET', '/workrequests/', params=params)
        return self._handle_response(response)

    def process_workrequests(self, workrequest_ids: List[int]) -> Optional[Dict]:
        """Process a list of work request IDs"""
        request_data = {"workrequest_ids": workrequest_ids}
        response = self._make_request('POST', '/workrequests/process', json=request_data)
        return self._handle_response(response)

    def process_workflows(self, flow_type: str, workrequest_ids: Optional[List[int]] = None) -> Optional[Dict]:
        """Process workflows by flow type, optionally filtering by work request IDs"""
        params = {"flow_type": flow_type}
        request_data = {}
        if workrequest_ids:
            request_data["workrequest_ids"] = workrequest_ids

        response = self._make_request('POST', '/workflows/process', params=params, json=request_data)
        return self._handle_response(response)