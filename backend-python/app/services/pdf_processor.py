"""
PDF Processing Service

MVP: Extract text from PDF pages using pdfplumber.
"""

import pdfplumber
from typing import Optional, List
from pathlib import Path


class PDFProcessor:
    """
    PDF processing service for text extraction.
    
    MVP: Uses pdfplumber for text extraction.
    Future: Can switch to Docling for better structure extraction.
    """
    
    def __init__(self):
        """Initialize PDF processor."""
        pass
    
    async def extract_page_text(self, pdf_path: str, page_number: int) -> Optional[str]:
        """
        Extract text from a specific PDF page.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number (1-indexed)
            
        Returns:
            Extracted text or None if page not found
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    return None
                
                page = pdf.pages[page_number - 1]  # Convert to 0-indexed
                text = page.extract_text()
                return text if text else None
                
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
    
    async def extract_all_pages(self, pdf_path: str) -> List[str]:
        """
        Extract text from all pages.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text per page
        """
        pages_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    pages_text.append(text if text else "")
            return pages_text
        except Exception as e:
            print(f"Error extracting all pages: {e}")
            return []
    
    async def get_page_count(self, pdf_path: str) -> int:
        """Get total number of pages in PDF."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            print(f"Error getting page count: {e}")
            return 0
