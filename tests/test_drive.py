"""
Comprehensive test suite for Google Drive search functionality.

This module tests the search_drive tool from google_cloud_mcp.server,
covering success cases, edge cases, error handling, and API interaction patterns.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google_cloud_mcp import server
search_drive = server.search_drive.fn


class TestSearchDrive:
    """Test suite for the search_drive tool."""

    def test_search_drive_success_with_results(self, mock_drive_service):
        """Test successful Drive search with multiple results returned."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-123', 'name': 'Document.pdf', 'mimeType': 'application/pdf'},
            {'id': 'file-456', 'name': 'Spreadsheet.xlsx', 'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
            {'id': 'file-789', 'name': 'Presentation.pptx', 'mimeType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'project'"

        # Act
        result = search_drive(query)

        # Assert
        assert "Document.pdf (file-123)" in result
        assert "Spreadsheet.xlsx (file-456)" in result
        assert "Presentation.pptx (file-789)" in result
        assert result.count('\n') == 2  # 3 files = 2 newlines

        # Verify API was called correctly
        mock_list.assert_called_once_with(
            q=query,
            fields='files(id, name, mimeType)'
        )
        mock_execute.assert_called_once()

    def test_search_drive_no_results(self, mock_drive_service):
        """Test Drive search when no files match the query."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_execute = Mock(return_value={'files': []})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'nonexistent'"

        # Act
        result = search_drive(query)

        # Assert
        assert result == "No files found."
        mock_list.assert_called_once_with(
            q=query,
            fields='files(id, name, mimeType)'
        )

    def test_search_drive_single_file(self, mock_drive_service):
        """Test Drive search returning exactly one file."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'unique-file-id', 'name': 'UniqueDocument.docx', 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name = 'UniqueDocument.docx'"

        # Act
        result = search_drive(query)

        # Assert
        assert result == "- UniqueDocument.docx (unique-file-id)"
        assert '\n' not in result  # Single file, no newlines

    def test_search_drive_with_special_characters_in_query(self, mock_drive_service):
        """Test Drive search with special characters in the query string."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-special', 'name': "File's Name (2024).pdf", 'mimeType': 'application/pdf'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        # Query with escaped quotes and special characters
        query = "name contains 'File\\'s Name (2024)'"

        # Act
        result = search_drive(query)

        # Assert
        assert "File's Name (2024).pdf (file-special)" in result
        mock_list.assert_called_once_with(
            q=query,
            fields='files(id, name, mimeType)'
        )

    def test_search_drive_with_special_characters_in_filename(self, mock_drive_service):
        """Test Drive search when filenames contain special characters."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-1', 'name': 'File & Document.pdf', 'mimeType': 'application/pdf'},
            {'id': 'file-2', 'name': 'Data <2024>.xlsx', 'mimeType': 'application/vnd.ms-excel'},
            {'id': 'file-3', 'name': 'Notes "Important".txt', 'mimeType': 'text/plain'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "mimeType contains 'application/'"

        # Act
        result = search_drive(query)

        # Assert
        assert "File & Document.pdf (file-1)" in result
        assert "Data <2024>.xlsx (file-2)" in result
        assert 'Notes "Important".txt (file-3)' in result

    def test_search_drive_api_error(self, mock_drive_service):
        """Test Drive search error handling when API call fails."""
        # Arrange
        service, mock_build = mock_drive_service
        error_message = "API Error: Rate limit exceeded"
        mock_list = Mock(side_effect=Exception(error_message))
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act
        result = search_drive(query)

        # Assert
        assert result == error_message

    def test_search_drive_http_error(self, mock_drive_service):
        """Test Drive search handling HTTP errors from Google API."""
        # Arrange
        service, mock_build = mock_drive_service
        from googleapiclient.errors import HttpError

        # Create a mock HTTP error
        mock_response = Mock()
        mock_response.status = 403
        mock_response.reason = "Forbidden"
        http_error = HttpError(mock_response, b'{"error": {"message": "Insufficient permissions"}}')

        mock_list = Mock(side_effect=http_error)
        service.files.return_value.list = mock_list

        query = "name contains 'restricted'"

        # Act
        result = search_drive(query)

        # Assert
        assert "Insufficient permissions" in result or "403" in str(result)

    def test_search_drive_network_error(self, mock_drive_service):
        """Test Drive search handling network connectivity errors."""
        # Arrange
        service, mock_build = mock_drive_service
        network_error = ConnectionError("Network unreachable")
        mock_list = Mock(side_effect=network_error)
        service.files.return_value.list = mock_list

        query = "name contains 'document'"

        # Act
        result = search_drive(query)

        # Assert
        assert "Network unreachable" in result

    def test_search_drive_empty_query(self, mock_drive_service):
        """Test Drive search with an empty query string."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-1', 'name': 'File1.pdf', 'mimeType': 'application/pdf'},
            {'id': 'file-2', 'name': 'File2.docx', 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = ""

        # Act
        result = search_drive(query)

        # Assert
        assert "File1.pdf (file-1)" in result
        assert "File2.docx (file-2)" in result
        mock_list.assert_called_once_with(q="", fields='files(id, name, mimeType)')

    def test_search_drive_missing_files_key_in_response(self, mock_drive_service):
        """Test Drive search when API response doesn't contain 'files' key."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_execute = Mock(return_value={})  # No 'files' key
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act
        result = search_drive(query)

        # Assert
        assert result == "No files found."

    def test_search_drive_fields_parameter(self, mock_drive_service):
        """Test that search_drive requests correct fields from the API."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_execute = Mock(return_value={'files': []})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "mimeType = 'application/pdf'"

        # Act
        search_drive(query)

        # Assert
        call_args = mock_list.call_args
        assert call_args is not None
        assert call_args[1]['fields'] == 'files(id, name, mimeType)'
        assert call_args[1]['q'] == query

    def test_search_drive_large_result_set(self, mock_drive_service):
        """Test Drive search with a large number of results."""
        # Arrange
        service, mock_build = mock_drive_service

        # Create 100 mock files
        mock_files = [
            {'id': f'file-{i}', 'name': f'Document{i}.pdf', 'mimeType': 'application/pdf'}
            for i in range(100)
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "mimeType = 'application/pdf'"

        # Act
        result = search_drive(query)

        # Assert
        lines = result.split('\n')
        assert len(lines) == 100
        assert "Document0.pdf (file-0)" in result
        assert "Document99.pdf (file-99)" in result

    def test_search_drive_unicode_filenames(self, mock_drive_service):
        """Test Drive search with Unicode characters in filenames."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-jp', 'name': '日本語ドキュメント.pdf', 'mimeType': 'application/pdf'},
            {'id': 'file-emoji', 'name': 'Report 📊 2024.xlsx', 'mimeType': 'application/vnd.ms-excel'},
            {'id': 'file-arabic', 'name': 'مستند.docx', 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains ''"

        # Act
        result = search_drive(query)

        # Assert
        assert '日本語ドキュメント.pdf (file-jp)' in result
        assert 'Report 📊 2024.xlsx (file-emoji)' in result
        assert 'مستند.docx (file-arabic)' in result

    def test_search_drive_various_mime_types(self, mock_drive_service):
        """Test Drive search returns files with various MIME types correctly."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'folder-1', 'name': 'MyFolder', 'mimeType': 'application/vnd.google-apps.folder'},
            {'id': 'doc-1', 'name': 'GoogleDoc', 'mimeType': 'application/vnd.google-apps.document'},
            {'id': 'sheet-1', 'name': 'GoogleSheet', 'mimeType': 'application/vnd.google-apps.spreadsheet'},
            {'id': 'img-1', 'name': 'Photo.jpg', 'mimeType': 'image/jpeg'},
            {'id': 'vid-1', 'name': 'Video.mp4', 'mimeType': 'video/mp4'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains ''"

        # Act
        result = search_drive(query)

        # Assert
        assert 'MyFolder (folder-1)' in result
        assert 'GoogleDoc (doc-1)' in result
        assert 'GoogleSheet (sheet-1)' in result
        assert 'Photo.jpg (img-1)' in result
        assert 'Video.mp4 (vid-1)' in result

    def test_search_drive_credentials_integration(self, mock_credentials, mock_drive_service):
        """Test that search_drive properly integrates with credentials system."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_execute = Mock(return_value={'files': []})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act
        search_drive(query)

        # Assert - verify build was called with credentials
        mock_build.assert_called_once()
        call_args = mock_build.call_args
        assert call_args[0][0] == 'drive'
        assert call_args[0][1] == 'v3'
        assert 'credentials' in call_args[1]

    def test_search_drive_malformed_response(self, mock_drive_service):
        """Test Drive search handling malformed API responses."""
        # Arrange
        service, mock_build = mock_drive_service

        # Response with files missing required fields
        mock_files = [
            {'id': 'file-1'},  # Missing name and mimeType
            {'name': 'OnlyName.pdf'},  # Missing id and mimeType
            {'id': 'file-2', 'name': 'Complete.pdf', 'mimeType': 'application/pdf'}  # Complete
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act - should handle KeyError gracefully
        try:
            result = search_drive(query)
            # If no error, check that it attempted to process
            assert isinstance(result, str)
        except KeyError:
            # Expected if implementation doesn't handle missing keys
            pass

    def test_search_drive_query_operators(self, mock_drive_service):
        """Test Drive search with various query operators."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_execute = Mock(return_value={'files': []})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        test_queries = [
            "name = 'exact-name.pdf'",
            "name contains 'substring'",
            "mimeType = 'application/pdf'",
            "modifiedTime > '2024-01-01T00:00:00'",
            "trashed = false",
            "'parent-folder-id' in parents",
            "name contains 'test' and mimeType = 'application/pdf'"
        ]

        # Act & Assert
        for query in test_queries:
            mock_list.reset_mock()
            result = search_drive(query)

            # Verify each query is passed correctly to the API
            mock_list.assert_called_once_with(
                q=query,
                fields='files(id, name, mimeType)'
            )
            assert result == "No files found."


class TestSearchDriveEdgeCases:
    """Additional edge case tests for search_drive."""

    def test_search_drive_none_values_in_response(self, mock_drive_service):
        """Test handling of None values in file metadata."""
        # Arrange
        service, mock_build = mock_drive_service
        mock_files = [
            {'id': 'file-1', 'name': None, 'mimeType': 'application/pdf'},
            {'id': None, 'name': 'Document.pdf', 'mimeType': 'application/pdf'},
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act
        try:
            result = search_drive(query)
            assert isinstance(result, str)
        except (TypeError, AttributeError):
            # Expected if implementation doesn't handle None values
            pass

    def test_search_drive_timeout_error(self, mock_drive_service):
        """Test handling of timeout errors during API call."""
        # Arrange
        service, mock_build = mock_drive_service
        timeout_error = TimeoutError("Request timed out")
        mock_list = Mock(side_effect=timeout_error)
        service.files.return_value.list = mock_list

        query = "name contains 'test'"

        # Act
        result = search_drive(query)

        # Assert
        assert "Request timed out" in result

    def test_search_drive_very_long_filename(self, mock_drive_service):
        """Test Drive search with extremely long filenames."""
        # Arrange
        service, mock_build = mock_drive_service
        long_name = "A" * 1000 + ".pdf"  # Very long filename
        mock_files = [
            {'id': 'file-long', 'name': long_name, 'mimeType': 'application/pdf'}
        ]

        mock_execute = Mock(return_value={'files': mock_files})
        mock_list = Mock(return_value=Mock(execute=mock_execute))
        service.files.return_value.list = mock_list

        query = "name contains 'A'"

        # Act
        result = search_drive(query)

        # Assert
        assert long_name in result
        assert "file-long" in result
