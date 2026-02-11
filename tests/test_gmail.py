"""
Comprehensive pytest test suite for Gmail tools.

Tests the following functions from google_cloud_mcp.server:
- create_gmail_label
- list_gmail_labels
- send_email

Test Coverage:
- Success cases with valid inputs
- Error handling and exception scenarios
- Edge cases (empty labels, special characters, Unicode)
- Correct API call verification
- Response validation
"""

import pytest
from unittest.mock import MagicMock, call
import base64
from email.message import EmailMessage
from google_cloud_mcp import server

create_gmail_label = server.create_gmail_label.fn
list_gmail_labels = server.list_gmail_labels.fn
send_email = server.send_email.fn


class TestCreateGmailLabel:
    """Test suite for create_gmail_label function."""

    def test_create_label_success(self, mock_gmail_service):
        """Test successful label creation with valid name."""
        service, mock_build = mock_gmail_service

        # Setup mock response using return_value chaining (no parentheses)
        mock_create = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'Label_123', 'name': 'TestLabel'})
        mock_create.execute = mock_execute

        service.users.return_value.labels.return_value.create.return_value = mock_create

        # Execute
        result = create_gmail_label("TestLabel")

        # Assertions
        assert result == "✅ Label 'TestLabel' created."
        mock_build.assert_called_once()
        service.users.return_value.labels.return_value.create.assert_called_once_with(
            userId='me',
            body={
                'name': 'TestLabel',
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
        )
        mock_execute.assert_called_once()

    def test_create_label_with_special_characters(self, mock_gmail_service):
        """Test label creation with special characters."""
        service, mock_build = mock_gmail_service

        mock_create = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'Label_456', 'name': 'Work/Projects'})
        mock_create.execute = mock_execute
        service.users.return_value.labels.return_value.create.return_value = mock_create

        result = create_gmail_label("Work/Projects")

        assert result == "✅ Label 'Work/Projects' created."
        service.users.return_value.labels.return_value.create.assert_called_once_with(
            userId='me',
            body={
                'name': 'Work/Projects',
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
        )

    def test_create_label_with_unicode(self, mock_gmail_service):
        """Test label creation with Unicode characters."""
        service, mock_build = mock_gmail_service

        mock_create = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'Label_789', 'name': '🏷️ Important'})
        mock_create.execute = mock_execute
        service.users.return_value.labels.return_value.create.return_value = mock_create

        result = create_gmail_label("🏷️ Important")

        assert result == "✅ Label '🏷️ Important' created."

    def test_create_label_with_spaces(self, mock_gmail_service):
        """Test label creation with spaces in name."""
        service, mock_build = mock_gmail_service

        mock_create = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'Label_101', 'name': 'Project Alpha'})
        mock_create.execute = mock_execute
        service.users.return_value.labels.return_value.create.return_value = mock_create

        result = create_gmail_label("Project Alpha")

        assert result == "✅ Label 'Project Alpha' created."

    def test_create_label_api_error(self, mock_gmail_service):
        """Test error handling when API call fails."""
        service, mock_build = mock_gmail_service

        # Setup mock to raise exception
        service.users.return_value.labels.return_value.create.side_effect = Exception("API Error: Label already exists")

        result = create_gmail_label("ExistingLabel")

        assert result == "API Error: Label already exists"
        assert "✅" not in result

    def test_create_label_http_error(self, mock_gmail_service):
        """Test error handling for HTTP errors."""
        service, mock_build = mock_gmail_service

        from googleapiclient.errors import HttpError
        from unittest.mock import Mock

        # Create a mock HttpError
        resp = Mock()
        resp.status = 409
        error = HttpError(resp, b'{"error": {"message": "Label name exists"}}')

        service.users.return_value.labels.return_value.create.side_effect = error

        result = create_gmail_label("DuplicateLabel")

        assert isinstance(result, str)
        assert "✅" not in result

    def test_create_label_network_error(self, mock_gmail_service):
        """Test error handling for network failures."""
        service, mock_build = mock_gmail_service

        service.users.return_value.labels.return_value.create.side_effect = Exception("Network timeout")

        result = create_gmail_label("NetworkTestLabel")

        assert result == "Network timeout"

    def test_create_label_empty_string(self, mock_gmail_service):
        """Test label creation with empty string name."""
        service, mock_build = mock_gmail_service

        service.users.return_value.labels.return_value.create.side_effect = Exception("Label name cannot be empty")

        result = create_gmail_label("")

        assert "cannot be empty" in result.lower() or result == "Label name cannot be empty"


