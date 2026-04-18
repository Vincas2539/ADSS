"""
API endpoint handlers for the Astronomy TAP Client.
"""

from .queries import QueriesEndpoint
from .users import UsersEndpoint
from .metadata import MetadataEndpoint
from .images import (
    ImagesEndpoint,
    LuptonImagesEndpoint,
    StampImagesEndpoint,
    TrilogyImagesEndpoint,
)

__all__ = [
    "QueriesEndpoint",
    "UsersEndpoint",
    "MetadataEndpoint",
    "ImagesEndpoint",
    "LuptonImagesEndpoint",
    "StampImagesEndpoint",
    "TrilogyImagesEndpoint",
]
