#!/usr/bin/env python3

from ecommerce_client import EcommerceAPIClient, Product


def main():
    # Initialize the client
    client = EcommerceAPIClient("http://127.0.0.1:8000")

    print("=== Ecommerce API Client Demo ===\n")

    try:
        # 1. Get all products
        print("1. Fetching all products...")
        products = client.get_products()
        print(f"Found {len(products)} products")
        for product in products[:3]:  # Show first 3
            print(f"  - {product.name}: ${product.price}")
        print()

        # 2. Get categories
        print("2. Fetching categories...")
        categories = client.get_categories()
        print(f"Available categories: {', '.join(categories)}")
        print()

        # 3. Search for products
        print("3. Searching for products...")
        search_results = client.search_products("laptop")
        print(f"Found {len(search_results)} products matching 'laptop'")
        for product in search_results:
            print(f"  - {product.name}: ${product.price}")
        print()

        # 4. Create a new product
        print("4. Creating a new product...")
        new_product = Product(
            name="Test Product",
            description="A test product created by the API client",
            price=99.99,
            category="electronics",
            stock_quantity=50,
            sku="TEST001"
        )
        created_product = client.create_product(new_product)
        if created_product:
            print(f"Created product: {created_product.name} (ID: {created_product.id})")

            # 5. Get the created product by ID
            print("5. Fetching the created product by ID...")
            fetched_product = client.get_product(created_product.id)
            if fetched_product:
                print(f"Fetched by ID: {fetched_product.name}")

            # 5b. Get the created product by SKU
            print("5b. Fetching the created product by SKU...")
            fetched_by_sku = client.get_product_by_sku(created_product.sku)
            if fetched_by_sku:
                print(f"Fetched by SKU '{created_product.sku}': {fetched_by_sku.name}")

            # 6. Update the product
            print("6. Updating the product...")
            fetched_product.price = 89.99
            fetched_product.description = "Updated description"
            updated_product = client.update_product(created_product.id, fetched_product)
            if updated_product:
                print(f"Updated product price to ${updated_product.price}")

            # 7. Delete the product
            print("7. Deleting the test product...")
            if client.delete_product(created_product.id):
                print("Product deleted successfully")
            else:
                print("Failed to delete product")
        print()

        # 8. Get products by category
        if categories:
            category = categories[0]
            print(f"8. Getting products in '{category}' category...")
            category_products = client.get_products_by_category(category)
            print(f"Found {len(category_products)} products in '{category}'")
            for product in category_products[:3]:  # Show first 3
                print(f"  - {product.name}: ${product.price}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()