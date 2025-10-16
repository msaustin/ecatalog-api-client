# Data Directory

Place your spreadsheet files here for import workflows.

## Supported Formats

- **CSV**: `.csv` files
- **Excel**: `.xlsx`, `.xls` files

## Expected Columns

The item import workflow looks for these columns (case-insensitive):

### Required Fields
- `SKU` - Stock Keeping Unit
- `Site` - Marketplace site (RTG, OTG, etc.)
- `Category` - Item category
- `Collection` - Collection name
- `PDM_Description` - PDM description
- `Title` - Item title
- `Advertising_Copy` - Marketing description
- `Image` - Image filename
- `Dimensions` - Item dimensions (e.g., "84w x 36d x 32h")
- `Generic_Name` - Generic product name
- `Delivery_Type` - Delivery type (D, O, etc.)

### Optional Fields
- `Brand` - Brand name
- `Additional_Notes` - Extra notes
- `Delivery_Sub_Type` - Delivery sub-type
- `Shipping_Code` - Shipping code
- `Group_Key` - Group key
- `Group_Key_Modifier` - Group key modifier
- `Single_Item_Room` - Boolean for single item room

### Division Fields
- `FL_Active` - Florida division active (TRUE/FALSE)
- `SE_Active` - Southeast division active (TRUE/FALSE)
- `TX_Active` - Texas division active (TRUE/FALSE)

### Attribute Fields
- `Color` - Colors (comma-separated)
- `Style` - Styles (comma-separated)
- `Material` - Materials (comma-separated)
- `Finish` - Finishes (comma-separated)
- `Features` - Features (comma-separated)
- `Size` - Sizes (comma-separated)
- `Shape` - Shapes (comma-separated)
- `Theme` - Themes (comma-separated)
- `Team` - Teams (comma-separated)

## Sample Files

- `sample_items.csv` - Example CSV format for item imports

## Usage

```bash
# Preview what would be imported (dry-run mode)
uv run python cli.py workflow import-items data/sample_items.csv

# Actually import items
uv run python cli.py workflow import-items data/sample_items.csv --execute
```