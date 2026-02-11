"""
Comprehensive test suite for Google Calendar MCP tools.

Tests cover:
- list_calendar_events: success, no events, default params, custom params, error handling
- create_calendar_event: success, error handling, API call verification, time formatting
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import MagicMock, call
from datetime import datetime, timedelta
from google_cloud_mcp import server

list_calendar_events = server.list_calendar_events.fn
create_calendar_event = server.create_calendar_event.fn


class TestListCalendarEvents:
    """Test suite for list_calendar_events function."""

    def test_list_events_success_with_defaults(self, mock_calendar_service):
        """Test listing events with default parameters (10 events, 0 days back)."""
        service, mock_build = mock_calendar_service

        # Mock API response with sample events
        mock_events = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'Team Meeting',
                    'start': {'dateTime': '2026-02-11T10:00:00+07:00'}
                },
                {
                    'id': 'event2',
                    'summary': 'Code Review',
                    'start': {'dateTime': '2026-02-11T14:00:00+07:00'}
                },
                {
                    'id': 'event3',
                    'summary': 'All-day Event',
                    'start': {'date': '2026-02-12'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute
        result = list_calendar_events()

        # Verify build was called correctly
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_build.call_args[1]['credentials'])

        # Verify API call parameters
        events_list = service.events.return_value.list
        events_list.assert_called_once()
        call_kwargs = events_list.call_args[1]

        assert call_kwargs['calendarId'] == 'primary'
        assert call_kwargs['maxResults'] == 10
        assert call_kwargs['singleEvents'] is True
        assert call_kwargs['orderBy'] == 'startTime'
        assert 'timeMin' in call_kwargs
        assert call_kwargs['timeMin'].endswith('Z')

        # Verify result format
        assert 'Team Meeting' in result
        assert 'Code Review' in result
        assert 'All-day Event' in result
        assert 'event1' in result
        assert 'event2' in result
        assert 'event3' in result
        assert '2026-02-11T10:00:00+07:00' in result
        assert '2026-02-12' in result

    def test_list_events_with_custom_max_results(self, mock_calendar_service):
        """Test listing events with custom max_results parameter."""
        service, mock_build = mock_calendar_service

        mock_events = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'Event 1',
                    'start': {'dateTime': '2026-02-11T10:00:00+07:00'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute with custom max_results
        result = list_calendar_events(max_results=5)

        # Verify maxResults parameter
        call_kwargs = service.events.return_value.list.call_args[1]
        assert call_kwargs['maxResults'] == 5
        assert 'Event 1' in result

    def test_list_events_with_days_back(self, mock_calendar_service):
        """Test listing events with days_back parameter."""
        service, mock_build = mock_calendar_service

        mock_events = {
            'items': [
                {
                    'id': 'past_event',
                    'summary': 'Past Event',
                    'start': {'dateTime': '2026-02-08T10:00:00+07:00'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute with days_back
        result = list_calendar_events(days_back=7)

        # Verify timeMin is adjusted for days_back
        call_kwargs = service.events.return_value.list.call_args[1]
        time_min = call_kwargs['timeMin']

        # Parse the time_min and verify it's approximately 7 days ago
        expected_time = datetime.utcnow() - timedelta(days=7)
        actual_time = datetime.fromisoformat(time_min.rstrip('Z'))

        # Allow 1 minute tolerance for test execution time
        time_diff = abs((expected_time - actual_time).total_seconds())
        assert time_diff < 60, f"Time difference too large: {time_diff} seconds"

        assert 'Past Event' in result

    def test_list_events_with_custom_params_combined(self, mock_calendar_service):
        """Test listing events with both max_results and days_back."""
        service, mock_build = mock_calendar_service

        mock_events = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'Combined Test Event',
                    'start': {'dateTime': '2026-02-10T10:00:00+07:00'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute with both parameters
        result = list_calendar_events(max_results=20, days_back=3)

        # Verify both parameters are applied
        call_kwargs = service.events.return_value.list.call_args[1]
        assert call_kwargs['maxResults'] == 20

        # Verify timeMin for 3 days back
        time_min = call_kwargs['timeMin']
        expected_time = datetime.utcnow() - timedelta(days=3)
        actual_time = datetime.fromisoformat(time_min.rstrip('Z'))
        time_diff = abs((expected_time - actual_time).total_seconds())
        assert time_diff < 60

        assert 'Combined Test Event' in result

    def test_list_events_no_events_found(self, mock_calendar_service):
        """Test listing events when calendar is empty."""
        service, mock_build = mock_calendar_service

        # Mock empty response
        mock_events = {'items': []}
        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute
        result = list_calendar_events()

        # Verify result
        assert result == "No events found."

    def test_list_events_no_items_key(self, mock_calendar_service):
        """Test listing events when API response has no 'items' key."""
        service, mock_build = mock_calendar_service

        # Mock response without items key
        mock_events = {}
        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute
        result = list_calendar_events()

        # Verify result
        assert result == "No events found."

    def test_list_events_datetime_and_date_formats(self, mock_calendar_service):
        """Test that both dateTime and date formats are handled correctly."""
        service, mock_build = mock_calendar_service

        mock_events = {
            'items': [
                {
                    'id': 'timed_event',
                    'summary': 'Timed Event',
                    'start': {'dateTime': '2026-02-11T15:30:00+07:00'}
                },
                {
                    'id': 'all_day_event',
                    'summary': 'All Day Event',
                    'start': {'date': '2026-02-12'}
                },
                {
                    'id': 'another_timed',
                    'summary': 'Another Timed',
                    'start': {'dateTime': '2026-02-13T09:00:00+07:00'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute
        result = list_calendar_events()

        # Verify both formats are in result
        assert '2026-02-11T15:30:00+07:00' in result  # dateTime format
        assert '2026-02-12' in result  # date format
        assert '2026-02-13T09:00:00+07:00' in result

    def test_list_events_api_error(self, mock_calendar_service):
        """Test error handling when API call fails."""
        service, mock_build = mock_calendar_service

        # Mock API error
        service.events.return_value.list.return_value.execute.side_effect = Exception("API Error: Rate limit exceeded")

        # Execute
        result = list_calendar_events()

        # Verify error is returned as string
        assert "API Error: Rate limit exceeded" in result

    def test_list_events_authentication_error(self, mock_calendar_service):
        """Test error handling for authentication failures."""
        service, mock_build = mock_calendar_service

        # Mock authentication error
        service.events.return_value.list.return_value.execute.side_effect = Exception("Invalid credentials")

        # Execute
        result = list_calendar_events()

        # Verify error message
        assert "Invalid credentials" in result

    def test_list_events_timezone_info(self, mock_calendar_service):
        """Test that timezone is correctly documented as Asia/Ho_Chi_Minh."""
        service, mock_build = mock_calendar_service

        # This is a documentation test - verifying the docstring
        assert "Asia/Ho_Chi_Minh" in list_calendar_events.__doc__

    def test_list_events_ordering(self, mock_calendar_service):
        """Test that events are ordered by start time."""
        service, mock_build = mock_calendar_service

        mock_events = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'First Event',
                    'start': {'dateTime': '2026-02-11T08:00:00+07:00'}
                },
                {
                    'id': 'event2',
                    'summary': 'Second Event',
                    'start': {'dateTime': '2026-02-11T10:00:00+07:00'}
                }
            ]
        }

        service.events.return_value.list.return_value.execute.return_value = mock_events

        # Execute
        result = list_calendar_events()

        # Verify orderBy parameter
        call_kwargs = service.events.return_value.list.call_args[1]
        assert call_kwargs['orderBy'] == 'startTime'
        assert call_kwargs['singleEvents'] is True


class TestCreateCalendarEvent:
    """Test suite for create_calendar_event function."""

    def test_create_event_success(self, mock_calendar_service):
        """Test creating a calendar event successfully."""
        service, mock_build = mock_calendar_service

        # Mock successful creation response
        mock_response = {
            'id': 'created_event_123',
            'htmlLink': 'https://calendar.google.com/event?eid=abc123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute
        result = create_calendar_event(
            summary="Team Standup",
            start_time="2026-02-12T09:00",
            end_time="2026-02-12T09:30",
            description="Daily team standup meeting"
        )

        # Verify build was called correctly
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_build.call_args[1]['credentials'])

        # Verify API call
        insert_call = service.events.return_value.insert
        insert_call.assert_called_once()
        call_kwargs = insert_call.call_args[1]

        assert call_kwargs['calendarId'] == 'primary'

        # Verify event body structure
        event_body = call_kwargs['body']
        assert event_body['summary'] == "Team Standup"
        assert event_body['description'] == "Daily team standup meeting"
        assert event_body['start']['dateTime'] == "2026-02-12T09:00:00"
        assert event_body['start']['timeZone'] == "Asia/Ho_Chi_Minh"
        assert event_body['end']['dateTime'] == "2026-02-12T09:30:00"
        assert event_body['end']['timeZone'] == "Asia/Ho_Chi_Minh"

        # Verify result
        assert "Event created" in result
        assert "https://calendar.google.com/event?eid=abc123" in result

    def test_create_event_without_description(self, mock_calendar_service):
        """Test creating event with default empty description."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_456',
            'htmlLink': 'https://calendar.google.com/event?eid=def456'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute without description
        result = create_calendar_event(
            summary="Quick Meeting",
            start_time="2026-02-12T14:00",
            end_time="2026-02-12T15:00"
        )

        # Verify event body
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['summary'] == "Quick Meeting"
        assert event_body['description'] == ""

        # Verify result
        assert "Event created" in result

    def test_create_event_time_formatting(self, mock_calendar_service):
        """Test that time format is correctly appended with :00 for seconds."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_789',
            'htmlLink': 'https://calendar.google.com/event?eid=ghi789'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute
        create_calendar_event(
            summary="Format Test",
            start_time="2026-02-15T10:30",
            end_time="2026-02-15T11:45"
        )

        # Verify time formatting
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['start']['dateTime'] == "2026-02-15T10:30:00"
        assert event_body['end']['dateTime'] == "2026-02-15T11:45:00"

    def test_create_event_with_long_description(self, mock_calendar_service):
        """Test creating event with a long description."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_long',
            'htmlLink': 'https://calendar.google.com/event?eid=long123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        long_description = """
        This is a comprehensive meeting to discuss:
        1. Project milestones
        2. Team performance
        3. Budget allocation
        4. Next quarter planning

        Please prepare your reports in advance.
        """

        # Execute
        result = create_calendar_event(
            summary="Quarterly Review",
            start_time="2026-02-20T13:00",
            end_time="2026-02-20T16:00",
            description=long_description
        )

        # Verify description is preserved
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['description'] == long_description
        assert "Event created" in result

    def test_create_event_special_characters_in_summary(self, mock_calendar_service):
        """Test creating event with special characters in summary."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_special',
            'htmlLink': 'https://calendar.google.com/event?eid=special123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute with special characters
        result = create_calendar_event(
            summary="Team Meeting: Q&A Session @ Office #1",
            start_time="2026-02-12T10:00",
            end_time="2026-02-12T11:00",
            description="Discuss R&D progress & budget"
        )

        # Verify special characters are preserved
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['summary'] == "Team Meeting: Q&A Session @ Office #1"
        assert event_body['description'] == "Discuss R&D progress & budget"
        assert "Event created" in result

    def test_create_event_api_error(self, mock_calendar_service):
        """Test error handling when event creation fails."""
        service, mock_build = mock_calendar_service

        # Mock API error
        service.events.return_value.insert.return_value.execute.side_effect = Exception("API Error: Insufficient permissions")

        # Execute
        result = create_calendar_event(
            summary="Test Event",
            start_time="2026-02-12T10:00",
            end_time="2026-02-12T11:00"
        )

        # Verify error is returned as string
        assert "API Error: Insufficient permissions" in result

    def test_create_event_invalid_time_format_error(self, mock_calendar_service):
        """Test error handling for invalid time format."""
        service, mock_build = mock_calendar_service

        # Mock error for invalid time format
        service.events.return_value.insert.return_value.execute.side_effect = Exception("Invalid time format")

        # Execute with potentially problematic format
        result = create_calendar_event(
            summary="Test Event",
            start_time="invalid-time",
            end_time="also-invalid"
        )

        # Verify error is captured
        assert "Invalid time format" in result

    def test_create_event_timezone_verification(self, mock_calendar_service):
        """Test that timezone is set to Asia/Ho_Chi_Minh for both start and end."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_tz',
            'htmlLink': 'https://calendar.google.com/event?eid=tz123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute
        create_calendar_event(
            summary="Timezone Test",
            start_time="2026-02-12T16:00",
            end_time="2026-02-12T17:00"
        )

        # Verify timezone for both start and end
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['start']['timeZone'] == "Asia/Ho_Chi_Minh"
        assert event_body['end']['timeZone'] == "Asia/Ho_Chi_Minh"

    def test_create_event_cross_day(self, mock_calendar_service):
        """Test creating an event that spans across days."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_cross_day',
            'htmlLink': 'https://calendar.google.com/event?eid=cross123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute with cross-day event
        result = create_calendar_event(
            summary="Overnight Workshop",
            start_time="2026-02-12T22:00",
            end_time="2026-02-13T02:00",
            description="Late night coding session"
        )

        # Verify times are correct
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['start']['dateTime'] == "2026-02-12T22:00:00"
        assert event_body['end']['dateTime'] == "2026-02-13T02:00:00"
        assert "Event created" in result

    def test_create_event_early_morning(self, mock_calendar_service):
        """Test creating an early morning event."""
        service, mock_build = mock_calendar_service

        mock_response = {
            'id': 'event_early',
            'htmlLink': 'https://calendar.google.com/event?eid=early123'
        }
        service.events.return_value.insert.return_value.execute.return_value = mock_response

        # Execute with early morning time
        result = create_calendar_event(
            summary="Early Standup",
            start_time="2026-02-12T06:00",
            end_time="2026-02-12T06:15"
        )

        # Verify result
        assert "Event created" in result

        # Verify times
        call_kwargs = service.events.return_value.insert.call_args[1]
        event_body = call_kwargs['body']

        assert event_body['start']['dateTime'] == "2026-02-12T06:00:00"
        assert event_body['end']['dateTime'] == "2026-02-12T06:15:00"

    def test_create_event_docstring_format_info(self, mock_calendar_service):
        """Test that docstring contains format information."""
        # Verify documentation includes format
        assert "YYYY-MM-DDTHH:MM" in create_calendar_event.__doc__
        assert "VN Time" in create_calendar_event.__doc__


class TestCalendarIntegration:
    """Integration tests for calendar operations."""

    def test_create_and_list_workflow(self, mock_calendar_service):
        """Test typical workflow of creating and then listing events."""
        service, mock_build = mock_calendar_service

        # Mock create response
        create_response = {
            'id': 'new_event_123',
            'htmlLink': 'https://calendar.google.com/event?eid=new123'
        }
        service.events.return_value.insert.return_value.execute.return_value = create_response

        # Create event
        create_result = create_calendar_event(
            summary="Integration Test Event",
            start_time="2026-02-12T10:00",
            end_time="2026-02-12T11:00",
            description="Testing integration"
        )

        assert "Event created" in create_result

        # Mock list response including the created event
        list_response = {
            'items': [
                {
                    'id': 'new_event_123',
                    'summary': 'Integration Test Event',
                    'start': {'dateTime': '2026-02-12T10:00:00+07:00'}
                }
            ]
        }
        service.events.return_value.list.return_value.execute.return_value = list_response

        # List events
        list_result = list_calendar_events()

        assert 'Integration Test Event' in list_result
        assert 'new_event_123' in list_result
