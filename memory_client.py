"""
memory_client.py
================

This module provides a simple client interface for interacting with the
Memory API defined in ``memory_api.py``. It uses the ``requests``
library to perform HTTP operations against a running instance of the
API. The client exposes two convenience methods:

* ``store_memory``: Sends a POST request to the ``/store_memory``
  endpoint with a ``user_id`` and ``message`` to be stored.

* ``get_memory``: Sends a GET request to the ``/get_memory``
  endpoint with a ``user_id`` and returns the list of stored
  messages.

These functions can be imported into other Python code or used in
lambda functions to integrate the memory API into your Custom GPT
actions. For example, within the Custom GPT Builder you might
register an action named ``storeUserMessage`` that calls
``memory_client.store_memory`` to persist conversation history.

Example
-------

    from memory_client import MemoryClient

    client = MemoryClient("https://my-memory-api.example.com")
    client.store_memory("alice", "Hello world")
    history = client.get_memory("alice")
    print(history)

Note that error handling here is minimal; in a production
environment you should add retries, timeouts, and more robust
exception handling as appropriate.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

import requests


class MemoryClient:
    """Client for the Custom GPT Memory API.

    Parameters
    ----------
    base_url: str
        Base URL of the Memory API, e.g. ``http://localhost:8000`` or the
        full hosted URL of your deployment. The URL should not end with
        a trailing slash.
    """

    def __init__(self, base_url: str) -> None:
        # Remove trailing slash if present to avoid double slashes in
        # requests.
        self.base_url = base_url.rstrip("/")

    def store_memory(self, user_id: str, message: str) -> Dict[str, Any]:
        """Persist a message for a given user.

        Sends a POST request to the API. Raises ``HTTPError`` if the
        response status code is not 200.

        Parameters
        ----------
        user_id: str
            Identifier for the user or session.
        message: str
            The text to store.

        Returns
        -------
        dict
            Parsed JSON response from the API.
        """
        url = f"{self.base_url}/store_memory"
        payload = {"user_id": user_id, "message": message}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_memory(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve stored messages for a given user.

        Sends a GET request to the API. Raises ``HTTPError`` if the
        response status code is not 200.

        Parameters
        ----------
        user_id: str
            Identifier for the user or session.

        Returns
        -------
        list
            A list of dictionaries containing the stored messages.
        """
        url = f"{self.base_url}/get_memory"
        params = {"user_id": user_id}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("memories", [])