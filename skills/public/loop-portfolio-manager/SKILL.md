---
name: loop-portfolio-manager
description: Portfolio management system for LOOP experiments. Tracks experiment lifecycle over weeks (not overnight), manages active experiments, kills poor performers after 2 weeks, scales winners. Central dashboard for all LOOP activity. Use daily to check experiment status, weekly to review portfolio, and every 2 weeks to score and make SCALE/ITERATE/PIVOT/KILL decisions.
trigger: portfolio management, experiment tracking, loop dashboard, active experiments, kill list, scale winners, loop portfolio
---

# LOOP Portfolio Manager

Manages a portfolio of experiments over weeks — not overnight spam. Ruthlessly kills losers, doubles down on winners.

## Philosophy

**NOT autoresearch overnight batch.**
**YES portfolio management over time.**

- Run 3-5 experiments simultaneously max
- Each experiment lives for 2+ weeks
- Check metrics daily
- Make decisions every 2 weeks
- Kill ruthlessly, scale aggressively

## Experiment Lifecycle

```
IDEA → RESEARCH → BUILD → ACTIVE (2+ weeks) → SCORE → DECISION
                                            ↓
                              ┌─────────────┼─────────────┐
                              ↓             ↓             ↓
                           SCALE        ITERATE         KILL
                              ↓             ↓             ↓
                         Continue      Return to      Add to
                         building      BUILD with     kill list
                                       fixes
```

## Input
- **COMMAND**: What to do
  - `status` — Show all experiments and current status
  - `review` — Weekly portfolio review
  - `score` — Run HCD scorer for active experiments
  - `new` — Start new experiment from idea
  - `kill` — Kill experiment manually

## Output Format

### Status View
```json
{
  "active_experiments": [
    {
      "id": "loop-001",
      "name": "HabitBuddy",
      "status": "ACTIVE",
      "days_running": 12,
      "live_url": "https://...",
      "next_action": "HCD Score in 2 days",
      "early_signals": "High waitlist conversion"
    }
  ],
  "iteration_queue": [
    {
      "id": "loop-002",
      "name": "FocusFlow",
      "status": "ITERATING",
      "fix_needed": "Demo clarity",
      "return_to_build": true
    }
  ],
  "kill_list": [
    {
      "id": "loop-003",
      "name": "TaskMaster",
      "killed_date": "2024-03-15",
      "reason": "Lovability 4.2 < 6.0 threshold",
      "learnings": "Users don't want another task app"
    }
  ],
  "scaled_experiments": [
    {
      "id": "loop-000",
      "name": "Synapse Daily",
      "status": "SCALED",
      "hcd_score": 0.82,
      "current_focus": "Marketing automation"
    }
  ],
  "portfolio_health": {
    "active_count": 3,
    "max_active": 5,
    "avg_hcd_score": 0.68,
    "kill_rate": 0.33,
    "portfolio_age_days": 45
  }
}
```

## Process

### Daily (Automated)
- Check waitlist signups for all ACTIVE experiments
- Track conversion rates
- Alert if any experiment crashes or breaks
- Update metrics dashboard

### Weekly (Manual Review)
- Review all ACTIVE experiments
- Check early signals (waitlist growth, engagement)
- Flag experiments needing attention
- Plan upcoming HCD scoring sessions

### Every 2 Weeks (Scoring & Decisions)
For each ACTIVE experiment:
1. Run **loop-hcd-scorer**
2. Calculate HCD composite
3. Make decision:
   - **SCALE** (score > 0.75, lovability > 8) → Continue building, add resources
   - **ITERATE** (score > 0.50, friction exists) → Fix top issue, rebuild
   - **PIVOT** (score < 0.50, lovability > 6) → Wrong solution, reframe problem
   - **KILL** (lovability < 6 OR time_to_aha > 120s) → Add to kill list, stop work

### New Experiment Flow
1. Add idea to backlog
2. When slot opens (active < max_active), start:
   - Run **loop-user-researcher**
   - Run **loop-problem-framer**
   - Run **loop-mvp-builder**
   - Set status to ACTIVE
   - Schedule 2-week scoring

## Portfolio Constraints

**Hard Limits:**
- Max 5 ACTIVE experiments simultaneously
- Min 2 weeks in ACTIVE before scoring
- Kill immediately if lovability < 6.0
- Kill immediately if time_to_aha > 120s

**Resource Allocation:**
- SCALED experiments: 60% of attention
- ACTIVE experiments: 30% of attention  
- ITERATING experiments: 10% of attention
- KILLED experiments: 0% (learn and move on)

## The Kill List

**Why maintain it:**
- Prevent zombie ideas from coming back
- Document learnings
- Track kill rate (healthy portfolios have 30-50% kill rate)

**Kill List Entry:**
```json
{
  "experiment_id": "loop-003",
  "name": "TaskMaster",
  "idea": "AI task prioritization",
  "killed_date": "2024-03-15",
  "days_survived": 14,
  "hcd_score": 0.42,
  "lovability": 4.2,
  "kill_reason": "Lovability below threshold",
  "key_learning": "Users don't want AI to prioritize — they want control",
  "artifacts": {
    "repo": "https://github.com/...",
    "research": "link-to-notion"
  }
}
```

## Success Metrics (Portfolio Level)

**Track over time:**
- Experiments launched per month: Target 2-4
- Kill rate: Target 30-50% (shows ruthlessness)
- Avg HCD score of scaled experiments: Target > 0.75
- Time from idea to first HCD score: Target < 3 weeks
- Portfolio ROI (revenue from scaled / total spent): Target > 3x

## Integration

**Notion Sync:**
- Each experiment has Notion page
- Portfolio Manager updates status
- Kill list maintained in Notion database

**Git Management:**
- Each experiment is a git branch
- SCALE → merge to main
- ITERATE → reset branch, rebuild
- KILL → archive branch

## Dashboard Commands

```bash
# Daily check
python -m loop portfolio status

# Weekly review  
python -m loop portfolio review

# Score experiments (run every 2 weeks)
python -m loop portfolio score

# Start new experiment
python -m loop portfolio new "Your idea here"

# Manual kill
python -m loop portfolio kill loop-003 "Reason for killing"
```
