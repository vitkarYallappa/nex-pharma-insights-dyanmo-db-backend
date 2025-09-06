"""
Base Seeder Class
Abstract base class for all database seeders
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.core.logging import get_logger

logger = get_logger("seeder")

class BaseSeeder(ABC):
    """Abstract base class for database seeders"""
    
    def __init__(self):
        self.logger = logger
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the seeder name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the seeder description"""
        pass
    
    @abstractmethod
    async def seed(self) -> bool:
        """
        Run the seeder to populate data
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear the seeded data
        Returns True if successful, False otherwise
        """
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """
        Return list of seeder names that must run before this one
        Override in subclasses if needed
        """
        return []
    
    def log_info(self, message: str):
        """Log info message with seeder context"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message with seeder context"""
        self.logger.error(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message with seeder context"""
        self.logger.warning(f"[{self.name}] {message}") 