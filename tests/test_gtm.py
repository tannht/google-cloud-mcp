"""Tests for Google Tag Manager tools."""

from google_cloud_mcp import server

list_gtm_accounts = server.list_gtm_accounts
list_gtm_containers = server.list_gtm_containers
list_gtm_workspaces = server.list_gtm_workspaces
list_gtm_tags = server.list_gtm_tags
list_gtm_triggers = server.list_gtm_triggers
list_gtm_variables = server.list_gtm_variables
get_gtm_live_version = server.get_gtm_live_version
create_gtm_version = server.create_gtm_version
publish_gtm_version = server.publish_gtm_version


def _ws(service):
    return service.accounts.return_value.containers.return_value.workspaces.return_value


def _versions(service):
    return service.accounts.return_value.containers.return_value.versions.return_value


class TestGTMListing:
    def test_accounts(self, mock_gmail_service):
        service, mock_build = mock_gmail_service
        service.accounts.return_value.list.return_value.execute.return_value = {
            'account': [{'name': 'Acme', 'accountId': '1', 'path': 'accounts/1'}]}
        assert list_gtm_accounts() == "- Acme (ID: 1, path: accounts/1)"
        assert mock_build.call_args.args[:2] == ('tagmanager', 'v2')

    def test_containers_uses_parent(self, mock_gmail_service):
        service, _ = mock_gmail_service
        lst = service.accounts.return_value.containers.return_value.list
        lst.return_value.execute.return_value = {
            'container': [{'name': 'Web', 'containerId': '2', 'publicId': 'GTM-ABC', 'path': 'accounts/1/containers/2'}]}
        assert 'GTM-ABC' in list_gtm_containers('1')
        assert lst.call_args.kwargs['parent'] == 'accounts/1'

    def test_workspaces(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).list.return_value.execute.return_value = {
            'workspace': [{'name': 'Default Workspace', 'workspaceId': '3', 'path': 'p'}]}
        assert 'Default Workspace (ID: 3' in list_gtm_workspaces('accounts/1/containers/2')

    def test_tags_triggers_variables(self, mock_gmail_service):
        service, _ = mock_gmail_service
        ws = _ws(service)
        ws.tags.return_value.list.return_value.execute.return_value = {
            'tag': [{'name': 'GA4', 'tagId': '5', 'type': 'gaawc', 'firingTriggerId': ['2147479553']}]}
        ws.triggers.return_value.list.return_value.execute.return_value = {
            'trigger': [{'name': 'All Pages', 'triggerId': '6', 'type': 'PAGEVIEW'}]}
        ws.variables.return_value.list.return_value.execute.return_value = {
            'variable': [{'name': 'Page URL', 'variableId': '7', 'type': 'u'}]}
        assert 'GA4 (ID: 5, type: gaawc' in list_gtm_tags('w')
        assert 'All Pages (ID: 6, type: PAGEVIEW)' in list_gtm_triggers('w')
        assert 'Page URL (ID: 7, type: u)' in list_gtm_variables('w')

    def test_empty_list(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).tags.return_value.list.return_value.execute.return_value = {}
        assert list_gtm_tags('w') == "No tag found."

    def test_error_returned_as_string(self, mock_gmail_service):
        service, _ = mock_gmail_service
        service.accounts.return_value.list.return_value.execute.side_effect = Exception('boom')
        assert list_gtm_accounts() == 'boom'


class TestGTMVersions:
    def test_live_version(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _versions(service).live.return_value.execute.return_value = {
            'containerVersionId': '9', 'name': 'v9', 'tag': [1, 2], 'trigger': [1], 'variable': [], 'path': 'p'}
        out = get_gtm_live_version('accounts/1/containers/2')
        assert 'Version 9: v9' in out and 'Tags: 2, triggers: 1, variables: 0' in out

    def test_create_version(self, mock_gmail_service):
        service, _ = mock_gmail_service
        cv = _ws(service).create_version
        cv.return_value.execute.return_value = {'containerVersion': {'containerVersionId': '10', 'path': 'vp'}}
        assert 'Version 10 created' in create_gtm_version('w', 'Release', 'notes')
        assert cv.call_args.kwargs['body'] == {'name': 'Release', 'notes': 'notes'}

    def test_create_version_failure(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _ws(service).create_version.return_value.execute.return_value = {'syncStatus': {'mergeConflict': True}}
        assert create_gtm_version('w', 'x').startswith('❌')

    def test_publish_version(self, mock_gmail_service):
        service, _ = mock_gmail_service
        pub = _versions(service).publish
        pub.return_value.execute.return_value = {}
        assert publish_gtm_version('accounts/1/containers/2/versions/10').startswith('✅')
        assert pub.call_args.kwargs['path'] == 'accounts/1/containers/2/versions/10'

    def test_publish_compiler_error(self, mock_gmail_service):
        service, _ = mock_gmail_service
        _versions(service).publish.return_value.execute.return_value = {'compilerError': True}
        assert publish_gtm_version('p').startswith('❌')
