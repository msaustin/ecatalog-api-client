#!/usr/bin/env python3

from ecatalog_client import (
    ECatalogAPIClient, ItemNew, ItemPartialUpdate, ItemDeleteRequest,
    ItemDivisions, ItemDivision, ItemAttributes, SkuSubstitutionRequest
)


def main():
    # Initialize the client
    client = ECatalogAPIClient("http://127.0.0.1:8000")

    print("=== eCatalog API Client Demo ===\n")

    try:
        # 1. SKU Lookup - Check if a SKU exists and get its type
        print("1. Looking up SKU status...")
        test_sku = "83288348"
        sku_info = client.lookup_sku(test_sku)
        if sku_info:
            print(f"SKU {test_sku}:")
            print(f"  Type: {sku_info.type}")
            print(f"  Site: {sku_info.site}")
            print(f"  Exists: {sku_info.exists}")
            print(f"  Divisions: {sku_info.divisions}")
        else:
            print(f"SKU {test_sku} not found or error occurred")
        print()

        # 2. Get Item by SKU
        print("2. Getting item by SKU...")
        if sku_info and sku_info.exists and sku_info.type == "Item":
            item = client.get_item(test_sku)
            if item:
                print(f"Found item: {item.Title}")
                print(f"  Category: {item.Category}")
                print(f"  Price Info: {item.AdvertisingCopy[:100]}...")
                print(f"  Dimensions: {item.Dimensions}")
            else:
                print("Failed to retrieve item details")
        print()

        # 3. Create a new item (example)
        print("3. Creating a new test item...")
        new_item = ItemNew(
            Sku="TEST001",
            Site="RTG",
            Category="Test : Items",
            Collection="Test Collection",
            Brand="Test Brand",
            PDMDescription="Test item description",
            Title="Test Item",
            AdvertisingCopy="This is a test item for demonstration purposes.",
            Image="test_item_image",
            Dimensions="10w x 10d x 10h",
            GenericName="Test Item",
            DeliveryType="O",
            Divisions=ItemDivisions(
                FL=ItemDivision(Active=True),
                SE=ItemDivision(Active=True),
                TX=ItemDivision(Active=False)
            )
        )

        result = client.create_item(new_item)
        if result:
            workrequest_id = result.get("workrequest_id")
            if workrequest_id:
                print(f"Test item created successfully (Work Request: {workrequest_id})")
            else:
                print("Test item created successfully")

            # 4. Update the item
            print("4. Updating the test item...")
            update = ItemPartialUpdate(
                Title="Updated Test Item",
                AdvertisingCopy="This item has been updated via the API.",
                Dimensions="12w x 12d x 12h"
            )
            update_result = client.update_item("TEST001", update)
            if update_result:
                print(f"Item updated: {update_result.get('message', 'Success')}")

            # 5. Delete the test item
            print("5. Deleting the test item...")
            delete_request = ItemDeleteRequest(
                Site="RTG",
                Division="FL",
                DeleteImportData=False
            )
            delete_result = client.delete_item("TEST001", delete_request)
            if delete_result:
                print(f"Delete request submitted: {delete_result.get('message', 'Success')}")
        else:
            print("Failed to create test item")
        print()

        # 6. Get Room by SKU (if we find a room SKU)
        print("6. Looking for room SKUs...")
        room_test_skus = ["7013461P", "4294773P"]  # Common room SKU patterns

        for room_sku in room_test_skus:
            sku_info = client.lookup_sku(room_sku)
            if sku_info and sku_info.exists and sku_info.type == "Room":
                print(f"Found room SKU: {room_sku}")
                room = client.get_room(room_sku)
                if room:
                    print(f"  Title: {room.Title}")
                    print(f"  Category: {room.Category}")
                    if room.RoomItems and room.RoomItems.FL:
                        print(f"  Contains {len(room.RoomItems.FL)} items in FL division")
                break
        print()

        # 7. SKU Substitution example (prevalidation)
        print("7. Testing SKU substitution prevalidation...")
        substitution_request = SkuSubstitutionRequest(
            Site="RTG",
            ReplacedSkus=["7013878P"],
            SubstitutedSkus=["7013879P"],
            Divisions=["FL", "SE"],
            PackageSkus=["83288348"]
        )

        prevalidation = client.prevalidate_sku_substitution(substitution_request)
        if prevalidation:
            print(f"Prevalidation result: {prevalidation.get('valid', False)}")
            if prevalidation.get('errors'):
                print(f"  Errors: {prevalidation['errors']}")
            if prevalidation.get('warnings'):
                print(f"  Warnings: {prevalidation['warnings']}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()