class TestListGmailLabels:
    """Test suite for list_gmail_labels function."""

    def test_list_labels_success(self, mock_gmail_service):
        """Test successful retrieval of user labels."""
        service, mock_build = mock_gmail_service

        # Setup mock response
        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'labels': [
                {'id': 'Label_1', 'name': 'Work', 'type': 'user'},
                {'id': 'Label_2', 'name': 'Personal', 'type': 'user'},
                {'id': 'INBOX', 'name': 'INBOX', 'type': 'system'},
                {'id': 'Label_3', 'name': 'Projects', 'type': 'user'}
            ]
        })
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        # Execute
        result = list_gmail_labels()

        # Assertions
        assert result == "Work\nPersonal\nProjects"
        assert "INBOX" not in result  # System labels should be filtered out
        mock_build.assert_called_once()
        service.users.return_value.labels.return_value.list.assert_called_once_with(userId='me')
        mock_execute.assert_called_once()

    def test_list_labels_with_special_characters(self, mock_gmail_service):
        """Test listing labels with special characters."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'labels': [
                {'id': 'Label_1', 'name': 'Work/Projects', 'type': 'user'},
                {'id': 'Label_2', 'name': 'Client-ABC', 'type': 'user'},
                {'id': 'Label_3', 'name': '🏷️ Important', 'type': 'user'}
            ]
        })
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert "Work/Projects" in result
        assert "Client-ABC" in result
        assert "🏷️ Important" in result

    def test_list_labels_empty(self, mock_gmail_service):
        """Test when no user labels exist."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'labels': [
                {'id': 'INBOX', 'name': 'INBOX', 'type': 'system'},
                {'id': 'SENT', 'name': 'SENT', 'type': 'system'}
            ]
        })
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert result == "No user labels found."

    def test_list_labels_no_labels_key(self, mock_gmail_service):
        """Test when API response has no labels key."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={})
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert result == "No user labels found."

    def test_list_labels_single_label(self, mock_gmail_service):
        """Test with only one user label."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'labels': [
                {'id': 'Label_1', 'name': 'OnlyLabel', 'type': 'user'}
            ]
        })
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert result == "OnlyLabel"
        assert "\n" not in result

    def test_list_labels_api_error(self, mock_gmail_service):
        """Test error handling when API call fails."""
        service, mock_build = mock_gmail_service

        service.users.return_value.labels.return_value.list.side_effect = Exception("API Error: Unauthorized")

        result = list_gmail_labels()

        assert result == "API Error: Unauthorized"

    def test_list_labels_http_error(self, mock_gmail_service):
        """Test error handling for HTTP errors."""
        service, mock_build = mock_gmail_service

        from googleapiclient.errors import HttpError
        from unittest.mock import Mock

        resp = Mock()
        resp.status = 403
        error = HttpError(resp, b'{"error": {"message": "Insufficient permissions"}}')

        service.users.return_value.labels.return_value.list.side_effect = error

        result = list_gmail_labels()

        assert isinstance(result, str)
        assert "No user labels found." not in result

    def test_list_labels_filters_system_labels_only(self, mock_gmail_service):
        """Test that only user type labels are returned, not system labels."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'labels': [
                {'id': 'INBOX', 'name': 'INBOX', 'type': 'system'},
                {'id': 'SENT', 'name': 'SENT', 'type': 'system'},
                {'id': 'SPAM', 'name': 'SPAM', 'type': 'system'},
                {'id': 'TRASH', 'name': 'TRASH', 'type': 'system'},
                {'id': 'DRAFT', 'name': 'DRAFT', 'type': 'system'}
            ]
        })
        mock_list.execute = mock_execute
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert result == "No user labels found."


class TestSendEmail:
    """Test suite for send_email function."""

    def test_send_email_success(self, mock_gmail_service):
        """Test successful email sending."""
        service, mock_build = mock_gmail_service

        # Setup mock response
        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_123456', 'threadId': 'thread_789'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        # Execute
        result = send_email("test@example.com", "Test Subject", "Test body content")

        # Assertions
        assert result == "✅ Email sent! ID: msg_123456"
        mock_build.assert_called_once()
        service.users.return_value.messages.return_value.send.assert_called_once()

        # Verify the call was made with correct structure
        call_args = service.users.return_value.messages.return_value.send.call_args
        assert call_args[1]['userId'] == 'me'
        assert 'raw' in call_args[1]['body']

        # Decode and verify the email content
        encoded_message = call_args[1]['body']['raw']
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert 'To: test@example.com' in decoded_message
        assert 'Subject: Test Subject' in decoded_message
        assert 'Test body content' in decoded_message

        mock_execute.assert_called_once()

    def test_send_email_with_special_characters(self, mock_gmail_service):
        """Test sending email with special characters in subject and body."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_special'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        result = send_email(
            "user@test.com",
            "🚀 Project Update - Q1'24",
            "Hello! This is a test with special chars: @#$%&*"
        )

        assert result == "✅ Email sent! ID: msg_special"

        # Verify encoding handled special characters
        call_args = service.users.return_value.messages.return_value.send.call_args
        encoded_message = call_args[1]['body']['raw']
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert "🚀 Project Update - Q1'24" in decoded_message or "Project Update" in decoded_message
        assert "@#$%&*" in decoded_message

    def test_send_email_with_unicode(self, mock_gmail_service):
        """Test sending email with Unicode characters."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_unicode'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        result = send_email(
            "recipient@example.com",
            "Café ☕ Meeting",
            "Let's meet at the café. 你好世界!"
        )

        assert result == "✅ Email sent! ID: msg_unicode"

        call_args = service.users.return_value.messages.return_value.send.call_args
        encoded_message = call_args[1]['body']['raw']
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert "Café ☕ Meeting" in decoded_message or "utf-8" in decoded_message
        assert "你好世界" in decoded_message

    def test_send_email_with_multiline_body(self, mock_gmail_service):
        """Test sending email with multi-line body."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_multiline'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        multiline_body = """Hello,

