#!/usr/bin/env python3

from ecatalog_client import (
    ECatalogAPIClient,
    ItemNew,
    ItemPartialUpdate,
    ItemDeleteRequest,
    ItemDivisions,
    ItemDivision,
    ItemAttributes,
    SkuSubstitutionRequest,
    OAuthConfig,
)


def oauth_flow_demo():
    """Demonstrate OAuth with PKCE authentication flow"""
    print("=== OAuth PKCE Demo ===\n")

    # Configure OAuth with PKCE
    oauth_config = OAuthConfig(
        client_id="product-readiness-client",
        authorization_url="http://127.0.0.1:8000/auth/authorize",
        token_url="http://127.0.0.1:8000/auth/token",
        redirect_uri="http://127.0.0.1:8080/callback",
        scope="catalog:read catalog:validate workflows:submit workflows:monitor openid profile",
        use_pkce=True,
    )

    client = ECatalogAPIClient("http://127.0.0.1:8000", oauth_config=oauth_config)

    try:
        # Step 1: Get authorization URL
        auth_url, pkce_challenge = client.get_authorization_url()
        print("1. Visit this URL to authorize the application:")
        print(f"   {auth_url}\n")

        # Step 2: Get authorization code from user
        print("2. After authorizing, copy the 'code' parameter from the redirect URL")
        authorization_code = input("   Enter authorization code: ")

        # Step 3: Exchange code for token
        print("\n3. Exchanging authorization code for access token...")
        token = client.exchange_code_for_token(authorization_code, pkce_challenge)
        print(f"   Access token obtained: {token.access_token[:20]}...")

        if token.expires_in:
            print(f"   Token expires in: {token.expires_in} seconds")

        # Step 4: Now make API calls
        print("\n4. Making authenticated API call...")
        test_sku = "1409223P"
        sku_info = client.lookup_sku(test_sku)
        if sku_info:
            print(f"SKU {test_sku}:")
            print(f"  Type: {sku_info.type}")
            print(f"  Site: {sku_info.site}")
            print(f"  Exists: {sku_info.exists}")
        else:
            print(f"SKU {test_sku} not found or error occurred")

    except Exception as e:
        print(f"OAuth flow error: {e}")


def simple_token_demo():
    """Demonstrate using a pre-obtained access token"""
    print("=== Simple Token Demo ===\n")

    # If you already have an access token
    access_token = "your_access_token_here"
    client = ECatalogAPIClient("http://127.0.0.1:8000", access_token=access_token)

    try:
        print("Looking up SKU status...")
        test_sku = "1409223P"
        sku_info = client.lookup_sku(test_sku)
        if sku_info:
            print(f"SKU {test_sku}:")
            print(f"  Type: {sku_info.type}")
            print(f"  Site: {sku_info.site}")
            print(f"  Exists: {sku_info.exists}")
            print(f"  Divisions: {sku_info.divisions}")
        else:
            print(f"SKU {test_sku} not found or error occurred")

    except Exception as e:
        print(f"Error occurred: {e}")


def main():
    print("Choose authentication method:")
    print("1. OAuth with PKCE flow")
    print("2. Pre-obtained access token")

    choice = input("Enter choice (1 or 2): ")

    if choice == "1":
        oauth_flow_demo()
    elif choice == "2":
        simple_token_demo()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
