"""conduit_py: a unified client for authenticating and working with Google APIs.

Exposes the top-level ``Conduit`` factory; see ``conduit_py.client`` for
details on how it resolves credentials and builds service clients.
"""

from conduit_py.client import Conduit

__all__ = ["Conduit"]