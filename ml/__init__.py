"""
Machine Learning Module for Business Backend.

This module provides ML capabilities:
- preprocessing/  : Data transformation pipelines
- models/         : Model wrappers and registry
- serving/        : Inference service
- training/       : Re-training and experiment tracking

This module is optional and can be removed if ML is not needed.
"""

from business_backend.ml.models.registry import ModelRegistry
from business_backend.ml.serving.inference_service import InferenceService

__all__ = ["ModelRegistry", "InferenceService"]
