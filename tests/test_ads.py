"""Tests for Google Ads tools (REST API via requests)."""

import pytest
from unittest.mock import patch, MagicMock
from google_cloud_mcp import server

list_ads_accounts = server.list_ads_accounts
ads_search = server.ads_search
list_ads_campaigns = server.list_ads_campaigns
get_ads_campaign_performance = server.get_ads_campaign_performance
set_ads_campaign_status = server.set_ads_campaign_status


@pytest.fixture
def ads_http(mock_credentials):
    mock_credentials.return_value.token = 'tok'
    with patch.object(server, 'ADS_DEVELOPER_TOKEN', 'dev-token'), \
         patch.object(server, 'ADS_LOGIN_CUSTOMER_ID', '111-222-3333'), \
         patch('google_cloud_mcp.server.requests.request') as req:
        resp = MagicMock(ok=True)
        req.return_value = resp
        yield req, resp


class TestAds:
    def test_missing_developer_token(self, mock_credentials):
        with patch.object(server, 'ADS_DEVELOPER_TOKEN', None):
            assert 'GOOGLE_ADS_DEVELOPER_TOKEN' in list_ads_accounts()

    def test_list_accounts_and_headers(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {'resourceNames': ['customers/123', 'customers/456']}
        assert list_ads_accounts() == "- 123\n- 456"
        headers = req.call_args.kwargs['headers']
        assert headers['developer-token'] == 'dev-token'
        assert headers['login-customer-id'] == '1112223333'
        assert headers['Authorization'] == 'Bearer tok'

    def test_search_strips_dashes_and_sends_query(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {'results': [{'campaign': {'id': '1'}}]}
        out = ads_search('123-456-7890', 'SELECT campaign.id FROM campaign')
        assert '"id": "1"' in out
        assert 'customers/1234567890/googleAds:search' in req.call_args.args[1]
        assert req.call_args.kwargs['json'] == {'query': 'SELECT campaign.id FROM campaign'}  # no pageSize (unsupported since v23)

    def test_search_no_results(self, ads_http):
        _, resp = ads_http
        resp.json.return_value = {}
        assert ads_search('1', 'q') == "No results."

    def test_list_campaigns_formats_budget(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {'results': [{
            'campaign': {'id': '9', 'name': 'Brand', 'status': 'ENABLED', 'advertisingChannelType': 'SEARCH'},
            'campaignBudget': {'amountMicros': '5000000'}}]}
        out = list_ads_campaigns('1', status='paused')
        assert 'Brand (ID: 9, ENABLED, SEARCH, budget/day: 5)' in out
        assert "campaign.status = 'PAUSED'" in req.call_args.kwargs['json']['query']

    def test_list_campaigns_excludes_removed_by_default(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        list_ads_campaigns('1')
        assert "campaign.status != 'REMOVED'" in req.call_args.kwargs['json']['query']

    def test_performance_skips_zero_impressions(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        get_ads_campaign_performance('1', 'last_7_days')
        q = req.call_args.kwargs['json']['query']
        assert 'DURING LAST_7_DAYS' in q and 'metrics.impressions > 0' in q

    def test_performance_converts_cost(self, ads_http):
        _, resp = ads_http
        resp.json.return_value = {'results': [{
            'campaign': {'name': 'Brand'},
            'metrics': {'impressions': '100', 'clicks': '10', 'costMicros': '2500000', 'conversions': 2}}]}
        out = get_ads_campaign_performance('1')
        assert 'cost 2.50' in out and 'clicks 10' in out and 'conv 2' in out

    def test_set_status_validates(self, ads_http):
        req, _ = ads_http
        assert set_ads_campaign_status('1', '9', 'REMOVED').startswith('❌')
        req.assert_not_called()

    def test_set_status_mutates(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        assert 'PAUSED' in set_ads_campaign_status('123-4', '9', 'paused')
        body = req.call_args.kwargs['json']['operations'][0]
        assert body['update']['resourceName'] == 'customers/1234/campaigns/9'
        assert body['updateMask'] == 'status'

    def test_api_error_returned_as_string(self, ads_http):
        _, resp = ads_http
        resp.ok = False
        resp.status_code = 403
        resp.text = 'denied'
        assert 'Google Ads API error 403: denied' in ads_search('1', 'q')


class TestAdsLoginFallback:
    def test_retries_without_login_id_on_permission_denied(self, ads_http):
        req, ok = ads_http
        denied = MagicMock(ok=False, status_code=403, text='{"authorizationError":"USER_PERMISSION_DENIED"}')
        ok.json.return_value = {'results': [{'customer': {'id': '1'}}]}
        req.side_effect = [denied, ok]
        assert '"id": "1"' in ads_search('1', 'q')
        assert 'login-customer-id' in req.call_args_list[0].kwargs['headers']
        assert 'login-customer-id' not in req.call_args_list[1].kwargs['headers']

    def test_no_retry_on_other_403(self, ads_http):
        req, _ = ads_http
        req.return_value = MagicMock(ok=False, status_code=403, text='CUSTOMER_NOT_ENABLED')
        assert 'CUSTOMER_NOT_ENABLED' in ads_search('1', 'q')
        assert req.call_count == 1
