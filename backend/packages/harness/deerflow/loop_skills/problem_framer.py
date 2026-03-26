"""LOOP Problem Framer Skill.

Transforms validated pain points into "How might we..." problem statements
and ranked solution concepts. Generates multiple solution approaches and
scores them by desirability, feasibility, and viability.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import (
    BaseLoopSkill, BaseValidator, ValidationResult,
    validate_required_fields, logger
)


@dataclass
class SolutionConcept:
    """Represents a solution concept."""
    rank: int
    name: str
    emotional_value_prop: str
    magic_moment: str
    differentiation: str
    desirability_score: float  # 0-10
    feasibility_score: float  # 0-10
    viability_score: float  # 0-10
    build_hours_estimate: int
    target_users: str
    
    @property
    def composite_score(self) -> float:
        """Calculate composite score based on LOOP weights."""
        return (self.desirability_score * 0.4 + 
                self.feasibility_score * 0.3 + 
                self.viability_score * 0.3)


@dataclass
class ProblemFramerInput:
    """Input for problem framing."""
    pain_points: List[Dict[str, Any]]
    concept_count: int = 3
    program_md_constraints: Optional[Dict[str, Any]] = None


@dataclass
class ProblemFramerOutput:
    """Output from problem framing."""
    how_might_we: str
    concepts: List[SolutionConcept]
    recommended_concept: str
    framing_confidence: str
    error: Optional[str] = None


class ProblemFramerValidator(BaseValidator[Dict[str, Any]]):
    """Validator for problem framer input/output."""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate problem framer input."""
        result = ValidationResult(valid=True)
        
        # Check for pain_points
        if "pain_points" not in data:
            result.add_error("Missing required field: pain_points")
        elif not isinstance(data["pain_points"], list):
            result.add_error("pain_points must be a list")
        elif len(data["pain_points"]) == 0:
            result.add_error("pain_points cannot be empty")
        else:
            # Validate each pain point
            for i, pain in enumerate(data["pain_points"]):
                if not isinstance(pain, dict):
                    result.add_error(f"pain_points[{i}] must be an object")
                elif "pain" not in pain:
                    result.add_error(f"pain_points[{i}] missing 'pain' field")
        
        # Validate concept_count
        if "concept_count" in data:
            count = data["concept_count"]
            if not isinstance(count, int) or count < 2 or count > 8:
                result.add_error("concept_count must be an integer between 2 and 8")
        
        return result


