# LOOP Architecture & Verification Plan
## Verify Before Speak Protocol

---

## 1. What Does "Working LOOP" Mean?

### Success Definition:
LOOP is "working" when it can:
1. **Accept an idea** from program.md
2. **Run User Researcher** — Actually recruit and interview 3+ real users
3. **Run Problem Framer** — Generate ranked solution concepts
4. **Run MVP Builder** — Deploy working MVP to Vercel with magic moment
5. **Run HCD Scorer** — Test with 5 real users, calculate HCD score
6. **Run Portfolio Manager** — Track experiment, make SCALE/ITERATE/PIVOT/KILL decision
7. **Update Notion** — Sync all results to Projects database

**Proof Required:**
- Screenshot of deployed MVP
- Screenshot/transcript of real user interviews
- Screenshot of HCD score calculation
- Screenshot of Notion entry with status
- User confirmation: "Yes, this is a real deployed product"

---

## 2. Architecture Phases (Incremental)

### Phase 0: Foundation (Week 1)
**Goal:** DeerFlow 2.0 running locally with LOOP skills loaded

**Components:**
- Clone DeerFlow 2.0
- Configure backend (PostgreSQL, Redis)
- Load 5 LOOP skills into DeerFlow
- Test skill loading: `deerflow skill list` shows LOOP skills

**Verification:**
```bash
# DeerFlow backend running
curl http://localhost:8000/health
# Response: {"status": "ok"}

# Skills loaded
curl http://localhost:8000/skills | jq '.[] | select(.name | contains("loop"))'
# Response: Shows all 5 LOOP skills
```

---

### Phase 1: User Researcher (Week 2)
**Goal:** Actually recruit and interview real users

**Components:**
- Reddit/LinkedIn search automation
- Outreach message templates
- JTBD interview protocol
- Response collection system

**Verification:**
```bash
# Run skill
python -m deerflow.run_skill loop-user-researcher \
  --idea "Habit accountability partner" \
  --target "solo founders who struggle with habits"

# Verify: Actually sent 5+ outreach messages
# Verify: Got 3+ responses with interview answers
# Verify: Generated pain_points.json with ranking
```

**Proof Required:**
- Screenshots of sent outreach messages
- Interview response transcripts
- pain_points.json output

---

### Phase 2: Problem Framer (Week 2)
**Goal:** Generate actionable solution concepts

**Components:**
- Pain point synthesis
- HMW statement generation
- Concept generation (3-5 distinct approaches)
- Magic moment definition

**Verification:**
```bash
# Run skill
python -m deerflow.run_skill loop-problem-framer \
  --pain-points pain_points.json

# Verify: Generated 3+ distinct concepts
# Verify: Each has magic moment < 60s
# Verify: Top concept scores > 5 on all dimensions
```

**Proof Required:**
- concepts.json with scoring
- HMW statement
- Magic moment specification

---

### Phase 3: MVP Builder (Week 3)
**Goal:** Deploy real MVP to Vercel

**Components:**
- Next.js + Tailwind code generation
- Landing page with emotion-first copy
- Interactive demo with magic moment
- Vercel deployment automation

**Verification:**
```bash
# Run skill
python -m deerflow.run_skill loop-mvp-builder \
  --concept concept.json

# Verify: Build succeeds
# Verify: Deploys to Vercel
# Verify: Live URL accessible
# Verify: Magic moment works in < 60s
```

**Proof Required:**
- Screenshot of deployed landing page
- Screen recording of magic moment flow
- Vercel dashboard showing deployment

---

### Phase 4: HCD Scorer (Week 4)
**Goal:** Real user testing with calculated score

**Components:**
- User recruitment from waitlist
- Screenshare session protocol
- Lovability rating collection
- HCD composite calculation

**Verification:**
```bash
# Run skill 2 weeks after deployment
python -m deerflow.run_skill loop-hcd-scorer \
  --live-url https://habitbuddy-xyz.vercel.app \
  --test-count 5

# Verify: 5 user sessions completed
# Verify: HCD score calculated
# Verify: Recommendation made (SCALE/ITERATE/PIVOT/KILL)
```

**Proof Required:**
- Screenshots of user sessions
- hcd_score.json output
- results.tsv entry

---

### Phase 5: Portfolio Manager (Week 4)
**Goal:** Track multiple experiments over time

**Components:**
- Experiment lifecycle tracking
- Daily metrics collection
- 2-week scoring triggers
- Kill list maintenance

**Verification:**
```bash
# Run daily
python -m deerflow.run_skill loop-portfolio-manager --command status

# Verify: Shows all active experiments
# Verify: Shows days running
# Verify: Shows next action dates
```

**Proof Required:**
- Screenshot of portfolio dashboard
- Notion entries updated with statuses

---

## 3. Technical Architecture

### Stack:
- **Runtime:** DeerFlow 2.0 (LangGraph/LangChain)
- **Backend:** PostgreSQL (state), Redis (queue)
- **Deployment:** Vercel (frontend), Supabase (backend if needed)
- **Monitoring:** Notion (project tracking)

### Data Flow:
```
program.md (idea)
    ↓
User Researcher → pain_points.json
    ↓
Problem Framer → concepts.json
    ↓
MVP Builder → Vercel deployment
    ↓
[Wait 2 weeks]
    ↓
HCD Scorer → hcd_score.json
    ↓
Portfolio Manager → Notion update
    ↓
Decision: SCALE/ITERATE/PIVOT/KILL
```

---

## 4. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DeerFlow 2.0 breaking changes | High | High | Pin to working commit |
| Can't recruit real users | Medium | High | Offer incentives, expand channels |
| Build agent generates broken code | Medium | Medium | E2B sandbox testing |
| HCD scoring takes too long | Medium | Medium | Async written surveys as backup |
| Notion API rate limits | Low | Low | Batch updates, caching |

---

## 5. Verification Checkpoints

**Before claiming each phase complete:**

- [ ] Phase 0: DeerFlow health check passes
- [ ] Phase 1: Real user responses received
- [ ] Phase 2: Concepts generated with magic moments
- [ ] Phase 3: Live URL accessible, magic moment works
- [ ] Phase 4: HCD score calculated from real users
- [ ] Phase 5: Portfolio tracking multiple experiments

**Final verification:**
- [ ] End-to-end test: Idea → Deployed MVP → HCD Score → Notion
- [ ] User confirmation: "This is a real product I can use"

---

## 6. Current Status

**What exists:**
- ✅ 5 skill definitions (SKILL.md files)
- ✅ program.md HCD constitution
- ✅ Repo structure

**What doesn't exist:**
- ❌ DeerFlow 2.0 backend running
- ❌ Skill execution code (not just definitions)
- ❌ Real user recruitment system
- ❌ Actual deployment automation
- ❌ Integration testing

**Next step:** Phase 0 — Get DeerFlow 2.0 running locally.

---

## 7. Decision Required

**Option A:** Build incrementally (Phase 0 → 1 → 2 → 3 → 4 → 5)
- Pros: Verifiable at each step
- Cons: Takes 4-5 weeks
- Risk: Low

**Option B:** Build end-to-end skeleton first
- Pros: See full picture quickly
- Cons: May have gaps
- Risk: Medium

**Option C:** Use existing DeerFlow deployment
- Pros: Skip infrastructure setup
- Cons: Depends on external service
- Risk: Medium (vendor dependency)

**Which approach?** Or something else?

---

*Verification plan created before any further implementation.*
