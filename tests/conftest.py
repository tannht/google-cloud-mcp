import pytest
from unittest.mock import patch, MagicMock
import json


@pytest.fixture
def mock_credentials():
    with patch('google_cloud_mcp.server.get_credentials') as mock:
        creds = MagicMock()
        creds.valid = True
        creds.expired = False
        mock.return_value = creds
        yield mock


@pytest.fixture
def mock_gmail_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build


@pytest.fixture
def mock_calendar_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build


@pytest.fixture
def mock_drive_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build


@pytest.fixture
def mock_docs_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build


@pytest.fixture
def mock_sheets_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build


@pytest.fixture
def mock_slides_service(mock_credentials):
    with patch('google_cloud_mcp.server.build') as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service, mock_build
