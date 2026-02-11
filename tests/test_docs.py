"""
Comprehensive test suite for Google Docs tools.

Tests all functions from google_cloud_mcp.server:
- create_document
- get_document
- append_to_document
- search_documents
- export_document

Covers success paths, error paths, and edge cases with mocked Google API clients.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import base64


# Import the functions to test
# @mcp.tool() wraps functions into FunctionTool objects,
# so we use .fn to get the underlying callable.
try:
    from google_cloud_mcp import server
    create_document = server.create_document.fn
    get_document = server.get_document.fn
    append_to_document = server.append_to_document.fn
    search_documents = server.search_documents.fn
    export_document = server.export_document.fn
except ImportError:
    # If import fails, skip all tests
    pytest.skip("google_cloud_mcp.server module not found", allow_module_level=True)


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    with patch('google_cloud_mcp.server.get_credentials') as mock_creds:
        mock_creds.return_value = Mock()
        yield mock_creds


@pytest.fixture
def mock_docs_service():
    """Mock Google Docs service."""
    mock_service = Mock()
    return mock_service


@pytest.fixture
def mock_drive_service():
    """Mock Google Drive service."""
    mock_service = Mock()
    return mock_service


class TestCreateDocument:
    """Test suite for create_document function."""

    def test_create_document_success_with_body(self, mock_credentials):
        """Test successful document creation with body text."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock document creation response
            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'test-doc-id-123'
            }

            # Mock batch update for body text
            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            result = create_document("Test Document", "This is test content")

            # Verify the service was built correctly
            mock_build.assert_called_once_with('docs', 'v1', credentials=mock_credentials.return_value)

            # Verify document creation was called
            mock_service.documents.return_value.create.assert_called_once_with(
                body={'title': 'Test Document'}
            )

            # Verify batch update was called to insert text
            mock_service.documents.return_value.batchUpdate.assert_called_once_with(
                documentId='test-doc-id-123',
                body={
                    'requests': [{
                        'insertText': {
                            'location': {'index': 1},
                            'text': 'This is test content'
                        }
                    }]
                }
            )

            assert "✅ Document created: https://docs.google.com/document/d/test-doc-id-123/edit" == result

    def test_create_document_success_without_body(self, mock_credentials):
        """Test successful document creation without body text."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'test-doc-id-456'
            }

            result = create_document("Empty Document")

            # Verify batch update was NOT called when no body text
            mock_service.documents.return_value.batchUpdate.assert_not_called()

            assert "✅ Document created: https://docs.google.com/document/d/test-doc-id-456/edit" == result

    def test_create_document_with_empty_string_body(self, mock_credentials):
        """Test document creation with empty string body."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'test-doc-id-789'
            }

            result = create_document("Document with Empty Body", "")

            # Verify batch update was NOT called with empty string
            mock_service.documents.return_value.batchUpdate.assert_not_called()

            assert "✅ Document created:" in result

    def test_create_document_api_error(self, mock_credentials):
        """Test error handling when API call fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.side_effect = Exception("API Error: Permission denied")

            result = create_document("Failed Document")

            assert "API Error: Permission denied" == result

    def test_create_document_batch_update_error(self, mock_credentials):
        """Test error handling when batch update fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'test-doc-id-999'
            }
            mock_service.documents.return_value.batchUpdate.return_value.execute.side_effect = Exception("Batch update failed")

            result = create_document("Document", "Content that fails")

            assert "Batch update failed" == result


