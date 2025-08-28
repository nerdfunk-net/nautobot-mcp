"""
Device query modules for Nautobot MCP Server
"""

from .by_name import DevicesByNameQuery
from .by_location import DevicesByLocationQuery  
from .by_role import DevicesByRoleQuery
from .by_tag import DevicesByTagQuery
from .by_devicetype import DevicesByDeviceTypeQuery
from .by_manufacturer import DevicesByManufacturerQuery
from .by_platform import DevicesByPlatformQuery
from .interfaces import DeviceInterfacesQuery
from .customized import DevicesCustomizedQuery
from .basic_details import DeviceBasicDetailsQuery
from .test_minimal import TestMinimalQuery

__all__ = [
    'DevicesByNameQuery',
    'DevicesByLocationQuery', 
    'DevicesByRoleQuery',
    'DevicesByTagQuery',
    'DevicesByDeviceTypeQuery',
    'DevicesByManufacturerQuery',
    'DevicesByPlatformQuery',
    'DeviceInterfacesQuery',
    'DevicesCustomizedQuery',
    'DeviceBasicDetailsQuery',
    'TestMinimalQuery'
]