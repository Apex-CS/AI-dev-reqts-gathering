from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
import os
import json
import chromadb

# /Volumes/Respaldos/Projects/AI-dev-reqts-gathering/src/functions/chroma_settings.py

# Chroma client imports (handle different versions)
try:
    try:
        # optional config import; some chroma versions have Settings
        from chromadb.config import Settings  # type: ignore
    except Exception:
        Settings = None  # type: ignore
except Exception as e:  # chromadb not installed
    chromadb = None  # type: ignore
    Settings = None  # type: ignore
    _chroma_import_error = e  # keep for error messages

# Streamlit lazy import placeholder
_streamlit_available = True
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # type: ignore
    _streamlit_available = False


def init_chroma_client(persist_directory: Optional[str] = None, chroma_db_impl: Optional[str] = None):
    """
    Initialize and return a chromadb client.
    If persist_directory is provided, tries to use Settings to persist to disk.
    """
    if chromadb is None:
        raise RuntimeError(f"chromadb is not installed: {_chroma_import_error}")

    # Prefer explicit Settings if available (for persistence options).
    # When persisting locally, default to a local DB impl to avoid attempting to connect to a remote tenant.
    if Settings is not None:
        settings_kwargs = {}
        if persist_directory:
            settings_kwargs["persist_directory"] = persist_directory
        # prefer explicit impl if provided, otherwise default to local duckdb+parquet for persistence
        if chroma_db_impl:
            settings_kwargs["chroma_db_impl"] = chroma_db_impl
        elif persist_directory:
            settings_kwargs["chroma_db_impl"] = "duckdb+parquet"
        # Try constructing a Settings object even if no kwargs were provided; some chroma versions require Settings()
        try:
            return chromadb.Client(Settings(**settings_kwargs))
        except Exception:
            # If constructing with Settings fails, continue to other fallbacks below.
            pass

    # Fallback: try passing known kwargs directly to Client (older/newer chromadb versions may accept them).
    if persist_directory or chroma_db_impl:
        try:
            kwargs = {}
            if persist_directory:
                kwargs["persist_directory"] = persist_directory
            if chroma_db_impl:
                kwargs["chroma_db_impl"] = chroma_db_impl
            elif persist_directory:
                kwargs["chroma_db_impl"] = "duckdb+parquet"
            return chromadb.Client(**kwargs)
        except TypeError:
            # Client didn't accept kwargs; fall through to other construction attempts below.
            pass
        except Exception as e:
            raise RuntimeError("Failed to initialize chromadb client with provided persistence options.") from e

    # Final fallback: try default client construction and also try Client(Settings()) if available,
    # and surface the original exception for debugging.
    last_exc: Optional[BaseException] = None

    # Prefer constructing with a Settings() instance if available (some chroma versions require it)
    if Settings is not None:
        try:
            return chromadb.Client(Settings())
        except Exception as e:
            last_exc = e

    # Next, explicitly prefer a local DB implementation to avoid connecting to a remote tenant named "default_tenant".
    try:
        kwargs = {}
        if persist_directory:
            kwargs["persist_directory"] = persist_directory
        # Use a local duckdb+parquet implementation by default to prevent remote tenant resolution.
        kwargs.setdefault("chroma_db_impl", "duckdb+parquet")
        return chromadb.Client(**kwargs)
    except TypeError:
        # Client didn't accept kwargs; try the bare constructor as a last resort.
        try:
            return chromadb.Client()
        except Exception as e:
            last_exc = e
    except Exception as e:
        last_exc = e

    # If we get here, all attempts failed; raise with the last underlying exception for clarity.
    raise RuntimeError(
        "Failed to initialize chromadb client; ensure chromadb is up-to-date or provide chroma_db_impl/persist_directory."
    ) from last_exc


