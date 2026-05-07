"""
Generator: formats a prompt from retrieved context and calls the LLM.

Why a separate generator module?
  - Keeps prompt logic in one place (easy to iterate)
  - LLM provider is swappable: Ollama (local) or OpenRouter (cloud)
  - Purely functional — easy to unit test with a mock LLM

Prompt strategy (Phase 1):
  Simple "Answer based on the context below" RAG prompt.
  The LLM is explicitly told to say "I don't know" if the answer isn't
  present — this reduces hallucination.
"""

import logging

logger = logging.getLogger(__name__)

_RAG_PROMPT_TEMPLATE = """\
You are a helpful assistant that answers questions based strictly on the provided context.
If the answer is not present in the context, say "I don't have enough information to answer that."
Do not make up information.

Context:
{context}

Question: {question}

Answer:"""


def _build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    return _RAG_PROMPT_TEMPLATE.format(context=context, question=question)


def _call_ollama(prompt: str, base_url: str, model: str) -> str:
    try:
        from ollama import Client
    except ImportError as e:
        raise RuntimeError("ollama Python client not installed. Run: uv add ollama") from e

    client = Client(host=base_url)
    response = client.generate(model=model, prompt=prompt)
    return response["response"]


def _call_openrouter(prompt: str, api_key: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("openai package not installed. Run: uv add openai") from e

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content or ""


def generate_answer(
    question: str,
    context_chunks: list[str],
    llm_provider: str,
    ollama_base_url: str,
    ollama_model: str,
    openrouter_api_key: str,
    openrouter_model: str,
) -> str:
    """
    Generate an answer from retrieved context chunks using the configured LLM.

    Args:
        question:        The user's question.
        context_chunks:  List of retrieved text chunks to use as context.
        llm_provider:    "ollama" or "openrouter".
        ...              Provider-specific connection details from settings.

    Returns:
        The LLM's answer string.
    """
    if not context_chunks:
        return "No relevant documents were found to answer your question."

    prompt = _build_prompt(question, context_chunks)
    logger.info("Calling LLM (provider=%s) for question: %.80s...", llm_provider, question)

    if llm_provider == "ollama":
        return _call_ollama(prompt, base_url=ollama_base_url, model=ollama_model)
    elif llm_provider == "openrouter":
        return _call_openrouter(prompt, api_key=openrouter_api_key, model=openrouter_model)
    else:
        raise ValueError(f"Unknown LLM provider: {llm_provider!r}")
