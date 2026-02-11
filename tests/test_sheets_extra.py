"""
Comprehensive tests for Google Sheets extra tools.

Tests the following tools from google_cloud_mcp.server:
- search_spreadsheets: Search for spreadsheets using Drive API v3
- clear_spreadsheet_range: Clear a range in a spreadsheet
- batch_update_spreadsheet: Batch update multiple ranges
- add_sheet: Add a new sheet to a spreadsheet
- export_spreadsheet: Export spreadsheet in various formats
"""

import base64
import json
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from googleapiclient.errors import HttpError

from google_cloud_mcp import server
search_spreadsheets = server.search_spreadsheets.fn
clear_spreadsheet_range = server.clear_spreadsheet_range.fn
batch_update_spreadsheet = server.batch_update_spreadsheet.fn
add_sheet = server.add_sheet.fn
export_spreadsheet = server.export_spreadsheet.fn


class TestSearchSpreadsheets:
    """Test search_spreadsheets functionality."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_search_spreadsheets_success(self, mock_get_creds, mock_build):
        """Test successful spreadsheet search with results."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        mock_drive.files.return_value.list.return_value.execute.return_value = {
            'files': [
                {
                    'id': 'spreadsheet-1',
                    'name': 'Sales Report 2024',
                    'mimeType': 'application/vnd.google-apps.spreadsheet',
                    'modifiedTime': '2024-02-10T14:30:00.000Z'
                },
                {
                    'id': 'spreadsheet-2',
                    'name': 'Budget Planning',
                    'mimeType': 'application/vnd.google-apps.spreadsheet',
                    'modifiedTime': '2024-02-11T11:20:00.000Z'
                }
            ]
        }

        result = search_spreadsheets(query="Sales", max_results=10)

        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)

        # Verify query parameters
        call_kwargs = mock_drive.files.return_value.list.call_args[1]
        assert 'q' in call_kwargs
        assert 'application/vnd.google-apps.spreadsheet' in call_kwargs['q']
        assert 'Sales' in call_kwargs['q']
        assert call_kwargs['pageSize'] == 10

        # The actual function returns a formatted string
        assert 'Sales Report 2024' in result
        assert 'Budget Planning' in result
        assert 'spreadsheet-1' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_search_spreadsheets_empty_query(self, mock_get_creds, mock_build):
        """Test search with empty query returns all spreadsheets."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        mock_drive.files.return_value.list.return_value.execute.return_value = {'files': []}

        result = search_spreadsheets(query="", max_results=20)

        # Verify query only filters by mimeType
        call_kwargs = mock_drive.files.return_value.list.call_args[1]
        assert "mimeType='application/vnd.google-apps.spreadsheet'" in call_kwargs['q']
        assert call_kwargs['pageSize'] == 20

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_search_spreadsheets_no_results(self, mock_get_creds, mock_build):
        """Test search with no results."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        mock_drive.files.return_value.list.return_value.execute.return_value = {'files': []}

        result = search_spreadsheets(query="NonexistentSpreadsheet", max_results=20)

        assert result == "No spreadsheets found."

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_search_spreadsheets_api_error(self, mock_get_creds, mock_build):
        """Test search handles API errors gracefully."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        error_content = b'{"error": {"code": 403, "message": "Forbidden"}}'
        mock_drive.files.return_value.list.return_value.execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = search_spreadsheets(query="test", max_results=20)
        assert isinstance(result, str)


class TestClearSpreadsheetRange:
    """Test clear_spreadsheet_range functionality."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_clear_range_success(self, mock_get_creds, mock_build):
        """Test successful range clearing."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        mock_sheets.spreadsheets.return_value.values.return_value.clear.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id',
            'clearedRange': 'Sheet1!A1:B10'
        }

        result = clear_spreadsheet_range(
            spreadsheet_id='test-spreadsheet-id',
            range='Sheet1!A1:B10'
        )

        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        # The actual function returns a success string
        assert 'Cleared' in result or 'Sheet1!A1:B10' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_clear_range_invalid_range(self, mock_get_creds, mock_build):
        """Test clearing with invalid range."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        error_content = b'{"error": {"code": 400, "message": "Invalid range"}}'
        mock_sheets.spreadsheets.return_value.values.return_value.clear.return_value.execute.side_effect = HttpError(
            resp=Mock(status=400),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = clear_spreadsheet_range(
            spreadsheet_id='test-spreadsheet-id',
            range='InvalidRange!!!'
        )
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_clear_range_not_found(self, mock_get_creds, mock_build):
        """Test clearing range in non-existent spreadsheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        error_content = b'{"error": {"code": 404, "message": "Spreadsheet not found"}}'
        mock_sheets.spreadsheets.return_value.values.return_value.clear.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = clear_spreadsheet_range(
            spreadsheet_id='nonexistent-id',
            range='Sheet1!A1:B10'
        )
        assert isinstance(result, str)


class TestBatchUpdateSpreadsheet:
    """Test batch_update_spreadsheet functionality."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_batch_update_success(self, mock_get_creds, mock_build):
        """Test successful batch update."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        mock_sheets.spreadsheets.return_value.values.return_value.batchUpdate.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id',
            'totalUpdatedCells': 45
        }

        batch_data = [
            {
                'range': 'Sheet1!A1:B5',
                'values': [
                    ['Header1', 'Header2'],
                    ['Value1', 'Value2'],
                ]
            },
            {
                'range': 'Sheet2!C1:D10',
                'values': [['Data'] * 2] * 10
            }
        ]

        result = batch_update_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            data=json.dumps(batch_data)
        )

        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        # Verify batch update parameters
        call_kwargs = mock_sheets.spreadsheets.return_value.values.return_value.batchUpdate.call_args[1]
        assert call_kwargs['spreadsheetId'] == 'test-spreadsheet-id'
        assert 'body' in call_kwargs
        assert call_kwargs['body']['valueInputOption'] == 'USER_ENTERED'
        assert len(call_kwargs['body']['data']) == 2

        # The actual function returns a success string
        assert 'Batch updated' in result or '2 ranges' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_batch_update_json_parse_error(self, mock_get_creds, mock_build):
        """Test batch update with invalid JSON."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        # Invalid JSON string
        invalid_json = "{'invalid': json syntax}"

        # The actual function catches JSONDecodeError and returns an error string
        result = batch_update_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            data=invalid_json
        )

        assert 'Invalid JSON' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_batch_update_malformed_data(self, mock_get_creds, mock_build):
        """Test batch update with malformed data structure."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        error_content = b'{"error": {"code": 400, "message": "Invalid batch update data"}}'
        mock_sheets.spreadsheets.return_value.values.return_value.batchUpdate.return_value.execute.side_effect = HttpError(
            resp=Mock(status=400),
            content=error_content
        )

        # Valid JSON but missing required fields
        malformed_data = json.dumps([{'range': 'A1'}])  # Missing 'values'

        # The actual function catches exceptions and returns error string
        result = batch_update_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            data=malformed_data
        )
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_batch_update_empty_data(self, mock_get_creds, mock_build):
        """Test batch update with empty data array."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        mock_sheets.spreadsheets.return_value.values.return_value.batchUpdate.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id',
            'totalUpdatedCells': 0
        }

        result = batch_update_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            data=json.dumps([])
        )

        # The actual function returns a success string
        assert 'Batch updated' in result or '0 ranges' in result


