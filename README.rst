==========================
Staticdocs Plugin for Trac
==========================

The staticdocs-plugin_ allows one to serve a directory of static web documents
through `trac`_.   The motivation for writing this was to be able
to control access to static files (e.g. project documentation)
using trac’s authentication and authorization system.

.. _staticdocs-plugin: http://github.com/dairiki/staticdocs-plugin
.. _trac: http://trac.edgewall.org/

Requirements
============

This has been tested under trac 0.12.  It may well work in earlier versions.
It probably requires python >= 2.6.

Configuration
=============

Somewhere in your trac configs put a section like::

    [staticdocs]

    # (Optional) Set the required permission for viewing static docs
    # The default is WIKI_VIEW
    permission         = WIKI_VIEW

    # Set up some aliases (you need at least one alias for this plugin
    # to be worthwhile.)
    alias./docs/       = /path/to/docs/
    alias./docs/other/ = /path/to/other/docs/

    # (Optional) Override the required permission for a specific alias
    permission./docs/other/  = TICKET_VIEW

Also, you will want to enable the plugin.  Probably like this::

    [components]

    staticdocsplugin.* = enabled

Now if you visit, e.g.,
``http://example.com/yourtrac/docs/file.html``, you will get served the
file ``/path/to/docs/file.html``.

Notes, Possible Buglets
========================

Hidden and backup files
^^^^^^^^^^^^^^^^^^^^^^^

Any requests for URLs which have a path component starting with ``.``
or ending with ``~`` will result in a ``404 Not Found`` response.

(Any request with a path component of ``..`` will result in a ``400
Bad Request`` response.)

Content Types
^^^^^^^^^^^^^

Currently, `mimetype.guess_type`_ is used to deduced the content type.

.. _mimetype.guess_type:
   http://docs.python.org/library/mimetypes.html#mimetypes.guess_type

Directory Indexes
^^^^^^^^^^^^^^^^^

If the URL ends in a slash, ``index.html`` is added.   This should
probably be fixed so as to look for ``index.htm`` as well.


Other Hints
===========

The NavAddPlugin_ (from trac-hacks_) will let you add links to your
static docs (or anywhere else) to the trac navigation bar.

The standard ExtraPermissionsProvider_ plugin can be used to add
a new custom permission (say ``STATIC_DOCS_VIEW``) if you would like
one to control access to your static files.

.. _trac-hacks: http://trac-hacks.org/
.. _NavAddPlugin: http://trac-hacks.org/wiki/NavAddPlugin
.. _ExtraPermissionsProvider:
   http://trac.edgewall.org/wiki/ExtraPermissionsProvider


Author
======

`Jeff Dairiki`__.

__ mailto:dairiki@dairiki.org
