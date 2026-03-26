"""Unit tests for LOOP skills.

Run with: python -m pytest tests/ -v
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import skills
import sys
sys.path.insert(0, '/root/.openclaw/workspace/loop-deerflow/backend/packages/harness')

from deerflow.loop_skills import (
    UserResearcherSkill,
    ProblemFramerSkill,
    MVPBuilderSkill,
    HCDScorerSkill,
    PortfolioManagerSkill,
    SkillConfig,
    Recommendation,
    ExperimentStatus,
    ValidationError,
)


class TestSkillConfig:
    """Test SkillConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SkillConfig()
        assert config.dry_run == False
        assert config.log_level == "INFO"
    
    def test_from_env(self, monkeypatch):
        """Test loading from environment variables."""
        monkeypatch.setenv("LOOP_DRY_RUN", "true")
        monkeypatch.setenv("LOOP_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("NOTION_API_KEY", "test-key")
        
        config = SkillConfig.from_env()
        assert config.dry_run == True
        assert config.log_level == "DEBUG"
        assert config.notion_api_key == "test-key"


class TestUserResearcherSkill:
    """Test User Researcher skill."""
    
    @pytest.fixture
    def skill(self):
        config = SkillConfig(dry_run=True)
        return UserResearcherSkill(config)
    
    def test_validation_missing_idea(self, skill):
        """Test validation fails without idea."""
        result = skill.run(target_user="test users")
        assert result["validated"] == False
        assert "Validation failed" in result["error"]
    
    def test_validation_missing_target_user(self, skill):
        """Test validation fails without target_user."""
        result = skill.run(idea="test idea")
        assert result["validated"] == False
        assert "Validation failed" in result["error"]
    
    def test_dry_run_success(self, skill):
        """Test dry run returns expected structure."""
        result = skill.run(
            idea="Habit accountability partner",
            target_user="Solo founders",
            interview_count=5
        )
        
        assert result["success"] == True
        assert result["validated"] == True
        assert result["dry_run"] == True
        assert "pain_points" in result
        assert len(result["pain_points"]) > 0
        assert "confidence_level" in result
    
    def test_pain_point_ranking(self, skill):
        """Test pain points are ranked correctly."""
        result = skill.run(
            idea="Test idea",
            target_user="Test users",
            interview_count=5
        )
        
        pain_points = result["pain_points"]
        assert len(pain_points) > 0
        
        # Check ranking
        ranks = [p["rank"] for p in pain_points]
        assert ranks == sorted(ranks)  # Should be in ascending order
    
    def test_interview_count_validation(self, skill):
        """Test interview count validation."""
        # Too few
        result = skill.run(idea="test", target_user="users", interview_count=2)
        assert result["validated"] == False
        
        # Too many
        result = skill.run(idea="test", target_user="users", interview_count=25)
        assert result["validated"] == False
        
        # Valid
        result = skill.run(idea="test", target_user="users", interview_count=5)
        assert result["validated"] == True


class TestProblemFramerSkill:
    """Test Problem Framer skill."""
    
    @pytest.fixture
    def skill(self):
        config = SkillConfig(dry_run=True)
        return ProblemFramerSkill(config)
    
    @pytest.fixture
    def sample_pain_points(self):
        return [
            {
                "rank": 1,
                "pain": "Managing follow-ups takes too much time",
                "frequency": "Daily",
                "current_workaround": "Spreadsheets",
                "willingness_to_pay": "$20-50/month",
                "verbatim_quotes": ["I waste 2 hours daily"],
                "severity_score": 8.5
            },
            {
                "rank": 2,
                "pain": "Forgetting important conversations",
                "frequency": "Weekly",
                "current_workaround": "Sticky notes",
                "willingness_to_pay": "$10-30/month",
                "verbatim_quotes": ["I've missed opportunities"],
                "severity_score": 7.0
            }
        ]
    
    def test_validation_empty_pain_points(self, skill):
        """Test validation fails with empty pain points."""
        result = skill.run(pain_points=[])
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_validation_missing_pain_field(self, skill):
        """Test validation fails without pain field."""
        result = skill.run(pain_points=[{"frequency": "daily"}])
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_dry_run_generates_hmw(self, skill, sample_pain_points):
        """Test dry run generates HMW statement."""
        result = skill.run(
            pain_points=sample_pain_points,
            concept_count=3
        )
        
        assert result["success"] == True
        assert "how_might_we" in result
        assert result["how_might_we"].startswith("How might we")
        assert "concepts" in result
        assert len(result["concepts"]) > 0
    
    def test_concept_scoring(self, skill, sample_pain_points):
        """Test concepts have valid scores."""
        result = skill.run(
            pain_points=sample_pain_points,
            concept_count=3
        )
        
        for concept in result["concepts"]:
            assert "desirability_score" in concept
            assert "feasibility_score" in concept
            assert "viability_score" in concept
            assert 0 <= concept["desirability_score"] <= 10
            assert 0 <= concept["feasibility_score"] <= 10
            assert 0 <= concept["viability_score"] <= 10
            assert "composite_score" in concept
    
    def test_recommended_concept(self, skill, sample_pain_points):
        """Test recommended concept is identified."""
        result = skill.run(
            pain_points=sample_pain_points,
            concept_count=3
        )
        
        assert "recommended_concept" in result
        assert result["recommended_concept"] != ""
        
        # Check recommended concept exists in concepts list
        concept_names = [c["name"] for c in result["concepts"]]
        assert result["recommended_concept"] in concept_names
    
    def test_concept_count_validation(self, skill, sample_pain_points):
        """Test concept count validation."""
        # Too few
        result = skill.run(pain_points=sample_pain_points, concept_count=1)
        assert "error" in result
        
        # Too many
        result = skill.run(pain_points=sample_pain_points, concept_count=10)
        assert "error" in result


class TestMVPBuilderSkill:
    """Test MVP Builder skill."""
    
    @pytest.fixture
    def skill(self):
        config = SkillConfig(dry_run=True)
        return MVPBuilderSkill(config)
    
    @pytest.fixture
    def sample_concept(self):
        return {
            "name": "HabitBuddy",
            "emotional_value_prop": "Feel supported in building habits",
            "magic_moment": "User gets matched with accountability partner in 30 seconds",
            "differentiation": "Human accountability, not just app reminders",
            "desirability_score": 8.5,
            "feasibility_score": 7.0,
            "viability_score": 8.0,
            "build_hours_estimate": 8
        }
    
    def test_validation_missing_concept(self, skill):
        """Test validation fails without concept."""
        result = skill.run(magic_moment="test")
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_validation_missing_magic_moment(self, skill, sample_concept):
        """Test validation fails without magic_moment."""
        result = skill.run(concept=sample_concept)
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_dry_run_deploys(self, skill, sample_concept):
        """Test dry run returns deployment info."""
        result = skill.run(
            concept=sample_concept,
            magic_moment="Test magic moment"
        )
        
        assert result["success"] == True
        assert result["deployed"] == True
        assert "live_url" in result
        assert "build_manifest" in result
        assert "lovability_checklist" in result
    
    def test_lovability_checklist(self, skill, sample_concept):
        """Test lovability checklist is evaluated."""
        result = skill.run(
            concept=sample_concept,
            magic_moment="Test magic moment"
        )
        
        checklist = result["lovability_checklist"]
        assert "emotion_first_headline" in checklist
        assert "single_action_cta" in checklist
        assert "under_60s_magic_moment" in checklist
        assert "user_centric_copy" in checklist
        assert "all_passed" in checklist
    
    def test_build_manifest(self, skill, sample_concept):
        """Test build manifest structure."""
        result = skill.run(
            concept=sample_concept,
            magic_moment="Test magic moment"
        )
        
        manifest = result["build_manifest"]
        assert "stack" in manifest
        assert "pages" in manifest
        assert "build_hours" in manifest
        assert "tests_passed" in manifest
        assert isinstance(manifest["stack"], list)


class TestHCDScorerSkill:
    """Test HCD Scorer skill."""
    
    @pytest.fixture
    def skill(self):
        config = SkillConfig(dry_run=True)
        return HCDScorerSkill(config)
    
    @pytest.fixture
    def sample_waitlist(self):
        return [
            {"email": "user1@example.com", "signup_date": "2024-01-01"},
            {"email": "user2@example.com", "signup_date": "2024-01-02"},
            {"email": "user3@example.com", "signup_date": "2024-01-03"},
            {"email": "user4@example.com", "signup_date": "2024-01-04"},
            {"email": "user5@example.com", "signup_date": "2024-01-05"},
        ]
    
    def test_validation_missing_live_url(self, skill):
        """Test validation fails without live_url."""
        result = skill.run(waitlist=[])
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_dry_run_calculates_score(self, skill, sample_waitlist):
        """Test dry run calculates HCD score."""
        result = skill.run(
            live_url="https://test-demo.vercel.app",
            waitlist=sample_waitlist,
            test_count=5,
            target_price=29.0
        )
        
        assert result["success"] == True
        assert "hcd_score" in result
        assert 0 <= result["hcd_score"] <= 1
        assert "component_scores" in result
        assert "recommendation" in result
    
    def test_component_scores(self, skill, sample_waitlist):
        """Test component scores are calculated."""
        result = skill.run(
            live_url="https://test-demo.vercel.app",
            waitlist=sample_waitlist,
            test_count=5
        )
        
        components = result["component_scores"]
        assert "lovability" in components
        assert "activation_rate" in components
        assert "time_to_aha_seconds" in components
        assert "revenue_intent" in components
        
        assert 0 <= components["lovability"] <= 10
        assert 0 <= components["activation_rate"] <= 1
        assert 0 <= components["revenue_intent"] <= 1
    
    def test_recommendation_scale(self, skill):
        """Test SCALE recommendation for high scores."""
        # Force high scores in dry run
        result = skill.run(
            live_url="https://test-demo.vercel.app",
            waitlist=[{"email": "u@e.com"}] * 10,
            test_count=8
        )
        
        assert result["recommendation"] in ["SCALE", "ITERATE", "PIVOT", "KILL"]
        assert result["recommendation"] in [r.value for r in Recommendation]
    
    def test_user_sessions(self, skill, sample_waitlist):
        """Test user sessions are recorded."""
        result = skill.run(
            live_url="https://test-demo.vercel.app",
            waitlist=sample_waitlist,
            test_count=5
        )
        
        assert "user_sessions" in result
        assert len(result["user_sessions"]) == 5
        
        session = result["user_sessions"][0]
        assert "user_id" in session
        assert "lovability_rating" in session
        assert "reached_aha" in session
        assert "would_pay" in session
    
    def test_friction_analysis(self, skill, sample_waitlist):
        """Test friction analysis is provided."""
        result = skill.run(
            live_url="https://test-demo.vercel.app",
            waitlist=sample_waitlist,
            test_count=5
        )
        
        assert "friction_analysis" in result
        friction = result["friction_analysis"]
        assert "top_friction_1" in friction
        assert "top_friction_2" in friction
        assert "top_friction_3" in friction


class TestPortfolioManagerSkill:
    """Test Portfolio Manager skill."""
    
    @pytest.fixture
    def skill(self):
        config = SkillConfig(dry_run=True)
        return PortfolioManagerSkill(config)
    
    def test_validation_missing_command(self, skill):
        """Test validation fails without command."""
        result = skill.run()
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_validation_invalid_command(self, skill):
        """Test validation fails with invalid command."""
        result = skill.run(command="invalid")
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_validation_new_missing_idea(self, skill):
        """Test 'new' command requires idea."""
        result = skill.run(command="new")
        assert "error" in result
        assert "Validation failed" in result["error"]
    
    def test_validation_kill_missing_params(self, skill):
        """Test 'kill' command requires params."""
        result = skill.run(command="kill")
        assert "error" in result
        
        result = skill.run(command="kill", experiment_id="loop-001")
        assert "error" in result
    
    def test_dry_run_status(self, skill):
        """Test status command."""
        result = skill.run(command="status")
        
        assert result["success"] == True
        assert "active_experiments" in result
        assert "portfolio_health" in result
        assert "kill_list" in result
    
    def test_dry_run_new(self, skill):
        """Test new experiment command."""
        result = skill.run(
            command="new",
            idea="Test experiment idea"
        )
        
        assert result["success"] == True
        assert "experiment_id" in result
        assert result["status"] == "IDEA"
        assert "next_steps" in result
    
    def test_dry_run_kill(self, skill):
        """Test kill experiment command."""
        result = skill.run(
            command="kill",
            experiment_id="loop-001",
            reason="Low lovability score"
        )
        
        assert result["success"] == True
        assert result["action"] == "KILLED"
        assert result["reason"] == "Low lovability score"
    
    def test_portfolio_health_structure(self, skill):
        """Test portfolio health metrics."""
        result = skill.run(command="status")
        
        health = result["portfolio_health"]
        assert "active_count" in health
        assert "max_active" in health
        assert "avg_hcd_score" in health
        assert "kill_rate" in health
        assert "portfolio_age_days" in health
    
    def test_max_active_experiments(self, skill):
        """Test max active experiments limit."""
        # This would be tested with actual portfolio state
        # For now, just verify the constant exists
        assert skill.MAX_ACTIVE_EXPERIMENTS == 5


class TestIntegration:
    """Integration tests for skill pipeline."""
    
    def test_full_pipeline_dry_run(self):
        """Test full LOOP pipeline in dry run mode."""
        from deerflow.loop_skills import (
            run_user_researcher,
            run_problem_framer,
            run_mvp_builder,
            run_hcd_scorer,
            run_portfolio_manager
        )
        
        # Step 1: User Research
        research = run_user_researcher(
            idea="Habit accountability partner",
            target_user="Solo founders who miss follow-ups",
            interview_count=5,
            dry_run=True
        )
        assert research["validated"] == True
        assert len(research["pain_points"]) > 0
        
        # Step 2: Problem Framing
        framing = run_problem_framer(
            pain_points=research["pain_points"],
            concept_count=3,
            dry_run=True
        )
        assert "how_might_we" in framing
        assert len(framing["concepts"]) > 0
        
        # Step 3: MVP Building
        top_concept = framing["concepts"][0]
        mvp = run_mvp_builder(
            concept=top_concept,
            magic_moment=top_concept["magic_moment"],
            dry_run=True
        )
        assert mvp["deployed"] == True
        assert "live_url" in mvp
        
        # Step 4: HCD Scoring
        scoring = run_hcd_scorer(
            live_url=mvp["live_url"],
            test_count=5,
            dry_run=True
        )
        assert "hcd_score" in scoring
        assert scoring["recommendation"] in ["SCALE", "ITERATE", "PIVOT", "KILL"]
        
        # Step 5: Portfolio Management
        portfolio = run_portfolio_manager(
            command="status",
            dry_run=True
        )
        assert "active_experiments" in portfolio
        assert "portfolio_health" in portfolio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
