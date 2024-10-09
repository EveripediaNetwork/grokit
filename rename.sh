#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Set sed command based on availability
if command_exists gsed; then
    sed_cmd="gsed"
else
    sed_cmd="sed"
fi

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local input

    if [ -z "$default" ]; then
        read -ep "${prompt}: " input
    else
        read -ep "${prompt} [${default}]: " input
    fi
    echo "${input:-$default}"
}

# Prompt for package information
PACKAGE=$(prompt_with_default "Package name" "")
DESCRIPTION=$(prompt_with_default "Package description" "")
URL=$(prompt_with_default "Package URL" "")
AUTHOR=$(prompt_with_default "Author name" "Rodrigo Martínez (brunneis)")
EMAIL=$(prompt_with_default "Author email" "dev@brunneis.com")

# Function to perform sed replacement
sed_replace() {
    local pattern="$1"
    local replacement="$2"
    local file="$3"
    $sed_cmd -i "s~${pattern}~${replacement}~g" "$file"
}

# Update files
sed_replace "package_name" "$PACKAGE" "package_name/__init__.py"
mv "package_name/package_name.py" "package_name/${PACKAGE}.py"
mv "package_name" "$PACKAGE"

# Update pyproject.toml
sed_replace "package_name" "$PACKAGE" "pyproject.toml"
sed_replace "description_value" "$DESCRIPTION" "pyproject.toml"
sed_replace "url_value" "$URL" "pyproject.toml"
sed_replace "author_value" "$AUTHOR" "pyproject.toml"
sed_replace "email@example.com" "$EMAIL" "pyproject.toml"

# Clean up
rm "rename.sh"

echo "Package renaming completed successfully."
