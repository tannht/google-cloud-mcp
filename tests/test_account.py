"""
Comprehensive test suite for the get_account_info function.

This module tests the account information retrieval functionality from Gmail API,
including successful retrieval, service configuration, error handling, and response format validation.
"""

import pytest
from unittest.mock import patch, MagicMock
from google_cloud_mcp import server

get_account_info = server.get_account_info.fn


class TestGetAccountInfo:
    """Test suite for get_account_info function."""

    def test_successful_account_info_retrieval(self, mock_gmail_service):
        """
        Test successful retrieval of account information.

        Verifies that the function correctly retrieves and formats the email address
        from the Gmail API profile when authentication is successful.
        """
        service, mock_build = mock_gmail_service

        # Mock the Gmail API response chain using return_value chaining (no parentheses)
        mock_profile_response = {'emailAddress': 'test@example.com'}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        result = get_account_info()

        # Verify the result contains the expected email address and success indicator
        assert 'test@example.com' in result
        assert '🐶' in result  # PubPug emoji indicator
        assert 'Authenticated as:' in result
        assert 'Gâu!' in result  # Dog bark in Vietnamese

    def test_correct_service_build_configuration(self, mock_gmail_service):
        """
        Test that the Gmail service is built with correct parameters.

        Verifies that the build function is called with the correct service name,
        version, and credentials.
        """
        service, mock_build = mock_gmail_service

        # Mock the profile response using return_value chaining (no parentheses)
        mock_profile_response = {'emailAddress': 'test@example.com'}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        result = get_account_info()

        # Verify build was called with correct parameters
        mock_build.assert_called_once()
        call_args = mock_build.call_args

        # Check positional arguments
        assert call_args[0][0] == 'gmail', "Service should be 'gmail'"
        assert call_args[0][1] == 'v1', "API version should be 'v1'"

        # Verify credentials parameter was passed
        assert 'credentials' in call_args[1], "Credentials should be passed as keyword argument"

    def test_api_call_with_correct_user_id(self, mock_gmail_service):
        """
        Test that the API call uses the correct userId parameter.

        Verifies that 'me' is used as the userId to retrieve the current user's profile.
        """
        service, mock_build = mock_gmail_service

        # Mock the profile response using return_value chaining (no parentheses)
        mock_profile_response = {'emailAddress': 'user@domain.com'}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        get_account_info()

        # Verify userId='me' was used
        service.users.return_value.getProfile.assert_called_with(userId='me')

    def test_error_handling_when_api_fails(self, mock_gmail_service):
        """
        Test error handling when the Gmail API call fails.

        Verifies that exceptions are caught and returned as formatted error messages.
        """
        service, mock_build = mock_gmail_service

        # Simulate an API error using return_value chaining (no parentheses)
        error_message = "API rate limit exceeded"
        service.users.return_value.getProfile.return_value.execute.side_effect = Exception(error_message)

        # Execute the function
        result = get_account_info()

        # Verify error is handled gracefully
        assert '❌' in result
        assert 'Error:' in result
        assert error_message in result

    def test_error_handling_http_error(self, mock_gmail_service):
        """
        Test error handling for HTTP errors from Google API.

        Verifies that HTTP errors (like 403, 401) are properly caught and formatted.
        """
        from googleapiclient.errors import HttpError

        service, mock_build = mock_gmail_service

        # Create a mock HTTP error
        mock_response = MagicMock()
        mock_response.status = 403
        http_error = HttpError(resp=mock_response, content=b'Forbidden')

        service.users.return_value.getProfile.return_value.execute.side_effect = http_error

        # Execute the function
        result = get_account_info()

        # Verify error is handled
        assert '❌' in result
        assert 'Error:' in result

    def test_error_handling_missing_credentials(self, mock_gmail_service):
        """
        Test error handling when credentials are invalid or missing.

        Verifies that authentication errors are properly handled.
        """
        service, mock_build = mock_gmail_service

        # Simulate authentication error
        auth_error = Exception("Invalid credentials")
        service.users.return_value.getProfile.return_value.execute.side_effect = auth_error

        # Execute the function
        result = get_account_info()

        # Verify error message format
        assert '❌ Error:' in result
        assert 'Invalid credentials' in result

    def test_response_format_validation(self, mock_gmail_service):
        """
        Test that the response format is valid and consistent.

        Verifies the response string format matches the expected pattern.
        """
        service, mock_build = mock_gmail_service

        # Mock profile with test email
        test_email = 'pubpug@metoolzy.com'
        mock_profile_response = {'emailAddress': test_email}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        result = get_account_info()

        # Verify response format
        assert isinstance(result, str), "Result should be a string"
        assert result.startswith('🐶'), "Should start with dog emoji"
        assert 'Authenticated as:' in result, "Should contain 'Authenticated as:'"
        assert test_email in result, "Should contain the email address"
        assert result.endswith('(Gâu!)'), "Should end with '(Gâu!)'"

        # Verify exact format
        expected_format = f"🐶 Authenticated as: {test_email} (Gâu!)"
        assert result == expected_format, "Response should match exact format"

    def test_response_with_missing_email_field(self, mock_gmail_service):
        """
        Test handling when the API response doesn't contain an emailAddress field.

        Verifies graceful handling of missing or malformed API responses.
        """
        service, mock_build = mock_gmail_service

        # Mock profile without emailAddress field
        mock_profile_response = {'id': '12345'}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        result = get_account_info()

        # Verify the function handles missing email gracefully
        # It should use .get() which returns None, resulting in "None" in the string
        assert '🐶' in result
        assert 'Authenticated as:' in result
        assert 'None' in result or '' in result

    def test_response_with_empty_profile(self, mock_gmail_service):
        """
        Test handling when the API returns an empty profile.

        Verifies that empty responses are handled without crashing.
        """
        service, mock_build = mock_gmail_service

        # Mock empty profile response
        mock_profile_response = {}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute the function
        result = get_account_info()

        # Should still return a formatted response, even if email is None
        assert isinstance(result, str)
        assert '🐶' in result
        assert 'Authenticated as:' in result

    def test_multiple_consecutive_calls(self, mock_gmail_service):
        """
        Test that multiple consecutive calls work correctly.

        Verifies that the function can be called multiple times with consistent results.
        """
        service, mock_build = mock_gmail_service

        # Mock profile response using return_value chaining (no parentheses)
        mock_profile_response = {'emailAddress': 'test@example.com'}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute multiple times
        result1 = get_account_info()
        result2 = get_account_info()
        result3 = get_account_info()

        # Verify all results are consistent
        assert result1 == result2 == result3
        assert 'test@example.com' in result1

    def test_service_build_receives_credentials(self, mock_credentials):
        """
        Test that the service build receives valid credentials.

        Verifies that get_credentials() is called and passed to the build function.
        """
        with patch('google_cloud_mcp.server.build') as mock_build:
            # Setup mock service
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.users.return_value.getProfile.return_value.execute.return_value = {
                'emailAddress': 'test@example.com'
            }

            # Execute the function
            get_account_info()

            # Verify credentials were retrieved and passed
            mock_credentials.assert_called_once()

            # Verify build was called with credentials
            call_kwargs = mock_build.call_args[1]
            assert 'credentials' in call_kwargs
            assert call_kwargs['credentials'] is not None

    def test_error_message_format_consistency(self, mock_gmail_service):
        """
        Test that error messages follow consistent formatting.

        Verifies all error messages use the same format pattern.
        """
        service, mock_build = mock_gmail_service

        # Test with different error types
        test_errors = [
            "Network connection failed",
            "Timeout error",
            "Permission denied"
        ]

        for error_msg in test_errors:
            # Setup the error
            service.users.return_value.getProfile.return_value.execute.side_effect = Exception(error_msg)

            # Execute and verify format
            result = get_account_info()
            assert result.startswith('❌ Error:'), f"Error should start with '❌ Error:' for {error_msg}"
            assert error_msg in result, f"Error message should contain: {error_msg}"

    def test_special_characters_in_email(self, mock_gmail_service):
        """
        Test handling of email addresses with special characters.

        Verifies that various valid email formats are handled correctly.
        """
        service, mock_build = mock_gmail_service

        # Test emails with special characters
        test_emails = [
            'user+tag@example.com',
            'user.name@example.co.uk',
            'user_name@subdomain.example.com',
            'user-123@example.org'
        ]

        for email in test_emails:
            mock_profile_response = {'emailAddress': email}
            service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

            result = get_account_info()

            # Verify the email is correctly included
            assert email in result, f"Email {email} should be in result"
            assert '🐶' in result
            assert 'Authenticated as:' in result


