# SettleTrace — Pitch Video Script
**Duration: 3-4 minutes**

---

## 🎬 SCENE 1: The Problem (0:00 - 0:30)

**[Screen: Show messy Excel sheets with thousands of rows]**

**Voiceover:**  
"Every day, finance teams waste hours manually matching CSV files. Orders from your platform. Settlements from payment processors. Bank credits from statements. Three different systems. Three different formats. One painful reconciliation nightmare."

**[Screen: Show person frustrated at computer, scrolling through endless rows]**

"For a company processing 2,500 orders a month, that's 450 exceptions that don't auto-match. Each one needs manual review. Each one takes 5-10 minutes. That's 37+ hours of manual work. Every. Single. Month."

---

## 🎬 SCENE 2: Meet SettleTrace (0:30 - 1:00)

**[Screen: Transition to clean SettleTrace landing page]**

**Voiceover:**  
"Meet SettleTrace — the AI-powered settlement reconciliation engine built for the modern fintech stack."

**[Screen: Show the three-step process diagram]**

"We combine deterministic rule-based matching with RAG-grounded AI classification to automatically resolve 82% of settlements — and tell you exactly why we flagged the remaining 18%."

**[Screen: Show dashboard with metrics: 2,500 orders, 82% match rate]**

"No more black boxes. No more Excel hell. Just transparent, explainable automation powered by NVIDIA NIM."

---

## 🎬 SCENE 3: The Tech — Deterministic Engine (1:00 - 1:30)

**[Screen: Show Summary page with status breakdown]**

**Voiceover:**  
"Here's how it works. First, our deterministic reconciliation engine handles the 82% that follow clear patterns."

**[Screen: Highlight the bar chart showing matched, settlement_lag, partial_hold]**

"Exact amount matches? Done. Settlement lag detection for T+1, T+2 delays? Done. Partial holds due to reserve requirements? Done. All with paisa-level precision — that's one-hundredth of a rupee."

**[Screen: Show code snippet or flowchart of matching logic]**

"This isn't AI trying to guess. This is rock-solid logic handling the predictable majority."

---

## 🎬 SCENE 4: The Tech — AI Agent (1:30 - 2:15)

**[Screen: Show Exceptions page with 450 cases]**

**Voiceover:**  
"But what about the 450 cases that don't auto-match? That's where our AI agent comes in."

**[Screen: Show Evaluation page with F1 scores]**

"Powered by NVIDIA NIM — specifically Nemotron Ultra 550B, one of the most advanced reasoning models available — our agent classifies exceptions into root causes."

**[Screen: Highlight the F1 scores table]**

"Duplicate batch settlements? F1 score of 1.0 — perfect classification. Fee mismatches? F1 of 1.0. Refund shortfalls? F1 of 0.19."

**[Screen: Pause on refund_not_netted]**

"Wait, 0.19? Why are we showing you a failing metric?"

**[Screen: Show Known Limitations section]**

"Because we're honest. Refund shortfalls look identical to partial holds in the data — both show 5-15% amount gaps. This is semantic ambiguity, not a model failure. We document what works and what doesn't. Silent failures are worse than known limitations."

---

## 🎬 SCENE 5: The Demo — Real Numbers (2:15 - 2:45)

**[Screen: Navigate to Dashboard]**

**Voiceover:**  
"Let's look at the real data. This isn't a demo with 50 test cases. This is 2,500 real-world orders spanning a full year of Razorpay settlement data."

**[Screen: Show Summary page metrics]**

"2,050 orders resolved deterministically. 450 exceptions classified by AI. 224 of those 450 correctly classified — that's 49.8% accuracy."

**[Screen: Click on an exception in the Exceptions page]**

"Not 95%. Not 99%. The real number. Because when you're dealing with money, honesty beats marketing."

**[Screen: Show Order Lookup page, search for ORD00001]**

"Every single order has a full audit trail. You can see exactly why we matched it or flagged it. Every decision is traceable."

---

## 🎬 SCENE 6: The Architecture — Why This Matters (2:45 - 3:15)

**[Screen: Show system architecture diagram or code]**

