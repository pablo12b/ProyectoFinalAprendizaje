"""
Base Model Abstract Class.

All ML models should inherit from this class to ensure
consistent interface across different model types.
"""

from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path


class BaseModel(ABC):
    """
    Abstract base class for ML models.

    Provides consistent interface for:
    - Model loading/unloading
    - Prediction (single and batch)
    - Model metadata
    """

    # Override in subclass
    model_type: str = "generic"  # image, text, tabular, audio
    input_shape: tuple[int, ...] | None = None

    def __init__(self) -> None:
        """Initialize model (not loaded yet)."""
        self._model: Any = None
        self._is_loaded: bool = False
        self._model_path: Path | None = None

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded

    @abstractmethod
    async def load(self, path: str | Path) -> None:
        """
        Load model weights/artifacts from path.

        Args:
            path: Path to model file or directory
        """
        # Here your code for loading model (Keras, PyTorch, ONNX, etc.)
        pass

    @abstractmethod
    async def predict(self, data: Any) -> dict[str, Any]:
        """
        Run inference on preprocessed data.

        Args:
            data: Preprocessed input data

        Returns:
            Dict with keys:
            - prediction: Model output (class label, value, etc.)
            - confidence: Optional confidence score (0-1)
            - metadata: Optional additional info
        """
        # Here your code for model inference
        pass

    async def predict_batch(self, data_list: list[Any]) -> list[dict[str, Any]]:
        """
        Run batch inference.

        Args:
            data_list: List of preprocessed inputs

        Returns:
            List of prediction dicts
        """
        # Here your code for batch inference (default: sequential)
        results = []
        for data in data_list:
            result = await self.predict(data)
            results.append(result)
        return results

    async def unload(self) -> None:
        """Release model from memory."""
        # Here your code for releasing model resources
        self._model = None
        self._is_loaded = False

    def get_info(self) -> dict[str, Any]:
        """
        Get model metadata.

        Returns:
            Dict with model information
        """
        return {
            "model_type": self.model_type,
            "input_shape": self.input_shape,
            "is_loaded": self._is_loaded,
            "model_path": str(self._model_path) if self._model_path else None,
        }
