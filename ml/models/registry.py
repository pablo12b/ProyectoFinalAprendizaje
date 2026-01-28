"""
Model Registry.

Manages ML model registration, loading, and lifecycle.
Follows MLflow registry pattern for model management.
"""

from typing import Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from business_backend.ml.models.base import BaseModel


class ModelStage(str, Enum):
    """Model lifecycle stages."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelInfo:
    """Metadata for a registered model."""

    name: str
    model_class: type[BaseModel]
    model_path: str | Path
    stage: ModelStage = ModelStage.DEVELOPMENT
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """
    Registry for ML models with lazy loading and caching.

    Provides:
    - Model registration with metadata
    - Lazy loading (models loaded on first use)
    - In-memory caching (singleton per model)
    - Version and stage management
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._registry: dict[str, ModelInfo] = {}
        self._loaded_models: dict[str, BaseModel] = {}

    def register(
        self,
        name: str,
        model_class: type[BaseModel],
        model_path: str | Path,
        stage: ModelStage = ModelStage.DEVELOPMENT,
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a model in the registry.

        Args:
            name: Unique model identifier
            model_class: Class that implements BaseModel
            model_path: Path to model weights/artifacts
            stage: Model lifecycle stage
            version: Model version string
            metadata: Additional model metadata
        """
        self._registry[name] = ModelInfo(
            name=name,
            model_class=model_class,
            model_path=model_path,
            stage=stage,
            version=version,
            metadata=metadata or {},
        )

    def unregister(self, name: str) -> None:
        """
        Remove model from registry and unload if cached.

        Args:
            name: Model identifier
        """
        if name in self._loaded_models:
            self._loaded_models.pop(name)
        if name in self._registry:
            self._registry.pop(name)

    async def load(self, name: str) -> BaseModel:
        """
        Load model by name (lazy loading with cache).

        Args:
            name: Model identifier

        Returns:
            Loaded model instance

        Raises:
            KeyError: If model not registered
        """
        if name not in self._registry:
            raise KeyError(f"Model '{name}' not found in registry")

        if name in self._loaded_models:
            return self._loaded_models[name]

        info = self._registry[name]
        
        # Instantiate and load
        model_instance = info.model_class()
        await model_instance.load(info.model_path)
        
        # Cache
        self._loaded_models[name] = model_instance
        return model_instance

    async def unload(self, name: str) -> None:
        """
        Unload model from memory (keeps registration).

        Args:
            name: Model identifier
        """
        if name in self._loaded_models:
            del self._loaded_models[name]

    async def reload(self, name: str) -> BaseModel:
        """
        Force reload model (useful after weights update).

        Args:
            name: Model identifier

        Returns:
            Reloaded model instance
        """
        await self.unload(name)
        return await self.load(name)

    def get_info(self, name: str) -> ModelInfo | None:
        """
        Get model info without loading.

        Args:
            name: Model identifier

        Returns:
            ModelInfo or None if not registered
        """
        return self._registry.get(name)

    def list_models(self, stage: ModelStage | None = None) -> list[ModelInfo]:
        """
        List all registered models.

        Args:
            stage: Optional filter by stage

        Returns:
            List of ModelInfo
        """
        if stage is None:
            return list(self._registry.values())
        return [m for m in self._registry.values() if m.stage == stage]

    def is_loaded(self, name: str) -> bool:
        """
        Check if model is currently loaded in memory.

        Args:
            name: Model identifier

        Returns:
            True if loaded
        """
        return name in self._loaded_models
