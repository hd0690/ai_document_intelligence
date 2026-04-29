"""LLM response generation using Ollama."""

from typing import Optional

import ollama

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMGenerator:
    """Generates responses using a local Ollama model."""

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the LLM generator.

        Args:
            model: Ollama model name (uses settings.ollama_llm_model if None)
        """
        self.model = model or settings.ollama_llm_model
        self.base_url = settings.ollama_base_url

        logger.info(f"LLMGenerator initialized with Ollama model: {self.model}")

    def generate_prompt(self, query: str, retrieved_chunks: list[str]) -> str:
        """
        Build the final prompt for the LLM.

        Args:
            query: User's query
            retrieved_chunks: List of retrieved document chunks

        Returns:
            Formatted prompt string
        """
        context = "\n\n".join(retrieved_chunks)

        prompt = f"""You are a helpful assistant. Answer the question based on the provided context. If the context doesn't contain the answer, say "I don't have enough information to answer this question."

Context:
{context}

Question:
{query}

Answer:"""

        return prompt

    def generate(self, query: str, retrieved_chunks: list[str]) -> str:
        """
        Generate a response using the local Ollama model.

        Args:
            query: User's query
            retrieved_chunks: List of retrieved document chunks

        Returns:
            Generated response from the LLM
        """
        prompt = self.generate_prompt(query, retrieved_chunks)

        logger.info(f"Generating response for query: {query}")
        logger.debug(f"Using Ollama model: {self.model}")

        try:
            client = ollama.Client(host=self.base_url)
            response = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7},
            )
            generated_text = response.message.content

            logger.info("Successfully generated response")
            return generated_text

        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    def stream_generate(self, query: str, retrieved_chunks: list[str]):
        """
        Generate a response using Ollama streaming.

        Args:
            query: User's query
            retrieved_chunks: List of retrieved document chunks

        Yields:
            Chunks of generated text
        """
        prompt = self.generate_prompt(query, retrieved_chunks)

        logger.info(f"Generating response (streaming) for query: {query}")

        try:
            client = ollama.Client(host=self.base_url)
            stream = client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7},
                stream=True,
            )
            for chunk in stream:
                content = chunk.message.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise

        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