def get_or_create_collection(client, name: str, metadata: Optional[Dict[str, Any]] = None, get_if_exists: bool = True):
    """
    Get a collection by name. If it doesn't exist and get_if_exists is False, raises.
    If it doesn't exist and get_if_exists is True, creates it.
    """
    # client.get_collection may raise if not exists; client.list_collections also available.
    try:
        return client.get_collection(name)
    except Exception:
        if not get_if_exists:
            raise
        # create collection; some versions accept metadata or metadata_schema
        try:
            if metadata is not None:
                return client.create_collection(name=name, metadata=metadata)
            return client.create_collection(name=name)
        except Exception as e:
            # some chroma versions use different signature; try without metadata
            try:
                return client.create_collection(name=name)
            except Exception:
                raise RuntimeError(f"Failed to get or create collection '{name}'") from e


def save_documents(
    client,
    collection_name: str,
    documents: Sequence[str],
    ids: Optional[Sequence[str]] = None,
    metadatas: Optional[Sequence[Dict[str, Any]]] = None,
    embeddings: Optional[Sequence[Sequence[float]]] = None,
) -> Dict[str, Any]:
    """
    Add documents (and optional ids, metadatas, embeddings) to a chroma collection.
    Returns the collection.add response or raises on error.
    """
    collection = get_or_create_collection(client, collection_name)
    kwargs = {"documents": list(documents)}
    if ids is not None:
        kwargs["ids"] = list(ids)
    if metadatas is not None:
        kwargs["metadatas"] = list(metadatas)
    if embeddings is not None:
        kwargs["embeddings"] = list(embeddings)
    try:
        return collection.add(**kwargs)
    except TypeError:
        # some chroma versions expect different param names; try alternate call
        return collection.add(documents=list(documents), ids=(list(ids) if ids else None))


