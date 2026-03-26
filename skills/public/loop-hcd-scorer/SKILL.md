---
name: loop-hcd-scorer
description: Measure HCD (Human-Centered Design) score for deployed LOOP experiments. Recruits real users for screenshare sessions, measures lovability, activation, and revenue intent. Calculates composite HCD score and makes SCALE/ITERATE/PIVOT/KILL recommendation. Use 2 weeks after MVP deployment to assess traction.
trigger: hcd scoring, user testing, lovability score, experiment evaluation, loop experiment assessment, track kpi, measure traction
---

# LOOP HCD Scorer

Measures the actual HCD composite score with real users. Not synthetic — real screenshare sessions, real reactions.

## Goal
Calculate HCD score and make clear recommendation: SCALE / ITERATE / PIVOT / KILL.

## Input
- **LIVE_URL**: Deployed MVP from Builder
- **WAITLIST**: Users who signed up
- **TARGET_USERS**: Who to recruit for testing
- **TEST_COUNT**: Number of user sessions (default: 5)
- **TARGET_PRICE**: Price point to test willingness to pay

## Output Format
```json
{
  "hcd_score": 0.72,
  "component_scores": {
    "lovability": 7.8,
    "activation_rate": 0.85,
    "time_to_aha_seconds": 45,
    "revenue_intent": 0.60
  },
  "recommendation": "SCALE | ITERATE | PIVOT | KILL",
  "user_sessions": [
    {
      "user_id": "anon_1",
      "lovability_rating": 8,
      "reached_aha": true,
      "time_to_aha": 42,
      "would_pay": true,
      "friction_points": ["Confused by X", "Loved Y"],
      "verbatim": "Exact user quote"
    }
  ],
  "friction_analysis": {
    "top_friction_1": "Most common issue",
    "top_friction_2": "Second issue",
    "top_friction_3": "Third issue"
  },
  "confidence": "High | Medium | Low"
}
```

## Process

### 1. Recruitment (from waitlist + cold outreach)
- Prioritize: Actual waitlist signups (highest intent)
- Backup: Cold outreach matching target user profile
- Goal: TEST_COUNT completed 15-minute sessions

### 2. Screenshare Session Protocol (15 min)

**Setup (2 min):**
- "I'm testing a new product. Please think aloud as you use it."
- "There are no wrong answers — your honest reaction helps us."

**Landing Page Reaction (3 min):**
- "What's your first impression? What do you think this does?"
- "Does this speak to a problem you have?"

**Demo Walkthrough (5 min):**
- "Try it. Talk through what you're thinking."
- Measure: Time to reach magic moment
- Note: Where do they hesitate? Where do they smile?

**Lovability Rating (2 min):**
- "On a scale of 0-10, how much would you want this in your life?"
- "What would make it a 10?"

**Revenue Test (2 min):**
- "If this cost $[TARGET_PRICE]/month, would you pay?"
- "What would make it worth that to you?"

**Closing (1 min):**
- "What one thing would you change?"
- "Who else should see this?"

### 3. Scoring Calculation

**Lovability (0-10):**
- Average of user ratings
- Weight: 40% of HCD score
- Kill threshold: < 6.0 (always kill regardless of revenue)

**Activation Rate (0-1):**
- % of users who reached magic moment
- Weight: 35% of HCD score

**Revenue Intent (0-1):**
- % who said yes to target price
- Weight: 25% of HCD score

**Time to Aha (secondary):**
- Median seconds to magic moment
- Not in composite, but tracked
- Kill if > 120 seconds (demo clarity failure)

**HCD Formula:**
```
hcd_score = (lovability/10 × 0.40) + (activation × 0.35) + (revenue × 0.25)
```

### 4. Recommendation Matrix

| HCD Score | Lovability | Action |
|-----------|------------|--------|
| > 0.75 | > 8.0 | **SCALE** — Advance branch, begin marketing |
| > 0.50 | > 6.0 | **ITERATE** — Fix top friction, respawn scorer |
| < 0.50 | > 6.0 | **PIVOT** — Wrong solution, keep the pain |
| Any | < 6.0 | **KILL** — Users don't love it, period |
| Any | Any (time > 120s) | **KILL** — Demo clarity failure |

### 5. Results Ledger

Append to `results.tsv`:
```
experiment_id, hcd_score, lovability, activation, revenue_intent, time_to_aha, decision, friction_1, friction_2, friction_3
```

## Success Criteria
- ✅ TEST_COUNT completed sessions
- ✅ Clear HCD score calculated
- ✅ Recommendation made
- ✅ Friction points documented

## Failure Modes
- ❌ Can't recruit users → Lower standards, offer incentives
- ❌ Users don't show → Over-recruit by 2x
- ❌ Conflicting feedback → Run more sessions

## Integration
Results feed into **loop-portfolio-manager** for experiment lifecycle tracking.
