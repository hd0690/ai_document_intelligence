"""Document Intelligence Tool - CLI using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from config import settings
from ingestion import load_documents, chunk_documents, generate_embeddings
from retrieval import VectorStoreManager, DocumentRetriever
from llm import LLMGenerator
from utils import setup_logger, get_logger, log_query, print_query_pipeline

# Initialize CLI and console
app = typer.Typer(help="Document Intelligence Tool - RAG System")
console = Console()

# Setup logger
logger = get_logger(__name__)


@app.command()
def ingest(
    directory: str = typer.Argument(..., help="Directory path containing documents to ingest"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Ingest documents from a directory and store them in the vector database.

    Example:
        docintel ingest ./documents
    """
    console.print(Panel.fit("[bold cyan]Document Ingestion[/bold cyan]", border_style="cyan"))

    try:
        # Validate directory
        dir_path = Path(directory)
        if not dir_path.exists():
            console.print(f"[red]Error: Directory not found: {directory}[/red]")
            raise typer.Exit(code=1)

        if not dir_path.is_dir():
            console.print(f"[red]Error: Path is not a directory: {directory}[/red]")
            raise typer.Exit(code=1)

        console.print(f"[yellow]📂 Loading documents from:[/yellow] {directory}")

        # Step 1: Load documents
        documents = load_documents(directory)
        console.print(f"[green]✓ Loaded {len(documents)} documents[/green]")

        # Step 2: Chunk documents
        console.print("[yellow]📄 Chunking documents...[/yellow]")
        chunks = chunk_documents(documents)
        console.print(f"[green]✓ Created {len(chunks)} chunks[/green]")

        # Step 3: Generate embeddings
        console.print("[yellow]🔢 Generating embeddings...[/yellow]")
        nodes_with_embeddings = generate_embeddings(chunks)
        console.print(f"[green]✓ Generated embeddings for {len(nodes_with_embeddings)} nodes[/green]")

        # Step 4: Store in vector database
        console.print("[yellow]💾 Storing in vector database...[/yellow]")
        vector_store = VectorStoreManager()
        vector_store.add_documents(nodes_with_embeddings)
        console.print("[green]✓ Successfully stored documents in vector database[/green]")

        # Display collection info
        info = vector_store.get_collection_info()
        console.print(
            Panel(
                f"[cyan]Collection:[/cyan] {info['name']}\n"
                f"[cyan]Total Documents:[/cyan] {info['count']}\n"
                f"[cyan]Database Path:[/cyan] {info['db_path']}",
                title="Vector Store Info",
                border_style="green",
            )
        )

        console.print("[bold green]✅ Ingestion complete![/bold green]")

    except Exception as e:
        console.print(f"[red]❌ Error during ingestion: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def ask(
    query: str = typer.Argument(..., help="Question to ask about the documents"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    stream: bool = typer.Option(False, "--stream", "-s", help="Stream the response"),
) -> None:
    """
    Ask a question and get an answer from the documents.

    Example:
        docintel ask "What is the main topic?"
        docintel ask "What is the main topic?" --debug
        docintel ask "What is the main topic?" --stream
    """
    console.print(Panel.fit("[bold cyan]Query Processor[/bold cyan]", border_style="cyan"))

    try:
        # Update debug setting
        original_debug = settings.debug
        settings.debug = debug

        console.print(f"[yellow]❓ Query:[/yellow] {query}\n")

        # Step 1: Retrieve relevant documents
        console.print("[yellow]🔍 Retrieving relevant documents...[/yellow]")
        retriever = DocumentRetriever()
        retrieved_chunks = retriever.retrieve(query)
        console.print(f"[green]✓ Retrieved {len(retrieved_chunks)} relevant chunks[/green]\n")

        if debug:
            print_query_pipeline(query, retrieved_chunks, "")

        # Step 2: Generate response
        console.print("[yellow]🤖 Generating response...[/yellow]\n")
        llm = LLMGenerator()
        prompt = llm.generate_prompt(query, retrieved_chunks)

        if debug:
            console.print(
                Panel(
                    Syntax(prompt, "python", theme="monokai", line_numbers=False),
                    title="[yellow]Final Prompt[/yellow]",
                    border_style="yellow",
                )
            )

        # Generate response
        if stream:
            console.print("[cyan]Answer:[/cyan]")
            full_response = ""
            for chunk in llm.stream_generate(query, retrieved_chunks):
                console.print(chunk, end="", highlight=False)
                full_response += chunk
            console.print()  # New line after streaming
        else:
            response = llm.generate(query, retrieved_chunks)
            console.print(f"[cyan]Answer:[/cyan]\n{response}\n")
            full_response = response

        # Step 3: Log the query
        log_query(query, retrieved_chunks, prompt, full_response)

        console.print("[bold green]✅ Query complete![/bold green]")

        # Show retrieved chunks in debug mode
        if debug:
            console.print(
                Panel(
                    "\n".join(
                        [f"[{i}] {chunk[:100]}..." for i, chunk in enumerate(retrieved_chunks, 1)]
                    ),
                    title="Retrieved Chunks",
                    border_style="yellow",
                )
            )

        # Restore original debug setting
        settings.debug = original_debug

    except Exception as e:
        console.print(f"[red]❌ Error processing query: {e}[/red]")
        if debug:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def clear_db() -> None:
    """Clear all documents from the vector database."""
    console.print(Panel.fit("[bold red]Clear Database[/bold red]", border_style="red"))

    try:
        confirm = typer.confirm("[yellow]Are you sure you want to clear all documents?[/yellow]")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

        vector_store = VectorStoreManager()
        vector_store.clear_collection()
        console.print("[bold green]✅ Vector database cleared![/bold green]")

    except Exception as e:
        console.print(f"[red]❌ Error clearing database: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def info() -> None:
    """Display vector database information."""
    console.print(Panel.fit("[bold cyan]Database Information[/bold cyan]", border_style="cyan"))

    try:
        vector_store = VectorStoreManager()
        info = vector_store.get_collection_info()

        console.print(
            Panel(
                f"[cyan]Collection Name:[/cyan] {info['name']}\n"
                f"[cyan]Total Documents:[/cyan] {info['count']}\n"
                f"[cyan]Database Path:[/cyan] {info['db_path']}\n"
                f"[cyan]Log File:[/cyan] {settings.log_file}",
                title="Vector Store Status",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]❌ Error retrieving database info: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