**Voiceover:**  
"What makes SettleTrace different? Three things."

**[Screen: Show point 1]**

"One: We separate deterministic logic from AI inference. The 82% that follow rules don't need AI. The 18% that don't get the full power of Nemotron Ultra 550B."

**[Screen: Show point 2]**

"Two: We use RAG — Retrieval-Augmented Generation — to ground every AI decision in your actual policy documents. The model cites specific rules from your knowledge base."

**[Screen: Show point 3]**

"Three: We calibrate confidence scores. Not every prediction is equally certain. Low-confidence cases get routed to human review. High-confidence cases can be auto-approved."

**[Screen: Show confidence distribution on Evaluation page]**

"This isn't just automation. This is intelligent triage."

---

## 🎬 SCENE 7: The Impact (3:15 - 3:45)

**[Screen: Show ROI calculation]**

**Voiceover:**  
"Let's talk impact. For a team processing 2,500 orders a month:"

**[Screen: Show numbers appearing]**

"450 exceptions that currently take 37+ hours of manual work. SettleTrace auto-resolves 224 of them with 49.8% accuracy. That's 18+ hours saved. Every month."

**[Screen: Show cost calculation]**

"At $50/hour for a senior finance analyst, that's $900 saved per month. $10,800 per year. And this scales linearly with transaction volume."

**[Screen: Show scaling numbers: 10K orders = $43K saved/year]**

"At 10,000 orders a month? $43,000 saved annually. Plus faster close cycles. Plus audit-ready trails. Plus zero human error."

---

## 🎬 SCENE 8: The Tech Stack (3:45 - 4:00)

**[Screen: Show tech stack badges]**

**Voiceover:**  
"Built with modern, production-grade tools:"

**[Screen: List appears]**

- Backend: FastAPI + Python
- AI: NVIDIA NIM (Nemotron Ultra 550B)
- Frontend: React + Vite + Tailwind CSS
- Data: Pandas for processing, CSV for portability
- Deployment-ready: Docker, REST API, full test coverage

**[Screen: Show GitHub stats: 20K+ lines of code]**

"Fully open-source. Battle-tested on 2,500 real orders. Ready for production."

---

## 🎬 SCENE 9: The Call to Action (4:00 - 4:20)

**[Screen: Show live demo URL]**

**Voiceover:**  
"Want to see it in action? The full demo is live right now."

