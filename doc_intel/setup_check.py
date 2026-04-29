"""Quick start guide for setting up Document Intelligence Tool."""

import os
import sys
from pathlib import Path


def check_requirements():
    """Check if all required tools and dependencies are installed."""
    print("🔍 Checking system requirements...\n")

    checks = {
        "Python 3.12+": check_python(),
        "Ollama Running": check_ollama(),
        "OpenRouter API Key": check_openrouter_key(),
        "Virtual Environment": check_venv(),
    }

    print("\n✅ Requirements Check Summary:")
    print("=" * 50)
    for requirement, status in checks.items():
        symbol = "✓" if status else "✗"
        print(f"{symbol} {requirement}")

    all_passed = all(checks.values())
    return all_passed


def check_python():
    """Check Python version."""
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 12:
        print(f"✓ Python {version_info.major}.{version_info.minor} (3.12+ required)")
        return True
    else:
        print(f"✗ Python {version_info.major}.{version_info.minor} - Upgrade to 3.12+")
        return False


def check_venv():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✓ Virtual environment active")
        return True
    else:
        print("✗ Not in virtual environment")
        return False


def check_ollama():
    """Check if Ollama is running."""
    try:
        import httpx

        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2)
            print(f"✓ Ollama running on localhost:11434")
            return True
        except Exception:
            print("✗ Ollama not running at localhost:11434")
            print("  → Run: ollama serve")
            return False
    except ImportError:
        print("⚠ httpx not installed, skipping Ollama check")
        return False


def check_openrouter_key():
    """Check if OpenRouter API key is configured."""
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        masked_key = key[:7] + "*" * (len(key) - 10) + key[-3:]
        print(f"✓ OpenRouter API key configured: {masked_key}")
        return True
    else:
        print("✗ OPENROUTER_API_KEY not set")
        print("  → Add to .env: OPENROUTER_API_KEY=your_key_here")
        return False


def setup_instructions():
    """Print setup instructions."""
    print("\n" + "=" * 70)
    print("📋 SETUP INSTRUCTIONS")
    print("=" * 70 + "\n")

    instructions = """
1. CREATE VIRTUAL ENVIRONMENT:
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

2. INSTALL DEPENDENCIES:
   pip install -e .

3. CONFIGURE ENVIRONMENT:
   cp .env.example .env
   # Edit .env and add your OpenRouter API key

4. START OLLAMA:
   ollama serve

5. PREPARE DOCUMENTS:
   mkdir -p data/docs
   cp /path/to/documents/* data/docs/

6. INGEST DOCUMENTS:
   docintel ingest ./data/docs

7. ASK QUESTIONS:
   docintel ask "Your question here?"
   docintel ask "Your question here?" --debug  # With debug info
    """
    print(instructions)


def quick_start():
    """Quick start guide."""
    print("\n" + "=" * 70)
    print("⚡ QUICK START")
    print("=" * 70 + "\n")

    quick_cmds = """
# Test setup
python example.py

# Check vector database
docintel info

# Ingest documents
docintel ingest ./data/docs -v

# Ask question with debug
docintel ask "What is this about?" --debug

# Stream response
docintel ask "Tell me more..." --stream

# View logs
tail -f logs/queries.log

# Clear database
docintel clear-db
    """
    print(quick_cmds)


if __name__ == "__main__":
    all_ok = check_requirements()

    if not all_ok:
        print("\n⚠️  Some requirements are missing. Follow setup instructions below:\n")

    setup_instructions()
    quick_start()

    if all_ok:
        print("\n✅ All systems ready! You can now use 'docintel' commands.")
    else:
        print("\n❌ Please fix missing requirements before proceeding.")
