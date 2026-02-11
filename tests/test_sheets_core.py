"""
Comprehensive test suite for Google Sheets core tools.

Tests the following tools from google_cloud_mcp.server:
- create_spreadsheet
- read_spreadsheet
- update_spreadsheet
- append_to_spreadsheet
- get_spreadsheet_info

All tests use mocked Google Sheets API v4 and credentials.
"""

import json
import pytest
from unittest.mock import Mock, MagicMock, patch, call

# Import the functions to test
# @mcp.tool() wraps functions into FunctionTool objects,
# so we access the underlying function via .fn
from google_cloud_mcp import server
create_spreadsheet = server.create_spreadsheet.fn
read_spreadsheet = server.read_spreadsheet.fn
update_spreadsheet = server.update_spreadsheet.fn
append_to_spreadsheet = server.append_to_spreadsheet.fn
get_spreadsheet_info = server.get_spreadsheet_info.fn


class TestCreateSpreadsheet:
    """Test suite for create_spreadsheet tool."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_create_spreadsheet_success_default_sheet(self, mock_get_creds, mock_build):
        """Test successful spreadsheet creation with default sheet name."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.create.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id-123',
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test-spreadsheet-id-123/edit',
            'properties': {'title': 'Test Spreadsheet'}
        }

        result = create_spreadsheet(title='Test Spreadsheet')

        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        # Verify the API call structure
        call_kwargs = mock_service.spreadsheets.return_value.create.call_args[1]
        assert 'body' in call_kwargs
        body = call_kwargs['body']
        assert body['properties']['title'] == 'Test Spreadsheet'
        assert 'sheets' in body
        assert len(body['sheets']) == 1
        assert body['sheets'][0]['properties']['title'] == 'Sheet1'

        # The actual function returns a string with the URL
        assert 'test-spreadsheet-id-123' in result
        assert 'Spreadsheet created' in result or 'spreadsheets' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_create_spreadsheet_success_custom_sheet(self, mock_get_creds, mock_build):
        """Test successful spreadsheet creation with custom sheet name."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.create.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id-456',
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test-spreadsheet-id-456/edit',
            'properties': {'title': 'Custom Spreadsheet'}
        }

        result = create_spreadsheet(title='Custom Spreadsheet', sheet_name='CustomSheet')

        call_kwargs = mock_service.spreadsheets.return_value.create.call_args[1]
        body = call_kwargs['body']

        assert body['properties']['title'] == 'Custom Spreadsheet'
        assert body['sheets'][0]['properties']['title'] == 'CustomSheet'
        assert 'test-spreadsheet-id-456' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_create_spreadsheet_api_error(self, mock_get_creds, mock_build):
        """Test handling of API errors during spreadsheet creation."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 403
        error = HttpError(resp=mock_response, content=b'Permission denied')

        mock_service.spreadsheets.return_value.create.return_value.execute.side_effect = error

        # The function catches all exceptions and returns error string
        result = create_spreadsheet(title='Test Spreadsheet')
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_create_spreadsheet_empty_title(self, mock_get_creds, mock_build):
        """Test spreadsheet creation with empty title."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.create.return_value.execute.return_value = {
            'spreadsheetId': 'test-spreadsheet-id-789',
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test-spreadsheet-id-789/edit'
        }

        result = create_spreadsheet(title='')

        call_kwargs = mock_service.spreadsheets.return_value.create.call_args[1]
        body = call_kwargs['body']
        assert body['properties']['title'] == ''
        assert 'test-spreadsheet-id-789' in result


class TestReadSpreadsheet:
    """Test suite for read_spreadsheet tool."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_spreadsheet_success_default_range(self, mock_get_creds, mock_build):
        """Test successful reading of spreadsheet with default range."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            'range': 'Sheet1!A1:Z1000',
            'majorDimension': 'ROWS',
            'values': [
                ['Header 1', 'Header 2', 'Header 3'],
                ['Value 1', 'Value 2', 'Value 3'],
                ['Value 4', 'Value 5', 'Value 6']
            ]
        }

        result = read_spreadsheet(spreadsheet_id='test-id-123')

        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        mock_service.spreadsheets.return_value.values.return_value.get.assert_called_once_with(
            spreadsheetId='test-id-123',
            range='Sheet1'
        )

        # The actual function returns tab-separated text
        assert 'Header 1' in result
        assert 'Value 1' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_spreadsheet_success_custom_range(self, mock_get_creds, mock_build):
        """Test successful reading of spreadsheet with custom range."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            'range': 'Sheet1!A1:C3',
            'majorDimension': 'ROWS',
            'values': [
                ['A1', 'B1', 'C1'],
                ['A2', 'B2', 'C2'],
                ['A3', 'B3', 'C3']
            ]
        }

        result = read_spreadsheet(spreadsheet_id='test-id-456', range='Sheet1!A1:C3')

        mock_service.spreadsheets.return_value.values.return_value.get.assert_called_once_with(
            spreadsheetId='test-id-456',
            range='Sheet1!A1:C3'
        )

        # The actual function returns tab-separated text
        assert 'A1' in result
        assert 'B2' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_spreadsheet_empty_data(self, mock_get_creds, mock_build):
        """Test reading spreadsheet with no data."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            'range': 'Sheet1!A1:Z1000',
            'majorDimension': 'ROWS'
            # No 'values' key when empty
        }

        result = read_spreadsheet(spreadsheet_id='test-id-789')

        # The actual function returns "No data found." when values is empty
        assert result == "No data found."

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_spreadsheet_not_found_error(self, mock_get_creds, mock_build):
        """Test handling of spreadsheet not found error."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 404
        error = HttpError(resp=mock_response, content=b'Spreadsheet not found')

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.side_effect = error

        # The function catches all exceptions and returns error string
        result = read_spreadsheet(spreadsheet_id='invalid-id')
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_spreadsheet_permission_error(self, mock_get_creds, mock_build):
        """Test handling of permission errors."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 403
        error = HttpError(resp=mock_response, content=b'Permission denied')

        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.side_effect = error

        # The function catches all exceptions and returns error string
        result = read_spreadsheet(spreadsheet_id='test-id-no-permission')
        assert isinstance(result, str)


class TestUpdateSpreadsheet:
    """Test suite for update_spreadsheet tool."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_success(self, mock_get_creds, mock_build):
        """Test successful spreadsheet update."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-123',
            'updatedRange': 'Sheet1!A1:B2',
            'updatedRows': 2,
            'updatedColumns': 2,
            'updatedCells': 4
        }

        values_json = json.dumps([['A1', 'B1'], ['A2', 'B2']])

        result = update_spreadsheet(
            spreadsheet_id='test-id-123',
            range='Sheet1!A1:B2',
            values=values_json
        )

        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        mock_service.spreadsheets.return_value.values.return_value.update.assert_called_once_with(
            spreadsheetId='test-id-123',
            range='Sheet1!A1:B2',
            valueInputOption='USER_ENTERED',
            body={'values': [['A1', 'B1'], ['A2', 'B2']]}
        )

        # The actual function returns a success string
        assert 'Updated' in result or 'test-id-123' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_complex_data(self, mock_get_creds, mock_build):
        """Test updating spreadsheet with complex data types."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-456',
            'updatedCells': 12
        }

        values = [
            ['Name', 'Age', 'Score', 'Total'],
            ['Alice', 25, 95, '=C2*2'],
            ['Bob', 30, 87, '=C3*2']
        ]
        values_json = json.dumps(values)

        result = update_spreadsheet(
            spreadsheet_id='test-id-456',
            range='Sheet1!A1:D3',
            values=values_json
        )

        call_kwargs = mock_service.spreadsheets.return_value.values.return_value.update.call_args[1]
        assert call_kwargs['valueInputOption'] == 'USER_ENTERED'
        assert call_kwargs['body']['values'] == values
        assert 'Updated' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_invalid_json(self, mock_get_creds, mock_build):
        """Test handling of invalid JSON input."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        invalid_json = "not a valid json string"

        # The actual function catches JSONDecodeError and returns an error string
        result = update_spreadsheet(
            spreadsheet_id='test-id-789',
            range='Sheet1!A1',
            values=invalid_json
        )

        assert 'Invalid JSON' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_malformed_json(self, mock_get_creds, mock_build):
        """Test handling of malformed JSON (missing brackets)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        malformed_json = "['A1', 'B1']"  # Single quotes instead of double

        # The actual function catches JSONDecodeError and returns an error string
        result = update_spreadsheet(
            spreadsheet_id='test-id-abc',
            range='Sheet1!A1',
            values=malformed_json
        )

        assert 'Invalid JSON' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_empty_values(self, mock_get_creds, mock_build):
        """Test updating spreadsheet with empty values."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-empty',
            'updatedCells': 0
        }

        values_json = json.dumps([])

        result = update_spreadsheet(
            spreadsheet_id='test-id-empty',
            range='Sheet1!A1',
            values=values_json
        )

        call_kwargs = mock_service.spreadsheets.return_value.values.return_value.update.call_args[1]
        assert call_kwargs['body']['values'] == []
        assert 'Updated' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_update_spreadsheet_api_error(self, mock_get_creds, mock_build):
        """Test handling of API errors during update."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 400
        error = HttpError(resp=mock_response, content=b'Invalid range')

        mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.side_effect = error

        values_json = json.dumps([['A1', 'B1']])

        # The function catches all exceptions and returns error string
        result = update_spreadsheet(
            spreadsheet_id='test-id-error',
            range='InvalidRange',
            values=values_json
        )
        assert isinstance(result, str)


