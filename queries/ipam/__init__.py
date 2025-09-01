"""
IPAM (IP Address Management) queries for Nautobot
"""

from .dynamic_ipam import DynamicIPAMQuery
from .filtered import IPAddressesFilteredQuery

__all__ = ["DynamicIPAMQuery", "IPAddressesFilteredQuery"]