class TestAddSheet:
    """Test add_sheet functionality."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_add_sheet_success(self, mock_get_creds, mock_build):
        """Test successfully adding a new sheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        mock_sheets.spreadsheets.return_value.batchUpdate.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id',
            'replies': [
                {
                    'addSheet': {
                        'properties': {
                            'sheetId': 123456,
                            'title': 'New Sheet'
                        }
                    }
                }
            ]
        }

        result = add_sheet(
            spreadsheet_id='test-spreadsheet-id',
            sheet_name='New Sheet'
        )

        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        # Verify batchUpdate request structure
        call_kwargs = mock_sheets.spreadsheets.return_value.batchUpdate.call_args[1]
        assert call_kwargs['spreadsheetId'] == 'test-spreadsheet-id'
        assert 'body' in call_kwargs
        assert 'requests' in call_kwargs['body']

        requests = call_kwargs['body']['requests']
        assert len(requests) == 1
        assert 'addSheet' in requests[0]
        assert requests[0]['addSheet']['properties']['title'] == 'New Sheet'

        # The actual function returns a success string
        assert 'New Sheet' in result or 'added' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_add_sheet_duplicate_name(self, mock_get_creds, mock_build):
        """Test adding sheet with duplicate name."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        error_content = b'{"error": {"code": 400, "message": "Sheet name already exists"}}'
        mock_sheets.spreadsheets.return_value.batchUpdate.return_value.execute.side_effect = HttpError(
            resp=Mock(status=400),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = add_sheet(
            spreadsheet_id='test-spreadsheet-id',
            sheet_name='ExistingSheet'
        )
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_add_sheet_invalid_spreadsheet(self, mock_get_creds, mock_build):
        """Test adding sheet to non-existent spreadsheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        error_content = b'{"error": {"code": 404, "message": "Spreadsheet not found"}}'
        mock_sheets.spreadsheets.return_value.batchUpdate.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = add_sheet(
            spreadsheet_id='nonexistent-id',
            sheet_name='New Sheet'
        )
        assert isinstance(result, str)