class TestAppendToSpreadsheet:
    """Test suite for append_to_spreadsheet tool."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_success(self, mock_get_creds, mock_build):
        """Test successful append to spreadsheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-123',
            'tableRange': 'Sheet1!A1:B5',
            'updates': {
                'spreadsheetId': 'test-id-123',
                'updatedRange': 'Sheet1!A6:B7',
                'updatedRows': 2,
                'updatedColumns': 2,
                'updatedCells': 4
            }
        }

        values_json = json.dumps([['New Row 1', 'Data 1'], ['New Row 2', 'Data 2']])

        result = append_to_spreadsheet(
            spreadsheet_id='test-id-123',
            range='Sheet1!A:B',
            values=values_json
        )

        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        mock_service.spreadsheets.return_value.values.return_value.append.assert_called_once_with(
            spreadsheetId='test-id-123',
            range='Sheet1!A:B',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [['New Row 1', 'Data 1'], ['New Row 2', 'Data 2']]}
        )

        # The actual function returns a success string
        assert 'Appended' in result or '2 rows' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_single_row(self, mock_get_creds, mock_build):
        """Test appending a single row."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-456',
            'updates': {
                'updatedRange': 'Sheet1!A10:C10',
                'updatedRows': 1,
                'updatedColumns': 3,
                'updatedCells': 3
            }
        }

        values_json = json.dumps([['Col1', 'Col2', 'Col3']])

        result = append_to_spreadsheet(
            spreadsheet_id='test-id-456',
            range='Sheet1',
            values=values_json
        )

        call_kwargs = mock_service.spreadsheets.return_value.values.return_value.append.call_args[1]
        assert call_kwargs['insertDataOption'] == 'INSERT_ROWS'
        assert call_kwargs['body']['values'] == [['Col1', 'Col2', 'Col3']]
        assert 'Appended' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_invalid_json(self, mock_get_creds, mock_build):
        """Test handling of invalid JSON input for append."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        invalid_json = "{invalid json}"

        # The actual function catches JSONDecodeError and returns an error string
        result = append_to_spreadsheet(
            spreadsheet_id='test-id-789',
            range='Sheet1',
            values=invalid_json
        )

        assert 'Invalid JSON' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_json_parse_error_incomplete(self, mock_get_creds, mock_build):
        """Test handling of incomplete JSON."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        incomplete_json = '[["A1", "B1"]'  # Missing closing bracket

        # The actual function catches JSONDecodeError and returns an error string
        result = append_to_spreadsheet(
            spreadsheet_id='test-id-incomplete',
            range='Sheet1',
            values=incomplete_json
        )

        assert 'Invalid JSON' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_empty_values(self, mock_get_creds, mock_build):
        """Test appending empty values array."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-empty',
            'updates': {
                'updatedRows': 0,
                'updatedColumns': 0,
                'updatedCells': 0
            }
        }

        values_json = json.dumps([])

        result = append_to_spreadsheet(
            spreadsheet_id='test-id-empty',
            range='Sheet1',
            values=values_json
        )

        call_kwargs = mock_service.spreadsheets.return_value.values.return_value.append.call_args[1]
        assert call_kwargs['body']['values'] == []
        assert 'Appended' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_with_formulas(self, mock_get_creds, mock_build):
        """Test appending rows with formulas (USER_ENTERED should evaluate them)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-formulas',
            'updates': {
                'updatedRange': 'Sheet1!A5:C5',
                'updatedRows': 1,
                'updatedColumns': 3,
                'updatedCells': 3
            }
        }

        values_json = json.dumps([['=SUM(A1:A4)', '=AVERAGE(B1:B4)', 'Total']])

        result = append_to_spreadsheet(
            spreadsheet_id='test-id-formulas',
            range='Sheet1!A:C',
            values=values_json
        )

        call_kwargs = mock_service.spreadsheets.return_value.values.return_value.append.call_args[1]
        assert call_kwargs['valueInputOption'] == 'USER_ENTERED'
        assert call_kwargs['body']['values'] == [['=SUM(A1:A4)', '=AVERAGE(B1:B4)', 'Total']]
        assert 'Appended' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_append_to_spreadsheet_api_error(self, mock_get_creds, mock_build):
        """Test handling of API errors during append."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 403
        error = HttpError(resp=mock_response, content=b'Permission denied')

        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.side_effect = error

        values_json = json.dumps([['Data']])

        # The function catches all exceptions and returns error string
        result = append_to_spreadsheet(
            spreadsheet_id='test-id-error',
            range='Sheet1',
            values=values_json
        )
        assert isinstance(result, str)


