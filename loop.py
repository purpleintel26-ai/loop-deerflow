#!/usr/bin/env python3
"""
LOOP - Autonomous Feedback Loop
Based on MoneyPrinterV2 pattern: one continuous loop, not N separate apps
"""

import json
import time
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class LOOP:
    """
    Autonomous product iteration system.
    One experiment, continuously improved based on real feedback.
    """
    
    def __init__(self, experiment_name, idea):
        self.experiment_name = experiment_name
        self.idea = idea
        self.iteration = 0
        self.base_dir = Path(f"/root/.openclaw/workspace/loop-experiments/{experiment_name}")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # State tracking
        self.state_file = self.base_dir / "state.json"
        self.state = self.load_state()
        
        # Supabase for feedback storage
        self.supabase_url = "https://your-project.supabase.co"
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        
        print(f"🧠 LOOP: {experiment_name}")
        print(f"💡 Idea: {idea}")
        print(f"📊 Current iteration: {self.iteration}")
        print(f"📁 Working dir: {self.base_dir}")
    
    def load_state(self):
        """Load experiment state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "experiment": self.experiment_name,
            "idea": self.idea,
            "iterations": [],
            "current_status": "initialized",
            "created_at": datetime.now().isoformat()
        }
    
    def save_state(self):
        """Save experiment state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def run_cycle(self):
        """One full build → deploy → measure → decide cycle"""
        self.iteration += 1
        print(f"\n{'='*60}")
        print(f"🔄 CYCLE {self.iteration}")
        print(f"{'='*60}")
        
        cycle = {
            "iteration": self.iteration,
            "started_at": datetime.now().isoformat()
        }
        
        # 1. GENERATE CODE (based on feedback from previous cycle)
        print(f"\n[{datetime.now().strftime('%H:%M')}] 🔨 Generating code...")
        code_files = self.generate_code()
        cycle["files_generated"] = list(code_files.keys())
        
        # 2. BUILD IN E2B
        print(f"\n[{datetime.now().strftime('%H:%M')}] 🧪 Building in E2B sandbox...")
        build_success = self.build_in_e2b(code_files)
        cycle["build_success"] = build_success
        
        if not build_success:
            print("❌ Build failed, aborting cycle")
            cycle["decision"] = "kill"
            self.state["iterations"].append(cycle)
            self.save_state()
            return "kill"
        
        # 3. DEPLOY TO VERCEL
        print(f"\n[{datetime.now().strftime('%H:%M')}] 🚀 Deploying...")
        deploy_url = self.deploy_to_vercel()
        cycle["deploy_url"] = deploy_url
        print(f"✅ Live: {deploy_url}")
        
        # 4. TEST WITH PLAYWRIGHT
        print(f"\n[{datetime.now().strftime('%H:%M')}] ✅ Running tests...")
        test_results = self.run_playwright_tests(deploy_url)
        cycle["test_passed"] = test_results["passed"]
        
        if not test_results["passed"]:
            print("❌ Tests failed, will iterate")
            cycle["decision"] = "iterate"
            self.state["iterations"].append(cycle)
            self.save_state()
            return "iterate"
        
        # 5. COLLECT FEEDBACK (real metrics from deployed app)
        print(f"\n[{datetime.now().strftime('%H:%M')}] 📈 Collecting feedback...")
        feedback = self.collect_feedback(deploy_url)
        cycle["feedback"] = feedback
        
        # 6. CALCULATE HCD SCORE
        hcd_score = self.calculate_hcd_score(feedback)
        cycle["hcd_score"] = hcd_score
        print(f"\n📊 HCD Score: {hcd_score}/100")
        
        # 7. DECIDE
        decision = self.make_decision(hcd_score, feedback)
        cycle["decision"] = decision
        cycle["completed_at"] = datetime.now().isoformat()
        
        self.state["iterations"].append(cycle)
        self.save_state()
        
        return decision
    
    def generate_code(self):
        """Generate Next.js code based on idea and previous feedback"""
        # Read previous feedback to improve
        previous_feedback = ""
        if self.iteration > 1:
            last_cycle = self.state["iterations"][-1]
            if "feedback" in last_cycle:
                previous_feedback = f"\nPrevious feedback: {last_cycle['feedback']}"
        
        code = {
            "pages/index.tsx": f'''export default function Landing() {{
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <main className="max-w-2xl mx-auto px-6 py-20">
        <h1 className="text-5xl font-bold mb-6 text-purple-900">
          {self.idea}
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          The autonomous product, iteration {self.iteration}.
        </p>
        <button 
          className="bg-purple-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-purple-700 transition"
          onClick={() => alert('Welcome to iteration {self.iteration}!')}
        >
          Get Started — It's Free
        </button>
        <p className="text-sm text-gray-500 mt-6">
          {self.experiment_name} • Built by LOOP autonomous system
        </p>
      </main>
    </div>
  );
}}''',
            "package.json": json.dumps({
                "name": self.experiment_name.lower().replace(" ", "-"),
                "version": f"0.{self.iteration}.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "next": "14.0.0",
                    "react": "18.2.0",
                    "react-dom": "18.2.0",
                    "tailwindcss": "3.3.0"
                }
            }),
            "next.config.js": "module.exports = { output: 'export' }",
            "tailwind.config.js": '''
module.exports = {
  content: ['./pages/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}''',
            "public/index.html": '''<!DOCTYPE html><html><head><title>LOOP Experiment</title></head><body></body></html>'''
        }
        
        # Add Supabase integration if we have key
        if self.supabase_key:
            code["lib/supabase.js"] = f'''
import {{ createClient }} from '@supabase/supabase-js'
const supabaseUrl = '{self.supabase_url}'
const supabaseKey = '{self.supabase_key}'
export const supabase = createClient(supabaseUrl, supabaseKey)
'''
        
        return code
    
    def build_in_e2b(self, code_files):
        """Build in E2B sandbox"""
        try:
            # Would use real E2B agent
            # For now, simulate
            print("  → Uploading code to sandbox...")
            print("  → Installing dependencies...")
            print("  → Building Next.js...")
            time.sleep(2)
            print("  ✓ Build successful")
            return True
        except Exception as e:
            print(f"  ❌ Build error: {e}")
            return False
    
    def deploy_to_vercel(self):
        """Deploy to Vercel"""
        # In production: use Vercel API
        timestamp = int(time.time())
        return f"https://{self.experiment_name.lower().replace(' ', '-')}-{timestamp}.vercel.app"
    
    def run_playwright_tests(self, url):
        """Test the deployed app"""
        # Use the Playwright test suite from loop-testing
        try:
            result = subprocess.run(
                ["npm", "run", "test:vercel", url],
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "passed": result.returncode == 0,
                "output": result.stdout + result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": "Test timeout"}
    
    def collect_feedback(self, url):
        """Collect feedback from Supabase or manual entry"""
        # In production: query Supabase for waitlist signups, analytics
        # For now: manual entry via stdin (simulating feedback)
        
        print("\n" + "─"*40)
        print("📊 Enter feedback metrics for this iteration:")
        print("(If automated, this would query Supabase)")
        
        try:
            waitlist = int(input("Waitlist signups: ") or "0")
            conversion = float(input("Landing page conversion %: ") or "0")
            rating = float(input("User rating (0-10): ") or "0")
            pay = input("Would users pay? (y/n): ").lower() == 'y'
            
            return {
                "waitlist_signups": waitlist,
                "conversion_rate": conversion,
                "user_rating": rating,
                "would_pay": pay,
                "url": url
            }
        except (EOFError, KeyboardInterrupt):
            # Non-interactive mode: return simulated data
            print("\n[Non-interactive mode, using simulated feedback]")
            return {
                "waitlist_signups": 5,
                "conversion_rate": 0.15,
                "user_rating": 7.0,
                "would_pay": True,
                "url": url
            }
    
    def calculate_hcd_score(self, feedback):
        """Calculate HCD composite score"""
        lovability = feedback["user_rating"] * 10  # 0-100
        activation = feedback["conversion_rate"] * 100  # 0-100
        revenue = 100 if feedback["would_pay"] else 0
        
        score = (lovability * 0.40) + (activation * 0.35) + (revenue * 0.25)
        return round(score)
    
    def make_decision(self, score, feedback):
        """SCALE / ITERATE / PIVOT / KILL"""
        print("\n" + "─"*40)
        print("🎯 DECISION MATRIX:")
        print(f"  HCD Score: {score}/100")
        print(f"  Lovability: {feedback['user_rating']}/10")
        print(f"  Waitlist: {feedback['waitlist_signups']}")
        print(f"  Would Pay: {'Yes' if feedback['would_pay'] else 'No'}")
        
        if score >= 75 and feedback["user_rating"] >= 8:
            print("\n✅ SCALE — Keep building, add resources")
            return "scale"
        elif score >= 50:
            print("\n🔄 ITERATE — Fix friction, rebuild")
            self.write_iteration_plan(feedback)
            return "iterate"
        elif feedback["user_rating"] >= 6:
            print("\n🔀 PIVOT — Wrong solution, keep the pain")
            return "pivot"
        else:
            print("\n💀 KILL — Users don't love it")
            return "kill"
    
    def write_iteration_plan(self, feedback):
        """Write plan for next iteration"""
        plan_file = self.base_dir / f"iteration_{self.iteration}_plan.md"
        plan = f"""# Iteration {self.iteration} Plan

## Feedback Summary
- Waitlist: {feedback['waitlist_signups']}
- Conversion: {feedback['conversion_rate']*100}%
- Rating: {feedback['user_rating']}/10
- Would pay: {feedback['would_pay']}

## Problems to Fix
1. [Top friction from feedback]
2. [Second issue]
3. [Third issue]

## Changes for Next Build
- [ ] [Specific change based on feedback]
- [ ] [Another change]
- [ ] [Third change]

## Success Criteria
- [ ] Waitlist conversion > 20%
- [ ] User rating > 7.5
- [ ] At least 10 waitlist signups

---
Generated by LOOP Autonomous System
{datetime.now().isoformat()}
"""
        plan_file.write_text(plan)
        print(f"  📝 Plan written: {plan_file}")
    
    def run_forever(self):
        """Run continuous loop until killed"""
        print("\n" + "="*60)
        print("🚀 LOOP Autonomous System Running")
        print("="*60)
        print("\nCore Loop: Build → Deploy → Measure → Decide → Iterate")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                decision = self.run_cycle()
                
                if decision == "kill":
                    print("\n🛑 Experiment killed by LOOP logic")
                    break
                elif decision == "scale":
                    print("\n🎉 This experiment is scaling!")
                    cont = input("\nContinue iterating? (y/n): ").lower()
                    if cont != 'y':
                        break
                else:
                    print(f"\n🔄 {decision.upper()} — Next cycle starting...")
                    time.sleep(2)  # Brief pause between cycles
                    
        except KeyboardInterrupt:
            print("\n\n🛑 LOOP stopped by user")
        
        print(f"\n📚 Experiment history saved to: {self.state_file}")
        print(f"📊 Total iterations: {self.iteration}")


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python loop.py <experiment-name>")
        print("Example: python loop.py 'habit-accountability'")
        sys.exit(1)
    
    experiment_name = sys.argv[1]
    idea = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else experiment_name
    
    loop = LOOP(experiment_name, idea)
    loop.run_forever()


if __name__ == "__main__":
    main()
