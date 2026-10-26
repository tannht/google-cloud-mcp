"""Tests for GTM write tools, GA4 key events and Ads conversion action updates."""

import json
import pytest
from unittest.mock import patch, MagicMock
from google_cloud_mcp import server

get_gtm_resource = server.get_gtm_resource
create_gtm_resource = server.create_gtm_resource
update_gtm_resource = server.update_gtm_resource
delete_gtm_resource = server.delete_gtm_resource
get_gtm_workspace_status = server.get_gtm_workspace_status
create_ga4_key_event = server.create_ga4_key_event
update_ads_conversion_action = server.update_ads_conversion_action

WS = 'accounts/1/containers/2/workspaces/3'


def _ws(service):
    return service.accounts.return_value.containers.return_value.workspaces.return_value


class TestGTMWrites:
    def test_get_resource_returns_json(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).triggers.return_value.get.return_value.execute.return_value = {'name': 'click-call', 'triggerId': '35'}
        out = get_gtm_resource(f'{WS}/triggers/35')
        assert json.loads(out)['name'] == 'click-call'

    def test_rejects_non_resource_path(self, mock_gmail_service):
        assert 'Path must point to a tag, trigger or variable' in get_gtm_resource(f'{WS}/versions/1')

    def test_create_trigger(self, mock_gmail_service):
        service, _ = mock_gmail_service
        create = _ws(service).triggers.return_value.create
        create.return_value.execute.return_value = {'name': 'lead', 'triggerId': '50', 'path': f'{WS}/triggers/50'}
        out = create_gtm_resource(WS, 'triggers', '{"name": "lead", "type": "customEvent"}')
        assert out.startswith("✅ Created trigger 'lead' (ID: 50")
        assert create.call_args.kwargs == {'parent': WS, 'body': {'name': 'lead', 'type': 'customEvent'}}

    def test_create_rejects_unknown_resource(self, mock_gmail_service):
        service, _ = mock_gmail_service
        assert create_gtm_resource(WS, 'versions', '{}').startswith('❌')

    def test_update_merges_and_sends_fingerprint(self, mock_gmail_service):
        service, _ = mock_gmail_service
        api = _ws(service).triggers.return_value
        api.get.return_value.execute.return_value = {'name': 'old', 'type': 'customEvent', 'fingerprint': 'fp1'}
        api.update.return_value.execute.return_value = {'name': 'new'}
        assert update_gtm_resource(f'{WS}/triggers/35', '{"name": "new"}').startswith("✅ Updated 'new'")
        kw = api.update.call_args.kwargs
        assert kw['fingerprint'] == 'fp1'
        assert kw['body'] == {'name': 'new', 'type': 'customEvent', 'fingerprint': 'fp1'}

    def test_delete(self, mock_gmail_service):
        service, _ = mock_gmail_service
        assert delete_gtm_resource(f'{WS}/triggers/39').startswith('✅ Deleted')
        assert _ws(service).triggers.return_value.delete.call_args.kwargs == {'path': f'{WS}/triggers/39'}

    def test_workspace_status(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).getStatus.return_value.execute.return_value = {
            'workspaceChange': [{'changeStatus': 'added', 'tag': {'name': 'Zalo'}},
                                {'changeStatus': 'updated', 'trigger': {'name': 'click-call'}}]}
        assert get_gtm_workspace_status(WS) == "- added: Zalo\n- updated: click-call"

    def test_workspace_status_clean(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).getStatus.return_value.execute.return_value = {}
        assert get_gtm_workspace_status(WS) == "No unpublished changes."


class TestGA4KeyEvent:
    def test_create(self, mock_gmail_service):
        service, mock_build = mock_gmail_service
        create = service.properties.return_value.keyEvents.return_value.create
        create.return_value.execute.return_value = {'eventName': 'generate_lead', 'name': 'properties/1/keyEvents/9'}
        assert create_ga4_key_event('properties/1', 'generate_lead').startswith('✅ Key event created: generate_lead')
        assert create.call_args.kwargs['parent'] == 'properties/1'
        assert create.call_args.kwargs['body'] == {'eventName': 'generate_lead', 'countingMethod': 'ONCE_PER_EVENT'}
        assert mock_build.call_args.args[:2] == ('analyticsadmin', 'v1beta')

    def test_bad_counting_method(self, mock_gmail_service):
        service, _ = mock_gmail_service
        assert create_ga4_key_event('1', 'x', 'ALWAYS').startswith('❌')


@pytest.fixture
def ads_http(mock_credentials):
    mock_credentials.return_value.token = 'tok'
    with patch.object(server, 'ADS_DEVELOPER_TOKEN', 'dev-token'), \
         patch.object(server, 'ADS_LOGIN_CUSTOMER_ID', None), \
         patch('google_cloud_mcp.server.requests.request') as req:
        resp = MagicMock(ok=True)
        resp.json.return_value = {}
        req.return_value = resp
        yield req, resp


class TestAdsConversionAction:
    def test_update_counting_type(self, ads_http):
        req, _ = ads_http
        out = update_ads_conversion_action('123-4', '66', counting_type='one_per_click')
        assert out.startswith('✅ Updated conversion action 66: counting_type')
        op = req.call_args.kwargs['json']['operations'][0]
        assert op == {'update': {'resourceName': 'customers/1234/conversionActions/66', 'countingType': 'ONE_PER_CLICK'},
                      'updateMask': 'counting_type'}

    def test_multiple_fields_and_validate_only(self, ads_http):
        req, _ = ads_http
        out = update_ads_conversion_action('1', '2', status='paused', primary_for_goal='false', validate_only=True)
        assert 'Validated' in out
        body = req.call_args.kwargs['json']
        assert body['validateOnly'] is True
        assert body['operations'][0]['updateMask'] == 'status,primary_for_goal'
        assert body['operations'][0]['update']['primaryForGoal'] is False

    @pytest.mark.parametrize('kwargs', [{}, {'counting_type': 'LOTS'}, {'status': 'GONE'}, {'primary_for_goal': 'maybe'}])
    def test_validation(self, ads_http, kwargs):
        req, _ = ads_http
        assert update_ads_conversion_action('1', '2', **kwargs).startswith('❌')
        req.assert_not_called()
