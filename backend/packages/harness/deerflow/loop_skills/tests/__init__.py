# LOOP Skills Tests

This directory contains comprehensive unit tests for all 5 LOOP DeerFlow skills.

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific skill tests
python -m pytest tests/test_loop_skills.py::TestUserResearcherSkill -v
python -m pytest tests/test_loop_skills.py::TestProblemFramerSkill -v
python -m pytest tests/test_loop_skills.py::TestMVPBuilderSkill -v
python -m pytest tests/test_loop_skills.py::TestHCDScorerSkill -v
python -m pytest tests/test_loop_skills.py::TestPortfolioManagerSkill -v

# Run integration tests
python -m pytest tests/test_loop_skills.py::TestIntegration -v

# Run with coverage
python -m pytest tests/ --cov=deerflow.loop_skills --cov-report=html
```

## Test Coverage

- **SkillConfig**: Environment loading, default values
- **UserResearcherSkill**: Validation, dry run, pain point ranking
- **ProblemFramerSkill**: HMW generation, concept scoring, validation
- **MVPBuilderSkill**: Deployment, lovability checklist, build manifest
- **HCDScorerSkill**: Score calculation, recommendations, user sessions
- **PortfolioManagerSkill**: Commands, experiment lifecycle, portfolio health
- **Integration**: Full LOOP pipeline test