def get_documents(
    client,
    collection_name: str,
    ids: Optional[Sequence[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Retrieve documents from a collection by ids or by filter (where).
    Returns dict with keys like 'ids', 'documents', 'metadatas'.
    """
    collection = get_or_create_collection(client, collection_name)
    try:
        if ids is not None:
            return collection.get(ids=list(ids))
        if where is not None:
            # some versions use where or where_document
            return collection.get(where=where, limit=limit) if limit else collection.get(where=where)
        # default: return all (may be expensive)
        return collection.get()
    except Exception as e:
        raise RuntimeError(f"Failed to get documents from '{collection_name}': {e}") from e


def query_collection(
    client,
    collection_name: str,
    query_embeddings: Optional[Sequence[float]] = None,
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query a collection using an embedding. If no embedding provided, raises.
    Returns query results (ids, documents, distances, metadatas).
    """
    if query_embeddings is None:
        raise ValueError("query_embeddings must be provided for vector query.")
    collection = get_or_create_collection(client, collection_name)
    try:
        return collection.query(query_embeddings=[list(query_embeddings)], n_results=n_results, where=where)
    except TypeError:
        # Some versions expect query_embeddings param name
        return collection.query(query_embedding=list(query_embeddings), n_results=n_results, where=where)
    except Exception as e:
        raise RuntimeError(f"Failed to query collection '{collection_name}': {e}") from e


def delete_documents(client, collection_name: str, ids: Sequence[str]) -> None:
    """
    Delete documents by ids from a collection.
    """
    collection = get_or_create_collection(client, collection_name)
    try:
        collection.delete(ids=list(ids))
    except Exception as e:
        # some versions use delete method signature with 'where' etc.
        try:
            collection.delete(ids=list(ids))
        except Exception:
            raise RuntimeError(f"Failed to delete ids from '{collection_name}': {e}") from e


def persist_client(client) -> None:
    """
    Persist chroma client data to disk (if supported).
    """
    try:
        # many chroma clients offer persist()
        client.persist()
    except Exception:
        # If persist not supported or client was configured without persistence, ignore
        pass


# ---------- Embedding and session-state helpers ----------
def _compute_embeddings_for_texts(texts: Sequence[str]) -> List[Sequence[float]]:
    """
    Compute embeddings for a list of texts.
    Tries Azure OpenAI embeddings via langchain_openai first, then falls back to sentence-transformers.
    Returns list of embedding vectors (lists of floats).
    """
    # Lazy imports so project can run without optional deps until feature is used.
    try:
        from langchain_openai import AzureOpenAIEmbeddings  # type: ignore

        # Construct with environment variables where possible; fall back to defaults
        emb_model = AzureOpenAIEmbeddings(
            model=os.environ.get("AZURE_EMBED_MODEL", "text-embedding-3-large"),
            deployment=os.environ.get("AZURE_OPENAI_EMBED_DEPLOYMENT", os.environ.get("AZURE_OPENAI_DEPLOYMENT")),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        )
        # langchain embeddings typically provide embed_documents
        return emb_model.embed_documents(list(texts))
    except Exception:
        # Try sentence-transformers locally
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            model_name = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
            model = SentenceTransformer(model_name)
            embs = model.encode(list(texts))
            # model.encode returns numpy array; convert rows to lists
            return [e.tolist() for e in embs]
        except Exception as e:
            raise RuntimeError("No embedding backend available. Install and configure Azure OpenAI or sentence-transformers.") from e


def save_session_state(
    client,
    collection_name: str,
    session_state: Dict[str, Any],
    overwrite: bool = True,
):
    """
    Vectorize and save Streamlit session_state into a Chroma collection.

    - session_state: a dict of key -> value (any JSON-serializable).
    - collection_name: name of the Chroma collection to use/create.
    - overwrite: if True, existing ids with same keys will be replaced via add/upsert.

    Each session entry is stored as a document with id equal to the key and metadata containing the original type.
    """
    # Normalize session_state into string documents
    keys = []
    docs = []
    metadatas: List[Dict[str, Any]] = []
    for k, v in session_state.items():
        try:
            # Prefer compact JSON representation for complex types
            text_val = json.dumps(v, default=str, ensure_ascii=False)
        except Exception:
            text_val = str(v)
        doc_text = f"{k}: {text_val}"
        keys.append(str(k))
        docs.append(doc_text)
        metadatas.append({"key": k, "py_type": type(v).__name__})

    # Compute embeddings; if it fails, save without embeddings (Chroma will compute if embedding_function set)
    try:
        embeddings = _compute_embeddings_for_texts(docs)
    except Exception:
        embeddings = None

    # Use existing save_documents helper (will create or get collection)
    save_documents(client, collection_name, documents=docs, ids=keys, metadatas=metadatas, embeddings=embeddings)
    # Try to persist
    try:
        persist_client(client)
    except Exception:
        pass


# Streamlit session_state utilities
def _ensure_streamlit():
    if not _streamlit_available or st is None:
        raise RuntimeError("streamlit is not available. Install streamlit to use session_state helpers.")


def set_session_state(key: str, value: Any) -> None:
    """
    Set st.session_state[key] = value.
    """
    _ensure_streamlit()
    st.session_state[key] = value


def get_session_state(key: str, default: Any = None) -> Any:
    """
    Return st.session_state.get(key, default)
    """
    _ensure_streamlit()
    return st.session_state.get(key, default)


def update_session_state(updates: Dict[str, Any]) -> None:
    """
    Update multiple keys in streamlit session_state.
    """
    _ensure_streamlit()
    for k, v in updates.items():
        st.session_state[k] = v


def pop_session_state(key: str, default: Any = None) -> Any:
    """
    Remove and return a value from session_state.
    """
    _ensure_streamlit()
    return st.session_state.pop(key, default)


def clear_session_state(keys: Optional[Iterable[str]] = None) -> None:
    """
    Clear specific keys from session_state, or clear all if keys is None.
    """
    _ensure_streamlit()
    if keys is None:
        for k in list(st.session_state.keys()):
            del st.session_state[k]
    else:
        for k in keys:
            if k in st.session_state:
                del st.session_state[k]