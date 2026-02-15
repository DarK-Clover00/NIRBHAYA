"""
Simple startup script for NIRBHAYA backend
Handles Python path configuration automatically
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the application
if __name__ == "__main__":
    import uvicorn
    from backend.config import settings
    
    print("=" * 60)
    print("🚀 Starting NIRBHAYA Women's Safety API")
    print("=" * 60)
    print(f"📍 API will be available at: http://localhost:{settings.API_PORT}")
    print(f"📚 API Documentation: http://localhost:{settings.API_PORT}/docs")
    print(f"❤️  Health Check: http://localhost:{settings.API_PORT}/health")
    print("=" * 60)
    print("\n⚠️  NOTE: Make sure PostgreSQL and Redis are running!")
    print("   - PostgreSQL: localhost:5432")
    print("   - Redis: localhost:6379")
    print("\n💡 Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
