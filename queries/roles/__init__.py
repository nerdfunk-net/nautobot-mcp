"""
Role query modules
"""

from .dynamic_role import DynamicRoleQuery
from .prompt_parser import parse_role_prompt

__all__ = ['DynamicRoleQuery', 'parse_role_prompt']