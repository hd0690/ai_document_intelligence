"""Debug utilities for Document Intelligence Tool."""

from typing import Any

from config import settings


def print_debug(title: str, content: Any, separator: bool = True) -> None:
    """
    Print debug information if debug mode is enabled.

    Args:
        title: Debug section title
        content: Content to print
        separator: Whether to print separator lines
    """
    if not settings.debug:
        return

    if separator:
        print("\n" + "=" * 80)
    print(f"\n[DEBUG] {title}")
    print("-" * 80)

    if isinstance(content, str):
        print(content)
    elif isinstance(content, list):
        for i, item in enumerate(content, 1):
            print(f"{i}. {item}\n")
    elif isinstance(content, dict):
        for key, value in content.items():
            print(f"{key}: {value}")
    else:
        print(content)

    if separator:
        print("=" * 80 + "\n")


def print_retrieved_chunks(chunks: list[str]) -> None:
    """Print retrieved chunks in debug mode."""
    if not settings.debug:
        return

    print("\n" + "=" * 80)
    print("[DEBUG] RETRIEVED CHUNKS")
    print("-" * 80)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}]")
        print(f"{chunk}")
        print("-" * 40)
    print("=" * 80 + "\n")


def print_query_pipeline(query: str, chunks: list[str], prompt: str) -> None:
    """Print the entire query pipeline in debug mode."""
    if not settings.debug:
        return

    print("\n" + "🔍 " * 20)
    print("[DEBUG] QUERY PIPELINE")
    print("🔍 " * 20)

    print("\n1️⃣  USER QUERY:")
    print(f"{query}")

    print("\n2️⃣  RETRIEVED CHUNKS:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}]")
        print(f"{chunk}")

    print("\n3️⃣  FINAL PROMPT TO LLM:")
    print(f"{prompt}")

    print("\n" + "🔍 " * 20 + "\n")
