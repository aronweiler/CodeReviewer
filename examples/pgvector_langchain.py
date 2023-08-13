"""VectorStore wrapper around a Postgres/PGVector database."""
# Importing necessary libraries and modules
from __future__ import annotations
import enum
import logging
import uuid
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, declarative_base

# Importing necessary modules from the project
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.utils import get_from_dict_or_env
from langchain.vectorstores.base import VectorStore

# Checking if the type checking is enabled
if TYPE_CHECKING:
    from langchain.vectorstores._pgvector_data_models import CollectionStore

# Enum class for distance strategies
class DistanceStrategy(str, enum.Enum):
    """Enumerator of the Distance strategies."""
    EUCLIDEAN = "l2"
    COSINE = "cosine"
    MAX_INNER_PRODUCT = "inner"

# Default distance strategy
DEFAULT_DISTANCE_STRATEGY = DistanceStrategy.COSINE

# Base class for SQLAlchemy ORM
Base = declarative_base()  # type: Any

# Default collection name
_LANGCHAIN_DEFAULT_COLLECTION_NAME = "langchain"

# Base model class for SQLAlchemy ORM
class BaseModel(Base):
    __abstract__ = True
    uuid = sqlalchemy.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```python
import logging
import sqlalchemy
import uuid
from typing import Any, Callable, List, Optional, Tuple, Type
from sqlalchemy.orm import Session
from sqlalchemy.sql import text as sqlalchemy_text

from langchain.vectorstores._pgvector_data_models import CollectionStore, EmbeddingStore
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore, Document
from langchain.vectorstores.utils import get_from_dict_or_env

# Constants for default values
_LANGCHAIN_DEFAULT_COLLECTION_NAME = "langchain"
DEFAULT_DISTANCE_STRATEGY = "COSINE"


class PGVector(VectorStore):
    """
    VectorStore implementation using Postgres and pgvector.
    """

    def __init__(
        self,
        connection_string: str,
        embedding_function: Embeddings,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        collection_metadata: Optional[dict] = None,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        pre_delete_collection: bool = False,
        logger: Optional[logging.Logger] = None,
        relevance_score_fn: Optional[Callable[[float], float]] = None,
    ) -> None:
        self.connection_string = connection_string
        self.embedding_function = embedding_function
        self.collection_name = collection_name
        self.collection_metadata = collection_metadata
        self._distance_strategy = distance_strategy
        self.pre_delete_collection = pre_delete_collection
        self.logger = logger or logging.getLogger(__name__)
        self.override_relevance_score_fn = relevance_score_fn
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Initialize the store.
        """
        self._conn = self.connect()
        self.CollectionStore = CollectionStore
        self.EmbeddingStore = EmbeddingStore
        self.create_tables_if_not_exists()
        self.create_collection()

    @property
    def embeddings(self) -> Embeddings:
        return self.embedding_function

    def connect(self) -> sqlalchemy.engine.Connection:
        engine = sqlalchemy.create_engine(self.connection_string)
        conn = engine.connect()
        return conn

    def create_tables_if_not_exists(self) -> None:
        with self._conn.begin():
            Base.metadata.create_all(self._conn)

    def create_collection(self) -> None:
        if self.pre_delete_collection:
            self.delete_collection()
        with Session(self._conn) as session:
            self.CollectionStore.get_or_create(
                session, self.collection_name, cmetadata=self.collection_metadata
            )

    def delete_collection(self) -> None:
        self.logger.debug("Trying to delete collection")
        with Session(self._conn) as session:
            collection = self.get_collection(session)
            if not collection:
                self.logger.warning("Collection not found")
                return
            session.delete(collection)
            session.commit()

    def get_collection(self, session: Session) -> Optional["CollectionStore"]:
        return self.CollectionStore.get_by_name(session, self.collection_name)

    @classmethod
    def __from(
        cls,
        texts: List[str],
        embeddings: List[List[float]],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        connection_string: Optional[str] = None,
        pre_delete_collection: bool = False,
        **kwargs: Any,
    ) -> "PGVector":
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]

        if not metadatas:
            metadatas = [{} for _ in texts]
        if connection_string is None:
            connection_string = cls.get_connection_string(kwargs)

        store = cls(
            connection_string=connection_string,
            collection_name=collection_name,
            embedding_function=embedding,
            distance_strategy=distance_strategy,
            pre_delete_collection=pre_delete_collection,
            **kwargs,
        )

        store.add_embeddings(
            texts=texts, embeddings=embeddings, metadatas=metadatas, ids=ids, **kwargs
        )

        return store

    def add_embeddings(
        self,
        texts: Iterable[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Add embeddings to the vectorstore.
        """
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]

        if not metadatas:
            metadatas = [{} for _ in texts]

        with Session(self._conn) as session:
            collection = self.get_collection(session)
            if not collection:
                raise ValueError("Collection not found")
            for text, metadata, embedding, id in zip(texts, metadatas, embeddings, ids):
                embedding_store = self.EmbeddingStore(
                    embedding=embedding,
                    document=text,
                    cmetadata=metadata,
                    custom_id=id,
                    collection_id=collection.uuid,
                )
                session.add(embedding_store)
            session.commit()

        return ids

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Run more texts through the embeddings and add to the vectorstore.
        """
        embeddings = self.embedding_function.embed_documents(list(texts))
        return self.add_embeddings(
            texts=texts, embeddings=embeddings, metadatas=metadatas, ids=ids, **kwargs
        )

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Run similarity search with PGVector with distance.
        """
        embedding = self.embedding_function.embed_query(text=query)
        return self.similarity_search_by_vector(
            embedding=embedding,
            k=k,
            filter=filter,
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Return docs most similar to query.
        """
        embedding = self.embedding_function.embed_query(query)
        docs = self.similarity_search_with_score_by_vector(
            embedding=embedding, k=k, filter=filter
        )
        return docs

    @property
    def distance_strategy(self) -> Any:
        if self._distance_strategy == "l2":
            return self.EmbeddingStore.embedding.l2_distance
        elif self._distance_strategy == "cosine":
            return self.EmbeddingStore.embedding.cosine_distance
        elif self._distance_strategy == "inner":
            return self.EmbeddingStore.embedding.max_inner_product
        else:
            raise ValueError(
                f"Got unexpected value for distance: {self._distance_strategy}. "
                f"Should be one of `l2`, `cosine`, `inner`."
            )

    def similarity_search_with_score_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Optional[dict] = None,
    ) -> List[Tuple[Document, float]]:
        with Session(self._conn) as session:
            collection = self.get_collection(session)
            if not collection:
                raise ValueError("Collection not found")

            filter_by = self.EmbeddingStore.collection_id == collection.uuid

            if filter is not None:
                filter_clauses = []
                for key, value in filter.items():
                    IN = "in"
                    if isinstance(value, dict) and IN in map(str.lower, value):
                        value_case_insensitive = {
                            k.lower(): v for k, v in value.items()
                        }
                        filter_by_metadata = self.EmbeddingStore.cmetadata[
                            key
                        ].astext.in_(value_case_insensitive[IN])
                        filter_clauses.append(filter_by_metadata)
                    else:
                        filter_by_metadata = self.EmbeddingStore.cmetadata[
                            key
                        ].astext == str(value)
                        filter_clauses.append(filter_by_metadata)

                filter_by = sqlalchemy.and_(filter_by, *filter_clauses)

            _type = self.EmbeddingStore

            results: List[Any] = (
                session.query(
                    self.EmbeddingStore,
                    self.distance_strategy(embedding).label("distance"),  # type: ignore
                )
                .filter(filter_by)
                .order_by(sqlalchemy.asc("distance"))
                .join(
                    self.CollectionStore,
                    self.EmbeddingStore.collection_id == self.CollectionStore.uuid,
                )
                .limit(k)
                .all()
            )

        docs = [
            (
                Document(
                    page_content=result.EmbeddingStore.document,
                    metadata=result.EmbeddingStore.cmetadata,
                ),
                result.distance if self.embedding_function is not None else None,
            )
            for result in results
        ]
        return docs

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Return docs most similar to embedding vector.
        """
        docs_and_scores = self.similarity_search_with_score_by_vector(
            embedding=embedding, k=k, filter=filter
        )
        return [doc for doc, _ in docs_and_scores]

    @classmethod
    def from_texts(
        cls: Type[PGVector],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        ids: Optional[List[str]] = None,
        pre_delete_collection: bool = False,
        **kwargs: Any,
    ) -> "PGVector":
        """
        Return VectorStore initialized from texts and embeddings.
        """
        embeddings = embedding.embed_documents(list(texts))

        return cls.__from(
            texts,
            embeddings,
            embedding,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name,
            distance_strategy=distance_strategy,
            pre_delete_collection=pre_delete_collection,
            **kwargs,
        )

    @classmethod
    def from_embeddings(
        cls,
        text_embeddings: List[Tuple[str, List[float]]],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        ids: Optional[List[str]] = None,
        pre_delete_collection: bool = False,
        **kwargs: Any,
    ) -> "PGVector":
        """
        Construct PGVector wrapper from raw documents and pre-
        generated embeddings.
        """
        texts = [t[0] for t in text_embeddings]
        embeddings = [t[1] for t in text_embeddings]

        return cls.__from(
            texts,
            embeddings,
            embedding,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name,
            distance_strategy=distance_strategy,
            pre_delete_collection=pre_delete_collection,
            **kwargs,
        )

    @classmethod
    def from_existing_index(
        cls: Type[PGVector],
        embedding: Embeddings,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        pre_delete_collection: bool = False,
        **kwargs: Any,
    ) -> "PGVector":
        """
        Get instance of an existing PGVector store.
        """
        connection_string = cls.get_connection_string(kwargs)

        store = cls(
            connection_string=connection_string,
            collection_name=collection_name,
            embedding_function=embedding,
            distance_strategy=distance_strategy,
            pre_delete_collection=pre_delete_collection,
        )

        return store

    @classmethod
    def get_connection_string(cls, kwargs: Dict[str, Any]) -> str:
        connection_string: str = get_from_dict_or_env(
            data=kwargs,
            key="connection_string",
            env_key="PGVECTOR_CONNECTION_STRING",
        )

        if not connection_string:
            raise ValueError(
                "Postgres connection string is required"
                "Either pass it as a parameter"
                "or set the PGVECTOR_CONNECTION_STRING environment variable."
            )

        return connection_string

    @classmethod
    def from_documents(
        cls: Type[PGVector],
        documents: List[Document],
        embedding: Embeddings,
        collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
        distance_strategy: str = DEFAULT_DISTANCE_STRATEGY,
        ids: Optional[List[str]] = None,
        pre_delete_collection: bool = False,
        **kwargs: Any,
    ) -> "PGVector":
        """
        Return VectorStore initialized from documents and embeddings.
        """
        texts = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]
        connection_string = cls.get_connection_string(kwargs)

        kwargs["connection_string"] = connection_string

        return cls.from_texts(
            texts=texts,
            pre_delete_collection=pre_delete_collection,
            embedding=embedding,
            distance_strategy=distance_strategy,
            metadatas=metadatas,
            ids=ids,
            collection_name=collection_name,
            **kwargs,
        )

    @classmethod
    def connection_string_from_db_params(
        cls,
        driver: str,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> str:
        """
        Return connection string from database parameters.
        """
        return f"postgresql+{driver}://{user}:{password}@{host}:{port}/{database}"

    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        """
        The 'correct' relevance function
        may differ depending on a few things, including:
        - the distance / similarity metric used by the VectorStore
        - the scale of your embeddings (OpenAI's are unit normed. Many others are not!)
        - embedding dimensionality
        - etc.
        """
        if self.override_relevance_score_fn is not None:
            return self.override_relevance_score_fn
```

# Refactored code

# The function below returns the appropriate relevance score function based on the distance strategy provided.
# If the distance strategy is not recognized, it raises a ValueError.
def get_relevance_score_fn(self):
    # Mapping of distance strategies to their corresponding relevance score functions
    strategy_to_function = {
        DistanceStrategy.COSINE: self._cosine_relevance_score_fn,
        DistanceStrategy.EUCLIDEAN: self._euclidean_relevance_score_fn,
        DistanceStrategy.MAX_INNER_PRODUCT: self._max_inner_product_relevance_score_fn
    }

    # Try to get the relevance score function based on the distance strategy
    try:
        return strategy_to_function[self._distance_strategy]
    except KeyError:
        # If the distance strategy is not recognized, raise a ValueError with a helpful message
        raise ValueError(
            f"No supported normalization function for distance_strategy of {self._distance_strategy}. "
            "Consider providing relevance_score_fn to PGVector constructor."
        )