🏆 AI Grant Proposal Writer – Task Decomposition
📌 Objective

The system generates a high-quality, grant-ready proposal by decomposing the complex task into smaller, manageable sub-tasks handled by specialized AI agents.

⚙️ Task Decomposition
1. 🧠 Project Understanding

Agent: Project Interpreter

Extracts project title, description, category, region, budget, and organization type
Identifies core problem, domain, and target users

Output: Structured project profile

2. 🔍 Grant Discovery

Agent: Grant Researcher

Searches real, active grants using Tavily API
Filters based on category, region, budget, and organization type

Output: List of relevant funding opportunities

3. 📊 Requirements Analysis

Agent: Requirements Analyzer

Extracts evaluation criteria from grants
Identifies eligibility requirements
Maps project strengths to grant expectations

Output: Key requirements and best-fit grants

4. ⚠️ Gap Identification

Agent: Gap Analyzer

Detects missing or weak areas in the project
Identifies issues like lack of data, unclear impact, or weak alignment

Output: List of improvements needed

5. ✍️ Proposal Generation

Agent: Proposal Writer

Generates the proposal in structured sections:

Executive Summary
Problem Statement
Objectives
Methodology
Expected Outcomes & Impact
Budget Rationale
Team & Qualifications
Sustainability Plan

Output: Complete grant proposal

6. ⭐ Proposal Evaluation

Agent: Judge

Evaluates proposal based on:
Grant alignment
Problem clarity
Methodology
Impact
Budget

Output: Quality score with feedback

7. 🔁 Refinement (Optional)

Agent: Refiner

Improves weak sections based on evaluation feedback

Output: Final optimized proposal
Overall Workflow:

User Input
↓
Project Interpreter
↓
Grant Researcher
↓
Requirements Analyzer
↓
Gap Analyzer
↓
Proposal Writer
↓
Judge
↓
Refiner (optional)
↓
Final Proposal
