# LOOP Skills - Implementation Summary

## Overview

Complete implementation of 5 LOOP DeerFlow skills for autonomous experimentation:

1. **User Researcher** - JTBD research and pain point validation
2. **Problem Framer** - Solution concept generation and scoring
3. **MVP Builder** - Full-stack MVP deployment with E2B
4. **HCD Scorer** - Human-centered design scoring and recommendations
5. **Portfolio Manager** - Experiment lifecycle management

## File Structure

```
loop-deerflow/backend/packages/harness/deerflow/loop_skills/
├── __init__.py              # Public API exports
├── base.py                  # Base classes, validators, Notion/E2B clients
├── user_researcher.py       # User Researcher skill implementation
├── problem_framer.py        # Problem Framer skill implementation
├── mvp_builder.py          # MVP Builder skill implementation
├── hcd_scorer.py           # HCD Scorer skill implementation
├── portfolio_manager.py    # Portfolio Manager skill implementation
└── tests/
    ├── __init__.py
    └── test_loop_skills.py  # Comprehensive unit tests
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install notion-client e2b

# Set environment variables
export LOOP_DRY_RUN=true  # Set to false for production
export NOTION_API_KEY="your-key"
export NOTION_DATABASE_ID="your-db-id"
export E2B_API_KEY="your-e2b-key"
export VERCEL_TOKEN="your-vercel-token"
```

### Usage

```python
from deerflow.loop_skills import (
    run_user_researcher,
    run_problem_framer,
    run_mvp_builder,
    run_hcd_scorer,
    run_portfolio_manager
)

# 1. Research
research = run_user_researcher(
    idea="Habit accountability partner",
    target_user="Solo founders who miss follow-ups",
    interview_count=5,
    dry_run=True
)

# 2. Frame
framing = run_problem_framer(
    pain_points=research["pain_points"],
    concept_count=3,
    dry_run=True
)

# 3. Build
mvp = run_mvp_builder(
    concept=framing["concepts"][0],
    magic_moment=framing["concepts"][0]["magic_moment"],
    dry_run=True
)

# 4. Score
scoring = run_hcd_scorer(
    live_url=mvp["live_url"],
    test_count=5,
    dry_run=True
)

# 5. Manage
portfolio = run_portfolio_manager(
    command="status",
    dry_run=True
)
```

## Features

### User Researcher
- JTBD interview protocol simulation
- Pain point ranking by severity × frequency
- Verbatim quote collection
- Confidence level calculation
- Notion sync for research results

### Problem Framer
- "How Might We" statement generation
- Multiple concept generation (Direct, AI, Community, Integration, Mobile)
- Desirability × Feasibility × Viability scoring
- Magic moment validation (60-second rule)
- Composite score calculation with LOOP weights

### MVP Builder
- Next.js 14 + Tailwind CSS + Supabase stack
- E2B sandbox code execution
- Emotion-first landing pages
- Interactive demo components
- Waitlist with micro-interactions
- Lovability checklist validation
- Vercel deployment integration

### HCD Scorer
- Screenshare session simulation
- Lovability rating (0-10 scale)
- Activation rate measurement
- Revenue intent testing
- HCD composite score: `(lovability×0.40) + (activation×0.35) + (revenue×0.25)`
- SCALE/ITERATE/PIVOT/KILL recommendations
- Friction point analysis

### Portfolio Manager
- Experiment lifecycle tracking (IDEA → RESEARCH → BUILD → ACTIVE → SCORE → DECISION)
- Max 5 active experiments enforcement
- 2-week minimum before scoring
- Kill list maintenance
- Portfolio health metrics
- Commands: status, review, score, new, kill

## Dry Run Mode

All skills support `--dry-run` mode for testing without external API calls:

```python
from deerflow.loop_skills import SkillConfig

config = SkillConfig(dry_run=True)
skill = UserResearcherSkill(config)
result = skill.run(idea="test", target_user="users")
```

## Error Handling

Custom exceptions for different failure modes:
- `ValidationError` - Input/output validation failures
- `ExecutionError` - Skill execution failures
- `NotionSyncError` - Notion synchronization failures
- `E2BExecutionError` - E2B sandbox execution failures

## Integration Points

### Notion Sync
- Automatic page creation for each skill execution
- Property updates for status tracking
- Content logging as JSON

### E2B Integration
- Sandboxed code execution for MVP building
- Command execution for deployment scripts
- Timeout and error handling

### Vercel Deployment
- GitHub repo creation
- Auto-deployment pipeline
- Live URL generation

## HCD Scoring Formula

```
hcd_score = (lovability/10 × 0.40) + (activation × 0.35) + (revenue × 0.25)

Recommendations:
- SCALE: hcd_score ≥ 0.75 AND lovability ≥ 8.0
- ITERATE: hcd_score ≥ 0.50
- PIVOT: hcd_score < 0.50 AND lovability ≥ 6.0
- KILL: lovability < 6.0 OR time_to_aha > 120s
```

## Testing

```bash
# Run all tests
python -m pytest loop_skills/tests/ -v

# Run with coverage
python -m pytest loop_skills/tests/ --cov=deerflow.loop_skills

# Run integration tests
python -m pytest loop_skills/tests/test_loop_skills.py::TestIntegration -v
```

Test coverage includes:
- Input validation for all skills
- Dry run mode verification
- Error handling paths
- Integration pipeline
- Portfolio lifecycle management

## Configuration

Environment variables:
- `LOOP_DRY_RUN` - Enable dry run mode (default: false)
- `LOOP_LOG_LEVEL` - Logging level (default: INFO)
- `NOTION_API_KEY` - Notion integration API key
- `NOTION_DATABASE_ID` - Notion database for sync
- `E2B_API_KEY` - E2B sandbox API key
- `VERCEL_TOKEN` - Vercel deployment token
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key

## License

Part of LOOP DeerFlow - Human-Centered Autonomous Build System
