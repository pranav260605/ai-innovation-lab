AI Demo Factory

What this is, in one sentence: you type a plain-English question like "Can AI detect spam emails?" and this system automatically tests it against 3 real AI models, checks their answers against each other, and hands you back a report telling you which AI to use and why — all in about 2 minutes, with zero manual work.

Why this exists

Imagine you work at a company that gets asked questions like this all the time:

"Can AI read our customer emails and flag the urgent ones?"
"Can AI detect spam automatically?"
"Which AI model should we use for this task?"

Normally, answering this properly takes a person 1-2 days:

Think about which AI models to test
Write a prompt (the instructions given to the AI)
Find or create sample data to test on
Run the same test on 3 different AI models by hand
Compare the results
Write up a report with a recommendation

This project automates all 6 of those steps into a single command. You ask the question, wait 2 minutes, and get a finished report.

How it works — the journey of your question

Think of it like a small factory production line. Your question goes in one end, a finished report comes out the other end, passing through 5 stations along the way.

"Can AI detect spam emails?"
            │
            ▼
  ┌───────────────────┐
  │   STATION 1        │   An AI "manager" reads your question and
  │   The Planner       │   decides: what kind of task is this, which
  │                     │   3 AI models should test it, and what exact
  │                     │   instructions should be given to them.
  └──────────┬──────────┘
             ▼
  ┌───────────────────┐
  │   STATION 2         │   The plan is handed to 3 different AI
  │   The Runner         │   models. Each one is given 20 sample
  │                     │   emails and asked to classify them —
  │                     │   60 tests run automatically, back to back.
  └──────────┬──────────┘
             ▼
  ┌───────────────────┐
  │   STATION 3         │   Instead of a human checking all 60
  │   The Judge          │   answers by hand, the 3 AI models check
  │  (Consensus Checker) │   EACH OTHER. If 2 out of 3 agree on an
  │                     │   answer, that's treated as likely correct.
  │                     │   Only disagreements get flagged for a human
  │                     │   to look at — saving huge amounts of time.
  └──────────┬──────────┘
             ▼
  ┌───────────────────┐
  │   STATION 4         │   All the results are turned into a clean,
  │   The Report Maker   │   visual dashboard — bar charts showing
  │                     │   which AI was fastest, most accurate, and
  │                     │   most reliable. Opens like a webpage,
  │                     │   works on any device, no installation.
  └──────────┬──────────┘
             ▼
  ┌───────────────────┐
  │   STATION 5         │   The system writes its own summary
  │   The Explainer       │   document explaining what was tested,
  │                     │   what was found, and which AI model is
  │                     │   recommended — in plain English.
  └──────────┬──────────┘
             ▼
     Finished Report
  "Use Llama-70B — 100% accuracy,
   275ms response time"
What makes this actually clever (not just automated)

Most importantly: it doesn't need a human to grade the answers.

Normally, to know if an AI's answer is "correct," you need a person to have already labeled the right answers ahead of time — which takes hours or days for large amounts of data.

This system instead uses a trick: it makes the 3 AI models check each other's work. If Model A, Model B, and Model C all look at the same email and 2 of them say "this is spam" while 1 says "this is not spam" — the system trusts the majority. It's like asking 3 friends for their opinion and going with what most of them say, instead of needing an expert to verify every single answer.

This means the system only needs a human to review the handful of cases where the AIs genuinely disagreed — turning a job that would take hours into a job that takes minutes.

What you get at the end

Two files, automatically created:

File	What it is	Who reads it
dashboard.html	A visual report with charts	Anyone — just double-click to open in a browser
README.md	A written summary of findings	Anyone — reads like a short report

Both are single, self-contained files. No installation, no login, no internet connection needed to view them once created. You can email them to anyone and they'll open instantly.

A real example from this project

Question asked: "Can AI detect spam emails?"

What happened automatically:

3 AI models were tested (Llama-70B, Llama-8B, Qwen-32B)
Each was given 20 sample emails to classify as spam or not spam
60 total tests ran in under 2 minutes
The 3 models cross-checked each other's answers
Only 4 out of 20 emails had any disagreement between the models

The final recommendation:

Use Llama-70B — 100% agreement with the group consensus, at 275 milliseconds average response time.

That recommendation, along with the full breakdown, was generated entirely without a human writing a single line of it.

Why this matters for the business

Every time someone asks "can AI do X for us," instead of a person spending 1-2 days researching and testing, this system gives a data-backed answer in under 2 minutes, with:

Real test results, not guesses
A specific number to back up the recommendation (like "275ms" or "100% agreement")
A visual report anyone can understand, not a technical spreadsheet
Complete transparency about where the AIs disagreed, so nothing is hidden
Honesty about limitations

This system is upfront about what it can and can't guarantee:

It doesn't know the "true" correct answer — it only knows what the majority of AI models agree on. If all 3 models happen to share the same mistake, the system won't catch it. This is clearly labeled in every report it produces.
Response times can vary — free AI services sometimes respond slower depending on how busy they are.
It's built to test simple yes/no or category-style questions well (like spam/not spam, urgent/not urgent) — more complex questions may need a person to double check the results.
How to run it (for the person setting it up)
bash
git clone [repository link]
cd ai-innovation-lab
pip install -r requirements.txt
python demo_factory/factory.py --problem "Can AI detect spam emails?"

Two minutes later, open output/dashboard.html in any web browser to see the results.

In one sentence, for someone in a hurry

This is a system that turns any "can AI do this?" question into a real, tested, visual answer — automatically, in about 2 minutes, without needing anyone to manually check the AI's work.