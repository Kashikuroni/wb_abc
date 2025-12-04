from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .core import APIClient


class BaseApi:
    """
    Base class for all Yandex Market API endpoints.

    Provides common initialization and client access for all API classes.
    """

    def __init__(self, client: "APIClient") -> None:
        """
        Initialize API endpoint with client.

        Args:
            client: Configured APIClient instance for making HTTP requests.
        """
        self.client = client
