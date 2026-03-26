# LOOP program.md
## Human-Centered Autonomous Build System
### Anand's Personal Experimentation Layer

---

## 1. The Core Philosophy

**We don't build demos. We build lovable products.**

The goal of LOOP is not to prove technical feasibility. It is to validate that real humans feel real pain, and that our solution genuinely improves their lives.

**North Star:** Wake up to a deployed product that solved a real user pain — not just a working demo that proves a technical point.

---

## 2. The LOOP Commitment

### 2.1 Lovability Over Everything

If users don't love it, we kill it — regardless of revenue potential.

**Kill Conditions (Automatic):**
- Lovability score < 6.0/10
- Time to magic moment > 120 seconds
- No willingness to pay signals in research

**Why:** A product that makes money but users hate is a liability, not an asset.

### 2.2 Ruthless Experimentation

We run few experiments, but we run them right:

- **Max 5 active experiments simultaneously**
- **Each experiment gets 2+ weeks to prove itself**
- **Kill rate should be 30-50%** (shows we're being honest)
- **Scale only what users genuinely love**

### 2.3 Real Humans, Real Pain

No synthetic validation. Every experiment must:
- Interview real users before building
- Test with real users after deploying
- Measure real reactions, not vanity metrics

---

## 3. HCD Score Formula

```
hcd_score = (lovability × 0.40) + (activation_rate × 0.35) + (revenue_intent × 0.25)

Kill threshold: hcd_score < 0.50 OR lovability < 6.0
```

**Weighting Philosophy:**
- **Lovability 40%**: If users don't love it, nothing else matters
- **Activation 35%**: They must actually use it, not just say they like it
- **Revenue 25%**: Monetizable, but not at the expense of the above

---

## 4. The Magic Moment Rule

**Every MVP must have a defined magic moment.**

The magic moment is the exact interaction where a user goes from "interesting" to "I need this."

**Requirements:**
- Must be demonstrable in < 60 seconds
- Must be experienced in the interactive demo
- Must solve the core pain point identified in research

**Rule:** If a user cannot reach the magic moment in under 60 seconds, do not build. Reframe the concept first.

---

## 5. Lovability Checklist

Every MVP must pass this before it's considered valid:

| Dimension | Bad (Functional) | Good (Lovable) |
|-----------|------------------|----------------|
| **Headline** | "Sign up for our AI tool" | "Never write another follow-up email again" |
| **Onboarding** | Form with 5 required fields | Single button: "Get started in 10 seconds" |
| **Value Prop** | Feature list with checkmarks | Story of transformation: before → after |
| **Landing Page** | Generic hero + CTA | Personalized to user's specific named pain |
| **Demo** | "Contact sales to see a demo" | Interactive preview showing their exact use case |
| **Copy Voice** | Passive, product-centric | Active, user-centric — "you will..." not "our tool..." |

---

## 6. Style Constraints

### 6.1 Design Voice
- Warm editorial, not corporate
- Cream/ivory tones preferred
- Transformation copy, not feature lists
- Specific stories, not generic claims

### 6.2 Copy Principles
- **Lead with emotion**: "Feel organized" not "Task management"
- **Specificity wins**: "Never miss a follow-up" not "Stay productive"
- **Active voice**: "You'll save 5 hours/week" not "Time savings of 5 hours"
- **User-centric**: Every sentence starts with "you" or implied you

### 6.3 What to Avoid
- ❌ Corporate jargon ("synergy", "leverage", "optimize")
- ❌ Feature dumps ("AI-powered", "machine learning", "cloud-based")
- ❌ Generic promises ("better", "faster", "easier")
- ❌ Stock photos of smiling people
- ❌ Form fields before value demonstration

---

## 7. Experiment Budgets

**Per Experiment:**
- Max build time: 8 hours (agent time)
- Max API spend: $15
- Max active experiments: 5
- Min experiment duration: 2 weeks before scoring

**Portfolio Level:**
- Max new experiments per month: 4
- Target kill rate: 30-50%
- Min scaled experiments to maintain: 1 (keep building winners)

---

## 8. Decision Matrix

| Result | Condition | Action |
|--------|-----------|--------|
| **SCALE** | hcd_score > 0.75 AND lovability > 8.0 | Continue building. Add resources. Begin marketing loop. |
| **ITERATE** | hcd_score > 0.50 AND friction_points exist | Fix top friction. Return to BUILD. Respawn scorer in 1 week. |
| **PIVOT** | hcd_score < 0.50 AND lovability > 6.0 | Wrong solution. Keep the pain. Reframe with Problem Framer. |
| **KILL** | lovability < 6.0 (regardless of revenue) | Git revert. Log learnings. Add to kill list. Move on. |
| **KILL** | time_to_aha > 120 seconds | Demo clarity failure. Kill regardless of other scores. |

---

## 9. Current Active Idea Seeds

*Add your raw ideas here. LOOP will expand them into experiments.*

1. **Habit accountability partner** — Find someone with same habit goal, hold each other accountable
2. **Voice-first podcast creation** — Talk about your day, auto-generate podcast episode
3. **Decision journal** — Track decisions, outcomes, learn from patterns
4. **[Add more as they come...]**

---

## 10. Success Metrics for LOOP Itself

**System Health:**
- Experiments per month: Target 2-4
- Kill rate: Target 30-50%
- Avg HCD score of scaled experiments: Target > 0.75
- Time idea → deployed MVP: Target < 3 weeks
- Cost per experiment: Target < $5
- Manual work per experiment: Target < 20 minutes (just write idea)

**Business Outcomes:**
- Number of scaled products generating revenue: Target 1+ within 6 months
- Portfolio ROI (revenue / spend): Target 3x+
- User satisfaction of scaled products: Target NPS > 50

---

## 11. Remember

**The complexity lives in program.md, not the infrastructure.**

DeerFlow handles the runtime. You handle judgment — encoded once in this file, executed repeatedly by the system.

**Every principle here is executable.**

If it's not in program.md, it's not part of LOOP's philosophy.

---

**Version:** 1.0  
**Owner:** Anand  
**Last Updated:** March 26, 2026  
**Status:** Active Constitution
