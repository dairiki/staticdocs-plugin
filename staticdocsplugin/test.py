# coding: utf-8

from contextlib import nested
from mock import Mock
from mock import patch
from trac.core import ComponentManager
from trac.web import HTTPNotFound
from trac.web import HTTPBadRequest

from unittest import TestCase
if not hasattr(TestCase, 'assertIn'):
    # python < 2.7
    from unittest2 import TestCase

class TestStaticDocsPlugin(TestCase):
    DEFAULT_CONFIG = {
        'alias./src/': '/dst/',
        }

    def _get_plugin(self, config=DEFAULT_CONFIG):
        from staticdocsplugin.staticdocs import StaticDocsPlugin

        env = DummyEnvironment(config)
        plugin = StaticDocsPlugin(env)
        return plugin

    def _request(self, path_info='/'):
        req = Mock()
        req.path_info = path_info
        req.href.return_value = '/HREF'
        return req

    def test_init(self):
        staticdocs = self._get_plugin({
            'foo':	'ignored',
            'alias.':	'also ignored',
            'alias./foo/': '/foopath/',
            'alias./bar/': '/barpath/',
            'alias./longer/': '/x/',
            'permission': 'DEFAULT',
            'permission./bar/': 'VIEW_BAR',
            })
        aliases = staticdocs.aliases

        self.assertEqual(staticdocs.aliases, [
            ('/longer/', '/x/', 'DEFAULT'),
            ('/bar/', '/barpath/', 'VIEW_BAR'),
            ('/foo/', '/foopath/', 'DEFAULT'),
            ])

    def test_default_permission(self):
        staticdocs = self._get_plugin({
            'alias./foo/': '/bar/',
            })
        self.assertEqual(staticdocs.aliases, [
            ('/foo/', '/bar/', 'WIKI_VIEW'),
            ])

    def test_match_request(self):
        match_request = self._get_plugin().match_request
        self.assertTrue(match_request(self._request('/src/')))
        self.assertTrue(match_request(self._request('/src/foo.html')))
        self.assertFalse(match_request(self._request('/bad/foo.html')))
        self.assertFalse(match_request(self._request('/src')))
        self.assertFalse(match_request(self._request('src/')))

    def _process_request(self, req, isdir=False, isfile=True, access=True):
        plugin = self._get_plugin()

        with nested(
            patch('staticdocsplugin.staticdocs.os.path.isdir'),
            patch('staticdocsplugin.staticdocs.os.path.isfile'),
            patch('staticdocsplugin.staticdocs.os.access')
            ) as (isdir_, isfile_, access_):

            isdir_.return_value = isdir
            isfile_.return_value = isfile
            access_.return_value = access

            plugin.process_request(req)

    def test_process_request(self):
        req = self._request('/src/foo.html')
        self._process_request(req)
        self.assertTrue(req.perm.require.called)
        req.send_file.assert_called_once_with('/dst/foo.html')

    def test_process_request_file_not_readable(self):
        req = self._request('/src/foo.html')
        with self.assertRaises(HTTPNotFound):
            self._process_request(req, access=False)
        self.assertTrue(req.perm.require.called)


    def test_process_request_bad_prefix(self):
        req = self._request('/bad/')
        with self.assertRaises(HTTPNotFound):
            self._process_request(req)

    def test_process_request_add_slash(self):
        req = self._request('/src/dir')
        self._process_request(req, isdir=True)
        self.assertTrue(req.perm.require.called)
        req.redirect.assert_called_once_with('/HREF/src/dir/')


    def test_process_request_not_found(self):
        req = self._request('/src/foo.html')
        with self.assertRaises(HTTPNotFound):
            self._process_request(req, isfile=False)
        self.assertTrue(req.perm.require.called)

    def test_process_request_directory_index(self):
        req = self._request('/src/dir/')
        self._process_request(req)
        self.assertTrue(req.perm.require.called)
        req.send_file.assert_called_once_with('/dst/dir/index.html')

        req = self._request('/src/')
        self._process_request(req)
        self.assertTrue(req.perm.require.called)
        req.send_file.assert_called_once_with('/dst/index.html')

class Test_normalize_path(TestCase):
    def test(self):
        from staticdocsplugin.staticdocs import normalize_path

        self.assertEquals(normalize_path('file.html'), 'file.html')
        self.assertEquals(normalize_path('/abs/file.html'), '/abs/file.html')
        self.assertEquals(normalize_path('./file.html'), 'file.html')
        self.assertEquals(normalize_path('/abs/./file.html'), '/abs/file.html')

    def assertNotFound(self, path):
        from staticdocsplugin.staticdocs import normalize_path
        with self.assertRaises(HTTPNotFound):
            normalize_path(path)

    def assertBadPath(self, path):
        from staticdocsplugin.staticdocs import normalize_path
        with self.assertRaises(HTTPBadRequest):
            normalize_path(path)

    def test_bad_paths(self):
        self.assertBadPath('..')
        self.assertBadPath('../')
        self.assertBadPath('../sneaky')
        self.assertBadPath('path/../sneaky')
        self.assertBadPath('path/..')
        self.assertBadPath('path/../')

    def test_hidden_files(self):
        self.assertNotFound('.hidden')
        self.assertNotFound('.hidden/dir')
        self.assertNotFound('path/.hidden/dir')

    def test_backup_files(self):
        self.assertNotFound('backup~')
        self.assertNotFound('backup~/file.html')
        self.assertNotFound('path/backup~/file.html')

class DummyConfig(object):
    def __init__(self, config):
        self.config = config

    def get(self, section, name, default=None):
        return self.config.get(name, default)

    def options(self, section):
        return self.config.items()

class DummyEnvironment(ComponentManager):
    def __init__(self, config={}):
        super(DummyEnvironment, self).__init__()
        self.log = Mock()
        self.config = DummyConfig(config)

    def component_activated(self, component):
        component.log = self.log
        component.config = self.config
