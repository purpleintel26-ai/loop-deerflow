---
name: loop-problem-framer
description: Transform validated pain points into "How might we..." problem statements and ranked solution concepts. Use after User Researcher completes pain point validation. Feeds concepts to MVP Builder for implementation.
trigger: problem framing, solution concepts, how might we, HMW statements, idea generation, loop experiment framing
---

# LOOP Problem Framer

Transforms validated pain points into actionable problem statements and solution concepts with emotional value props.

## Goal
Generate 3-5 distinct solution concepts, ranked by desirability × feasibility × viability.

## Input
- **PAIN_POINTS**: Output from User Researcher (ranked pain matrix)
- **PROGRAM_MD**: Reference to HCD constraints and style guidelines
- **CONCEPT_COUNT**: Number of concepts to generate (default: 3)

## Output Format
```json
{
  "how_might_we": "HMW statement capturing the core problem",
  "concepts": [
    {
      "rank": 1,
      "name": "Concept name",
      "emotional_value_prop": "How it makes users feel (not what it does)",
      "magic_moment": "The 60-second aha moment users experience",
      "differentiation": "Why this vs status quo",
      "desirability_score": 0-10,
      "feasibility_score": 0-10,
      "viability_score": 0-10,
      "build_hours_estimate": "Estimated hours to MVP",
      "target_users": "Specific user segment for this concept"
    }
  ],
  "recommended_concept": "Name of top-ranked concept",
  "framing_confidence": "High/Medium/Low"
}
```

## Process

### 1. "How Might We" Statement
Transform top pain point into HMW format:
- NOT: "Build a todo app"
- YES: "How might we help solo founders never miss a follow-up without adding cognitive load?"

### 2. Concept Generation
Generate CONCEPT_COUNT distinct approaches:

**Concept A: Direct Solution**
- Obvious approach to the pain
- Pro: Fast to build, clear value
- Con: May be crowded market

**Concept B: Adjacent Solution**  
- Solve the pain indirectly through a different mechanism
- Pro: Differentiated positioning
- Con: Harder to explain

**Concept C: Emotion-First Solution**
- Lead with emotional transformation, not features
- Pro: Stronger lovability potential
- Con: Harder to validate technically

### 3. Scoring Rubric

**Desirability (0-10):**
- 8-10: Users explicitly said "I need this" during research
- 5-7: Users acknowledged pain but didn't express urgency
- 0-4: No clear user pull

**Feasibility (0-10):**
- 8-10: Can build in < 8 hours with existing tools
- 5-7: Requires custom development, < 40 hours
- 0-4: Requires complex infrastructure

**Viability (0-10):**
- 8-10: Clear path to revenue, users expressed willingness to pay
- 5-7: Monetizable but unclear pricing
- 0-4: No clear business model

### 4. Magic Moment Definition
For top concept, define:
- **The exact interaction** where user goes "I need this"
- **Time to aha**: Must be < 60 seconds in demo
- **Demonstrability**: Can be shown in interactive preview

If magic moment cannot be demonstrated in 60 seconds, reject concept and reframe.

## Success Criteria
- ✅ Clear HMW statement
- ✅ 3+ distinct concepts
- ✅ Top concept has identifiable magic moment
- ✅ All scores > 5 for recommended concept

## Failure Modes
- ❌ No concept scores > 5 on desirability → Back to User Research
- ❌ No magic moment < 60s → Reframe concepts
- ❌ All concepts similar → Force differentiation

## Integration
Feeds top concept to **loop-mvp-builder**. Include magic moment spec in handoff.