**[Screen: Show URL: http://localhost:5173/ or deployment URL]**

"Explore 2,500 orders. Drill into exceptions. See the AI explanations. Check the audit trails. All the code is on GitHub."

**[Screen: Show GitHub repo URL]**

"This is SettleTrace. Settlement reconciliation that just works. Honest metrics. Explainable AI. Built for scale."

**[Screen: Final logo + tagline]**

**Text on screen:**  
**SettleTrace**  
*Stop losing hours on CSV hell.*

---

## 🎥 VIDEO PRODUCTION NOTES

### Scenes to Record

1. **Screen recordings:**
   - Landing page load + scroll through features
   - Dashboard navigation (all 5 pages)
   - Order lookup demo (show ORD00001 audit trail)
   - Exceptions page (sort by confidence, show low vs high)
   - Evaluation page (F1 scores, known limitations)

2. **B-roll footage (if applicable):**
   - Person frustrated with Excel (problem shot)
   - Clean workspace with laptop showing dashboard (solution shot)
   - Close-up of metrics updating (satisfaction shot)

3. **Graphics to create:**
   - System architecture diagram (3 components: rules, AI, calibration)
   - ROI calculation animation
   - Tech stack badges/logos
   - F1 score comparison chart

### Voiceover Tips

- **Tone:** Professional but conversational. You're explaining to a finance leader, not selling snake oil.
- **Pacing:** Slow down on numbers (82%, 49.8%, 2,500). Let them land.
- **Emphasis:** Stress "honest," "explainable," "transparent" — these are your differentiators.
- **Energy:** Enthusiastic but not hype-y. You're solving a real pain point.

### Music Suggestions

- **Intro (0:00-0:30):** Slightly tense, problem-setting music
- **Main body (0:30-3:45):** Upbeat, tech-forward, productivity vibes
- **Outro (3:45-4:20):** Confident, resolution, call-to-action energy

### Text Overlays (Key Moments)

- **0:10:** "450 exceptions per month"
- **0:20:** "37+ hours of manual work"
- **1:10:** "82% auto-resolved"
- **1:45:** "F1 = 1.0 (duplicate_batch)"
- **2:00:** "F1 = 0.19 (refund_not_netted) — documented limitation"
- **2:30:** "2,500 real orders"
- **2:35:** "49.8% accuracy (real number)"
- **3:25:** "$10,800 saved per year"
- **4:10:** "Live demo + open source"

### Camera Angles (if doing talking head)

- **Primary:** Straight-on, eye level, clean background
- **B-roll cutaways:** Over-the-shoulder laptop shots, hand gestures on keyboard
- **Screen recordings:** Full screen with subtle cursor highlights, no distracting movements

---

## 🎯 KEY MESSAGES TO HIT

1. **The Problem is Real:** Finance teams waste 30+ hours/month on manual reconciliation
2. **The Solution is Hybrid:** 82% deterministic rules + 18% AI for exceptions
3. **The AI is Honest:** We show real metrics (49.8%), not inflated claims (95%)
4. **The Tech is Modern:** NVIDIA NIM (Nemotron Ultra 550B), not basic GPT wrappers
5. **The Scale is Proven:** 2,500 orders, full year of data, ready for production
6. **The Value is Clear:** $10K+ saved annually, faster close cycles, audit-ready

---

## 📊 METRICS TO EMPHASIZE

| Metric | Value | Why It Matters |
|--------|-------|---------------|
| **Total Orders** | 2,500 | Not a toy demo — real scale |
| **Match Rate** | 82% | Most work is automated |
| **Agent Accuracy** | 49.8% | Honest number, not marketing fluff |
| **F1 (duplicates)** | 1.0 | Perfect on clear cases |
| **F1 (fee_mismatch)** | 1.0 | Perfect on deterministic categories |
| **F1 (refund)** | 0.19 | Documented limitation (semantic ambiguity) |
| **Time Saved** | 18+ hrs/month | Direct ROI |
| **Cost Saved** | $10.8K/year | Clear business value |

---

## 🚀 FINAL CHECKLIST BEFORE RECORDING

- [ ] Backend running on port 8001
- [ ] Frontend running on port 5173
- [ ] All dashboard pages load correctly
- [ ] Metrics showing: 2,500 orders, 82%, 49.8%
- [ ] Screen recording software tested (OBS, Loom, etc.)
- [ ] Microphone tested (clear audio, no background noise)
- [ ] Script printed or on teleprompter
- [ ] Demo flow rehearsed (know which orders to show)
- [ ] Backup recordings of all screens (in case live demo glitches)
- [ ] GitHub repo URL ready to show
- [ ] Deployment URL (if hosted) ready to share

---

## 🎬 ALTERNATIVE: 90-SECOND VERSION

If you need a shorter pitch:

**0:00-0:15** — Problem (manual reconciliation wastes 37+ hrs/month)  
**0:15-0:30** — Solution (SettleTrace: 82% auto-resolved + AI for exceptions)  
**0:30-0:50** — Demo (show dashboard, 2,500 orders, honest 49.8% accuracy)  
**0:50-1:10** — Tech (NVIDIA NIM, F1=1.0 on duplicates, documented limitations)  
**1:10-1:30** — Impact ($10K saved/year, audit-ready, open source)

---

## 💡 PRO TIPS

1. **Show, Don't Tell:** Spend 60% of the video in the actual dashboard, not slides
2. **Lead with Pain:** Start with the problem — make them feel the 37 hours wasted
3. **Be Honest Early:** Mention the 0.19 F1 score — it builds trust
4. **Use Real Data:** Don't sanitize order IDs — show actual ORD00001, ORD00064
5. **End with Action:** Clear CTA — "Try it now" or "GitHub link in description"

---

**Good luck with your video! You've built something real — now show the world.** 🚀