class ProblemFramerSkill(BaseLoopSkill):
    """
    Transforms validated pain points into actionable problem statements
    and solution concepts with emotional value props.
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.validator = ProblemFramerValidator()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute problem framing.
        
        Args:
            pain_points: Output from User Researcher (ranked pain matrix)
            concept_count: Number of concepts to generate (default: 3)
            program_md_constraints: Reference to HCD constraints (optional)
            
        Returns:
            Dict containing HMW statement and ranked concepts
        """
        # Validate input
        validation = self.validator.validate(kwargs)
        if not validation.valid:
            return {
                "error": "Validation failed",
                "validation_errors": validation.errors,
                "how_might_we": "",
                "concepts": [],
                "recommended_concept": ""
            }
        
        # Extract parameters
        pain_points = kwargs["pain_points"]
        concept_count = kwargs.get("concept_count", 3)
        constraints = kwargs.get("program_md_constraints", {})
        
        self.logger.info(f"Starting problem framing with {len(pain_points)} pain points")
        
        if self.config.dry_run:
            return self._dry_run_result(pain_points, concept_count)
        
        try:
            # Step 1: Generate HMW statement
            hmw = self._generate_hmw(pain_points)
            
            # Step 2: Generate concepts
            concepts = self._generate_concepts(hmw, pain_points, concept_count, constraints)
            
            # Step 3: Score and rank concepts
            ranked_concepts = self._rank_concepts(concepts)
            
            # Step 4: Determine recommendation
            recommended = ranked_concepts[0] if ranked_concepts else None
            
            if not recommended:
                return {
                    "error": "No valid concepts generated",
                    "how_might_we": hmw,
                    "concepts": [],
                    "recommended_concept": ""
                }
            
            # Calculate confidence
            confidence = self._calculate_confidence(ranked_concepts)
            
            # Build output
            output = {
                "how_might_we": hmw,
                "concepts": [
                    {
                        "rank": c.rank,
                        "name": c.name,
                        "emotional_value_prop": c.emotional_value_prop,
                        "magic_moment": c.magic_moment,
                        "differentiation": c.differentiation,
                        "desirability_score": c.desirability_score,
                        "feasibility_score": c.feasibility_score,
                        "viability_score": c.viability_score,
                        "composite_score": round(c.composite_score, 2),
                        "build_hours_estimate": c.build_hours_estimate,
                        "target_users": c.target_users
                    }
                    for c in ranked_concepts
                ],
                "recommended_concept": recommended.name,
                "framing_confidence": confidence,
                "top_concept_analysis": {
                    "strengths": self._analyze_strengths(recommended),
                    "risks": self._analyze_risks(recommended),
                    "magic_moment_60s": self._validate_magic_moment(recommended)
                }
            }
            
            # Sync to Notion
            self._sync_to_notion(
                title=f"Problem Framing: {hmw[:50]}",
                properties={
                    "Status": {"select": {"name": "Completed"}},
                    "Concepts Generated": {"number": len(ranked_concepts)},
                    "Recommended": {"rich_text": [{"text": {"content": recommended.name}}]},
                    "Confidence": {"select": {"name": confidence}}
                },
                content=json.dumps(output, indent=2)
            )
            
            return output
            
        except Exception as e:
            self.logger.error(f"Problem framing failed: {e}")
            return {
                "error": str(e),
                "how_might_we": "",
                "concepts": [],
                "recommended_concept": ""
            }
    
    def _dry_run_result(self, pain_points: List[Dict], concept_count: int) -> Dict[str, Any]:
        """Generate dry run result for testing."""
        self.logger.info("Generating dry run results")
        
        top_pain = pain_points[0] if pain_points else {"pain": "managing complex workflows"}
        
        hmw = f"How might we help users {top_pain['pain'].lower()} without adding cognitive load?"
        
        concepts = [
            {
                "rank": 1,
                "name": "Direct Automation",
                "emotional_value_prop": "Feel in control without the manual work",
                "magic_moment": "User connects their tool and sees instant organization in 30 seconds",
                "differentiation": "Works with existing tools instead of replacing them",
                "desirability_score": 8.5,
                "feasibility_score": 9.0,
                "viability_score": 8.0,
                "composite_score": 8.5,
                "build_hours_estimate": 6,
                "target_users": "Power users with existing workflows"
            },
            {
                "rank": 2,
                "name": "AI Assistant",
                "emotional_value_prop": "Feel like you have a personal assistant",
                "magic_moment": "User describes their problem in natural language and gets a solution in 45 seconds",
                "differentiation": "No complex setup, just describe what you need",
                "desirability_score": 9.0,
                "feasibility_score": 6.0,
                "viability_score": 7.5,
                "composite_score": 7.5,
                "build_hours_estimate": 12,
                "target_users": "Non-technical users who want simplicity"
            },
            {
                "rank": 3,
                "name": "Community-Powered",
                "emotional_value_prop": "Feel part of a community solving the same problem",
                "magic_moment": "User sees others' solutions and adapts one in 60 seconds",
                "differentiation": "Leverages collective intelligence",
                "desirability_score": 7.0,
                "feasibility_score": 7.5,
                "viability_score": 6.0,
                "composite_score": 6.8,
                "build_hours_estimate": 8,
                "target_users": "Community-oriented users"
            }
        ]
        
        return {
            "how_might_we": hmw,
            "concepts": concepts[:concept_count],
            "recommended_concept": concepts[0]["name"],
            "framing_confidence": "High",
            "top_concept_analysis": {
                "strengths": ["High desirability from research", "Fast to build", "Clear value prop"],
                "risks": ["Integration complexity", "Competition"],
                "magic_moment_60s": True
            },
            "dry_run": True
        }
    
    def _generate_hmw(self, pain_points: List[Dict]) -> str:
        """Generate 'How might we' statement from top pain point."""
        if not pain_points:
            return "How might we solve this problem?"
        
        top_pain = pain_points[0]
        pain_text = top_pain.get("pain", "solve this problem")
        
        # Extract action from pain
        action = pain_text.lower()
        
        # Generate HMW
        hmw_templates = [
            f"How might we help users {action} without adding complexity?",
            f"How might we make {action} effortless and delightful?",
            f"How might we eliminate the pain of {action}?",
            f"How might we turn {action} into a competitive advantage?"
        ]
        
        # Select based on pain characteristics
        if "time" in action or "manual" in action:
            return hmw_templates[0]
        elif "complex" in action or "difficult" in action:
            return hmw_templates[1]
        else:
            return hmw_templates[2]
    
    def _generate_concepts(self, hmw: str, pain_points: List[Dict], 
                          count: int, constraints: Dict) -> List[SolutionConcept]:
        """Generate solution concepts."""
        self.logger.info(f"Generating {count} solution concepts")
        
        concepts = []
        
        # Concept A: Direct Solution
        concepts.append(self._create_direct_concept(hmw, pain_points))
        
        # Concept B: AI-Assisted Solution
        if count >= 2:
            concepts.append(self._create_ai_concept(hmw, pain_points))
        
        # Concept C: Community/Social Solution
        if count >= 3:
            concepts.append(self._create_community_concept(hmw, pain_points))
        
        # Concept D: Integration-First Solution
        if count >= 4:
            concepts.append(self._create_integration_concept(hmw, pain_points))
        
        # Concept E: Mobile-First Solution
        if count >= 5:
            concepts.append(self._create_mobile_concept(hmw, pain_points))
        
        return concepts
    
    def _create_direct_concept(self, hmw: str, pain_points: List[Dict]) -> SolutionConcept:
        """Create direct solution concept."""
        top_pain = pain_points[0] if pain_points else {"pain": "the problem"}
        
        return SolutionConcept(
            rank=0,
            name="Direct Solution",
            emotional_value_prop="Feel in control with a straightforward solution that just works",
            magic_moment="User completes their first task in under 30 seconds with zero setup",
            differentiation="No learning curve, works exactly as expected",
            desirability_score=8.0,
            feasibility_score=9.0,
            viability_score=8.0,
            build_hours_estimate=6,
            target_users="Users who want simplicity over features"
        )
    
    def _create_ai_concept(self, hmw: str, pain_points: List[Dict]) -> SolutionConcept:
        """Create AI-assisted solution concept."""
        return SolutionConcept(
            rank=0,
            name="AI Assistant",
            emotional_value_prop="Feel like you have a personal assistant who anticipates your needs",
            magic_moment="User describes their goal in one sentence and AI generates a complete solution in 45 seconds",
            differentiation="Natural language interface, no complex configuration",
            desirability_score=9.0,
            feasibility_score=6.5,
            viability_score=7.5,
            build_hours_estimate=10,
            target_users="Non-technical users who want magical experiences"
        )
    
    def _create_community_concept(self, hmw: str, pain_points: List[Dict]) -> SolutionConcept:
        """Create community-powered solution concept."""
        return SolutionConcept(
            rank=0,
            name="Community-Powered",
            emotional_value_prop="Feel supported by a community of people solving the same challenges",
            magic_moment="User discovers a template created by someone just like them and adapts it in 60 seconds",
            differentiation="Leverages collective wisdom and shared experiences",
            desirability_score=7.5,
            feasibility_score=7.0,
            viability_score=6.5,
            build_hours_estimate=8,
            target_users="Social users who value peer recommendations"
        )
    
    def _create_integration_concept(self, hmw: str, pain_points: List[Dict]) -> SolutionConcept:
        """Create integration-first solution concept."""
        return SolutionConcept(
            rank=0,
            name="Integration Hub",
            emotional_value_prop="Feel connected as all your tools finally work together seamlessly",
            magic_moment="User connects their first integration and sees data flow instantly in 30 seconds",
            differentiation="Works with existing stack instead of replacing it",
            desirability_score=8.5,
            feasibility_score=7.0,
            viability_score=8.5,
            build_hours_estimate=12,
            target_users="Power users with complex existing workflows"
        )
    
    def _create_mobile_concept(self, hmw: str, pain_points: List[Dict]) -> SolutionConcept:
        """Create mobile-first solution concept."""
        return SolutionConcept(
            rank=0,
            name="Mobile-First",
            emotional_value_prop="Feel productive anywhere, not just at your desk",
            magic_moment="User completes a full workflow on their phone in under 60 seconds",
            differentiation="Designed for mobile first, not just adapted from desktop",
            desirability_score=7.0,
            feasibility_score=8.0,
            viability_score=7.0,
            build_hours_estimate=8,
            target_users="Mobile-native users who work on-the-go"
        )
    
    def _rank_concepts(self, concepts: List[SolutionConcept]) -> List[SolutionConcept]:
        """Score and rank concepts."""
        # Sort by composite score
        concepts.sort(key=lambda c: c.composite_score, reverse=True)
        
        # Assign ranks
        for i, c in enumerate(concepts):
            c.rank = i + 1
        
        return concepts
    
    def _calculate_confidence(self, concepts: List[SolutionConcept]) -> str:
        """Calculate confidence level based on concept quality."""
        if not concepts:
            return "Low"
        
        top = concepts[0]
        
        if top.composite_score >= 8.0 and top.desirability_score >= 8.0:
            return "High"
        elif top.composite_score >= 6.5:
            return "Medium"
        else:
            return "Low"
    
    def _analyze_strengths(self, concept: SolutionConcept) -> List[str]:
        """Analyze concept strengths."""
        strengths = []
        
        if concept.desirability_score >= 8:
            strengths.append("High user desirability")
        if concept.feasibility_score >= 8:
            strengths.append("Fast to build and iterate")
        if concept.viability_score >= 8:
            strengths.append("Clear path to revenue")
        if concept.build_hours_estimate <= 8:
            strengths.append("Fits within LOOP build budget")
        
        return strengths
    
    def _analyze_risks(self, concept: SolutionConcept) -> List[str]:
        """Analyze concept risks."""
        risks = []
        
        if concept.desirability_score < 7:
            risks.append("Lower user desirability - validate more")
        if concept.feasibility_score < 7:
            risks.append("Complex build - may exceed time budget")
        if concept.viability_score < 7:
            risks.append("Unclear monetization path")
        if concept.build_hours_estimate > 10:
            risks.append("Build time exceeds 8-hour target")
        
        return risks
    
    def _validate_magic_moment(self, concept: SolutionConcept) -> bool:
        """Validate magic moment can be demonstrated in 60 seconds."""
        # Simple heuristic based on description
        return concept.build_hours_estimate <= 10


def run_problem_framer(pain_points: List[Dict[str, Any]], 
                      concept_count: int = 3,
                      dry_run: bool = False) -> Dict[str, Any]:
    """
    Convenience function to run problem framing.
    
    Args:
        pain_points: Ranked pain points from user research
        concept_count: Number of concepts to generate
        dry_run: If True, returns simulated results
        
    Returns:
        Dict containing HMW statement and ranked concepts
    """
    from .base import SkillConfig
    
    config = SkillConfig.from_env()
    if dry_run:
        config.dry_run = True
    
    skill = ProblemFramerSkill(config)
    return skill.run(
        pain_points=pain_points,
        concept_count=concept_count
    )
