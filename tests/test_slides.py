"""
Comprehensive pytest test suite for Google Slides tools.

Tests the following functions from google_cloud_mcp.server:
- create_presentation
- get_presentation
- add_slide
- add_text_to_slide
- search_presentations
- delete_slide
- export_presentation
"""

import pytest
from unittest.mock import MagicMock, patch
import base64
from google_cloud_mcp import server

# Extract the actual functions from the FunctionTool wrappers
create_presentation = server.create_presentation.fn
get_presentation = server.get_presentation.fn
add_slide = server.add_slide.fn
add_text_to_slide = server.add_text_to_slide.fn
search_presentations = server.search_presentations.fn
delete_slide = server.delete_slide.fn
export_presentation = server.export_presentation.fn


class TestCreatePresentation:
    """Test suite for create_presentation function."""

    def test_create_presentation_success(self, mock_slides_service):
        """Test successful presentation creation."""
        service, mock_build = mock_slides_service

        # Mock the API response using return_value chaining
        mock_pres = {'presentationId': 'test-pres-123'}
        service.presentations.return_value.create.return_value.execute.return_value = mock_pres

        result = create_presentation(title="Test Presentation")

        # Verify the build call
        mock_build.assert_called_once_with('slides', 'v1', credentials=mock_build.call_args[1]['credentials'])

        # Verify the API call
        service.presentations.return_value.create.assert_called_once_with(body={'title': 'Test Presentation'})
        service.presentations.return_value.create.return_value.execute.assert_called_once()

        # Verify the result
        assert "Presentation created" in result
        assert "https://docs.google.com/presentation/d/test-pres-123/edit" in result

    def test_create_presentation_api_error(self, mock_slides_service):
        """Test presentation creation with API error."""
        service, mock_build = mock_slides_service

        # Mock API error
        service.presentations.return_value.create.return_value.execute.side_effect = Exception("API Error")

        result = create_presentation(title="Test Presentation")

        # Verify error is returned as string
        assert "API Error" in result

    def test_create_presentation_with_empty_title(self, mock_slides_service):
        """Test presentation creation with empty title."""
        service, mock_build = mock_slides_service

        mock_pres = {'presentationId': 'test-pres-456'}
        service.presentations.return_value.create.return_value.execute.return_value = mock_pres

        result = create_presentation(title="")

        # Verify the API call with empty title
        service.presentations.return_value.create.assert_called_once_with(body={'title': ''})
        assert "Presentation created" in result


