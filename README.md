# eCatalog CLI Tool

A command-line tool and workflow engine for interacting with eCatalog FastAPI application. Includes item/room management, bulk imports from spreadsheets, and custom workflow scripts.

## Features

- **CLI Commands**: Interactive command-line interface for all operations
- **Item Management**: Create, read, update, delete items by SKU
- **Room Management**: Create, read, update, delete rooms by SKU
- **SKU Lookup**: Check SKU existence, type (Item/Room), and division availability
- **SKU Substitution**: Replace SKUs in package products with prevalidation
- **Bulk Import Workflows**: Import items from CSV/Excel spreadsheets
- **Division Support**: FL, SE, TX regional divisions
- **Rich Output**: Formatted tables and progress bars using Rich
- **Dry-Run Mode**: Preview operations before executing
- **Type-safe models** with Pydantic validation

## Installation

This project uses UV package manager for dependency management.

```bash
# Install UV if you haven't already
pip install uv

# Install dependencies
uv sync

# Activate virtual environment (if needed)
source .venv/bin/activate
```

## Quick Start

```bash
# Install dependencies
uv sync

# Check API connection
uv run python cli.py status

# Look up a SKU
uv run python cli.py lookup 83288348

# Get complete SKU details (automatic lookup + item/room details)
uv run python cli.py details 83288348

# Get item details directly
uv run python cli.py item get 83288348

# Get room details directly
uv run python cli.py room get 7013461P

# Preview bulk import from resku spreadsheet (dry-run)
uv run python cli.py workflow import-resku-items "data/BUILD_RESKU_NEFS 3123-CB_OCCASIONAL.xlsx" --sheet-name "Items"

# Actually import items
uv run python cli.py workflow import-resku-items "data/BUILD_RESKU_NEFS 3123-CB_OCCASIONAL.xlsx" --sheet-name "Items" --execute

# Update an item
uv run python cli.py item update TEST001 --title "New Title" --dimensions "12w x 12d x 12h"
```

## CLI Commands

### Basic Operations
```bash
# Check API server status
uv run python cli.py status

# Look up any SKU
uv run python cli.py lookup [SKU]

# Get complete SKU details (lookup + full item/room details)
uv run python cli.py details [SKU]
```

### Item Management
```bash
# Get item by SKU
uv run python cli.py item get [SKU]

# Update item fields
uv run python cli.py item update [SKU] --title "New Title" --advertising-copy "New description"

# Delete item
uv run python cli.py item delete [SKU] [SITE] --division FL
```

### Room Management
```bash
# Get room by SKU
uv run python cli.py room get [SKU]
```

### Bulk Operations
```bash
# Import items from resku spreadsheet (preview mode)
uv run python cli.py workflow import-resku-items "data/your_file.xlsx" --sheet-name "Items"

# Preview data field mapping
uv run python cli.py workflow import-resku-items "data/your_file.xlsx" --sheet-name "Items" --preview-mapping

# Test with only first N items
uv run python cli.py workflow import-resku-items "data/your_file.xlsx" --sheet-name "Items" --limit 2

# Actually create items
uv run python cli.py workflow import-resku-items "data/your_file.xlsx" --sheet-name "Items" --execute

# Create only first N items (for testing)
uv run python cli.py workflow import-resku-items "data/your_file.xlsx" --sheet-name "Items" --limit 1 --execute
```

### SKU Substitution
```bash
# Prevalidate substitution
uv run python cli.py substitution prevalidate RTG OLD_SKU --substituted-skus NEW_SKU --divisions FL SE
```

## Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[Field Mapping](docs/field-mapping.md)** - Spreadsheet to API field mapping guide

## Project Structure

```
├── README.md
├── pyproject.toml          # UV/pip configuration
├── cli.py                  # Main CLI application
├── ecatalog_client.py      # API client library
├── data/                   # Spreadsheet files for import
│   ├── README.md          # Data format documentation
│   └── sample_items.csv   # Sample import file
├── workflows/             # Workflow scripts
│   ├── __init__.py
│   └── import_items.py    # Bulk item import from spreadsheet
└── docs/
    ├── api.md             # API documentation
    ├── field-mapping.md   # Spreadsheet field mapping guide
    └── openapi.json       # OpenAPI specification
```

## Configuration

The client is configured to work with APIs at `http://127.0.0.1:8000` by default. You can specify a different base URL:

```bash
uv run python cli.py --api-url https://your-api-server.com [command]
```

### OAuth Authentication

By default, the CLI uses OAuth 2.0 with PKCE for authentication. On first run, you'll be prompted to visit an authorization URL:

```bash
# Normal operation with OAuth authentication
uv run python cli.py details 83288348

# Skip OAuth for testing/development
uv run python cli.py --no-auth details 83288348
```

The OAuth configuration uses:
- **Client ID**: `product-readiness-client`
- **Scopes**: `catalog:read catalog:validate workflows:submit workflows:monitor openid profile`
- **Flow**: Authorization Code with PKCE

## Error Handling

The client includes comprehensive error handling:

- HTTP errors are logged and re-raised
- JSON parsing errors are handled gracefully
- Invalid model data is validated with Pydantic
- Network issues are caught and logged

## Contributing

1. Ensure UV is installed
2. Run `uv sync` to install dependencies
3. Make your changes
4. Test with `uv run python example.py`

## License

MIT License