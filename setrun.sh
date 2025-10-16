#!/bin/bash

# setrun.sh - Set the .env.run file to source either .env.local or .env.prod
# Usage: ./setrun.sh [local|prod]

set -e  # Exit on any error

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: No environment specified"
    echo ""
    echo "Usage: ./setrun.sh [local|prod]"
    echo ""
    echo "Examples:"
    echo "  ./setrun.sh local   # Sets .env.run to source .env.local"
    echo "  ./setrun.sh prod    # Sets .env.run to source .env.prod"
    exit 1
fi

# Get the environment argument and convert to lowercase
ENV_ARG=$(echo "$1" | tr '[:upper:]' '[:lower:]')

# Validate argument
if [ "$ENV_ARG" != "local" ] && [ "$ENV_ARG" != "prod" ]; then
    echo "❌ Error: Invalid environment '$1'"
    echo ""
    echo "Valid options: local, prod"
    echo ""
    echo "Usage: ./setrun.sh [local|prod]"
    exit 1
fi

# Set the source file based on argument
if [ "$ENV_ARG" = "local" ]; then
    SOURCE_FILE=".env.local"
    ENV_DISPLAY="Local Development"
elif [ "$ENV_ARG" = "prod" ]; then
    SOURCE_FILE=".env.prod"
    ENV_DISPLAY="Production"
fi

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: Environment file '$SOURCE_FILE' not found"
    echo ""
    echo "Please ensure the following file exists:"
    echo "  $SOURCE_FILE"
    exit 1
fi

# Create/update .env.run file
echo "source $SOURCE_FILE" > .env.run

# Provide confirmation
echo "✅ Environment successfully set to: $ENV_DISPLAY"
echo ""
echo "📁 Updated .env.run:"
echo "   source $SOURCE_FILE"
echo ""
echo "🔄 To apply changes, restart your application or run:"
echo "   source .env.run"

# Optional: Show current content of .env.run for verification
echo ""
echo "📋 Current .env.run content:"
cat .env.run
