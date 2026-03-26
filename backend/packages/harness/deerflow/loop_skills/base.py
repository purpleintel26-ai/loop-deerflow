"""Base classes and utilities for LOOP skills.

This module provides the foundational infrastructure for all LOOP DeerFlow skills,
including base classes, input/output validation, error handling, and Notion/E2B integration.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("loop_skills")


class LoopSkillError(Exception):
    """Base exception for LOOP skill errors."""
    pass


class ValidationError(LoopSkillError):
    """Raised when input/output validation fails."""
    pass


class ExecutionError(LoopSkillError):
    """Raised when skill execution fails."""
    pass


class NotionSyncError(LoopSkillError):
    """Raised when Notion sync fails."""
    pass


class E2BExecutionError(LoopSkillError):
    """Raised when E2B code execution fails."""
    pass


class Recommendation(Enum):
    """HCD scoring recommendations."""
    SCALE = "SCALE"
    ITERATE = "ITERATE"
    PIVOT = "PIVOT"
    KILL = "KILL"


class ExperimentStatus(Enum):
    """Experiment lifecycle statuses."""
    IDEA = "IDEA"
    RESEARCH = "RESEARCH"
    BUILD = "BUILD"
    ACTIVE = "ACTIVE"
    ITERATING = "ITERATING"
    SCALED = "SCALED"
    KILLED = "KILLED"


@dataclass
class ValidationResult:
    """Result of input/output validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        self.valid = False
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


T = TypeVar('T')


class BaseValidator(ABC, Generic[T]):
    """Base class for input/output validators."""
    
    @abstractmethod
    def validate(self, data: T) -> ValidationResult:
        """Validate the given data."""
        pass


