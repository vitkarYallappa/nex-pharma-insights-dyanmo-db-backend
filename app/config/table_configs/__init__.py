"""
Tables Configuration Package
Contains individual table configuration files
"""

from .users_table import UsersTableConfig
from .projects_table import ProjectsTableConfig
from .project_request_statistics_table import ProjectRequestStatisticsTableConfig

__all__ = ["UsersTableConfig", "ProjectsTableConfig", "ProjectRequestStatisticsTableConfig"] 