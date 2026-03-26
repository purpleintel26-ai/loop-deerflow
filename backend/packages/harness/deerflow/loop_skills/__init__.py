"""LOOP Skills - Human-Centered Autonomous Build System.

This module provides 5 LOOP DeerFlow skills for running experiments:

1. User Researcher - Conducts JTBD research to validate pain points
2. Problem Framer - Transforms pain points into solution concepts
3. MVP Builder - Builds and deploys full-stack MVPs
4. HCD Scorer - Measures HCD score and makes recommendations
5. Portfolio Manager - Manages experiment lifecycle

Usage:
    from deerflow.loop_skills import (
        UserResearcherSkill,
        ProblemFramerSkill,
        MVPBuilderSkill,
        HCDScorerSkill,
        PortfolioManagerSkill,
        run_user_researcher,
        run_problem_framer,
        run_mvp_builder,
        run_hcd_scorer,
        run_portfolio_manager
    )
    
    # Run user research
    result = run_user_researcher(
        idea="Habit accountability partner",
        target_user="Solo founders who miss follow-ups",
        dry_run=True
    )
"""

from .base import (
    BaseLoopSkill,
    SkillConfig,
    ValidationResult,
    LoopSkillError,
    ValidationError,
    ExecutionError,
    NotionSyncError,
    E2BExecutionError,
    Recommendation,
    ExperimentStatus,
)

from .user_researcher import UserResearcherSkill, run_user_researcher
from .problem_framer import ProblemFramerSkill, run_problem_framer
from .mvp_builder import MVPBuilderSkill, run_mvp_builder
from .hcd_scorer import HCDScorerSkill, run_hcd_scorer
from .portfolio_manager import PortfolioManagerSkill, run_portfolio_manager

__version__ = "1.0.0"

__all__ = [
    # Skills
    "UserResearcherSkill",
    "ProblemFramerSkill",
    "MVPBuilderSkill",
    "HCDScorerSkill",
    "PortfolioManagerSkill",
    
    # Convenience functions
    "run_user_researcher",
    "run_problem_framer",
    "run_mvp_builder",
    "run_hcd_scorer",
    "run_portfolio_manager",
    
    # Base classes
    "BaseLoopSkill",
    "SkillConfig",
    "ValidationResult",
    
    # Exceptions
    "LoopSkillError",
    "ValidationError",
    "ExecutionError",
    "NotionSyncError",
    "E2BExecutionError",
    
    # Enums
    "Recommendation",
    "ExperimentStatus",
]
