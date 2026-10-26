"""Tests for Google Ads write tools: remove ad, negative keywords, RSA text update."""

import pytest
from unittest.mock import patch, MagicMock
from google_cloud_mcp import server

remove_ads_ad = server.remove_ads_ad
add_ads_negative_keywords = server.add_ads_negative_keywords
update_ads_responsive_search_ad = server.update_ads_responsive_search_ad


@pytest.fixture
def ads_http(mock_credentials):
    mock_credentials.return_value.token = 'tok'
    with patch.object(server, 'ADS_DEVELOPER_TOKEN', 'dev-token'), \
         patch.object(server, 'ADS_LOGIN_CUSTOMER_ID', None), \
         patch('google_cloud_mcp.server.requests.request') as req:
        resp = MagicMock(ok=True)
        req.return_value = resp
        yield req, resp


class TestRemoveAd:
    def test_remove(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        assert remove_ads_ad('123-4', '55', '66').startswith('✅ Removed')
        body = req.call_args.kwargs['json']
        assert body['operations'] == [{'remove': 'customers/1234/adGroupAds/55~66'}]
        assert body['validateOnly'] is False

    def test_validate_only(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        assert 'Validated' in remove_ads_ad('1', '5', '6', validate_only=True)
        assert req.call_args.kwargs['json']['validateOnly'] is True


class TestNegativeKeywords:
    def test_skips_existing_and_dedupes(self, ads_http):
        req, resp = ads_http
        resp.json.side_effect = [
            {'results': [{'campaignCriterion': {'keyword': {'text': 'Tại Nhà', 'matchType': 'PHRASE'}}}]}, {}]
        out = add_ads_negative_keywords('1', '9', 'tại nhà, thuốc\nthuốc, kem')
        assert 'Added 2' in out and 'thuốc, kem' in out and 'skipped 1' in out
        ops = req.call_args.kwargs['json']['operations']
        assert [o['create']['keyword']['text'] for o in ops] == ['thuốc', 'kem']
        assert all(o['create']['negative'] and o['create']['campaign'] == 'customers/1/campaigns/9' for o in ops)

    def test_nothing_new_makes_no_write(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {'results': [{'campaignCriterion': {'keyword': {'text': 'kem', 'matchType': 'PHRASE'}}}]}
        assert 'Nothing to add' in add_ads_negative_keywords('1', '9', 'kem')
        assert req.call_count == 1

    def test_bad_match_type(self, ads_http):
        req, _ = ads_http
        assert add_ads_negative_keywords('1', '9', 'x', 'LOOSE').startswith('❌')
        req.assert_not_called()


class TestUpdateRSA:
    def test_sends_update_mask(self, ads_http):
        req, resp = ads_http
        resp.json.return_value = {}
        out = update_ads_responsive_search_ad('1', '77', headlines='A|B|C', descriptions='d1|d2', path1='nam')
        assert out.startswith('✅ Updated')
        op = req.call_args.kwargs['json']['operations'][0]
        assert op['update']['resourceName'] == 'customers/1/ads/77'
        assert [h['text'] for h in op['update']['responsiveSearchAd']['headlines']] == ['A', 'B', 'C']
        assert op['updateMask'] == ('responsive_search_ad.headlines,responsive_search_ad.descriptions,'
                                    'responsive_search_ad.path1')

    @pytest.mark.parametrize('kwargs', [
        {'headlines': 'A|B'},                  # too few headlines
        {'headlines': 'A|B|' + 'x' * 31},      # headline too long
        {'headlines': 'A|B|a'},                # duplicate, case-insensitive
        {'descriptions': 'only one'},          # too few descriptions
        {'descriptions': 'a|' + 'x' * 91},     # description too long
        {'path1': 'x' * 16},                   # path too long
        {},                                    # nothing to update
    ])
    def test_validation_blocks_call(self, ads_http, kwargs):
        req, _ = ads_http
        assert update_ads_responsive_search_ad('1', '7', **kwargs).startswith('❌')
        req.assert_not_called()
