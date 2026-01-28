"""
Service for reading tenant data from CSV files.

This service loads FAQs and context chunks from CSV files stored in
business_backend/data/{tenant}/ directory.
"""

from pathlib import Path

import pandas as pd
from loguru import logger

from business_backend.domain.faq_models import (
    DocumentChunk,
    FAQData,
    FAQItemData,
    FAQResponses,
)


class TenantDataService:
    """Service for loading tenant-specific data from CSV files."""

    @staticmethod
    async def read_faqs_csv(tenant: str) -> FAQData:
        """
        Read FAQs from CSV and convert to structured format.

        CSV Format:
            type,patterns,response,category
            greeting,"pattern1;;;pattern2","Response text",greeting
            farewell,"pattern1;;;pattern2","Response text",farewell
            faq,"pattern1;;;pattern2","Answer text",category_name

        Args:
            tenant: Tenant name (app, supermart, coralmart)

        Returns:
            FAQData model with typed structure containing patterns, responses, and FAQ items.

        Raises:
            FileNotFoundError: If CSV file doesn't exist
        """
        csv_path = Path(f"business_backend/data/{tenant}/faqs.csv")

        if not csv_path.exists():
            raise FileNotFoundError(f"FAQs CSV not found: {csv_path}")

        logger.info(f"📖 Reading FAQs from: {csv_path}")

        df = pd.read_csv(csv_path)

        # Initialize lists and responses
        greeting_patterns: list[str] = []
        farewell_patterns: list[str] = []
        gratitude_patterns: list[str] = []
        assistant_info_patterns: list[str] = []
        help_request_patterns: list[str] = []
        responses_dict: dict[str, str] = {}
        faq_items: list[FAQItemData] = []

        # Process each row
        for _, row in df.iterrows():
            row_type = str(row["type"]).strip()
            patterns = str(row["patterns"]).strip().split(";;;")  # Split by ;;;
            response = str(row["response"]).strip()
            category = str(row["category"]).strip()

            if row_type == "greeting":
                greeting_patterns.extend(patterns)
                responses_dict["greeting"] = response
            elif row_type == "farewell":
                farewell_patterns.extend(patterns)
                responses_dict["farewell"] = response
            elif row_type == "gratitude":
                gratitude_patterns.extend(patterns)
                responses_dict["gratitude"] = response
            elif row_type == "assistant_info":
                assistant_info_patterns.extend(patterns)
                responses_dict["assistant_info"] = response
            elif row_type == "help_request":
                help_request_patterns.extend(patterns)
                responses_dict["help_request"] = response
            elif row_type == "faq":
                # FAQ items need question field (use category as question title)
                faq_item = FAQItemData(
                    question=category.replace("_", " ").title(),
                    patterns=patterns,
                    answer=response,
                    category=category,
                )
                faq_items.append(faq_item)

        # Build Pydantic model
        faq_data = FAQData(
            greeting_patterns=greeting_patterns,
            farewell_patterns=farewell_patterns,
            gratitude_patterns=gratitude_patterns,
            assistant_info_patterns=assistant_info_patterns,
            help_request_patterns=help_request_patterns,
            responses=FAQResponses(**responses_dict),
            faq_items=faq_items,
        )

        logger.info(
            f"✅ Loaded FAQs for tenant '{tenant}': {len(faq_data.faq_items)} items, {len(faq_data.greeting_patterns)} greetings"
        )

        return faq_data

    @staticmethod
    async def read_chunks_csv(tenant: str) -> list[DocumentChunk]:
        """
        Read context chunks from CSV.

        CSV Format:
            category,text
            company_info,"Text content..."
            departments,"Text content..."

        Args:
            tenant: Tenant name (app, supermart, coralmart)

        Returns:
            List of DocumentChunk models with typed structure.

        Raises:
            FileNotFoundError: If CSV file doesn't exist
        """
        csv_path = Path(f"business_backend/data/{tenant}/chunks.csv")

        if not csv_path.exists():
            raise FileNotFoundError(f"Chunks CSV not found: {csv_path}")

        logger.info(f"📖 Reading chunks from: {csv_path}")

        df = pd.read_csv(csv_path)

        # Convert to Pydantic models
        chunks: list[DocumentChunk] = []
        for _, row in df.iterrows():
            chunk = DocumentChunk(
                content=str(row.get("text", "")),
                category=str(row.get("category", "")),
                metadata={},
            )
            chunks.append(chunk)

        logger.info(f"✅ Loaded {len(chunks)} chunks for tenant '{tenant}'")

        return chunks
