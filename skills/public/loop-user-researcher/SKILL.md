---
name: loop-user-researcher
description: Conduct JTBD (Jobs-to-be-Done) user research for LOOP experiments. Recruits target users from relevant communities, runs async interviews, synthesizes pain points into ranked matrix. Use when starting a new LOOP experiment and you need validated pain points before building. Always run before Problem Framer.
trigger: user research, JTBD interviews, pain point validation, customer discovery, loop experiment research
---

# LOOP User Researcher

Conducts authentic JTBD research to validate pain points before building. Not synthetic — actually recruits and interviews real users.

## Goal
Transform raw idea into validated, ranked pain points with evidence from real users.

## Input
- **IDEA**: One-sentence description of the concept
- **TARGET_USER**: Specific user segment (not "busy professionals" — "solo founders who miss follow-ups")
- **RECRUITMENT_CHANNELS**: Where to find these users (Reddit communities, LinkedIn groups, Twitter, etc.)
- **INTERVIEW_COUNT**: Number of interviews to conduct (default: 5)

## Output Format
```json
{
  "validated": true/false,
  "pain_points": [
    {
      "rank": 1,
      "pain": "Specific pain description",
      "frequency": "How often this occurs",
      "current_workaround": "What they do now",
      "willingness_to_pay": "Signals of payment intent",
      "verbatim_quotes": ["Quote 1", "Quote 2"],
      "user_sources": ["reddit/r/xyz", "linkedin/group"]
    }
  ],
  "target_user_profile": "Refined user description based on interviews",
  "research_method": "JTBD async interviews via [channels]",
  "confidence_level": "High/Medium/Low based on response quality"
}
```

## Process

### 1. Recruitment
- Search specified channels for users matching TARGET_USER profile
- Send personalized outreach (not spam)
- Aim for INTERVIEW_COUNT completed interviews
- Offer incentive if needed (early access, recognition, small gift card)

### 2. JTBD Interview Protocol
Ask these questions asynchronously:

**Opening:**
- "Tell me about the last time you experienced [problem area]"
- "What were you trying to accomplish?"

**Frustration Mapping:**
- "What made that difficult?"
- "How did that make you feel?"
- "What did you try first?"

**Current Workarounds:**
- "How do you handle this now?"
- "What tools or processes do you use?"
- "What's the biggest pain point with your current solution?"

**Willingness to Pay:**
- "If this problem was magically solved, what would that be worth to you?"
- "Have you paid for solutions to this before?"
- "What would make you switch?"

### 3. Synthesis
- Group similar pains
- Rank by: severity × frequency × willingness to pay
- Extract verbatim quotes for authenticity
- Calculate confidence level

## Success Criteria
- ✅ At least 3 completed interviews
- ✅ Clear ranking of pain points
- ✅ Evidence of willingness to pay
- ✅ Verbatim quotes for Problem Framer

## Failure Modes
- ❌ Cannot find target users → Expand channels or refine target
- ❌ No willingness to pay → Kill experiment early
- ❌ Pain points too vague → Run follow-up interviews

## Integration
This skill feeds directly into **loop-problem-framer**. Do not proceed to framing without validated pain points.
