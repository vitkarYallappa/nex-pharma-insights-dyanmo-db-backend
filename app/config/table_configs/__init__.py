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
from .keywords_table import KeywordsTableConfig
from .source_urls_table import SourceUrlsTableConfig
from .content_repository_table import ContentRepositoryTableConfig
from .process_handling_table import ProcessHandlingTableConfig
from .content_url_mapping_table import ContentUrlMappingTableConfig
from .content_summary_table import ContentSummaryTableConfig
from .content_insight_table import ContentInsightTableConfig
from .content_implication_table import ContentImplicationTableConfig
from .content_analysis_mapping_table import ContentAnalysisMappingTableConfig
from .insight_comment_table import InsightCommentTableConfig
from .implication_comment_table import ImplicationCommentTableConfig
from .implication_qa_table import ImplicationQaTableConfig

__all__ = ["UsersTableConfig", "ProjectsTableConfig", "ProjectRequestStatisticsTableConfig", "ProjectModulesStatisticsTableConfig", "RequestsTableConfig", "GlobalKeywordsTableConfig", "GlobalBaseUrlsTableConfig", "KeywordsTableConfig", "SourceUrlsTableConfig", "ContentRepositoryTableConfig", "ProcessHandlingTableConfig", "ContentUrlMappingTableConfig", "ContentSummaryTableConfig", "ContentInsightTableConfig", "ContentImplicationTableConfig", "ContentAnalysisMappingTableConfig", "InsightCommentTableConfig", "ImplicationCommentTableConfig", "ImplicationQaTableConfig"] 