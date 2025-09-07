"""
Tables Configuration Package
Contains individual table configuration files
"""

from .users_table import UsersTableConfig
from .projects_table import ProjectsTableConfig
from .project_request_statistics_table import ProjectRequestStatisticsTableConfig
from .project_modules_statistics_table import ProjectModulesStatisticsTableConfig
from .requests_table import RequestsTableConfig
from .global_keywords_table import GlobalKeywordsTableConfig
from .global_base_urls_table import GlobalBaseUrlsTableConfig

__all__ = ["UsersTableConfig", "ProjectsTableConfig", "ProjectRequestStatisticsTableConfig", "ProjectModulesStatisticsTableConfig", "RequestsTableConfig", "GlobalKeywordsTableConfig", "GlobalBaseUrlsTableConfig"] 