class TestGetDocument:
    """Test suite for get_document function."""

    def test_get_document_success_with_content(self, mock_credentials):
        """Test successful document retrieval with content."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'title': 'My Test Document',
                'body': {
                    'content': [
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': 'First paragraph.\n'
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': 'Second paragraph.\n'
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

            result = get_document('doc-id-123')

            mock_build.assert_called_once_with('docs', 'v1', credentials=mock_credentials.return_value)
            mock_service.documents.return_value.get.assert_called_once_with(documentId='doc-id-123')

            assert "Title: My Test Document" in result
            assert "First paragraph.\n" in result
            assert "Second paragraph.\n" in result

    def test_get_document_empty_document(self, mock_credentials):
        """Test retrieval of document with no content."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'title': 'Empty Document',
                'body': {
                    'content': []
                }
            }

            result = get_document('empty-doc-id')

            assert "Title: Empty Document" in result
            # Should only have title, no content text
            assert result.count('\n') >= 2  # Title line + empty lines

    def test_get_document_no_title(self, mock_credentials):
        """Test document without title field."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': 'Some content\n'
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

            result = get_document('no-title-doc')

            assert "Title: \n" in result
            assert "Some content\n" in result

    def test_get_document_mixed_elements(self, mock_credentials):
        """Test document with mixed element types (some without textRun)."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'title': 'Mixed Content',
                'body': {
                    'content': [
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': 'Text content\n'
                                        }
                                    },
                                    {
                                        # Element without textRun (e.g., image)
                                        'inlineObject': {}
                                    }
                                ]
                            }
                        },
                        {
                            # Content without paragraph
                            'sectionBreak': {}
                        }
                    ]
                }
            }

            result = get_document('mixed-doc')

            assert "Title: Mixed Content" in result
            assert "Text content\n" in result

    def test_get_document_api_error(self, mock_credentials):
        """Test error handling when document retrieval fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.side_effect = Exception("Document not found")

            result = get_document('nonexistent-doc')

            assert "Document not found" == result

    def test_get_document_no_body(self, mock_credentials):
        """Test document without body field."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'title': 'No Body Document'
            }

            result = get_document('no-body-doc')

            assert "Title: No Body Document" in result


