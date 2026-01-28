"""
Domain models for FAQ and Document data.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel

class FAQItemData(BaseModel):
    """Data model for a single FAQ item."""
    question: str
    patterns: List[str]
    answer: str
    category: str


class FAQResponses(BaseModel):
    """Container for standard responses."""
    greeting: Optional[str] = None
    farewell: Optional[str] = None
    gratitude: Optional[str] = None
    assistant_info: Optional[str] = None
    help_request: Optional[str] = None


class FAQData(BaseModel):
    """Complete FAQ dataset for a tenant."""
    greeting_patterns: List[str] = []
    farewell_patterns: List[str] = []
    gratitude_patterns: List[str] = []
    assistant_info_patterns: List[str] = []
    help_request_patterns: List[str] = []
    
    responses: FAQResponses
    faq_items: List[FAQItemData] = []


class DocumentChunk(BaseModel):
    """Data model for a document chunk."""
    content: str
    category: str
    metadata: Dict[str, str] = {}
