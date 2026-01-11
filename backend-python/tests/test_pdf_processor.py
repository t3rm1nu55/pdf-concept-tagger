"""
Tests for PDF Processor

MVP: Test PDF text extraction.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_processor import PDFProcessor


@pytest.fixture
def pdf_processor():
    """Create PDFProcessor instance."""
    return PDFProcessor()


@pytest.mark.asyncio
async def test_extract_page_text_success(pdf_processor):
    """Test successful text extraction."""
    with patch("pdfplumber.open") as mock_open:
        # Mock PDF with pages
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = await pdf_processor.extract_page_text("/path/to/test.pdf", 1)
        
        assert result == "Sample PDF text"
        mock_open.assert_called_once()


@pytest.mark.asyncio
async def test_extract_page_text_page_not_found(pdf_processor):
    """Test handling of invalid page number."""
    with patch("pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_pdf.pages = []  # Empty pages
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = await pdf_processor.extract_page_text("/path/to/test.pdf", 1)
        
        assert result is None


@pytest.mark.asyncio
async def test_extract_all_pages(pdf_processor):
    """Test extracting all pages."""
    with patch("pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = await pdf_processor.extract_all_pages("/path/to/test.pdf")
        
        assert len(result) == 2
        assert result[0] == "Page 1 text"
        assert result[1] == "Page 2 text"


@pytest.mark.asyncio
async def test_get_page_count(pdf_processor):
    """Test getting page count."""
    with patch("pdfplumber.open") as mock_open:
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock(), MagicMock(), MagicMock()]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = await pdf_processor.get_page_count("/path/to/test.pdf")
        
        assert result == 3
