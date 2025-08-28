"""
IPAM (IP Address Management) queries for Nautobot
"""

from .customized import IPAddressesCustomizedQuery
from .filtered import IPAddressesFilteredQuery

__all__ = ['IPAddressesCustomizedQuery', 'IPAddressesFilteredQuery']