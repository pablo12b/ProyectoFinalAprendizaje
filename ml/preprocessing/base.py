"""
Base Preprocessor Abstract Class.

All preprocessors should inherit from this class to ensure
consistent interface across different data types.
"""

from abc import ABC, abstractmethod
from typing import Any


class BasePreprocessor(ABC):
    """
    Abstract base class for data preprocessors.

    Provides consistent interface for:
    - Single item processing
    - Batch processing
    - Configuration management
    """

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """
        Process a single data item.

        Args:
            data: Raw input data

        Returns:
            Preprocessed data ready for model input
        """
        # Here your code for single item preprocessing
        pass

    @abstractmethod
    async def process_batch(self, data_list: list[Any]) -> list[Any]:
        """
        Process a batch of data items.

        Args:
            data_list: List of raw input data

        Returns:
            List of preprocessed data items
        """
        # Here your code for batch preprocessing
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate input data before processing.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        # Here your code for input validation
        pass