class TestAppendToDocument:
    """Test suite for append_to_document function."""

    def test_append_to_document_success(self, mock_credentials):
        """Test successful text append to document."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock get document to retrieve end index
            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {'startIndex': 1, 'endIndex': 50},
                        {'startIndex': 50, 'endIndex': 100}
                    ]
                }
            }

            # Mock batch update
            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            result = append_to_document('doc-id-append', 'New text to append')

            # Verify get was called first
            mock_service.documents.return_value.get.assert_called_once_with(documentId='doc-id-append')

            # Verify batch update was called with correct index (100 - 1 = 99)
            mock_service.documents.return_value.batchUpdate.assert_called_once_with(
                documentId='doc-id-append',
                body={
                    'requests': [{
                        'insertText': {
                            'location': {'index': 99},
                            'text': 'New text to append'
                        }
                    }]
                }
            )

            assert "✅ Text appended to document doc-id-append" == result

    def test_append_to_document_single_element(self, mock_credentials):
        """Test append to document with single content element."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {'startIndex': 1, 'endIndex': 10}
                    ]
                }
            }

            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            result = append_to_document('single-elem-doc', 'Appended text')

            # Should use endIndex 10 - 1 = 9
            call_args = mock_service.documents.return_value.batchUpdate.call_args
            assert call_args[1]['body']['requests'][0]['insertText']['location']['index'] == 9

    def test_append_to_document_get_error(self, mock_credentials):
        """Test error handling when getting document fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.side_effect = Exception("Permission denied")

            result = append_to_document('no-access-doc', 'Text')

            assert "Permission denied" == result

    def test_append_to_document_batch_update_error(self, mock_credentials):
        """Test error handling when batch update fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {'endIndex': 50}
                    ]
                }
            }

            mock_service.documents.return_value.batchUpdate.return_value.execute.side_effect = Exception("Update failed")

            result = append_to_document('doc-id', 'Text')

            assert "Update failed" == result

    def test_append_empty_text(self, mock_credentials):
        """Test appending empty text."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {'endIndex': 50}
                    ]
                }
            }

            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            result = append_to_document('doc-id', '')

            # Should still call batch update with empty string
            call_args = mock_service.documents.return_value.batchUpdate.call_args
            assert call_args[1]['body']['requests'][0]['insertText']['text'] == ''

            assert "✅ Text appended" in result


class TestSearchDocuments:
    """Test suite for search_documents function."""

    def test_search_documents_with_query(self, mock_credentials):
        """Test successful document search with query."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': [
                    {
                        'id': 'doc-1',
                        'name': 'First Document',
                        'modifiedTime': '2024-01-01T10:00:00Z',
                        'owners': [{'emailAddress': 'owner@example.com'}]
                    },
                    {
                        'id': 'doc-2',
                        'name': 'Second Document',
                        'modifiedTime': '2024-01-02T10:00:00Z',
                        'owners': [{'emailAddress': 'owner2@example.com'}]
                    }
                ]
            }

            result = search_documents(query='test query', max_results=20)

            # Verify Drive service was used (not Docs)
            mock_build.assert_called_once_with('drive', 'v3', credentials=mock_credentials.return_value)

            # Verify search query
            call_args = mock_service.files.return_value.list.call_args
            expected_query = "mimeType='application/vnd.google-apps.document' and fullText contains 'test query'"
            assert call_args[1]['q'] == expected_query
            assert call_args[1]['pageSize'] == 20
            assert call_args[1]['orderBy'] == 'modifiedTime desc'

            assert "First Document" in result
            assert "doc-1" in result
            assert "2024-01-01T10:00:00Z" in result
            assert "Second Document" in result
            assert "doc-2" in result

    def test_search_documents_without_query(self, mock_credentials):
        """Test document search without query (list all)."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': [
                    {
                        'id': 'doc-all-1',
                        'name': 'All Documents Test',
                        'modifiedTime': '2024-01-15T10:00:00Z'
                    }
                ]
            }

            result = search_documents()

            # Verify query without fullText search
            call_args = mock_service.files.return_value.list.call_args
            assert call_args[1]['q'] == "mimeType='application/vnd.google-apps.document'"

            assert "All Documents Test" in result

    def test_search_documents_empty_query_string(self, mock_credentials):
        """Test with empty string query."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': [
                    {
                        'id': 'doc-empty',
                        'name': 'Empty Query Doc',
                        'modifiedTime': '2024-01-15T10:00:00Z'
                    }
                ]
            }

            result = search_documents(query='')

            # Empty string should not add fullText filter
            call_args = mock_service.files.return_value.list.call_args
            assert call_args[1]['q'] == "mimeType='application/vnd.google-apps.document'"

    def test_search_documents_no_results(self, mock_credentials):
        """Test search with no results found."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': []
            }

            result = search_documents(query='nonexistent')

            assert "No documents found." == result

    def test_search_documents_missing_files_key(self, mock_credentials):
        """Test search when 'files' key is missing from response."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {}

            result = search_documents()

            assert "No documents found." == result

    def test_search_documents_custom_max_results(self, mock_credentials):
        """Test search with custom max_results."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': []
            }

            search_documents(max_results=50)

            call_args = mock_service.files.return_value.list.call_args
            assert call_args[1]['pageSize'] == 50

    def test_search_documents_missing_modified_time(self, mock_credentials):
        """Test search result with missing modifiedTime."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {
                'files': [
                    {
                        'id': 'doc-no-time',
                        'name': 'No Modified Time'
                    }
                ]
            }

            result = search_documents()

            assert "No Modified Time" in result
            assert "Modified: N/A" in result

    def test_search_documents_api_error(self, mock_credentials):
        """Test error handling when search fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.side_effect = Exception("API quota exceeded")

            result = search_documents(query='test')

            assert "API quota exceeded" == result


class TestExportDocument:
    """Test suite for export_document function."""

    def test_export_document_as_text(self, mock_credentials):
        """Test exporting document as plain text."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.return_value = b'This is plain text content'

            result = export_document('doc-export-1', format='text')

            # Verify Drive service was used
            mock_build.assert_called_once_with('drive', 'v3', credentials=mock_credentials.return_value)

            # Verify export call
            mock_service.files.return_value.export.assert_called_once_with(
                fileId='doc-export-1',
                mimeType='text/plain'
            )

            assert result == 'This is plain text content'

    def test_export_document_as_html(self, mock_credentials):
        """Test exporting document as HTML."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.return_value = b'<html><body>HTML content</body></html>'

            result = export_document('doc-export-2', format='html')

            mock_service.files.return_value.export.assert_called_once_with(
                fileId='doc-export-2',
                mimeType='text/html'
            )

            assert result == '<html><body>HTML content</body></html>'

    def test_export_document_as_pdf(self, mock_credentials):
        """Test exporting document as PDF (returns base64)."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Simulate PDF binary content
            pdf_content = b'%PDF-1.4 fake pdf content here'
            mock_service.files.return_value.export.return_value.execute.return_value = pdf_content

            result = export_document('doc-export-3', format='pdf')

            mock_service.files.return_value.export.assert_called_once_with(
                fileId='doc-export-3',
                mimeType='application/pdf'
            )

            # Should return base64 encoded content
            assert "✅ Exported as pdf (base64" in result
            assert str(len(pdf_content)) in result

            # Verify base64 encoding is present
            expected_base64 = base64.b64encode(pdf_content).decode('utf-8')
            assert expected_base64[:200] in result

    def test_export_document_as_docx(self, mock_credentials):
        """Test exporting document as DOCX (returns base64)."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            docx_content = b'PK\x03\x04 fake docx binary'
            mock_service.files.return_value.export.return_value.execute.return_value = docx_content

            result = export_document('doc-export-4', format='docx')

            mock_service.files.return_value.export.assert_called_once_with(
                fileId='doc-export-4',
                mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )

            assert "✅ Exported as docx (base64" in result

    def test_export_document_default_format(self, mock_credentials):
        """Test export with default format (text)."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.return_value = b'Default text export'

            result = export_document('doc-export-5')

            # Should default to text/plain
            call_args = mock_service.files.return_value.export.call_args
            assert call_args[1]['mimeType'] == 'text/plain'

    def test_export_document_unsupported_format(self, mock_credentials):
        """Test export with unsupported format."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            result = export_document('doc-export-6', format='xlsx')

            assert "❌ Unsupported format 'xlsx'" in result
            assert "Use: text, html, pdf, docx" in result

            # Should not call export
            mock_service.files.return_value.export.assert_not_called()

    def test_export_document_text_already_string(self, mock_credentials):
        """Test when API returns string instead of bytes for text."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Some APIs might return string directly
            mock_service.files.return_value.export.return_value.execute.return_value = 'Already a string'

            result = export_document('doc-export-7', format='text')

            assert result == 'Already a string'

    def test_export_document_html_already_string(self, mock_credentials):
        """Test when API returns string instead of bytes for HTML."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.return_value = '<html>String HTML</html>'

            result = export_document('doc-export-8', format='html')

            assert result == '<html>String HTML</html>'

    def test_export_document_api_error(self, mock_credentials):
        """Test error handling when export fails."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.side_effect = Exception("Export failed: file not found")

            result = export_document('nonexistent-doc', format='pdf')

            assert "Export failed: file not found" == result

    def test_export_document_large_pdf(self, mock_credentials):
        """Test exporting large PDF file."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Simulate large PDF (1MB)
            large_pdf = b'x' * (1024 * 1024)
            mock_service.files.return_value.export.return_value.execute.return_value = large_pdf

            result = export_document('large-doc', format='pdf')

            assert "✅ Exported as pdf (base64" in result
            assert "1048576 bytes" in result  # 1MB in bytes

            # Verify truncation (only shows first 200 chars)
            full_base64 = base64.b64encode(large_pdf).decode('utf-8')
            assert full_base64[:200] in result
            assert "..." in result

    def test_export_document_empty_content(self, mock_credentials):
        """Test exporting document with empty content."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.export.return_value.execute.return_value = b''

            result = export_document('empty-doc', format='text')

            assert result == ''

    def test_export_all_formats(self, mock_credentials):
        """Test all supported export formats."""
        formats_and_mimes = {
            'text': 'text/plain',
            'html': 'text/html',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        for format_name, expected_mime in formats_and_mimes.items():
            with patch('google_cloud_mcp.server.build') as mock_build:
                mock_service = Mock()
                mock_build.return_value = mock_service

                if format_name in ('text', 'html'):
                    mock_service.files.return_value.export.return_value.execute.return_value = b'content'
                else:
                    mock_service.files.return_value.export.return_value.execute.return_value = b'binary content'

                export_document(f'doc-{format_name}', format=format_name)

                call_args = mock_service.files.return_value.export.call_args
                assert call_args[1]['mimeType'] == expected_mime


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple functions."""

    def test_create_and_get_document_flow(self, mock_credentials):
        """Test creating a document and then retrieving it."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Create document
            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'integration-doc-1'
            }
            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            create_result = create_document("Integration Test", "Initial content")
            assert "integration-doc-1" in create_result

            # Get document
            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'title': 'Integration Test',
                'body': {
                    'content': [
                        {
                            'paragraph': {
                                'elements': [
                                    {
                                        'textRun': {
                                            'content': 'Initial content'
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

            get_result = get_document('integration-doc-1')
            assert "Integration Test" in get_result
            assert "Initial content" in get_result

    def test_create_append_and_export_flow(self, mock_credentials):
        """Test creating, appending, and exporting a document."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Create
            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'flow-doc-1'
            }
            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            create_document("Flow Test", "Start")

            # Append
            mock_service.documents.return_value.get.return_value.execute.return_value = {
                'body': {
                    'content': [
                        {'endIndex': 10}
                    ]
                }
            }

            append_result = append_to_document('flow-doc-1', '\nAppended text')
            assert "✅ Text appended" in append_result

            # Export
            mock_service.files.return_value.export.return_value.execute.return_value = b'Start\nAppended text'

            export_result = export_document('flow-doc-1', 'text')
            assert 'Start\nAppended text' == export_result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_special_characters_in_content(self, mock_credentials):
        """Test handling of special characters and unicode."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'unicode-doc'
            }
            mock_service.documents.return_value.batchUpdate.return_value.execute.return_value = {}

            special_text = "Special chars: émojis 🎉 中文 العربية \n\t\r"
            result = create_document("Unicode Test", special_text)

            # Verify special characters are passed through
            call_args = mock_service.documents.return_value.batchUpdate.call_args
            assert call_args[1]['body']['requests'][0]['insertText']['text'] == special_text

    def test_very_long_document_title(self, mock_credentials):
        """Test with very long document title."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.documents.return_value.create.return_value.execute.return_value = {
                'documentId': 'long-title-doc'
            }

            long_title = "A" * 1000
            result = create_document(long_title)

            call_args = mock_service.documents.return_value.create.call_args
            assert call_args[1]['body']['title'] == long_title

    def test_search_with_special_characters_in_query(self, mock_credentials):
        """Test search with special characters in query."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {'files': []}

            special_query = "test's \"quoted\" text & symbols"
            search_documents(query=special_query)

            call_args = mock_service.files.return_value.list.call_args
            assert special_query in call_args[1]['q']

    def test_max_results_boundary_values(self, mock_credentials):
        """Test search with boundary values for max_results."""
        with patch('google_cloud_mcp.server.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            mock_service.files.return_value.list.return_value.execute.return_value = {'files': []}

            # Test with 0
            search_documents(max_results=0)
            assert mock_service.files.return_value.list.call_args[1]['pageSize'] == 0

            # Test with large number
            search_documents(max_results=1000)
            assert mock_service.files.return_value.list.call_args[1]['pageSize'] == 1000