class TestGetSpreadsheetInfo:
    """Test suite for get_spreadsheet_info tool."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_success_single_sheet(self, mock_get_creds, mock_build):
        """Test successful retrieval of spreadsheet info with single sheet."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-123',
            'properties': {
                'title': 'My Spreadsheet',
                'locale': 'en_US',
                'timeZone': 'America/New_York'
            },
            'sheets': [
                {
                    'properties': {
                        'sheetId': 0,
                        'title': 'Sheet1',
                        'index': 0,
                        'sheetType': 'GRID',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26
                        }
                    }
                }
            ]
        }

        result = get_spreadsheet_info(spreadsheet_id='test-id-123')

        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)

        mock_service.spreadsheets.return_value.get.assert_called_once_with(
            spreadsheetId='test-id-123'
        )

        # The actual function returns a formatted string
        assert 'My Spreadsheet' in result
        assert 'Sheet1' in result
        assert '1000' in result
        assert '26' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_success_multiple_sheets(self, mock_get_creds, mock_build):
        """Test retrieval of spreadsheet info with multiple sheets."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-456',
            'properties': {
                'title': 'Multi-Sheet Spreadsheet'
            },
            'sheets': [
                {
                    'properties': {
                        'sheetId': 0,
                        'title': 'Sheet1',
                        'index': 0,
                        'gridProperties': {'rowCount': 500, 'columnCount': 10}
                    }
                },
                {
                    'properties': {
                        'sheetId': 1,
                        'title': 'Sheet2',
                        'index': 1,
                        'gridProperties': {'rowCount': 1000, 'columnCount': 20}
                    }
                },
                {
                    'properties': {
                        'sheetId': 2,
                        'title': 'Data Analysis',
                        'index': 2,
                        'gridProperties': {'rowCount': 2000, 'columnCount': 50}
                    }
                }
            ]
        }

        result = get_spreadsheet_info(spreadsheet_id='test-id-456')

        assert 'Multi-Sheet Spreadsheet' in result
        assert 'Sheet1' in result
        assert 'Sheet2' in result
        assert 'Data Analysis' in result
        assert '2000' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_not_found(self, mock_get_creds, mock_build):
        """Test handling of spreadsheet not found error."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 404
        error = HttpError(resp=mock_response, content=b'Requested entity was not found')

        mock_service.spreadsheets.return_value.get.return_value.execute.side_effect = error

        # The function catches all exceptions and returns error string
        result = get_spreadsheet_info(spreadsheet_id='non-existent-id')
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_permission_denied(self, mock_get_creds, mock_build):
        """Test handling of permission denied error."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 403
        error = HttpError(resp=mock_response, content=b'The caller does not have permission')

        mock_service.spreadsheets.return_value.get.return_value.execute.side_effect = error

        # The function catches all exceptions and returns error string
        result = get_spreadsheet_info(spreadsheet_id='restricted-id')
        assert isinstance(result, str)

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_empty_sheets(self, mock_get_creds, mock_build):
        """Test handling of spreadsheet with no sheets (edge case)."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-empty',
            'properties': {
                'title': 'Empty Spreadsheet'
            },
            'sheets': []
        }

        result = get_spreadsheet_info(spreadsheet_id='test-id-empty')

        assert 'Empty Spreadsheet' in result

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_get_spreadsheet_info_with_frozen_rows_columns(self, mock_get_creds, mock_build):
        """Test retrieval of spreadsheet info with frozen rows and columns."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            'spreadsheetId': 'test-id-frozen',
            'properties': {
                'title': 'Spreadsheet with Frozen Headers'
            },
            'sheets': [
                {
                    'properties': {
                        'sheetId': 0,
                        'title': 'Data',
                        'index': 0,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 26,
                            'frozenRowCount': 1,
                            'frozenColumnCount': 2
                        }
                    }
                }
            ]
        }

        result = get_spreadsheet_info(spreadsheet_id='test-id-frozen')

        assert 'Spreadsheet with Frozen Headers' in result
        assert 'Data' in result
        assert '1000' in result


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_create_then_update_workflow(self, mock_get_creds, mock_build):
        """Test workflow: create spreadsheet, then update it."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock create response
        mock_service.spreadsheets.return_value.create.return_value.execute.return_value = {
            'spreadsheetId': 'new-spreadsheet-id',
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/new-spreadsheet-id/edit',
            'properties': {'title': 'New Spreadsheet'}
        }

        # Mock update response
        mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
            'spreadsheetId': 'new-spreadsheet-id',
            'updatedRange': 'Sheet1!A1:B2',
            'updatedRows': 2,
            'updatedColumns': 2,
            'updatedCells': 4
        }

        # Create spreadsheet
        created = create_spreadsheet(title='New Spreadsheet')
        assert 'new-spreadsheet-id' in created

        # Update spreadsheet
        values_json = json.dumps([['Header 1', 'Header 2'], ['Data 1', 'Data 2']])
        updated = update_spreadsheet(
            spreadsheet_id='new-spreadsheet-id',
            range='Sheet1!A1:B2',
            values=values_json
        )

        assert 'Updated' in updated

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_read_then_append_workflow(self, mock_get_creds, mock_build):
        """Test workflow: read existing data, then append new rows."""
        mock_creds = Mock()
        mock_get_creds.return_value = mock_creds

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock read response
        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            'range': 'Sheet1!A1:B3',
            'values': [
                ['Name', 'Score'],
                ['Alice', '95'],
                ['Bob', '87']
            ]
        }

        # Mock append response
        mock_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            'spreadsheetId': 'test-id',
            'updates': {
                'updatedRange': 'Sheet1!A4:B4',
                'updatedRows': 1,
                'updatedCells': 2
            }
        }

        # Read existing data
        existing_data = read_spreadsheet(spreadsheet_id='test-id', range='Sheet1')
        assert 'Name' in existing_data
        assert 'Alice' in existing_data

        # Append new row
        new_row_json = json.dumps([['Charlie', '92']])
        append_result = append_to_spreadsheet(
            spreadsheet_id='test-id',
            range='Sheet1!A:B',
            values=new_row_json
        )

        assert 'Appended' in append_result


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
