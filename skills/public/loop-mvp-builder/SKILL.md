---
name: loop-mvp-builder
description: Build and deploy full-stack MVPs to Vercel + Supabase. Creates landing pages with emotion-first copy, interactive demos with 60-second magic moments, and waitlists. Not prototypes — production deployments. Use after Problem Framer provides concept and magic moment spec.
trigger: mvp build, deploy product, vercel deployment, landing page creation, interactive demo, full stack mvp, loop experiment build
---

# LOOP MVP Builder

Builds lovable MVPs, not just functional demos. Deploys to Vercel + Supabase. Focus: 60-second magic moment.

## Goal
Ship a deployed, full-stack MVP that users can actually experience — not a clickable prototype.

## Input
- **CONCEPT**: Top concept from Problem Framer
- **MAGIC_MOMENT**: 60-second aha moment specification
- **STYLE_CONSTRAINTS**: From program.md (tone, colors, voice)
- **TECH_PREFERENCES**: Stack preferences (default: Next.js + Tailwind + Supabase)

## Output Format
```json
{
  "deployed": true/false,
  "live_url": "https://...",
  "repo_url": "https://github.com/...",
  "build_manifest": {
    "stack": ["Next.js 14", "Tailwind", "Supabase", "Vercel"],
    "pages": ["Landing", "Demo", "Waitlist"],
    "build_hours": 6.5,
    "tests_passed": true
  },
  "lovability_checklist": {
    "emotion_first_headline": true/false,
    "single_action_cta": true/false,
    "under_60s_magic_moment": true/false,
    "user_centric_copy": true/false
  }
}
```

## Process

### 1. Landing Page Architecture

**Hero Section:**
- Headline: Transformation story, not features
  - BAD: "AI-powered email tool"
  - GOOD: "Never write a follow-up email again"
- Subhead: Specific pain + specific outcome
- CTA: Single action, minimal friction
  - "Get started in 10 seconds" (not "Sign up")

**Social Proof Section:**
- Pull quotes from User Researcher verbatim
- "I tried 5 tools before this..." 
- Real user language, not marketing speak

**Waitlist Section:**
- Not a boring form
- Micro-interactions: progress bar, validation animation
- Immediate value: "You're #42 on the list"
- Referral boost: "Skip 10 spots by sharing"

### 2. Interactive Demo

**The 60-Second Rule:**
- User lands on demo page
- Within 60 seconds, they experience the magic moment
- No login required for core interaction
- Show, don't tell

**Demo Structure:**
1. **Context setter** (5s): "Here's the problem..."
2. **The interaction** (45s): User tries the tool
3. **The payoff** (10s): Clear transformation shown

**Example - Habit Tracker:**
- Context: "You want to build a meditation habit"
- Interaction: User enters habit + sees accountability partner match
- Payoff: "You're now accountable to Sarah. She'll check in daily."

### 3. Technical Implementation

**Stack (configurable):**
- Frontend: Next.js 14 + Tailwind CSS
- Backend: Supabase (PostgreSQL + Auth)
- Deployment: Vercel
- Testing: Playwright (if enabled)

**Must Include:**
- Responsive design (mobile-first)
- Analytics tracking (Plausible or simple events)
- Error boundaries
- Loading states
- 404 page

**Must NOT Include:**
- User auth barriers before magic moment
- Feature bloat (stick to ONE core flow)
- Corporate speak anywhere
- Generic stock photos

### 4. Deployment Pipeline

**Pre-deploy Checklist:**
- [ ] All builds pass
- [ ] Lighthouse score > 80
- [ ] Magic moment flows end-to-end
- [ ] Waitlist captures emails
- [ ] Mobile responsive

**Deploy:**
- Push to GitHub
- Vercel auto-deploy
- Configure custom domain (if specified)
- Test live URL

## Success Criteria
- ✅ Live URL accessible
- ✅ Magic moment works in < 60s
- ✅ Waitlist captures emails
- ✅ Passes lovability checklist
- ✅ Mobile responsive

## Failure Modes
- ❌ Build fails → Fix and retry
- ❌ Magic moment > 60s → Simplify flow
- ❌ Not lovable → Redesign with Style Constraints
- ❌ Deploy fails → Check Vercel logs, retry

## Integration
After deployment, handoff to **loop-hcd-scorer** for user testing.
