# Local imports
from uplink import converters

List = converters.TypingConverter.List
"""
A proxy for :py:class:`typing.List` that is safe to use in type 
hints with Python 3.4 and below.

.. code-block:: python

    @get("/users")
    def get_users(self) -> types.List[str]:
        \"""Fetches all users\"""

.. versionadded:: v0.5.0
"""

Dict = converters.TypingConverter.Dict
"""
A proxy for :py:class:`typing.Dict` that is safe to use in type 
hints with Python 3.4 and below.

.. code-block:: python

    @returns.json
    @get("/users")
    def get_users(self) -> types.Dict[str, str]:
        \"""Fetches all users\"""

.. versionadded:: v0.5.0
"""
