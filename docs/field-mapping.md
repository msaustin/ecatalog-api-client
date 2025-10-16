# Field Mapping Documentation

## Resku Spreadsheet to eCatalog API Mapping

This document shows how spreadsheet columns map to the eCatalog API `POST /item` endpoint fields.

### Required API Fields

| API Field | Spreadsheet Column | Description | Example |
|-----------|-------------------|-------------|---------|
| `Sku` | `New SKU` | Stock Keeping Unit | `2213124P` |
| `Site` | `Site` | Marketplace site | `RTG`, `OTG` |
| `Category` | `Ecat Category` | Item category | `Adult : Living Room : Cocktail Tables` |
| `Collection` | `Collection` | Collection name | `Edina` |
| `PDMDescription` | `Description` | PDM description | `EDINA ESPRESSO COCKTAIL TABLE` |
| `Title` | `Title` | Item display title | `Edina Espresso Cocktail Table` |
| `AdvertisingCopy` | `Advertising Copy` | Marketing description | `Elevate your style with...` |
| `Image` | `Ecat Image Name` | Image filename | `ct_coff_2213124P_edina_espresso` |
| `Dimensions` | `Out Of Box Dim` | Item dimensions | `60"W x 28"D x 18.25"H` |
| `GenericName` | `Generic Name` | Generic product name | `Cocktail Table` |
| `DeliveryType` | `Delivery Type` | Delivery method | `O` (Other), `D` (Delivery) |

### Optional API Fields

| API Field | Spreadsheet Column | Default Value | Description |
|-----------|-------------------|---------------|-------------|
| `Brand` | `Specialty Brand` | `""` (empty) | Brand name |
| `AdditionalNotes` | `Additional Notes` | `""` (empty) | Extra notes |
| `ShippingCode` | `Shipping Code` | `""` (empty) | Shipping classification |
| `DeliverySubType` | `Vendor Delivery Code` | `""` (empty) | Delivery sub-classification |
| `SingleItemRoom` | `Single Item Room` | `False` | Boolean: Is single item room |

### Special Handling Fields

#### Divisions
The `Region` column determines which divisions are active:

| Region Value | FL Division | SE Division | TX Division |
|-------------|-------------|-------------|-------------|
| `SE` | `null` | `Active: False` | `null` |
| `FL` | `Active: False` | `null` | `null` |
| `TX` | `null` | `null` | `Active: False` |
| `ALL` | `Active: False` | `Active: False` | `Active: False` |
| *empty* | `null` | `null` | `null` |

**Note**: All specified divisions start as `Active: False` (inactive) by default.

#### Attributes
Multiple spreadsheet columns map to the `Attributes` object:

| API Attribute | Spreadsheet Column | Type | Example |
|---------------|-------------------|------|---------|
| `Color` | `Color` | Array[string] | `["Espresso", "Brown"]` |
| `Decor` | `Décor` | Array[string] | `["Modern"]` |
| `Finish` | `Finish` | Array[string] | `["Espresso"]` |
| `Features` | `Features` | Array[string] | `["Storage"]` |
| `Material` | `Material` | Array[string] | `["Wood"]` |
| `Movement` | `Movement` | Array[string] | `["Stationary"]` |
| `PieceCount` | `Piece Count` | Array[string] | `["3 Pc"]` |
| `Shape` | `Shape` | Array[string] | `["Rectangular"]` |
| `Size` | `Size` | Array[string] | `["Large"]` |
| `Style` | `Style` | Array[string] | `["Contemporary"]` |
| `Theme` | `Theme` | Array[string] | `["Smal Spaces"]` |

**Note**: Comma-separated values are split into arrays. Empty cells result in empty arrays.

### Fallback Logic

#### Missing Required Fields
- **Collection**: If `Collection` is empty, defaults to `"Default Collection"`
- **Category**: Falls back to `Top Category` → `Category` → `"Uncategorized"`
- **Dimensions**: Falls back to `Size` → `"TBD"`

#### Critical Fields
These fields must be present or the item creation will fail:
- `Sku` (New SKU)
- `Site`
- `PDMDescription` (Description)
- `Title`
- `GenericName` (Generic Name)
- `DeliveryType` (Delivery Type)

## API Request Example

```json
{
  "Sku": "2213124P",
  "Site": "RTG",
  "Category": "Adult : Living Room : Cocktail Tables",
  "Collection": "Edina",
  "Brand": "",
  "PDMDescription": "EDINA ESPRESSO COCKTAIL TABLE",
  "Title": "Edina Espresso Cocktail Table",
  "AdvertisingCopy": "Elevate your style with the versatile Edina...",
  "Image": "ct_coff_2213124P_edina_espresso",
  "AdditionalNotes": "",
  "Dimensions": "60\"W x 28\"D x 18.25\"H",
  "GenericName": "Cocktail Table",
  "Attributes": {
    "Color": ["Espresso"],
    "Style": ["Contemporary"],
    "Material": ["Wood"],
    "Theme": ["Edina"]
  },
  "DeliveryType": "O",
  "DeliverySubType": "",
  "ShippingCode": "",
  "SingleItemRoom": false,
  "GroupKey": "",
  "GroupKeyModifier": "",
  "Divisions": {
    "FL": null,
    "SE": {
      "Active": false
    },
    "TX": null
  }
}
```

## CLI Commands

### Import with Field Mapping
```bash
# Preview field mapping
uv run python cli.py workflow import-resku-items "data/file.xlsx" --sheet-name "Items" --preview-mapping

# Test with limited rows
uv run python cli.py workflow import-resku-items "data/file.xlsx" --sheet-name "Items" --limit 1

# Execute import
uv run python cli.py workflow import-resku-items "data/file.xlsx" --sheet-name "Items" --execute
```

### Available Options
- `--sheet-name`: Excel sheet name (required for multi-sheet files)
- `--limit N`: Process only first N rows (for testing)
- `--preview-mapping`: Show field mapping preview
- `--execute`: Actually create items (default is dry-run)
- `--help`: Show all available options