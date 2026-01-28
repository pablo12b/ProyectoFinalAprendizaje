"""
Image Recognition Tool for LangChain.

This tool allows the LLM to "see" images by sending them to the InferenceService.
"""

from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from business_backend.ml.serving.inference_service import InferenceService


class ImageRecognitionInput(BaseModel):
    """Input schema for image recognition tool."""

    image_path: str = Field(
        description="The file path of the image to analyze."
    )


class ImageRecognitionTool(BaseTool):
    """
    LangChain tool for recognizing products in images.

    Uses InferenceService to classify images using the 'product_classifier' model.
    """

    name: str = "image_recognition"
    description: str = (
        "Analyzes an image to identify the product shown. "
        "Use this tool when the user provides an image path or asks 'what is in this image?'. "
        "Returns the name of the product identified."
    )
    args_schema: type[BaseModel] = ImageRecognitionInput

    # Service reference
    inference_service: InferenceService | None = None

    def _run(self, image_path: str) -> str:
        """Sync version - not used."""
        raise NotImplementedError("Use async version")

    async def _arun(self, image_path: str) -> str:
        """
        Async image recognition.

        Args:
            image_path: Path to image file

        Returns:
            Description of identified product
        """
        if self.inference_service is None:
            return "Error: Inference service not configured"

        try:
            # Predict using the standard product_classifier model
            # In a real app, we might check if model is loaded or handle missing files
            result = await self.inference_service.predict(
                model_name="product_classifier",
                data=image_path,  # Passing path directly as per our ImageClassifier mock support
                preprocess=False  # Mock classifier handles path strings directly
            )
            
            product_name = result.prediction
            confidence = result.confidence
            
            return (
                f"Image Analysis Result:\n"
                f"Detected Product: {product_name}\n"
                f"Confidence: {confidence:.2%}"
            )
        except Exception as e:
            return f"Error analyzing image: {str(e)}"


def create_image_recognition_tool(inference_service: InferenceService) -> ImageRecognitionTool:
    """
    Create an image recognition tool with the given service.

    Args:
        inference_service: InferenceService instance

    Returns:
        Configured ImageRecognitionTool
    """
    tool = ImageRecognitionTool()
    tool.inference_service = inference_service
    return tool
