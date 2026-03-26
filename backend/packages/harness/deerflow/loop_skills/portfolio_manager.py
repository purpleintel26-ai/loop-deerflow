"""LOOP Portfolio Manager Skill.

Portfolio management system for LOOP experiments. Tracks experiment lifecycle
over weeks (not overnight), manages active experiments, kills poor performers
after 2 weeks, scales winners. Central dashboard for all LOOP activity.
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from .base import (
    BaseLoopSkill, BaseValidator, ValidationResult,
    validate_required_fields, logger, ExperimentStatus, Recommendation
)


@dataclass
class Experiment:
    """Represents a LOOP experiment."""
    id: str
    name: str
    status: ExperimentStatus
    idea: str
    days_running: int
    created_at: datetime
    live_url: Optional[str] = None
    hcd_score: Optional[float] = None
    next_action: str = ""
    early_signals: str = ""
    kill_reason: Optional[str] = None
    learnings: Optional[str] = None
    killed_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "idea": self.idea,
            "days_running": self.days_running,
            "created_at": self.created_at.isoformat(),
            "live_url": self.live_url,
            "hcd_score": self.hcd_score,
            "next_action": self.next_action,
            "early_signals": self.early_signals,
            "kill_reason": self.kill_reason,
            "learnings": self.learnings,
            "killed_date": self.killed_date.isoformat() if self.killed_date else None
        }


@dataclass
class PortfolioHealth:
    """Portfolio health metrics."""
    active_count: int
    max_active: int
    avg_hcd_score: float
    kill_rate: float
    portfolio_age_days: int


@dataclass
class KillListEntry:
    """Entry in the kill list."""
    experiment_id: str
    name: str
    idea: str
    killed_date: datetime
    days_survived: int
    hcd_score: Optional[float]
    kill_reason: str
    key_learning: str
    artifacts: Dict[str, str]


class PortfolioManagerValidator(BaseValidator[Dict[str, Any]]):
    """Validator for portfolio manager input."""
    
    VALID_COMMANDS = ["status", "review", "score", "new", "kill"]
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate portfolio manager input."""
        result = ValidationResult(valid=True)
        
        # Check for command
        if "command" not in data:
            result.add_error("Missing required field: command")
        elif data["command"] not in self.VALID_COMMANDS:
            result.add_error(f"Invalid command: {data['command']}. Must be one of {self.VALID_COMMANDS}")
        
        # Validate new command has idea
        if data.get("command") == "new" and "idea" not in data:
            result.add_error("'new' command requires 'idea' field")
        
        # Validate kill command has experiment_id and reason
        if data.get("command") == "kill":
            if "experiment_id" not in data:
                result.add_error("'kill' command requires 'experiment_id' field")
            if "reason" not in data:
                result.add_error("'kill' command requires 'reason' field")
        
        return result


