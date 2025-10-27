#!/usr/bin/env python3
"""
PantryVision Setup Script

This script helps users set up PantryVision for the first time.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template."""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists!")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return False
    
    # Copy template to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template!")
    print("📝 Please edit .env file and add your OpenAI API key")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import openai
        import colorama
        import dotenv
        print("✅ All required dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False


def main():
    """Main setup function."""
    print("🍽️  PantryVision Setup")
    print("=" * 30)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create .env file
    create_env_file()
    
    print("\n🚀 Setup complete!")
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python src/main.py")
    print("\n💡 Get your OpenAI API key from: https://platform.openai.com/api-keys")


if __name__ == "__main__":
    main()
