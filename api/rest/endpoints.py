"""
REST Endpoints for Business Backend.
"""

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from aioinject import Inject
from aioinject.ext.fastapi import inject
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

from business_backend.ml.serving.inference_service import InferenceService

router = APIRouter()


@router.post("/detect")
@inject
async def detect_product(
    file: Annotated[UploadFile, File(...)],
    inference_service: Annotated[InferenceService, Inject],
):
    """
    Detect product in uploaded image.
    
    Uploads an image file and accepts it for processing by the ML Inference Service.
    """
    logger.info(f"📸 Received file for detection: {file.filename}")
    
    try:
        # Save uploaded file temporarily (to simulate real file processing)
        # In production, this might stream directly or save to S3
        suffix = Path(file.filename).suffix if file.filename else ".tmp"
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
            
        logger.debug(f"Saved temp file to: {tmp_path}")
        
        # Run inference
        result = await inference_service.predict(
            model_name="product_classifier",
            data=tmp_path,  # Passing file path
            preprocess=False # Our mock handles paths directly
        )
        
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            "status": "success",
            "filename": file.filename,
            "prediction": result.prediction,
            "confidence": result.confidence,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"❌ Error in detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
