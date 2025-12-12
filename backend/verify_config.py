"""
Configuration Verification Script
Checks all critical configurations before deployment
"""
import os
import sys

def check_env_var(name, required=True):
    value = os.getenv(name)
    if required and not value:
        print(f"❌ MISSING: {name}")
        return False
    elif value:
        # Mask sensitive values
        if any(keyword in name for keyword in ['KEY', 'PASSWORD', 'SECRET']):
            display = value[:10] + '...' if len(value) > 10 else '***'
        else:
            display = value
        print(f"✅ {name}: {display}")
        return True
    else:
        print(f"⚠️  OPTIONAL: {name} (not set)")
        return True

def main():
    print("=" * 60)
    print("UnLimi Backend Configuration Verification")
    print("=" * 60)
    print()

    all_ok = True

    print("🔍 Checking Required Environment Variables:")
    print("-" * 60)

    # Required variables
    all_ok &= check_env_var("DATABASE_URL", required=True)
    all_ok &= check_env_var("SECRET_KEY", required=True)
    all_ok &= check_env_var("OPENAI_API_KEY", required=True)

    print()
    print("🔍 Checking Optional Environment Variables:")
    print("-" * 60)

    # Optional variables
    check_env_var("AGNO_DB_URL", required=False)
    check_env_var("VITE_API_URL", required=False)

    print()
    print("=" * 60)

    if all_ok:
        print("✅ All required configurations are set!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some required configurations are missing!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