class PortfolioManagerSkill(BaseLoopSkill):
    """
    Manages a portfolio of experiments over weeks — not overnight spam.
    Ruthlessly kills losers, doubles down on winners.
    """
    
    MAX_ACTIVE_EXPERIMENTS = 5
    MIN_EXPERIMENT_DAYS = 14  # 2 weeks before scoring
    TARGET_KILL_RATE = 0.40  # 40% kill rate is healthy
    
    def __init__(self, config=None):
        super().__init__(config)
        self.validator = PortfolioManagerValidator()
        self.experiments: List[Experiment] = []
        self.kill_list: List[KillListEntry] = []
        self._load_portfolio()
    
    def _load_portfolio(self):
        """Load portfolio from storage (Notion or local)."""
        # In production, this loads from Notion database
        # For now, start with empty portfolio
        self.logger.info("Portfolio loaded")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute portfolio management command.
        
        Args:
            command: What to do (status, review, score, new, kill)
            idea: For 'new' command - the experiment idea
            experiment_id: For 'kill' command - which experiment to kill
            reason: For 'kill' command - why it's being killed
            
        Returns:
            Dict containing portfolio status or command results
        """
        # Validate input
        validation = self.validator.validate(kwargs)
        if not validation.valid:
            return {
                "error": "Validation failed",
                "validation_errors": validation.errors
            }
        
        command = kwargs["command"]
        self.logger.info(f"Executing portfolio command: {command}")
        
        if self.config.dry_run:
            return self._dry_run_result(command, kwargs)
        
        try:
            if command == "status":
                return self._cmd_status()
            elif command == "review":
                return self._cmd_review()
            elif command == "score":
                return self._cmd_score()
            elif command == "new":
                return self._cmd_new(kwargs["idea"])
            elif command == "kill":
                return self._cmd_kill(kwargs["experiment_id"], kwargs.get("reason", "Manual kill"))
            else:
                return {"error": f"Unknown command: {command}"}
                
        except Exception as e:
            self.logger.error(f"Portfolio command failed: {e}")
            return {"error": str(e)}
    
    def _dry_run_result(self, command: str, kwargs: Dict) -> Dict[str, Any]:
        """Generate dry run result for testing."""
        self.logger.info(f"Generating dry run result for {command}")
        
        if command == "status":
            return {
                "active_experiments": [
                    {
                        "id": "loop-001",
                        "name": "HabitBuddy",
                        "status": "ACTIVE",
                        "days_running": 12,
                        "live_url": "https://habitbuddy-demo.vercel.app",
                        "next_action": "HCD Score in 2 days",
                        "early_signals": "High waitlist conversion (18%)"
                    },
                    {
                        "id": "loop-002",
                        "name": "FocusFlow",
                        "status": "ACTIVE",
                        "days_running": 8,
                        "live_url": "https://focusflow-demo.vercel.app",
                        "next_action": "HCD Score in 6 days",
                        "early_signals": "Moderate engagement"
                    }
                ],
                "iteration_queue": [
                    {
                        "id": "loop-003",
                        "name": "TaskMaster",
                        "status": "ITERATING",
                        "fix_needed": "Demo clarity - users confused by navigation",
                        "return_to_build": True
                    }
                ],
                "kill_list": [
                    {
                        "experiment_id": "loop-000",
                        "name": "AutoPlan",
                        "killed_date": "2024-03-01",
                        "reason": "Lovability 4.2 < 6.0 threshold",
                        "learnings": "Users don't want AI to plan their day - they want control"
                    }
                ],
                "scaled_experiments": [
                    {
                        "id": "loop-099",
                        "name": "Synapse Daily",
                        "status": "SCALED",
                        "hcd_score": 0.82,
                        "current_focus": "Marketing automation"
                    }
                ],
                "portfolio_health": {
                    "active_count": 2,
                    "max_active": 5,
                    "avg_hcd_score": 0.68,
                    "kill_rate": 0.33,
                    "portfolio_age_days": 45
                },
                "dry_run": True
            }
        
        elif command == "new":
            return {
                "success": True,
                "experiment_id": f"loop-{random.randint(100, 999)}",
                "name": kwargs.get("idea", "New Experiment")[:30],
                "status": "IDEA",
                "next_steps": [
                    "Run User Researcher",
                    "Run Problem Framer", 
                    "Run MVP Builder",
                    "Schedule HCD Scoring in 2 weeks"
                ],
                "dry_run": True
            }
        
        elif command == "kill":
            return {
                "success": True,
                "experiment_id": kwargs.get("experiment_id"),
                "action": "KILLED",
                "reason": kwargs.get("reason"),
                "added_to_kill_list": True,
                "dry_run": True
            }
        
        else:
            return {
                "command": command,
                "dry_run": True,
                "message": f"Dry run for {command} command"
            }
    
    def _cmd_status(self) -> Dict[str, Any]:
        """Get current portfolio status."""
        self.logger.info("Getting portfolio status")
        
        # Categorize experiments
        active = [e for e in self.experiments if e.status == ExperimentStatus.ACTIVE]
        iterating = [e for e in self.experiments if e.status == ExperimentStatus.ITERATING]
        scaled = [e for e in self.experiments if e.status == ExperimentStatus.SCALED]
        
        # Build status output
        output = {
            "active_experiments": [
                {
                    "id": e.id,
                    "name": e.name,
                    "status": e.status.value,
                    "days_running": e.days_running,
                    "live_url": e.live_url,
                    "next_action": e.next_action or f"HCD Score in {max(0, self.MIN_EXPERIMENT_DAYS - e.days_running)} days",
                    "early_signals": e.early_signals or "Monitoring..."
                }
                for e in active
            ],
            "iteration_queue": [
                {
                    "id": e.id,
                    "name": e.name,
                    "status": e.status.value,
                    "fix_needed": e.next_action,
                    "return_to_build": True
                }
                for e in iterating
            ],
            "scaled_experiments": [
                {
                    "id": e.id,
                    "name": e.name,
                    "status": e.status.value,
                    "hcd_score": e.hcd_score,
                    "current_focus": e.next_action or "Growth optimization"
                }
                for e in scaled
            ],
            "kill_list": [
                {
                    "experiment_id": k.experiment_id,
                    "name": k.name,
                    "killed_date": k.killed_date.isoformat(),
                    "reason": k.kill_reason,
                    "learnings": k.key_learning
                }
                for k in self.kill_list[-10:]  # Last 10 kills
            ],
            "portfolio_health": self._calculate_portfolio_health()
        }
        
        return output
    
    def _cmd_review(self) -> Dict[str, Any]:
        """Weekly portfolio review."""
        self.logger.info("Running weekly portfolio review")
        
        active = [e for e in self.experiments if e.status == ExperimentStatus.ACTIVE]
        
        review_items = []
        for exp in active:
            # Flag experiments needing attention
            needs_attention = False
            attention_reason = ""
            
            if exp.days_running >= self.MIN_EXPERIMENT_DAYS and not exp.hcd_score:
                needs_attention = True
                attention_reason = "Ready for HCD scoring"
            elif exp.days_running < 7 and not exp.live_url:
                needs_attention = True
                attention_reason = "Still in build phase"
            
            review_items.append({
                "id": exp.id,
                "name": exp.name,
                "days_running": exp.days_running,
                "needs_attention": needs_attention,
                "attention_reason": attention_reason,
                "recommendation": "Continue monitoring" if not needs_attention else attention_reason
            })
        
        return {
            "review_date": datetime.utcnow().isoformat(),
            "active_count": len(active),
            "items_requiring_attention": [r for r in review_items if r["needs_attention"]],
            "all_items": review_items,
            "portfolio_health": self._calculate_portfolio_health(),
            "recommendations": [
                "Check waitlist growth daily",
                "Schedule HCD scoring when experiments hit 14 days",
                "Kill ruthlessly based on early signals"
            ]
        }
    
    def _cmd_score(self) -> Dict[str, Any]:
        """Score active experiments ready for evaluation."""
        self.logger.info("Scoring active experiments")
        
        ready_for_scoring = [
            e for e in self.experiments 
            if e.status == ExperimentStatus.ACTIVE 
            and e.days_running >= self.MIN_EXPERIMENT_DAYS
            and e.live_url
            and not e.hcd_score
        ]
        
        if not ready_for_scoring:
            return {
                "message": "No experiments ready for scoring",
                "experiments_ready": 0,
                "experiments_total": len([e for e in self.experiments if e.status == ExperimentStatus.ACTIVE])
            }
        
        scoring_results = []
        for exp in ready_for_scoring:
            # In production, this would call HCD Scorer skill
            scoring_results.append({
                "experiment_id": exp.id,
                "name": exp.name,
                "status": "Ready for HCD scoring",
                "live_url": exp.live_url,
                "action": "Run loop-hcd-scorer"
            })
        
        return {
            "experiments_ready": len(scoring_results),
            "experiments": scoring_results,
            "next_action": f"Run HCD scorer on {len(scoring_results)} experiments"
        }
    
    def _cmd_new(self, idea: str) -> Dict[str, Any]:
        """Start a new experiment."""
        self.logger.info(f"Starting new experiment: {idea}")
        
        # Check if we have capacity
        active_count = len([e for e in self.experiments if e.status == ExperimentStatus.ACTIVE])
        if active_count >= self.MAX_ACTIVE_EXPERIMENTS:
            return {
                "success": False,
                "error": f"Portfolio at capacity ({active_count}/{self.MAX_ACTIVE_EXPERIMENTS} active). Kill an experiment first.",
                "active_experiments": active_count,
                "max_active": self.MAX_ACTIVE_EXPERIMENTS
            }
        
        # Create new experiment
        exp_id = f"loop-{uuid.uuid4().hex[:6]}"
        exp_name = idea[:30] if len(idea) <= 30 else idea[:27] + "..."
        
        experiment = Experiment(
            id=exp_id,
            name=exp_name,
            status=ExperimentStatus.IDEA,
            idea=idea,
            days_running=0,
            created_at=datetime.utcnow(),
            next_action="Run User Researcher"
        )
        
        self.experiments.append(experiment)
        
        # Sync to Notion
        self._sync_to_notion(
            title=f"New Experiment: {exp_name}",
            properties={
                "Status": {"select": {"name": "IDEA"}},
                "Experiment ID": {"rich_text": [{"text": {"content": exp_id}}]},
                "Idea": {"rich_text": [{"text": {"content": idea[:100]}}]}
            },
            content=json.dumps(experiment.to_dict(), indent=2)
        )
        
        return {
            "success": True,
            "experiment_id": exp_id,
            "name": exp_name,
            "status": "IDEA",
            "next_steps": [
                "1. Run User Researcher to validate pain points",
                "2. Run Problem Framer to generate concepts",
                "3. Run MVP Builder to create and deploy MVP",
                f"4. Schedule HCD Scoring in {self.MIN_EXPERIMENT_DAYS} days"
            ]
        }
    
    def _cmd_kill(self, experiment_id: str, reason: str) -> Dict[str, Any]:
        """Kill an experiment."""
        self.logger.info(f"Killing experiment {experiment_id}: {reason}")
        
        # Find experiment
        exp = next((e for e in self.experiments if e.id == experiment_id), None)
        if not exp:
            return {
                "success": False,
                "error": f"Experiment {experiment_id} not found"
            }
        
        # Create kill list entry
        kill_entry = KillListEntry(
            experiment_id=exp.id,
            name=exp.name,
            idea=exp.idea,
            killed_date=datetime.utcnow(),
            days_survived=exp.days_running,
            hcd_score=exp.hcd_score,
            kill_reason=reason,
            key_learning=f"Killed: {reason}",
            artifacts={
                "live_url": exp.live_url or "",
                "repo": f"https://github.com/loop-experiments/{exp.id}"
            }
        )
        
        self.kill_list.append(kill_entry)
        
        # Update experiment status
        exp.status = ExperimentStatus.KILLED
        exp.kill_reason = reason
        exp.killed_date = datetime.utcnow()
        exp.learnings = kill_entry.key_learning
        
        # Sync to Notion
        self._sync_to_notion(
            title=f"KILLED: {exp.name}",
            properties={
                "Status": {"select": {"name": "KILLED"}},
                "Experiment ID": {"rich_text": [{"text": {"content": exp_id}}]},
                "Kill Reason": {"rich_text": [{"text": {"content": reason}}]}
            },
            content=json.dumps(kill_entry.__dict__, indent=2, default=str)
        )
        
        return {
            "success": True,
            "experiment_id": experiment_id,
            "action": "KILLED",
            "reason": reason,
            "added_to_kill_list": True,
            "portfolio_health": self._calculate_portfolio_health()
        }
    
    def _calculate_portfolio_health(self) -> Dict[str, Any]:
        """Calculate portfolio health metrics."""
        active = [e for e in self.experiments if e.status == ExperimentStatus.ACTIVE]
        killed = [e for e in self.experiments if e.status == ExperimentStatus.KILLED]
        scored = [e for e in self.experiments if e.hcd_score is not None]
        
        avg_hcd = sum(e.hcd_score for e in scored) / len(scored) if scored else 0.0
        kill_rate = len(killed) / len(self.experiments) if self.experiments else 0.0
        
        # Calculate portfolio age
        if self.experiments:
            oldest = min(e.created_at for e in self.experiments)
            age_days = (datetime.utcnow() - oldest).days
        else:
            age_days = 0
        
        return {
            "active_count": len(active),
            "max_active": self.MAX_ACTIVE_EXPERIMENTS,
            "avg_hcd_score": round(avg_hcd, 2),
            "kill_rate": round(kill_rate, 2),
            "portfolio_age_days": age_days,
            "total_experiments": len(self.experiments),
            "scaled_count": len([e for e in self.experiments if e.status == ExperimentStatus.SCALED])
        }
    
    def update_experiment_status(self, experiment_id: str, status: ExperimentStatus,
                                hcd_score: Optional[float] = None,
                                recommendation: Optional[Recommendation] = None) -> bool:
        """Update experiment status (called by other skills)."""
        exp = next((e for e in self.experiments if e.id == experiment_id), None)
        if not exp:
            return False
        
        exp.status = status
        if hcd_score is not None:
            exp.hcd_score = hcd_score
        
        if recommendation:
            if recommendation == Recommendation.SCALE:
                exp.next_action = "Continue building - begin marketing"
            elif recommendation == Recommendation.ITERATE:
                exp.next_action = "Fix top friction and rebuild"
            elif recommendation == Recommendation.PIVOT:
                exp.next_action = "Reframe with Problem Framer"
            elif recommendation == Recommendation.KILL:
                self._cmd_kill(experiment_id, "Low HCD score")
        
        return True


def run_portfolio_manager(command: str, 
                         idea: Optional[str] = None,
                         experiment_id: Optional[str] = None,
                         reason: Optional[str] = None,
                         dry_run: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run portfolio manager.
    
    Args:
        command: Command to run (status, review, score, new, kill)
        idea: For 'new' command - the experiment idea
        experiment_id: For 'kill' command
        reason: For 'kill' command - reason for killing
        dry_run: If True, returns simulated results
        
    Returns:
        Dict containing portfolio status or command results
    """
    from .base import SkillConfig
    
    config = SkillConfig.from_env()
    if dry_run:
        config.dry_run = True
    
    skill = PortfolioManagerSkill(config)
    return skill.run(
        command=command,
        idea=idea,
        experiment_id=experiment_id,
        reason=reason
    )
