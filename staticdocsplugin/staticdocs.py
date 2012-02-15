# -*- coding: utf-8 -*-
#
# NB: we put this in module staticdocsplugin/staticdocs.py, rather than
# just staticdocsplugin/__init__.py, because in the latter case, trac
# annotates log messages with "[__init__]" (we prefer "[staticdocs]")
#
import os
from collections import namedtuple

from trac.core import *
from trac.web import IRequestHandler
from trac.web import HTTPNotFound
from trac.web import HTTPBadRequest

# The name of our config section
SECTION = 'staticdocs'

AliasInfo = namedtuple('AliasInfo', ['prefix', 'path', 'permission'])

class StaticDocsPlugin(Component):
    implements(IRequestHandler)

    def __init__(self):
        """ Read configuration.
        """
        log = self.log
        self.aliases = aliases = []

        config = self.config
        default_permission = config.get(SECTION, 'permission',
                                        default='WIKI_VIEW')

        for name, path in config.options(SECTION):
            if not name.startswith('alias.'):
                continue
            prefix = name[len('alias.'):]
            if not prefix:
                continue

            permission = config.get(SECTION, 'permission.%s' % prefix)
            if not permission:
                permission = default_permission

            aliases.append(AliasInfo(prefix, path, permission))

        # Sort longest prefix first, then alphabetically by prefix
        def longest_prefix_first(alias):
            return -len(alias.prefix), alias.prefix
        aliases.sort(key=longest_prefix_first)

        for alias in aliases:
            log.info("configured alias %r => %r (permission %s)",
                     alias.prefix, alias.path, alias.permission)

    # IRequestHandler methods
    def match_request(self, req):
        path_info = req.path_info
        return any(path_info.startswith(alias.prefix)
                   for alias in self.aliases)

    def process_request(self, req):
        log = self.log
        path_info = req.path_info
        for alias in self.aliases:
            if path_info.startswith(alias.prefix):
                path_tail = path_info[len(alias.prefix):]
                break
        else:
            log.error("path_info %r has unknown prefix", path_info)
            raise HTTPNotFound("Not found")

        log.debug("path_info=%r matched prefix=%r, permission=%s",
                  path_info, alias.prefix, alias.permission)

        req.perm.require(alias.permission or 'WIKI_VIEW')

        # Hack, if path looks like a directory, add /index.html
        if path_info.endswith('/'):
            if path_tail or not alias.path.endswith('/'):
                path_tail += '/'
            path_tail += 'index.html'

        full_path = alias.path + normalize_path(path_tail)
        log.debug("path_info=%r mapped to path=%r", path_info, full_path)

        if os.path.isdir(full_path):
            slash_path = req.href() + req.path_info + '/'
            log.debug("redirecting to %r", slash_path)
            return req.redirect(slash_path)

        if not os.path.isfile(full_path):
            log.debug("%s: file does not exist", full_path)
            raise HTTPNotFound("Not found")

        if not os.access(full_path, os.R_OK):
            log.warning("%s: file is not readable", full_path)
            raise HTTPNotFound("Not found")

        return req.send_file(full_path)


def normalize_path(file_path):
    head = file_path
    while head and head != '/':
        head, tail = os.path.split(head)
        if tail == '..':
            raise HTTPBadRequest("Bad request") # '..' ... pure evil
        if tail.endswith('~'):
            raise HTTPNotFound("Not found") # backup files
        if tail.startswith('.') and tail != '.':
            raise HTTPNotFound("Not found") # hidden files

    return os.path.normpath(file_path)