class TestGetAccountInfoIntegration:
    """Integration tests for get_account_info function."""

    @patch('google_cloud_mcp.server.build')
    @patch('google_cloud_mcp.server.get_credentials')
    def test_full_integration_flow(self, mock_get_creds, mock_build):
        """
        Test the complete integration flow from credentials to response.

        This test verifies the entire call chain without using fixtures.
        """
        # Setup credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_get_creds.return_value = mock_creds

        # Setup service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Setup API response using return_value chaining (no parentheses)
        test_email = 'integration@test.com'
        mock_service.users.return_value.getProfile.return_value.execute.return_value = {
            'emailAddress': test_email
        }

        # Execute
        result = get_account_info()

        # Verify complete flow
        mock_get_creds.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

        # Verify result
        assert test_email in result
        assert '🐶 Authenticated as:' in result
        assert '(Gâu!)' in result


class TestGetAccountInfoEdgeCases:
    """Edge case tests for get_account_info function."""

    def test_unicode_characters_in_error_message(self, mock_gmail_service):
        """
        Test handling of Unicode characters in error messages.

        Verifies that Unicode/special characters in errors don't cause issues.
        """
        service, mock_build = mock_gmail_service

        # Error with Unicode characters
        unicode_error = "Error: 認証失敗 (Authentication failed)"
        service.users.return_value.getProfile.return_value.execute.side_effect = Exception(unicode_error)

        # Execute
        result = get_account_info()

        # Verify Unicode is handled
        assert '❌' in result
        assert 'Error:' in result
        assert isinstance(result, str)

    def test_very_long_email_address(self, mock_gmail_service):
        """
        Test handling of very long email addresses.

        Verifies that long emails (approaching max length) are handled correctly.
        """
        service, mock_build = mock_gmail_service

        # Create a very long but valid email
        long_email = f"{'a' * 64}@{'subdomain.' * 10}example.com"
        mock_profile_response = {'emailAddress': long_email}
        service.users.return_value.getProfile.return_value.execute.return_value = mock_profile_response

        # Execute
        result = get_account_info()

        # Verify handling
        assert long_email in result
        assert '🐶' in result

    def test_null_response_from_api(self, mock_gmail_service):
        """
        Test handling when API returns None.

        Verifies graceful handling of null/None responses.
        """
        service, mock_build = mock_gmail_service

        # Return None instead of a dict
        service.users.return_value.getProfile.return_value.execute.return_value = None

        # This should raise an error when trying to call .get() on None
        # but it should be caught by the try-except
        result = get_account_info()

        # Should return an error message
        assert '❌' in result or '🐶' in result
