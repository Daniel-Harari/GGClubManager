#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Read .env file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
        continue
    fi

    # Remove any trailing comments
    line=$(echo "$line" | sed 's/[[:space:]]*#.*$//')

    # Trim whitespace
    line=$(echo "$line" | xargs)

    # Export the variable
    if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
        export "$line"
        echo "Exported: $line"
    fi
done < .env

echo "Environment variables loaded successfully!"