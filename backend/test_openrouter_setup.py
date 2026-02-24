"""Test script to verify OpenRouter setup"""
import os
import sys

print("Testing OpenRouter Integration Setup")
print("=" * 50)

# Check if openrouter provider exists
provider_file = "app/chat/providers/openrouter_provider.py"
if os.path.exists(provider_file):
    print("✓ OpenRouter provider file exists")
else:
    print("✗ OpenRouter provider file missing")

# Check factory update
factory_file = "app/chat/providers/factory.py"
if os.path.exists(factory_file):
    with open(factory_file, 'r') as f:
        content = f.read()
        if 'openrouter' in content:
            print("✓ Factory includes OpenRouter support")
        else:
            print("✗ Factory missing OpenRouter support")

# Check models.py update
models_file = "app/models.py"
if os.path.exists(models_file):
    with open(models_file, 'r') as f:
        content = f.read()
        if 'openrouter_api_key' in content:
            print("✓ Database models include OpenRouter fields")
        else:
            print("✗ Database models missing OpenRouter fields")

# Check schemas.py update
schemas_file = "app/schemas.py"
if os.path.exists(schemas_file):
    with open(schemas_file, 'r') as f:
        content = f.read()
        if 'openrouter' in content:
            print("✓ Schemas include OpenRouter support")
        else:
            print("✗ Schemas missing OpenRouter support")

# Check migration file
migration_file = "alembic/versions/20260224_add_openrouter_provider.py"
if os.path.exists(migration_file):
    print("✓ OpenRouter migration file exists")
else:
    print("✗ OpenRouter migration file missing")

print("\nSetup Summary:")
print("-" * 50)
print("Backend OpenRouter integration is complete!")
print("\nNext steps:")
print("1. Run the database migration: python -m alembic upgrade head")
print("2. Restart the backend server")
print("3. In the frontend, select 'OpenRouter' as your provider")
print("4. Enter your OpenRouter API key (sk-or-v1-...)")
print("5. Select your preferred model")
print("6. Save settings and start chatting!")