@dataclass
class SkillConfig:
    """Configuration for LOOP skills."""
    dry_run: bool = False
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None
    e2b_api_key: Optional[str] = None
    vercel_token: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "SkillConfig":
        """Load configuration from environment variables."""
        return cls(
            dry_run=os.getenv("LOOP_DRY_RUN", "false").lower() == "true",
            notion_api_key=os.getenv("NOTION_API_KEY"),
            notion_database_id=os.getenv("NOTION_DATABASE_ID"),
            e2b_api_key=os.getenv("E2B_API_KEY"),
            vercel_token=os.getenv("VERCEL_TOKEN"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            log_level=os.getenv("LOOP_LOG_LEVEL", "INFO"),
        )


class NotionClient:
    """Client for syncing data to Notion."""
    
    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        self.enabled = bool(self.api_key and self.database_id)
        
        if self.enabled:
            try:
                from notion_client import Client
                self.client = Client(auth=self.api_key)
                logger.info("Notion client initialized")
            except ImportError:
                logger.warning("notion-client not installed, Notion sync disabled")
                self.enabled = False
                self.client = None
        else:
            self.client = None
    
    def sync_page(self, title: str, properties: Dict[str, Any], content: Optional[str] = None) -> Optional[str]:
        """Sync a page to Notion database."""
        if not self.enabled:
            logger.info(f"[DRY RUN] Would sync to Notion: {title}")
            return None
        
        try:
            # Create page
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    **properties
                }
            )
            
            # Add content if provided
            if content:
                self.client.blocks.children.append(
                    block_id=page["id"],
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": content}}]
                            }
                        }
                    ]
                )
            
            logger.info(f"Synced to Notion: {title} (page_id: {page['id']})")
            return page["id"]
            
        except Exception as e:
            logger.error(f"Failed to sync to Notion: {e}")
            raise NotionSyncError(f"Notion sync failed: {e}")
    
    def update_page(self, page_id: str, properties: Dict[str, Any]) -> bool:
        """Update an existing Notion page."""
        if not self.enabled:
            logger.info(f"[DRY RUN] Would update Notion page: {page_id}")
            return True
        
        try:
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Updated Notion page: {page_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update Notion page: {e}")
            return False


class E2BExecutor:
    """Executor for running code in E2B sandbox."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("E2B_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                from e2b import Sandbox
                self.Sandbox = Sandbox
                logger.info("E2B executor initialized")
            except ImportError:
                logger.warning("e2b not installed, E2B execution disabled")
                self.enabled = False
                self.Sandbox = None
        else:
            self.Sandbox = None
    
    def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute code in E2B sandbox."""
        if not self.enabled:
            logger.info(f"[DRY RUN] Would execute code in E2B: {code[:100]}...")
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "dry_run": True
            }
        
        try:
            with self.Sandbox(api_key=self.api_key) as sandbox:
                result = sandbox.run_code(code, timeout=timeout)
                
                output = {
                    "stdout": result.stdout if hasattr(result, 'stdout') else str(result),
                    "stderr": result.stderr if hasattr(result, 'stderr') else "",
                    "exit_code": result.exit_code if hasattr(result, 'exit_code') else 0,
                    "dry_run": False
                }
                
                logger.info(f"E2B execution completed with exit code: {output['exit_code']}")
                return output
                
        except Exception as e:
            logger.error(f"E2B execution failed: {e}")
            raise E2BExecutionError(f"E2B execution failed: {e}")
    
    def execute_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute a shell command in E2B sandbox."""
        if not self.enabled:
            logger.info(f"[DRY RUN] Would execute command in E2B: {command}")
            return {
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "dry_run": True
            }
        
        try:
            with self.Sandbox(api_key=self.api_key) as sandbox:
                result = sandbox.commands.run(command, timeout=timeout)
                
                output = {
                    "stdout": result.stdout if hasattr(result, 'stdout') else str(result),
                    "stderr": result.stderr if hasattr(result, 'stderr') else "",
                    "exit_code": result.exit_code if hasattr(result, 'exit_code') else 0,
                    "dry_run": False
                }
                
                logger.info(f"E2B command execution completed with exit code: {output['exit_code']}")
                return output
                
        except Exception as e:
            logger.error(f"E2B command execution failed: {e}")
            raise E2BExecutionError(f"E2B command execution failed: {e}")


class BaseLoopSkill(ABC):
    """Base class for all LOOP skills."""
    
    def __init__(self, config: Optional[SkillConfig] = None):
        self.config = config or SkillConfig.from_env()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        # Initialize clients
        self.notion = NotionClient(
            api_key=self.config.notion_api_key,
            database_id=self.config.notion_database_id
        )
        self.e2b = E2BExecutor(api_key=self.config.e2b_api_key)
        
        self.logger.info(f"Initialized {self.__class__.__name__} (dry_run={self.config.dry_run})")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill's main logic."""
        pass
    
    def _sync_to_notion(self, title: str, properties: Dict[str, Any], content: Optional[str] = None) -> Optional[str]:
        """Helper method to sync results to Notion."""
        try:
            return self.notion.sync_page(title, properties, content)
        except NotionSyncError as e:
            self.logger.error(f"Notion sync failed: {e}")
            return None
    
    def _run_in_e2b(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Helper method to run code in E2B."""
        try:
            return self.e2b.execute(code, timeout)
        except E2BExecutionError as e:
            self.logger.error(f"E2B execution failed: {e}")
            raise
    
    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors and return standardized error response."""
        error_info = {
            "error": True,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error(f"Skill execution failed: {error_info}")
        return error_info
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Run the skill with error handling."""
        try:
            self.logger.info(f"Starting {self.__class__.__name__} execution")
            result = self.execute(**kwargs)
            result["success"] = True
            result["timestamp"] = datetime.utcnow().isoformat()
            result["dry_run"] = self.config.dry_run
            self.logger.info(f"Completed {self.__class__.__name__} execution")
            return result
        except Exception as e:
            return self._handle_error(e)


def format_json_output(data: Dict[str, Any]) -> str:
    """Format output as pretty JSON."""
    return json.dumps(data, indent=2, default=str)


def validate_required_fields(data: Dict[str, Any], required: List[str]) -> ValidationResult:
    """Validate that required fields are present and not empty."""
    result = ValidationResult(valid=True)
    
    for field in required:
        if field not in data:
            result.add_error(f"Missing required field: {field}")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            result.add_error(f"Required field is empty: {field}")
    
    return result
