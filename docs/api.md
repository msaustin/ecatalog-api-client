# API Reference

## ECatalogAPIClient

A Python client for interacting with eCatalog FastAPI application for managing Items and Rooms.

### Initialization

```python
from ecatalog_client import ECatalogAPIClient

# Initialize with default localhost
client = ECatalogAPIClient()

# Or specify custom base URL
client = ECatalogAPIClient("https://api.example.com")
```

### SKU Operations

#### Lookup SKU Status
```python
sku_info = client.lookup_sku("83288348")
print(f"Type: {sku_info.type}, Site: {sku_info.site}, Exists: {sku_info.exists}")
```

### Item Operations

#### Get Item by SKU
```python
item = client.get_item("83288348")
```

#### Create Item
```python
from ecatalog_client import ItemNew, ItemDivisions, ItemDivision

new_item = ItemNew(
    Sku="TEST001",
    Site="RTG",
    Category="Test : Items",
    Collection="Test Collection",
    PDMDescription="Test Description",
    Title="Test Item",
    AdvertisingCopy="Test description",
    Image="test_image",
    Dimensions="10w x 10d x 10h",
    GenericName="Test",
    DeliveryType="O",
    Divisions=ItemDivisions(
        FL=ItemDivision(Active=True),
        SE=ItemDivision(Active=True)
    )
)
created = client.create_item(new_item)
```

#### Update Item
```python
from ecatalog_client import ItemPartialUpdate

update = ItemPartialUpdate(
    Title="Updated Title",
    AdvertisingCopy="Updated description"
)
result = client.update_item("TEST001", update)
```

#### Delete Item
```python
from ecatalog_client import ItemDeleteRequest

delete_request = ItemDeleteRequest(
    Site="RTG",
    Division="FL",
    DeleteImportData=False
)
result = client.delete_item("TEST001", delete_request)
```

### Room Operations

#### Get Room by SKU
```python
room = client.get_room("7013461P")
```

#### Create Room
```python
# Similar to items, but with Room model
created = client.create_room(room_data)
```

#### Update Room
```python
result = client.update_room("7013461P", update_data)
```

#### Delete Room
```python
result = client.delete_room("7013461P", delete_request)
```

### SKU Substitution Operations

#### Prevalidate Substitution
```python
from ecatalog_client import SkuSubstitutionRequest

substitution = SkuSubstitutionRequest(
    Site="RTG",
    ReplacedSkus=["7013878P"],
    SubstitutedSkus=["7013879P"],
    Divisions=["FL", "SE"],
    PackageSkus=["83288348"]
)
validation = client.prevalidate_sku_substitution(substitution)
```

#### Submit Substitution
```python
result = client.submit_sku_substitution(substitution)
```

### Error Handling

All methods include comprehensive error handling and logging. Check the logs for detailed error information when operations fail.

### Key Models

#### Item
- `Sku`: str - Stock Keeping Unit
- `Site`: str - Marketplace site (RTG, OTG, etc.)
- `Category`: str - Item category
- `Collection`: str - Collection name
- `Title`: str - Item title
- `Dimensions`: str - Item dimensions
- `Divisions`: ItemDivisions - Regional availability (FL, SE, TX)

#### Room
- Similar to Item but includes `RoomItems` and `PackageProducts`
- Contains lists of items that make up the room

#### SkuLookupResponse
- `sku`: str - The requested SKU
- `type`: str - "Item", "Room", "Product", or "Missing"
- `site`: str - Marketplace site
- `divisions`: Dict - Regional availability
- `exists`: bool - Whether SKU exists