class TestGetPresentation:
    """Test suite for get_presentation function."""

    def test_get_presentation_success(self, mock_slides_service):
        """Test successful retrieval of presentation metadata."""
        service, mock_build = mock_slides_service

        # Mock presentation with slides containing text
        mock_pres = {
            'title': 'My Presentation',
            'slides': [
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {
                            'shape': {
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Title Slide\n'}},
                                        {'textRun': {'content': 'Subtitle'}}
                                    ]
                                }
                            }
                        }
                    ]
                },
                {
                    'objectId': 'slide2',
                    'pageElements': [
                        {
                            'shape': {
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Content Slide'}}
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-123")

        # Verify the API call
        mock_build.assert_called_once_with('slides', 'v1', credentials=mock_build.call_args[1]['credentials'])
        service.presentations.return_value.get.assert_called_once_with(presentationId='test-pres-123')
        service.presentations.return_value.get.return_value.execute.assert_called_once()

        # Verify the result
        assert "Title: My Presentation" in result
        assert "Slides: 2" in result
        assert "Slide 1: Title Slide | Subtitle" in result
        assert "Slide 2: Content Slide" in result

    def test_get_presentation_empty_slides(self, mock_slides_service):
        """Test retrieval of presentation with empty slides."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'title': 'Empty Presentation',
            'slides': [
                {
                    'objectId': 'slide1',
                    'pageElements': []
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-456")

        assert "Title: Empty Presentation" in result
        assert "Slides: 1" in result
        assert "Slide 1: (empty)" in result

    def test_get_presentation_nested_text_extraction(self, mock_slides_service):
        """Test text extraction from nested structures."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'title': 'Complex Presentation',
            'slides': [
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {
                            'shape': {
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Text 1  '}},
                                        {'textRun': {'content': '  Text 2'}}
                                    ]
                                }
                            }
                        },
                        {
                            'shape': {
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Text 3'}}
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-789")

        assert "Slide 1: Text 1 | Text 2 | Text 3" in result

    def test_get_presentation_no_text_elements(self, mock_slides_service):
        """Test presentation with shapes but no text."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'title': 'Image Presentation',
            'slides': [
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {
                            'image': {
                                'imageProperties': {}
                            }
                        },
                        {
                            'shape': {}  # Shape without text
                        }
                    ]
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-img")

        assert "Slide 1: (empty)" in result

    def test_get_presentation_api_error(self, mock_slides_service):
        """Test get_presentation with API error."""
        service, mock_build = mock_slides_service

        service.presentations.return_value.get.return_value.execute.side_effect = Exception("Presentation not found")

        result = get_presentation(presentation_id="invalid-id")

        assert "Presentation not found" in result


class TestAddSlide:
    """Test suite for add_slide function."""

    def test_add_slide_blank_layout(self, mock_slides_service):
        """Test adding a slide with BLANK layout."""
        service, mock_build = mock_slides_service

        # Mock presentation with layouts
        mock_pres = {
            'presentationId': 'test-pres-123',
            'layouts': [
                {
                    'objectId': 'layout-blank',
                    'layoutProperties': {'name': 'BLANK', 'displayName': 'Blank'}
                },
                {
                    'objectId': 'layout-title',
                    'layoutProperties': {'name': 'TITLE', 'displayName': 'Title'}
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        # Mock batchUpdate response
        mock_batch_response = {
            'replies': [
                {'createSlide': {'objectId': 'new-slide-123'}}
            ]
        }
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = mock_batch_response

        result = add_slide(presentation_id="test-pres-123", layout="BLANK")

        # Verify API calls
        service.presentations.return_value.get.assert_called_once_with(presentationId='test-pres-123')

        # Verify batchUpdate was called with correct layout
        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        assert batch_call_args[1]['presentationId'] == 'test-pres-123'
        requests = batch_call_args[1]['body']['requests']
        assert len(requests) == 1
        assert 'createSlide' in requests[0]
        assert requests[0]['createSlide']['slideLayoutReference']['layoutId'] == 'layout-blank'

        assert "Slide added" in result
        assert "new-slide-123" in result

    def test_add_slide_title_layout(self, mock_slides_service):
        """Test adding a slide with TITLE layout."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'presentationId': 'test-pres-123',
            'layouts': [
                {
                    'objectId': 'layout-title',
                    'layoutProperties': {'name': 'TITLE', 'displayName': 'Title'}
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        mock_batch_response = {
            'replies': [
                {'createSlide': {'objectId': 'new-slide-title'}}
            ]
        }
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = mock_batch_response

        result = add_slide(presentation_id="test-pres-123", layout="TITLE")

        # Verify layout matching
        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        requests = batch_call_args[1]['body']['requests']
        assert requests[0]['createSlide']['slideLayoutReference']['layoutId'] == 'layout-title'

    def test_add_slide_layout_case_insensitive(self, mock_slides_service):
        """Test layout matching is case-insensitive."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'presentationId': 'test-pres-123',
            'layouts': [
                {
                    'objectId': 'layout-title',
                    'layoutProperties': {'name': 'TITLE', 'displayName': 'Title Slide'}
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        mock_batch_response = {
            'replies': [
                {'createSlide': {'objectId': 'new-slide-123'}}
            ]
        }
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = mock_batch_response

        result = add_slide(presentation_id="test-pres-123", layout="title")

        assert "Slide added" in result

    def test_add_slide_layout_not_found(self, mock_slides_service):
        """Test adding slide when layout is not found."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'presentationId': 'test-pres-123',
            'layouts': [
                {
                    'objectId': 'layout-blank',
                    'layoutProperties': {'name': 'BLANK'}
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        mock_batch_response = {
            'replies': [
                {'createSlide': {'objectId': 'new-slide-default'}}
            ]
        }
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = mock_batch_response

        # Request non-existent layout
        result = add_slide(presentation_id="test-pres-123", layout="CUSTOM_LAYOUT")

        # Should still create slide without specific layout
        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        requests = batch_call_args[1]['body']['requests']
        assert 'slideLayoutReference' not in requests[0]['createSlide']
        assert "Slide added" in result

    def test_add_slide_api_error(self, mock_slides_service):
        """Test add_slide with API error."""
        service, mock_build = mock_slides_service

        service.presentations.return_value.get.return_value.execute.side_effect = Exception("Failed to get presentation")

        result = add_slide(presentation_id="invalid-id")

        assert "Failed to get presentation" in result


class TestAddTextToSlide:
    """Test suite for add_text_to_slide function."""

    def test_add_text_to_slide_success(self, mock_slides_service):
        """Test successfully adding text to a slide."""
        service, mock_build = mock_slides_service

        # Mock presentation with slides
        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text="Hello World",
            x=100,
            y=100,
            width=400,
            height=200
        )

        # Verify batchUpdate was called
        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        assert batch_call_args[1]['presentationId'] == 'test-pres-123'

        requests = batch_call_args[1]['body']['requests']
        assert len(requests) == 2

        # Verify createShape request
        create_shape = requests[0]['createShape']
        assert create_shape['shapeType'] == 'TEXT_BOX'
        assert create_shape['elementProperties']['pageObjectId'] == 'slide-1'
        assert create_shape['elementProperties']['size']['width']['magnitude'] == 400
        assert create_shape['elementProperties']['size']['height']['magnitude'] == 200
        assert create_shape['elementProperties']['transform']['translateX'] == 100
        assert create_shape['elementProperties']['transform']['translateY'] == 100

        # Verify insertText request
        insert_text = requests[1]['insertText']
        assert insert_text['text'] == 'Hello World'
        assert 'objectId' in insert_text

        assert "Text box added to slide 1" in result

    def test_add_text_to_slide_custom_coordinates(self, mock_slides_service):
        """Test adding text with custom coordinates."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [{'objectId': 'slide-1'}]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text="Custom Position",
            x=50,
            y=75,
            width=300,
            height=150
        )

        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        create_shape = batch_call_args[1]['body']['requests'][0]['createShape']

        assert create_shape['elementProperties']['transform']['translateX'] == 50
        assert create_shape['elementProperties']['transform']['translateY'] == 75
        assert create_shape['elementProperties']['size']['width']['magnitude'] == 300
        assert create_shape['elementProperties']['size']['height']['magnitude'] == 150

    def test_add_text_to_slide_index_out_of_range(self, mock_slides_service):
        """Test adding text to slide with invalid index."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        # Try to add text to slide index 2 (only 0 and 1 exist)
        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=2,
            text="Should fail"
        )

        # Should return error without calling batchUpdate
        assert "Slide index 2 out of range" in result
        assert "total: 2" in result
        service.presentations.return_value.batchUpdate.assert_not_called()

    def test_add_text_to_slide_empty_presentation(self, mock_slides_service):
        """Test adding text to empty presentation."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': []
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text="No slides"
        )

        assert "Slide index 0 out of range" in result
        assert "total: 0" in result

    def test_add_text_to_slide_api_error(self, mock_slides_service):
        """Test add_text_to_slide with API error."""
        service, mock_build = mock_slides_service

        service.presentations.return_value.get.return_value.execute.side_effect = Exception("Network error")

        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text="Test"
        )

        assert "Network error" in result


class TestSearchPresentations:
    """Test suite for search_presentations function."""

    def test_search_presentations_with_query(self, mock_drive_service):
        """Test searching presentations with a query."""
        service, mock_build = mock_drive_service

        mock_files = {
            'files': [
                {
                    'id': 'pres-1',
                    'name': 'Project Presentation',
                    'modifiedTime': '2024-01-15T10:00:00Z'
                },
                {
                    'id': 'pres-2',
                    'name': 'Project Update',
                    'modifiedTime': '2024-01-14T09:00:00Z'
                }
            ]
        }
        service.files.return_value.list.return_value.execute.return_value = mock_files

        result = search_presentations(query="Project", max_results=20)

        # Verify the build call for Drive API
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_build.call_args[1]['credentials'])

        # Verify the query
        list_call_args = service.files.return_value.list.call_args
        query_param = list_call_args[1]['q']
        assert "mimeType='application/vnd.google-apps.presentation'" in query_param
        assert "fullText contains 'Project'" in query_param
        assert list_call_args[1]['pageSize'] == 20
        assert list_call_args[1]['orderBy'] == 'modifiedTime desc'

        # Verify the result
        assert "Project Presentation" in result
        assert "pres-1" in result
        assert "2024-01-15T10:00:00Z" in result

    def test_search_presentations_empty_query(self, mock_drive_service):
        """Test searching presentations with empty query (list recent)."""
        service, mock_build = mock_drive_service

        mock_files = {
            'files': [
                {
                    'id': 'pres-1',
                    'name': 'Recent Presentation',
                    'modifiedTime': '2024-01-15T10:00:00Z'
                }
            ]
        }
        service.files.return_value.list.return_value.execute.return_value = mock_files

        result = search_presentations(query="", max_results=10)

        # Verify query only has mimeType filter
        list_call_args = service.files.return_value.list.call_args
        query_param = list_call_args[1]['q']
        assert query_param == "mimeType='application/vnd.google-apps.presentation'"
        assert list_call_args[1]['pageSize'] == 10

        assert "Recent Presentation" in result

    def test_search_presentations_no_results(self, mock_drive_service):
        """Test searching presentations with no results."""
        service, mock_build = mock_drive_service

        mock_files = {'files': []}
        service.files.return_value.list.return_value.execute.return_value = mock_files

        result = search_presentations(query="NonExistent")

        assert "No presentations found" in result

    def test_search_presentations_custom_max_results(self, mock_drive_service):
        """Test searching presentations with custom max_results."""
        service, mock_build = mock_drive_service

        mock_files = {'files': []}
        service.files.return_value.list.return_value.execute.return_value = mock_files

        search_presentations(query="Test", max_results=50)

        list_call_args = service.files.return_value.list.call_args
        assert list_call_args[1]['pageSize'] == 50

    def test_search_presentations_api_error(self, mock_drive_service):
        """Test search_presentations with API error."""
        service, mock_build = mock_drive_service

        service.files.return_value.list.return_value.execute.side_effect = Exception("Drive API error")

        result = search_presentations(query="Test")

        assert "Drive API error" in result


class TestDeleteSlide:
    """Test suite for delete_slide function."""

    def test_delete_slide_success(self, mock_slides_service):
        """Test successfully deleting a slide."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'},
                {'objectId': 'slide-3'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = delete_slide(presentation_id="test-pres-123", slide_index=1)

        # Verify batchUpdate was called with correct deleteObject request
        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        assert batch_call_args[1]['presentationId'] == 'test-pres-123'

        requests = batch_call_args[1]['body']['requests']
        assert len(requests) == 1
        assert 'deleteObject' in requests[0]
        assert requests[0]['deleteObject']['objectId'] == 'slide-2'

        assert "Slide 2 deleted" in result

    def test_delete_slide_first_slide(self, mock_slides_service):
        """Test deleting the first slide."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = delete_slide(presentation_id="test-pres-123", slide_index=0)

        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        requests = batch_call_args[1]['body']['requests']
        assert requests[0]['deleteObject']['objectId'] == 'slide-1'
        assert "Slide 1 deleted" in result

    def test_delete_slide_last_slide(self, mock_slides_service):
        """Test deleting the last slide."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'},
                {'objectId': 'slide-3'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = delete_slide(presentation_id="test-pres-123", slide_index=2)

        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        requests = batch_call_args[1]['body']['requests']
        assert requests[0]['deleteObject']['objectId'] == 'slide-3'

    def test_delete_slide_index_out_of_range(self, mock_slides_service):
        """Test deleting slide with invalid index."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [
                {'objectId': 'slide-1'},
                {'objectId': 'slide-2'}
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = delete_slide(presentation_id="test-pres-123", slide_index=5)

        assert "Slide index 5 out of range" in result
        assert "total: 2" in result
        service.presentations.return_value.batchUpdate.assert_not_called()

    def test_delete_slide_empty_presentation(self, mock_slides_service):
        """Test deleting slide from empty presentation."""
        service, mock_build = mock_slides_service

        mock_pres = {'slides': []}
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = delete_slide(presentation_id="test-pres-123", slide_index=0)

        assert "Slide index 0 out of range" in result
        assert "total: 0" in result

    def test_delete_slide_api_error(self, mock_slides_service):
        """Test delete_slide with API error."""
        service, mock_build = mock_slides_service

        service.presentations.return_value.get.return_value.execute.side_effect = Exception("Permission denied")

        result = delete_slide(presentation_id="test-pres-123", slide_index=0)

        assert "Permission denied" in result


class TestExportPresentation:
    """Test suite for export_presentation function."""

    def test_export_presentation_pdf(self, mock_drive_service):
        """Test exporting presentation as PDF."""
        service, mock_build = mock_drive_service

        # Mock PDF content
        pdf_content = b'%PDF-1.4 fake pdf content'
        service.files.return_value.export.return_value.execute.return_value = pdf_content

        result = export_presentation(presentation_id="test-pres-123", format="pdf")

        # Verify Drive API build
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_build.call_args[1]['credentials'])

        # Verify export call
        export_call_args = service.files.return_value.export.call_args
        assert export_call_args[1]['fileId'] == 'test-pres-123'
        assert export_call_args[1]['mimeType'] == 'application/pdf'

        # Verify result contains base64 encoded content
        assert "Exported as pdf" in result
        assert "base64" in result
        expected_encoded = base64.b64encode(pdf_content).decode('utf-8')
        assert expected_encoded[:200] in result

    def test_export_presentation_pptx(self, mock_drive_service):
        """Test exporting presentation as PPTX."""
        service, mock_build = mock_drive_service

        pptx_content = b'PK fake pptx content'
        service.files.return_value.export.return_value.execute.return_value = pptx_content

        result = export_presentation(presentation_id="test-pres-123", format="pptx")

        export_call_args = service.files.return_value.export.call_args
        assert export_call_args[1]['mimeType'] == 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

        assert "Exported as pptx" in result
        assert "base64" in result

    def test_export_presentation_txt(self, mock_drive_service):
        """Test exporting presentation as TXT."""
        service, mock_build = mock_drive_service

        txt_content = b'Slide 1: Title\nSlide 2: Content'
        service.files.return_value.export.return_value.execute.return_value = txt_content

        result = export_presentation(presentation_id="test-pres-123", format="txt")

        export_call_args = service.files.return_value.export.call_args
        assert export_call_args[1]['mimeType'] == 'text/plain'

        # TXT should be returned as decoded text, not base64
        assert result == 'Slide 1: Title\nSlide 2: Content'

    def test_export_presentation_txt_already_string(self, mock_drive_service):
        """Test exporting presentation as TXT when API returns string."""
        service, mock_build = mock_drive_service

        txt_content = 'Already a string'
        service.files.return_value.export.return_value.execute.return_value = txt_content

        result = export_presentation(presentation_id="test-pres-123", format="txt")

        assert result == 'Already a string'

    def test_export_presentation_unsupported_format(self, mock_drive_service):
        """Test exporting with unsupported format."""
        service, mock_build = mock_drive_service

        result = export_presentation(presentation_id="test-pres-123", format="docx")

        assert "Unsupported format 'docx'" in result
        assert "Use: pdf, pptx, txt" in result
        service.files.return_value.export.assert_not_called()

    def test_export_presentation_invalid_format(self, mock_drive_service):
        """Test exporting with invalid format."""
        service, mock_build = mock_drive_service

        result = export_presentation(presentation_id="test-pres-123", format="invalid")

        assert "Unsupported format 'invalid'" in result
        service.files.return_value.export.assert_not_called()

    def test_export_presentation_default_format(self, mock_drive_service):
        """Test exporting with default format (pdf)."""
        service, mock_build = mock_drive_service

        pdf_content = b'PDF content'
        service.files.return_value.export.return_value.execute.return_value = pdf_content

        result = export_presentation(presentation_id="test-pres-123")

        export_call_args = service.files.return_value.export.call_args
        assert export_call_args[1]['mimeType'] == 'application/pdf'

    def test_export_presentation_api_error(self, mock_drive_service):
        """Test export_presentation with API error."""
        service, mock_build = mock_drive_service

        service.files.return_value.export.return_value.execute.side_effect = Exception("Export failed")

        result = export_presentation(presentation_id="test-pres-123", format="pdf")

        assert "Export failed" in result


class TestEdgeCases:
    """Test suite for edge cases and integration scenarios."""

    def test_unicode_text_handling(self, mock_slides_service):
        """Test handling of unicode characters in text."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [{'objectId': 'slide-1'}]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        unicode_text = "Hello 世界 🌍 Café"
        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text=unicode_text
        )

        batch_call_args = service.presentations.return_value.batchUpdate.call_args
        insert_text = batch_call_args[1]['body']['requests'][1]['insertText']
        assert insert_text['text'] == unicode_text

    def test_large_presentation_handling(self, mock_slides_service):
        """Test handling presentation with many slides."""
        service, mock_build = mock_slides_service

        # Create 100 slides
        mock_pres = {
            'title': 'Large Presentation',
            'slides': [{'objectId': f'slide-{i}'} for i in range(100)]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-large")

        assert "Title: Large Presentation" in result
        assert "Slides: 100" in result

    def test_special_characters_in_title(self, mock_slides_service):
        """Test creating presentation with special characters in title."""
        service, mock_build = mock_slides_service

        mock_pres = {'presentationId': 'test-pres-special'}
        service.presentations.return_value.create.return_value.execute.return_value = mock_pres

        special_title = "Q&A: \"What's Next?\" <2024>"
        result = create_presentation(title=special_title)

        service.presentations.return_value.create.assert_called_once_with(body={'title': special_title})
        assert "Presentation created" in result

    def test_presentation_with_complex_nested_elements(self, mock_slides_service):
        """Test presentation with deeply nested text elements."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'title': 'Complex',
            'slides': [
                {
                    'objectId': 'slide-1',
                    'pageElements': [
                        {
                            'shape': {
                                'text': {
                                    'textElements': [
                                        {'textRun': {'content': 'Line 1\n'}},
                                        {'textRun': {'content': ''}},  # Empty run
                                        {'textRun': {'content': 'Line 2'}},
                                        {'otherElement': {}},  # Non-textRun element
                                    ]
                                }
                            }
                        },
                        {
                            'shape': {
                                # No text field
                            }
                        }
                    ]
                }
            ]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres

        result = get_presentation(presentation_id="test-pres-complex")

        assert "Slide 1: Line 1 | Line 2" in result

    def test_zero_dimensions_text_box(self, mock_slides_service):
        """Test adding text box with zero dimensions."""
        service, mock_build = mock_slides_service

        mock_pres = {
            'slides': [{'objectId': 'slide-1'}]
        }
        service.presentations.return_value.get.return_value.execute.return_value = mock_pres
        service.presentations.return_value.batchUpdate.return_value.execute.return_value = {}

        result = add_text_to_slide(
            presentation_id="test-pres-123",
            slide_index=0,
            text="Zero size",
            x=0,
            y=0,
            width=0,
            height=0
        )

        # Should still call the API (API might handle it or error)
        assert "Text box added" in result
