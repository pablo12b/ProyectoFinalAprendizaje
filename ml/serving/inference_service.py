"""
Inference Service.

Generic service for running ML model inference.
Orchestrates preprocessing, prediction, and postprocessing pipeline.
"""

from typing import Any
from dataclasses import dataclass

from business_backend.ml.models.registry import ModelRegistry
from business_backend.ml.preprocessing.base import BasePreprocessor


@dataclass
class PredictionResult:
    """Result from ML inference."""

    model_name: str
    prediction: Any
    confidence: float | None = None
    metadata: dict[str, Any] | None = None


class InferenceService:
    """
    ML inference service.

    Orchestrates:
    1. Input preprocessing
    2. Model inference
    3. Result formatting

    Usage:
        service = InferenceService(registry, preprocessor)
        result = await service.predict("image_classifier", image_data)
    """

    def __init__(
        self,
        model_registry: ModelRegistry,
        preprocessor: BasePreprocessor | None = None,
    ) -> None:
        """
        Initialize inference service.

        Args:
            model_registry: Registry for loading models
            preprocessor: Optional preprocessor for input data
        """
        self.registry = model_registry
        self.preprocessor = preprocessor

    async def predict(
        self,
        model_name: str,
        data: Any,
        preprocess: bool = True,
    ) -> PredictionResult:
        """
        Run inference on data using specified model.

        Args:
            model_name: Name of registered model
            data: Input data (raw or preprocessed)
            preprocess: Whether to run preprocessing

        Returns:
            PredictionResult with prediction and metadata
        """
        # 1. Load model from registry
        model = await self.registry.load(model_name)
        
        # 2. Preprocess data if enabled and preprocessor available
        input_data = data
        if preprocess and self.preprocessor:
            input_data = await self.preprocessor.process(data)
            
        # 3. Run model.predict()
        result = await model.predict(input_data)
        
        # 4. Format and return PredictionResult
        prediction_value = result.get("prediction")
        confidence = result.get("confidence")
        metadata = result.get("metadata")
        
        return PredictionResult(
            model_name=model_name,
            prediction=prediction_value,
            confidence=confidence,
            metadata=metadata
        )

    async def predict_batch(
        self,
        model_name: str,
        data_list: list[Any],
        preprocess: bool = True,
    ) -> list[PredictionResult]:
        """
        Run batch inference.

        Args:
            model_name: Name of registered model
            data_list: List of input data items
            preprocess: Whether to run preprocessing

        Returns:
            List of PredictionResults
        """
        model = await self.registry.load(model_name)
        
        processed_list = data_list
        if preprocess and self.preprocessor:
            processed_list = await self.preprocessor.process_batch(data_list)
            
        batch_results = await model.predict_batch(processed_list)
        
        return [
            PredictionResult(
                model_name=model_name,
                prediction=res.get("prediction"),
                confidence=res.get("confidence"),
                metadata=res.get("metadata")
            )
            for res in batch_results
        ]

    def list_available_models(self) -> list[str]:
        """
        List all models available for inference.

        Returns:
            List of model names
        """
        return [m.name for m in self.registry.list_models()]

    async def get_model_info(self, model_name: str) -> dict[str, Any]:
        """
        Get information about a model.

        Args:
            model_name: Model identifier

        Returns:
            Model metadata
        """
        info = self.registry.get_info(model_name)
        if not info:
            return {}
        return {
            "name": info.name,
            "stage": info.stage,
            "version": info.version,
            "metadata": info.metadata,
        }

    async def health_check(self, model_name: str) -> dict[str, Any]:
        """
        Check if model is ready for inference.

        Args:
            model_name: Model identifier

        Returns:
            Health status dict
        """
        is_registered = self.registry.get_info(model_name) is not None
        is_loaded = self.registry.is_loaded(model_name)
        
        return {
            "model": model_name,
            "status": "ready" if is_loaded else "registered",
            "registered": is_registered,
            "loaded": is_loaded
        }
