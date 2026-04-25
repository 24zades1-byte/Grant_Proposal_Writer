# 🏆 GrantCraft — AI Grant Proposal Writer

### *Find active grants. Understand their requirements. Get a complete proposal — in minutes.*

<br>

> You describe your project idea and select a grant category.
> Our AI searches for real active grants, analyzes what funders want,
> and writes a full 8-section proposal ready to submit.
> No fluff. No guessing. Just a winning proposal.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Tavily](https://img.shields.io/badge/Tavily_Search-FF6B35?style=for-the-badge)
![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)

---

## 🔴 The Problem

Writing a grant proposal is hard. Most applicants fail not because their idea is bad —
but because they don't know:

```
❌  Which grants are actually open right now
❌  What specific criteria each funder looks for
❌  How to structure a proposal that gets shortlisted
❌  What budget justification funders expect
```

**GrantCraft fixes all of that.**

---

## ✅ What It Does

You enter your project. The AI does the rest.

```
  You enter            →    AI searches        →    AI analyzes       →    You get
  your project idea         active grants            requirements          a full proposal

  Project title             grants.gov               Funder criteria       8 complete sections
  Description               dst.gov.in               Must-have content     Budget breakdown
  Grant category            NIH, NSF, EU             Gaps to address       Ready to submit
  Budget range              Gates, Wellcome          Best-fit grants       Quality score
```

---

## 🤖 How The AI Works — 4 Agents

GrantCraft uses a **4-step AI agent pipeline.** Each agent has one job.

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│   📋 Your Project                                          │
│   Title · Description · Category · Region · Budget        │
│                                                            │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  🔍  AGENT 1 — GRANT RESEARCHER                            │
│                                                            │
│  Searches for real, active grants in real time             │
│  Sources: grants.gov · DST · SERB · NIH · EU Horizon      │
│  Returns: grant name, amount, deadline, requirements       │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  📋  AGENT 2 — REQUIREMENTS ANALYZER                       │
│                                                            │
│  Reads grant criteria and maps them to your project        │
│  Identifies what the proposal MUST include to win          │
│  Recommends the top 2-3 best-fit grants to apply for       │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  ✍️  AGENT 3 — PROPOSAL WRITER                             │
│                                                            │
│  Writes all 8 sections of a complete grant proposal        │
│  Tailored to the specific grant criteria found             │
│  Professional, persuasive, evidence-based tone             │
└───────────────────────┬────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  ⭐  AGENT 4 — JUDGE                                       │
│                                                            │
│  Evaluates the proposal like a real grant reviewer         │
│  Scores on 5 criteria out of 5 each                        │
│  Gives feedback on strengths and improvements              │
└────────────────────────────────────────────────────────────┘
                        │
                        ▼
              🏆 Your Complete Proposal
```

---

## 📄 Proposal Sections Generated

Every proposal includes all 8 sections:

| # | Section | What it covers |
|---|---------|---------------|
| 1 | **Executive Summary** | 3-4 line elevator pitch |
| 2 | **Problem Statement** | Evidence-backed case for funding |
| 3 | **Project Objectives** | 3-5 SMART goals |
| 4 | **Methodology** | Step-by-step approach with phases |
| 5 | **Expected Outcomes & Impact** | Measurable results and beneficiaries |
| 6 | **Budget Rationale** | Itemized breakdown with justification |
| 7 | **Team & Qualifications** | Why your team can deliver |
| 8 | **Sustainability Plan** | How impact continues after grant ends |

---

## ⭐ Judge Evaluation Rubric

The AI evaluates its own proposal on 5 criteria:

| Criterion | What it checks | Max Score |
|-----------|---------------|-----------|
| **Grant Alignment** | Does proposal match funder's exact criteria? | 5 |
| **Problem Clarity** | Is the problem specific and evidence-backed? | 5 |
| **Methodology** | Is the approach realistic and well-structured? | 5 |
| **Impact & Outcomes** | Are outcomes measurable and significant? | 5 |
| **Budget Rationale** | Is every budget item justified? | 5 |

**Score interpretation:**

| Score | Label | Meaning |
|-------|-------|---------|
| 85–100% | 🟢 Highly Competitive | Ready to submit |
| 70–84% | 🟡 Strong Proposal | Minor refinements needed |
| Below 70% | 🔴 Needs Refinement | Review before submitting |

---

## 📁 Project Structure

```
Grant_Proposal_Writer/
│
├── 🐍  app.py          →  Main Streamlit UI + pipeline
├── 🤖  agents.py       →  All 4 AI agents + fallback logic
├── 💬  prompts.py      →  System prompts for each agent
│
├── 📦  requirements.txt →  Python dependencies
├── 🔒  .env            →  API keys (never share this)
├── 📄  .env.example    →  Template for environment variables
└── 🚫  .gitignore      →  Keeps .env out of GitHub
```

---

## 🚀 Run It Locally

**Step 1 — Clone the repo**
```bash
git clone https://github.com/24zades1-byte/Grant_Proposal_Writer.git
cd Grant_Proposal_Writer
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Add your API keys**

Create a `.env` file and add:
```
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

| Key | Where to get it | Cost |
|-----|----------------|------|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | Free tier available |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | Free tier available |

**Step 4 — Run the app**
```bash
python -m streamlit run app.py
```

Open → [http://localhost:8501](http://localhost:8501)

---

## 🚂 Deploy on Railway

**Step 1** — Push code to GitHub (make sure `.env` is in `.gitignore`)

**Step 2** — Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub

**Step 3** — Add environment variables in Railway **Variables** tab:
```
GEMINI_API_KEY = your_key
TAVILY_API_KEY = your_key
```

**Step 4** — Set Start Command in **Settings → Deploy**:
```
python -m pip install -r requirements.txt && python -m streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

**Step 5** — Railway auto-deploys. Done ✅

---

## 🎯 Grant Categories Supported

| Category | Example Grants |
|----------|---------------|
| 🔬 **Research** | SERB, DST, NIH, NSF, EU Horizon |
| 🌍 **Social Impact** | Gates Foundation, Tata Trusts, Azim Premji |
| 💡 **Innovation** | BIRAC, NIF, Startup India, Innovate UK |
| 🎓 **Education** | Wellcome Trust, Commonwealth, UNESCO |
| 🏥 **Health** | WHO, NIH, Wellcome, ICMR |
| 🌱 **Environment** | GEF, WWF, Green Climate Fund |

---

## 🛠️ Tech Stack

| What | Technology |
|------|-----------|
| **UI** | Streamlit |
| **AI Agents** | Google Gemini 2.0 Flash |
| **Live Search** | Tavily Search API |
| **Deployment** | Railway |
| **Language** | Python 3.10+ |

---

## ⚠️ Disclaimer

GrantCraft generates AI-assisted proposal drafts.
Always review, customize, and verify grant details before submitting to any funder.
This tool does not guarantee grant approval.

**Useful grant portals:**

| Portal | Link |
|--------|------|
| 🇮🇳 India Grants | [dst.gov.in](https://dst.gov.in) · [serb.gov.in](https://serb.gov.in) |
| 🇺🇸 US Grants | [grants.gov](https://grants.gov) |
| 🌍 EU Grants | [ec.europa.eu/info/funding-tenders](https://ec.europa.eu/info/funding-tenders) |
| 🌐 Global | [gatesfoundation.org](https://gatesfoundation.org) |

---

## 📄 License

MIT License — free to use, modify, and share.

---

<div align="center">

**Turn your project idea into a winning grant proposal. 🏆**

*If this helped you, give it a ⭐ on GitHub!*

</div>
