#!/usr/bin/env python3
"""Test M2M OAuth authentication with the eCatalog API"""

import os
from dotenv import load_dotenv
from ecatalog_client import ECatalogAPIClient, OAuthConfig
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()

def test_m2m_authentication():
    """Test Machine-to-Machine authentication"""

    # Get OAuth configuration from environment
    oauth_config = OAuthConfig(
        client_id=os.getenv("OAUTH_CLIENT_ID"),
        client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
        token_url=os.getenv("OAUTH_TOKEN_URL"),
        use_m2m=True,
        use_pkce=False,
    )

    console.print("[bold blue]Testing M2M Authentication...[/bold blue]")
    console.print(f"Token URL: {oauth_config.token_url}")
    console.print(f"Client ID: {oauth_config.client_id}")
    console.print(f"Client Secret: {'*' * len(oauth_config.client_secret) if oauth_config.client_secret else 'None'}")

    # Initialize client with OAuth config
    client = ECatalogAPIClient(
        base_url="http://127.0.0.1:8000",  # API server
        oauth_config=oauth_config
    )

    try:
        # Authenticate using M2M
        console.print("\n[yellow]Requesting access token...[/yellow]")
        token = client.authenticate_m2m()

        console.print("[green]✓ Authentication successful![/green]")
        console.print(f"Access Token: {token.access_token[:20]}...")
        console.print(f"Token Type: {token.token_type}")
        console.print(f"Expires In: {token.expires_in} seconds")
        if token.scope:
            console.print(f"Scope: {token.scope}")

        # Test a simple API call (list workrequests)
        console.print("\n[yellow]Testing API call with token...[/yellow]")
        workrequests = client.list_workrequests()
        console.print(f"[green]✓ API call successful! Found {len(workrequests) if workrequests else 0} workrequests[/green]")

        return True

    except Exception as e:
        console.print(f"[red]✗ Authentication failed: {e}[/red]")
        return False

if __name__ == "__main__":
    success = test_m2m_authentication()
    exit(0 if success else 1)
