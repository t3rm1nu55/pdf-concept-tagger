#!/usr/bin/env python3
"""
Test Setup Script

Quick verification that MVP setup is correct.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all imports work."""
    print("🔍 Testing imports...")
    try:
        from app.main import app
        print("   ✅ app.main imports OK")
        
        from app.services.cognizant_proxy import CognizantProxyLLM
        print("   ✅ CognizantProxyLLM imports OK")
        
        from app.services.pdf_processor import PDFProcessor
        print("   ✅ PDFProcessor imports OK")
        
        from app.models.concept import Concept, Document, Relationship
        print("   ✅ Models import OK")
        
        from app.database.postgres import get_db, check_connection
        print("   ✅ Database imports OK")
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False


def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment...")
    
    proxy_endpoint = os.getenv("COGNIZANT_PROXY_ENDPOINT")
    proxy_key = os.getenv("COGNIZANT_PROXY_API_KEY")
    postgres_url = os.getenv("POSTGRES_URL")
    
    if proxy_endpoint:
        print(f"   ✅ COGNIZANT_PROXY_ENDPOINT: {proxy_endpoint[:50]}...")
    else:
        print("   ⚠️  COGNIZANT_PROXY_ENDPOINT not set")
    
    if proxy_key:
        print(f"   ✅ COGNIZANT_PROXY_API_KEY: {'*' * 20}...")
    else:
        print("   ⚠️  COGNIZANT_PROXY_API_KEY not set")
    
    if postgres_url:
        print(f"   ✅ POSTGRES_URL: postgresql://...")
    else:
        print("   ⚠️  POSTGRES_URL not set")
    
    return bool(proxy_endpoint and proxy_key and postgres_url)


def test_database_connection():
    """Test database connection."""
    print("\n🔍 Testing database connection...")
    try:
        import asyncio
        from app.database.postgres import check_connection
        
        is_connected = asyncio.run(check_connection())
        if is_connected:
            print("   ✅ Database connection OK")
            return True
        else:
            print("   ⚠️  Database connection failed (is PostgreSQL running?)")
            return False
    except Exception as e:
        print(f"   ⚠️  Database test error: {e}")
        print("   💡 Start PostgreSQL: docker-compose -f docker-compose.mvp.yml up -d")
        return False


def test_proxy_config():
    """Test proxy configuration."""
    print("\n🔍 Testing proxy configuration...")
    try:
        from app.services.cognizant_proxy import CognizantProxyLLM
        
        proxy = CognizantProxyLLM()
        print(f"   ✅ Proxy configured: {proxy.provider}/{proxy.model}")
        return True
    except ValueError as e:
        print(f"   ⚠️  Proxy configuration error: {e}")
        print("   💡 Set COGNIZANT_PROXY_ENDPOINT and COGNIZANT_PROXY_API_KEY in .env")
        return False
    except Exception as e:
        print(f"   ⚠️  Proxy test error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 MVP Setup Verification\n")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("Database", test_database_connection()))
    results.append(("Proxy Config", test_proxy_config()))
    
    print("\n" + "=" * 50)
    print("\n📊 Results:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "⚠️  CHECK"
        print(f"   {status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("\n🎉 All checks passed! MVP is ready to use.")
        print("\nNext steps:")
        print("  1. Start server: uvicorn app.main:app --reload")
        print("  2. Test API: curl http://localhost:8000/health")
    else:
        print("\n⚠️  Some checks need attention. See above for details.")
        print("\nQuick fixes:")
        print("  1. Configure .env file (see .env.example)")
        print("  2. Start PostgreSQL: docker-compose -f docker-compose.mvp.yml up -d")
        print("  3. Run migrations: alembic upgrade head")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
