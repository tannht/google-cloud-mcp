"""Tests for Search Console and GA4 tools."""

from google_cloud_mcp import server

list_search_console_sites = server.list_search_console_sites
search_console_query = server.search_console_query
list_search_console_sitemaps = server.list_search_console_sitemaps
inspect_url = server.inspect_url
list_ga4_properties = server.list_ga4_properties
run_ga4_report = server.run_ga4_report


class TestSearchConsole:
    def test_list_sites(self, mock_gmail_service):
        service, mock_build = mock_gmail_service
        service.sites.return_value.list.return_value.execute.return_value = {
            'siteEntry': [{'siteUrl': 'https://a.com/', 'permissionLevel': 'siteOwner'}]}
        assert list_search_console_sites() == "- https://a.com/ (siteOwner)"
        assert mock_build.call_args.args[:2] == ('searchconsole', 'v1')

    def test_query(self, mock_gmail_service):
        service, _ = mock_gmail_service
        q = service.searchanalytics.return_value.query
        q.return_value.execute.return_value = {'rows': [
            {'keys': ['seo', 'https://a.com/'], 'clicks': 5, 'impressions': 100, 'ctr': 0.05, 'position': 3.24}]}
        out = search_console_query('https://a.com/', '2026-01-01', '2026-01-31', 'query, page')
        assert 'seo | https://a.com/: clicks 5, impr 100, ctr 5.00%, pos 3.2' in out
        assert q.call_args.kwargs['body']['dimensions'] == ['query', 'page']

    def test_query_no_data(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.searchanalytics.return_value.query.return_value.execute.return_value = {}
        assert search_console_query('s', 'a', 'b') == "No data."

    def test_sitemaps(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.sitemaps.return_value.list.return_value.execute.return_value = {
            'sitemap': [{'path': 'https://a.com/sitemap.xml', 'errors': 1}]}
        assert 'sitemap.xml (errors: 1, warnings: 0' in list_search_console_sitemaps('s')

    def test_inspect_url(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.urlInspection.return_value.index.return_value.inspect.return_value.execute.return_value = {
            'inspectionResult': {'indexStatusResult': {'verdict': 'PASS', 'coverageState': 'Indexed'}}}
        out = inspect_url('s', 'https://a.com/x')
        assert 'Verdict: PASS' in out and 'Coverage: Indexed' in out

    def test_error_returned_as_string(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.sites.return_value.list.return_value.execute.side_effect = Exception('boom')
        assert list_search_console_sites() == 'boom'


class TestGA4:
    def test_list_properties(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.accountSummaries.return_value.list.return_value.execute.return_value = {
            'accountSummaries': [{'displayName': 'Acme', 'propertySummaries': [
                {'displayName': 'Web', 'property': 'properties/1'}]}]}
        out = list_ga4_properties()
        assert 'Acme' in out and 'Web (properties/1)' in out

    def test_run_report(self, mock_gmail_service):
        service, mock_build = mock_gmail_service
        run = service.properties.return_value.runReport
        run.return_value.execute.return_value = {'rows': [
            {'dimensionValues': [{'value': '20260101'}],
             'metricValues': [{'value': '10'}, {'value': '20'}]}]}
        out = run_ga4_report('properties/123')
        assert out == "- 20260101: activeUsers 10, sessions 20"
        assert run.call_args.kwargs['property'] == 'properties/123'
        assert mock_build.call_args.args[:2] == ('analyticsdata', 'v1beta')

    def test_run_report_no_data(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.properties.return_value.runReport.return_value.execute.return_value = {}
        assert run_ga4_report('1') == "No data."


list_ga4_data_streams = server.list_ga4_data_streams
list_ga4_key_events = server.list_ga4_key_events
run_ga4_realtime_report = server.run_ga4_realtime_report
get_ga4_metadata = server.get_ga4_metadata
add_search_console_site = server.add_search_console_site
submit_search_console_sitemap = server.submit_search_console_sitemap


class TestGA4Extra:
    def test_data_streams(self, mock_gmail_service):
        service, _ = mock_gmail_service
        lst = service.properties.return_value.dataStreams.return_value.list
        lst.return_value.execute.return_value = {'dataStreams': [{
            'displayName': 'Web', 'type': 'WEB_DATA_STREAM', 'name': 'properties/1/dataStreams/2',
            'webStreamData': {'measurementId': 'G-ABC'}}]}
        assert 'measurement ID: G-ABC' in list_ga4_data_streams('1')
        assert lst.call_args.kwargs['parent'] == 'properties/1'

    def test_key_events(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.properties.return_value.keyEvents.return_value.list.return_value.execute.return_value = {
            'keyEvents': [{'eventName': 'purchase', 'countingMethod': 'ONCE_PER_EVENT'}]}
        assert list_ga4_key_events('properties/1') == "- purchase (counting: ONCE_PER_EVENT)"

    def test_realtime(self, mock_gmail_service):
        service, _ = mock_gmail_service
        rt = service.properties.return_value.runRealtimeReport
        rt.return_value.execute.return_value = {'rows': [
            {'dimensionValues': [{'value': 'Vietnam'}], 'metricValues': [{'value': '3'}]}]}
        assert run_ga4_realtime_report('1') == "- Vietnam: activeUsers 3"
        assert rt.call_args.kwargs['property'] == 'properties/1'

    def test_metadata_filters_kind(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.properties.return_value.getMetadata.return_value.execute.return_value = {
            'dimensions': [{'apiName': 'country', 'uiName': 'Country'}],
            'metrics': [{'apiName': 'sessions', 'uiName': 'Sessions'}]}
        out = get_ga4_metadata('1', 'metrics')
        assert 'sessions' in out and 'country' not in out


class TestSearchConsoleExtra:
    def test_add_site(self, mock_gmail_service):
        service, _ = mock_gmail_service
        assert add_search_console_site('https://a.com/').startswith('✅')
        assert service.sites.return_value.add.call_args.kwargs['siteUrl'] == 'https://a.com/'

    def test_submit_sitemap(self, mock_gmail_service):
        service, _ = mock_gmail_service
        assert submit_search_console_sitemap('https://a.com/', 'https://a.com/sitemap.xml').startswith('✅')
        kw = service.sitemaps.return_value.submit.call_args.kwargs
        assert kw == {'siteUrl': 'https://a.com/', 'feedpath': 'https://a.com/sitemap.xml'}