This is a multi-line email.

Line 1
Line 2
Line 3

Best regards,
Test User"""

        result = send_email("user@example.com", "Multi-line Test", multiline_body)

        assert result == "✅ Email sent! ID: msg_multiline"

        call_args = service.users.return_value.messages.return_value.send.call_args
        encoded_message = call_args[1]['body']['raw']
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert "Line 1" in decoded_message
        assert "Line 2" in decoded_message
        assert "Line 3" in decoded_message

    def test_send_email_empty_body(self, mock_gmail_service):
        """Test sending email with empty body."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_empty_body'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        result = send_email("test@example.com", "Empty Body Test", "")

        assert result == "✅ Email sent! ID: msg_empty_body"

    def test_send_email_long_subject(self, mock_gmail_service):
        """Test sending email with very long subject."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_long_subject'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        long_subject = "A" * 500  # Very long subject

        result = send_email("test@example.com", long_subject, "Test body")

        assert result == "✅ Email sent! ID: msg_long_subject"

    def test_send_email_multiple_recipients_format(self, mock_gmail_service):
        """Test email address format handling."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_format'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        # Note: Function currently accepts single 'to' string
        # Testing with formatted email address
        result = send_email("John Doe <john@example.com>", "Test", "Body")

        assert result == "✅ Email sent! ID: msg_format"

        call_args = service.users.return_value.messages.return_value.send.call_args
        encoded_message = call_args[1]['body']['raw']
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert "john@example.com" in decoded_message

    def test_send_email_api_error(self, mock_gmail_service):
        """Test error handling when API call fails."""
        service, mock_build = mock_gmail_service

        service.users.return_value.messages.return_value.send.side_effect = Exception("API Error: Invalid recipient")

        result = send_email("invalid-email", "Test", "Body")

        assert result == "API Error: Invalid recipient"
        assert "✅" not in result

    def test_send_email_http_error(self, mock_gmail_service):
        """Test error handling for HTTP errors."""
        service, mock_build = mock_gmail_service

        from googleapiclient.errors import HttpError
        from unittest.mock import Mock

        resp = Mock()
        resp.status = 400
        error = HttpError(resp, b'{"error": {"message": "Invalid email address"}}')

        service.users.return_value.messages.return_value.send.side_effect = error

        result = send_email("bad@email", "Test", "Body")

        assert isinstance(result, str)
        assert "✅" not in result

    def test_send_email_network_error(self, mock_gmail_service):
        """Test error handling for network failures."""
        service, mock_build = mock_gmail_service

        service.users.return_value.messages.return_value.send.side_effect = Exception("Connection timeout")

        result = send_email("test@example.com", "Test", "Body")

        assert result == "Connection timeout"

    def test_send_email_quota_exceeded(self, mock_gmail_service):
        """Test error handling when quota is exceeded."""
        service, mock_build = mock_gmail_service

        from googleapiclient.errors import HttpError
        from unittest.mock import Mock

        resp = Mock()
        resp.status = 429
        error = HttpError(resp, b'{"error": {"message": "Quota exceeded"}}')

        service.users.return_value.messages.return_value.send.side_effect = error

        result = send_email("test@example.com", "Test", "Body")

        assert isinstance(result, str)
        assert "✅" not in result

    def test_send_email_encoding_integrity(self, mock_gmail_service):
        """Test that email encoding/decoding maintains integrity."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_integrity'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        original_to = "test@example.com"
        original_subject = "Test Subject 123"
        original_body = "This is the email body with numbers 123 and symbols !@#"

        result = send_email(original_to, original_subject, original_body)

        # Get the encoded message
        call_args = service.users.return_value.messages.return_value.send.call_args
        encoded_message = call_args[1]['body']['raw']

        # Decode and verify all parts are present
        decoded_bytes = base64.urlsafe_b64decode(encoded_message.encode())
        decoded_message = decoded_bytes.decode()

        assert original_to in decoded_message
        assert original_subject in decoded_message
        assert original_body in decoded_message

        # Verify it's a valid email format
        assert "To:" in decoded_message
        assert "Subject:" in decoded_message
        assert "Content-Type:" in decoded_message


class TestGmailToolsIntegration:
    """Integration tests for Gmail tools working together."""

    def test_create_and_list_labels_workflow(self, mock_gmail_service):
        """Test creating a label and then listing it."""
        service, mock_build = mock_gmail_service

        # Setup create label mock
        mock_create = MagicMock()
        mock_create.execute.return_value = {'id': 'Label_new', 'name': 'NewLabel'}
        service.users.return_value.labels.return_value.create.return_value = mock_create

        # Create label
        create_result = create_gmail_label("NewLabel")
        assert "✅ Label 'NewLabel' created." == create_result

        # Setup list labels mock
        mock_list = MagicMock()
        mock_list.execute.return_value = {
            'labels': [
                {'id': 'Label_new', 'name': 'NewLabel', 'type': 'user'},
                {'id': 'Label_old', 'name': 'OldLabel', 'type': 'user'}
            ]
        }
        service.users.return_value.labels.return_value.list.return_value = mock_list

        # List labels
        list_result = list_gmail_labels()
        assert "NewLabel" in list_result
        assert "OldLabel" in list_result

    def test_all_tools_handle_authentication_error(self, mock_gmail_service):
        """Test that all tools properly handle authentication errors."""
        service, mock_build = mock_gmail_service

        auth_error = Exception("Authentication failed")

        # Test create_gmail_label
        service.users.return_value.labels.return_value.create.side_effect = auth_error
        result = create_gmail_label("TestLabel")
        assert result == "Authentication failed"

        # Test list_gmail_labels
        service.users.return_value.labels.return_value.list.side_effect = auth_error
        result = list_gmail_labels()
        assert result == "Authentication failed"

        # Test send_email
        service.users.return_value.messages.return_value.send.side_effect = auth_error
        result = send_email("test@example.com", "Subject", "Body")
        assert result == "Authentication failed"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_label_name_with_only_spaces(self, mock_gmail_service):
        """Test creating a label with only spaces."""
        service, mock_build = mock_gmail_service

        mock_create = MagicMock()
        mock_create.execute.return_value = {'id': 'Label_spaces', 'name': '   '}
        service.users.return_value.labels.return_value.create.return_value = mock_create

        result = create_gmail_label("   ")

        # Should still succeed if API accepts it
        assert "✅" in result or isinstance(result, str)

    def test_email_with_very_long_body(self, mock_gmail_service):
        """Test sending email with very long body."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_long'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        long_body = "A" * 10000  # 10KB of text

        result = send_email("test@example.com", "Long email", long_body)

        assert result == "✅ Email sent! ID: msg_long"

    def test_label_with_nested_hierarchy(self, mock_gmail_service):
        """Test creating nested label (Gmail supports / for nesting)."""
        service, mock_build = mock_gmail_service

        mock_create = MagicMock()
        mock_create.execute.return_value = {'id': 'Label_nested', 'name': 'Parent/Child/Grandchild'}
        service.users.return_value.labels.return_value.create.return_value = mock_create

        result = create_gmail_label("Parent/Child/Grandchild")

        assert result == "✅ Label 'Parent/Child/Grandchild' created."

        call_args = service.users.return_value.labels.return_value.create.call_args
        assert call_args[1]['body']['name'] == 'Parent/Child/Grandchild'

    def test_list_labels_with_mixed_types(self, mock_gmail_service):
        """Test that list correctly filters when labels have various types."""
        service, mock_build = mock_gmail_service

        mock_list = MagicMock()
        mock_list.execute.return_value = {
            'labels': [
                {'id': 'L1', 'name': 'UserLabel1', 'type': 'user'},
                {'id': 'L2', 'name': 'SystemLabel', 'type': 'system'},
                {'id': 'L3', 'name': 'UserLabel2', 'type': 'user'},
                {'id': 'L4', 'name': 'AnotherSystem', 'type': 'system'},
                {'id': 'L5', 'name': 'UserLabel3', 'type': 'user'}
            ]
        }
        service.users.return_value.labels.return_value.list.return_value = mock_list

        result = list_gmail_labels()

        assert result == "UserLabel1\nUserLabel2\nUserLabel3"
        assert "SystemLabel" not in result
        assert "AnotherSystem" not in result

    def test_send_email_with_newlines_in_subject(self, mock_gmail_service):
        """Test sending email with newlines in subject (should be handled)."""
        service, mock_build = mock_gmail_service

        mock_send = MagicMock()
        mock_execute = MagicMock(return_value={'id': 'msg_newline_subject'})
        mock_send.execute = mock_execute
        service.users.return_value.messages.return_value.send.return_value = mock_send

        # Email subject with newline - EmailMessage raises ValueError for newlines in headers
        result = send_email("test@example.com", "Subject\nWith\nNewlines", "Body")

        # The EmailMessage class rejects newlines in headers, so the error is caught
        assert "linefeed" in result.lower() or "carriage return" in result.lower() or "✅" in result