class TestExportSpreadsheet:
    """Test export_spreadsheet functionality."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_csv_success(self, mock_get_creds, mock_build):
        """Test successful CSV export (text format)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        csv_content = b"Name,Age,City\nJohn,30,NYC\nJane,25,LA"
        mock_drive.files.return_value.export.return_value.execute.return_value = csv_content

        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            format='csv',
            sheet_id=0
        )

        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)

        # Verify export parameters
        call_kwargs = mock_drive.files.return_value.export.call_args[1]
        assert call_kwargs['fileId'] == 'test-spreadsheet-id'
        assert call_kwargs['mimeType'] == 'text/csv'

        # CSV should be returned as string
        assert isinstance(result, str)
        assert result == csv_content.decode('utf-8')
        assert 'Name,Age,City' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_tsv_success(self, mock_get_creds, mock_build):
        """Test successful TSV export (text format)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        tsv_content = b"Name\tAge\tCity\nJohn\t30\tNYC\nJane\t25\tLA"
        mock_drive.files.return_value.export.return_value.execute.return_value = tsv_content

        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            format='tsv',
            sheet_id=0
        )

        # Verify export MIME type
        call_kwargs = mock_drive.files.return_value.export.call_args[1]
        assert call_kwargs['mimeType'] == 'text/tab-separated-values'

        # TSV should be returned as string
        assert isinstance(result, str)
        assert '\t' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_xlsx_success(self, mock_get_creds, mock_build):
        """Test successful XLSX export (binary format)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        # Simulate binary XLSX content
        xlsx_content = b'\x50\x4b\x03\x04'  # ZIP file signature (XLSX files are ZIP)
        mock_drive.files.return_value.export.return_value.execute.return_value = xlsx_content

        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            format='xlsx',
            sheet_id=0
        )

        # Verify export MIME type
        call_kwargs = mock_drive.files.return_value.export.call_args[1]
        assert call_kwargs['mimeType'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        # The actual function returns a formatted string with base64 excerpt
        assert isinstance(result, str)
        assert 'Exported as xlsx' in result or 'base64' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_pdf_success(self, mock_get_creds, mock_build):
        """Test successful PDF export (binary format)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        # Simulate binary PDF content
        pdf_content = b'%PDF-1.4\n%\xE2\xE3\xCF\xD3'  # PDF file signature
        mock_drive.files.return_value.export.return_value.execute.return_value = pdf_content

        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            format='pdf',
            sheet_id=0
        )

        # Verify export MIME type
        call_kwargs = mock_drive.files.return_value.export.call_args[1]
        assert call_kwargs['mimeType'] == 'application/pdf'

        # The actual function returns a formatted string with base64 excerpt
        assert isinstance(result, str)
        assert 'Exported as pdf' in result or 'base64' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_unsupported_format(self, mock_get_creds, mock_build):
        """Test export with unsupported format."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        # The actual function returns an error string for unsupported formats
        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            format='unsupported_format',
            sheet_id=0
        )

        assert 'Unsupported format' in result or 'unsupported_format' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_default_format(self, mock_get_creds, mock_build):
        """Test export with default format (CSV)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        csv_content = b"Data"
        mock_drive.files.return_value.export.return_value.execute.return_value = csv_content

        # Call without specifying format (should default to CSV)
        result = export_spreadsheet(
            spreadsheet_id='test-spreadsheet-id',
            sheet_id=0
        )

        # Verify CSV MIME type was used
        call_kwargs = mock_drive.files.return_value.export.call_args[1]
        assert call_kwargs['mimeType'] == 'text/csv'

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_spreadsheet_not_found(self, mock_get_creds, mock_build):
        """Test export of non-existent spreadsheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        error_content = b'{"error": {"code": 404, "message": "File not found"}}'
        mock_drive.files.return_value.export.return_value.execute.side_effect = HttpError(
            resp=Mock(status=404),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = export_spreadsheet(
            spreadsheet_id='nonexistent-id',
            format='csv',
            sheet_id=0
        )
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_export_permission_denied(self, mock_get_creds, mock_build):
        """Test export with insufficient permissions."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_drive = MagicMock()
        mock_build.return_value = mock_drive

        error_content = b'{"error": {"code": 403, "message": "Permission denied"}}'
        mock_drive.files.return_value.export.return_value.execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=error_content
        )

        # The actual function catches exceptions and returns error string
        result = export_spreadsheet(
            spreadsheet_id='restricted-spreadsheet-id',
            format='csv',
            sheet_id=0
        )
        assert isinstance(result, str)


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_search_and_export_workflow(self, mock_get_creds, mock_build):
        """Test workflow: search for spreadsheet, then export it."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        # Setup mocks for both Drive and Sheets services
        def build_service(service_name, version, credentials):
            if service_name == 'drive':
                mock_drive = MagicMock()
                mock_files = MagicMock()

                # Mock search
                mock_list = MagicMock()
                mock_list.execute.return_value = {
                    'files': [{'id': 'found-spreadsheet-id', 'name': 'Target Sheet', 'modifiedTime': '2024-01-01'}]
                }
                mock_files.list.return_value = mock_list

                # Mock export
                mock_export = MagicMock()
                mock_export.execute.return_value = b"exported,data"
                mock_files.export.return_value = mock_export

                mock_drive.files.return_value = mock_files
                return mock_drive
            return MagicMock()

        mock_build.side_effect = build_service

        # Search for spreadsheet
        search_results = search_spreadsheets(query="Target", max_results=1)
        assert 'Target Sheet' in search_results
        assert 'found-spreadsheet-id' in search_results

        # Export found spreadsheet
        exported_data = export_spreadsheet(
            spreadsheet_id='found-spreadsheet-id',
            format='csv',
            sheet_id=0
        )

        assert exported_data == "exported,data"

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_add_sheet_and_batch_update_workflow(self, mock_get_creds, mock_build):
        """Test workflow: add new sheet, then batch update data."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_sheets = MagicMock()
        mock_build.return_value = mock_sheets

        # Mock add sheet
        mock_sheets.spreadsheets.return_value.batchUpdate.return_value.execute.return_value = {
            'replies': [{'addSheet': {'properties': {'sheetId': 999, 'title': 'DataSheet'}}}]
        }

        # Mock batch update values
        mock_sheets.spreadsheets.return_value.values.return_value.batchUpdate.return_value.execute.return_value = {
            'totalUpdatedCells': 10
        }

        # Add new sheet
        add_result = add_sheet(
            spreadsheet_id='test-id',
            sheet_name='DataSheet'
        )

        assert 'DataSheet' in add_result or 'added' in add_result

        # Update data in new sheet
        batch_data = json.dumps([{
            'range': 'DataSheet!A1:B2',
            'values': [['Header1', 'Header2'], ['Value1', 'Value2']]
        }])

        update_result = batch_update_spreadsheet(
            spreadsheet_id='test-id',
            data=batch_data
        )

        assert 'Batch updated' in update_result or '1 ranges' in update_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
