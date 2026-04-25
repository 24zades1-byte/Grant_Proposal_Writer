import json
from google.genai import types
from prompts import (
    GRANT_RESEARCHER_SYSTEM_PROMPT,
    REQUIREMENTS_ANALYZER_SYSTEM_PROMPT,
    PROPOSAL_WRITER_SYSTEM_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    JUDGE_EVAL_PROMPT,
)


class AgentExecutionError(Exception):
    def __init__(self, user_message: str, original_error: Exception | None = None):
        super().__init__(user_message)
        self.user_message = user_message
        self.original_error = original_error


tavily_decl = types.FunctionDeclaration(
    name="tavily_search_tool",
    description="Search the web for real active grants, funding opportunities, and grant requirements from official sources.",
    parameters=types.Schema(
        type="object",
        properties={
            "query": types.Schema(
                type="string",
                description="The search query string",
            )
        },
        required=["query"],
    ),
)


def _is_quota_error(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "resource_exhausted" in message
        or "quota exceeded" in message
        or "429" in message
    )


def _raise_agent_error(agent_name: str, error: Exception) -> None:
    if _is_quota_error(error):
        raise AgentExecutionError(
            f"{agent_name} could not use Gemini because the API quota is exhausted.",
            original_error=error,
        ) from error
    raise AgentExecutionError(
        f"{agent_name} failed because the Gemini request returned an unexpected error.",
        original_error=error,
    ) from error


def _run_tavily_search(query: str, tavily_client) -> str:
    result = tavily_client.search(query=query, max_results=5)
    snippets = []
    for item in result.get("results", []):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        content = item.get("content", "")
        snippets.append(f"- [{title}]({url}): {content[:300]}")
    return "\n".join(snippets)


def _extract_profile_sections(project_profile: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for line in project_profile.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        sections[key.strip().lower()] = value.strip()
    return sections


def _build_search_queries(project_profile: str) -> list[str]:
    sections = _extract_profile_sections(project_profile)
    title       = sections.get("project title", "")
    category    = sections.get("grant category", "research")
    region      = sections.get("target region", "India")
    org_type    = sections.get("organization type", "")
    budget      = sections.get("budget range", "")

    queries = []

    if title:
        queries.append(f"{title} grant funding {category} 2025 open applications")
    if region.lower() == "india":
        queries.append(f"active {category} grants India DST SERB 2025 apply")
    elif region.lower() in ["usa", "us"]:
        queries.append(f"active {category} grants USA NIH NSF 2025 open")
    elif region.lower() in ["european union", "eu"]:
        queries.append(f"EU Horizon {category} grants 2025 open call")
    else:
        queries.append(f"international {category} grants 2025 open applications")

    if org_type:
        queries.append(f"{category} grant for {org_type} {region} funding 2025")

    return queries[:3]


# ─── FALLBACK FUNCTIONS ───────────────────────────────────────────────────────

def fallback_grant_brief(tavily_client, project_profile: str) -> str:
    queries = _build_search_queries(project_profile)
    sections = [
        "## Grant Research Brief (Fallback Mode)",
        "Gemini quota was unavailable. This brief was assembled directly from Tavily search results.",
    ]
    for query in queries:
        snippets = _run_tavily_search(query, tavily_client)
        if snippets:
            sections.append(f"### Search: {query}")
            sections.append(snippets)

    sections.append("### Common Grant Sources to Check")
    sections.append(
        "**India:**\n"
        "- SERB (Science & Engineering Research Board): serb.gov.in\n"
        "- DST (Dept of Science & Technology): dst.gov.in\n"
        "- BIRAC (Biotech grants): birac.nic.in\n"
        "- National Innovation Foundation: nif.org.in\n\n"
        "**International:**\n"
        "- Gates Foundation: gatesfoundation.org/grants\n"
        "- NIH (US): grants.nih.gov\n"
        "- EU Horizon: ec.europa.eu/info/funding-tenders\n"
        "- World Bank: worldbank.org/en/projects-operations/products-and-services/brief/grants\n"
        "- Wellcome Trust: wellcome.org/grant-funding"
    )
    return "\n\n".join(sections)


def fallback_requirements_analysis(grant_brief: str, project_profile: str) -> str:
    sections = _extract_profile_sections(project_profile)
    category = sections.get("grant category", "research")
    title    = sections.get("project title", "Your Project")
    region   = sections.get("target region", "India")

    return f"""## Requirements Analysis (Fallback Mode)
Gemini quota was unavailable. This is a standard requirements checklist for {category} grants.

### Project: {title}

### Key Grant Evaluation Criteria (Standard for {category.title()} Grants)

**1. Problem Statement**
- Must be specific, evidence-backed, and urgent
- Include statistics or data that show the scale of the problem
- Explain why existing solutions are insufficient

**2. Innovation & Originality**
- What makes your approach different from existing work?
- Is there a clear gap in the market or knowledge?

**3. Methodology**
- Clear, realistic, step-by-step plan
- Show you understand risks and have mitigation strategies
- Phase-wise timeline expected by most funders

**4. Team Qualifications**
- Relevant experience and credentials
- Past track record of similar projects
- Partnerships or collaborations strengthen the proposal

**5. Budget**
- Itemized and justified — no lump sums
- Align with the grant's typical funding range
- Show co-funding or in-kind contributions if available

**6. Impact & Scalability**
- Who benefits? How many? By when?
- Can the project scale beyond the grant period?
- Sustainability plan after funding ends

### Recommended Grant Types for {region}
- **{category.title()} Focus:** Look for grants that specifically mention your domain
- **Budget Match:** Apply only to grants within your stated budget range
- **Eligibility:** Confirm your organization type is eligible before applying

### Next Steps
1. Visit the official grant portals listed in the research brief
2. Download the full RFP (Request for Proposal) document
3. Check eligibility criteria carefully
4. Note the deadline and required documents
"""


def fallback_proposal(grant_brief: str, requirements: str, project_profile: str) -> str:
    sections = _extract_profile_sections(project_profile)
    title    = sections.get("project title", "Project Title")
    desc     = sections.get("description", "A project aimed at creating meaningful impact.")
    category = sections.get("grant category", "research")
    region   = sections.get("target region", "India")
    budget   = sections.get("budget range", "To be determined")
    org      = sections.get("organization type", "Organization")

    return f"""# Grant Proposal — {title}
*(Fallback Mode — Gemini quota unavailable. This is a template-based draft.)*

---

## 1. Executive Summary
{title} is a {category} initiative proposed by a {org} based in {region}. This project addresses a critical gap
in {desc[:100]}... We seek funding to implement a structured, evidence-based intervention that delivers
measurable outcomes within the project timeline.

---

## 2. Problem Statement
*(Customize this section with specific data and statistics)*

The challenge addressed by {title} is significant and growing. Current approaches have proven
insufficient because they lack the scale, innovation, or targeted focus required to create lasting change.
This project directly responds to this gap with a proven methodology adapted for the local context.

**Key evidence of the problem:**
- [Add Statistic 1 here]
- [Add Statistic 2 here]
- [Add expert citation or report reference here]

---

## 3. Project Objectives
By the end of the grant period, this project will:

1. **Objective 1:** [Specific, measurable goal — e.g., "Train 500 beneficiaries in X skill"]
2. **Objective 2:** [Specific, measurable goal]
3. **Objective 3:** [Specific, measurable goal]
4. **Objective 4:** [Long-term outcome — e.g., "Establish a sustainable model replicable in 3 districts"]

---

## 4. Methodology

**Phase 1 — Research & Planning (Months 1–2)**
- Stakeholder mapping and baseline assessment
- Finalize implementation team and partnerships
- Develop detailed work plan and monitoring framework

**Phase 2 — Implementation (Months 3–8)**
- Core project activities as per objectives
- Regular progress monitoring and data collection
- Mid-term review and course correction

**Phase 3 — Evaluation & Scale-up (Months 9–12)**
- Final impact assessment
- Documentation of learnings and best practices
- Dissemination of results and scale-up planning

---

## 5. Expected Outcomes & Impact

| Outcome | Metric | Target |
|---------|--------|--------|
| Direct beneficiaries reached | Number of people | [Target] |
| Knowledge/skill improvement | % improvement in assessments | [Target]% |
| Systems or tools created | Number of deliverables | [Target] |
| Sustained impact post-project | Follow-up metric | [Target] |

---

## 6. Budget Rationale

**Total Requested: {budget}**

| Item | Amount | Justification |
|------|--------|---------------|
| Personnel (salaries/consultants) | [Amount] | Core team required for delivery |
| Equipment & Materials | [Amount] | Essential tools for implementation |
| Travel & Field Operations | [Amount] | Required for ground-level work |
| Training & Capacity Building | [Amount] | Direct program cost |
| Monitoring & Evaluation | [Amount] | Ensuring accountability |
| Administrative Overhead (max 10%) | [Amount] | Organizational support costs |

---

## 7. Team & Qualifications
Our {org} brings relevant expertise in {category} with a demonstrated track record of successful
project implementation. The core team includes specialists in [relevant domains] with combined
experience of [X] years in [field].

**Key team members:**
- **Project Lead:** [Name, Qualification, Years of Experience]
- **Technical Expert:** [Name, Qualification]
- **Field Coordinator:** [Name, Qualification]

---

## 8. Sustainability Plan
Beyond the grant period, {title} will sustain its impact through:
- **Revenue model:** [e.g., fee-for-service, government integration, community ownership]
- **Partnerships:** Formal MOUs with [organizations] for continued support
- **Knowledge products:** Open-source tools/manuals for replication by others
- **Policy advocacy:** Engagement with policymakers to institutionalize the approach

---

*This proposal was generated as a draft template. Please customize all sections marked [in brackets]
with specific data, evidence, and details relevant to your project and target grant.*
"""


def fallback_judge_result() -> dict:
    return {
        "scores": {
            "grant_alignment":  {"score": 3, "reasoning": "Fallback mode — alignment based on category matching, not live grant criteria."},
            "problem_clarity":  {"score": 3, "reasoning": "Template problem statement provided. Needs specific data to score higher."},
            "methodology":      {"score": 3, "reasoning": "Phase-wise structure included but lacks project-specific detail."},
            "impact_outcomes":  {"score": 3, "reasoning": "Outcome framework provided but targets not yet filled in."},
            "budget_rationale": {"score": 3, "reasoning": "Budget categories listed. Actual amounts need to be specified."},
        },
        "overall_score": 3.0,
        "summary": "This is a fallback template proposal generated without live AI. It provides a solid structural framework but requires significant customization with project-specific data, evidence, and tailored language before submission to any funder.",
        "top_strength": "Clear structure with all required sections present.",
        "top_improvement": "Replace all placeholder text with specific evidence, data, and tailored language for the target grant.",
    }


# ─── AGENT FUNCTIONS ──────────────────────────────────────────────────────────

def grant_researcher_agent(client, tavily_client, project_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Researcher: searching for active grants")

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(
                text=(
                    f"Find real, currently active grants for this project:\n\n"
                    f"{project_profile}\n\n"
                    "Use the search tool to find specific grants from official sources. "
                    "Search for both government and private foundation grants matching this category and region. "
                    "Produce a research brief listing found grants with eligibility, amounts, deadlines, and requirements."
                )
            )]
        )
    ]

    tools = [types.Tool(function_declarations=[tavily_decl])]

    for turn in range(8):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=GRANT_RESEARCHER_SYSTEM_PROMPT,
                    tools=tools,
                ),
            )
        except Exception as error:
            _raise_agent_error("Researcher", error)

        parts = response.candidates[0].content.parts
        function_calls = [part.function_call for part in parts if part.function_call]

        if not function_calls:
            final_text = "".join(part.text for part in parts if part.text)
            if log_step:
                log_step(f"Researcher: done in {turn + 1} turn(s)")
            return final_text

        contents.append(types.Content(role="model", parts=parts))

        tool_results = []
        for function_call in function_calls:
            query = function_call.args.get("query", "active grants 2025")
            if log_step:
                log_step(f"Researcher: searching → '{query}'")
            search_result = _run_tavily_search(query, tavily_client)
            tool_results.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": search_result},
                )
            )

        contents.append(types.Content(role="user", parts=tool_results))

    if log_step:
        log_step("Researcher: max turns reached")
    return "".join(part.text for part in parts if part.text)


def requirements_analyzer_agent(client, grant_brief: str, project_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Requirements Analyzer: identifying what this proposal needs")

    prompt = f"""Analyze this project and the grants found. Identify exactly what this proposal needs to win.

PROJECT PROFILE:
{project_profile}

GRANT RESEARCH BRIEF:
{grant_brief}

For each recommended grant:
1. State why this project IS a good fit
2. List the exact evaluation criteria the funder uses
3. Identify what the proposal MUST include to score well
4. Flag any gaps or risks in the current project profile
5. Recommend the TOP 2-3 grants to apply for, ranked by fit"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=REQUIREMENTS_ANALYZER_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Requirements Analyzer", error)

    if log_step:
        log_step("Requirements Analyzer: analysis complete")
    return response.text


def proposal_writer_agent(client, grant_brief: str, requirements: str, project_profile: str, log_step=None) -> str:
    if log_step:
        log_step("Proposal Writer: drafting your grant proposal")

    prompt = f"""Write a complete, compelling grant proposal for this project.

PROJECT PROFILE:
{project_profile}

GRANT RESEARCH BRIEF (target these grants):
{grant_brief}

REQUIREMENTS ANALYSIS (what the proposal must include):
{requirements}

Write all 8 sections of the proposal in full. Be specific, persuasive, and evidence-based.
Tailor the language and emphasis to the grant criteria identified in the requirements analysis.
Do not use placeholder text — write actual content based on the project profile."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=PROPOSAL_WRITER_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Proposal Writer", error)

    if log_step:
        log_step("Proposal Writer: proposal draft complete")
    return response.text


def judge_agent(client, project_profile: str, grant_brief: str, proposal: str, log_step=None) -> dict:
    if log_step:
        log_step("Judge: evaluating proposal quality")

    eval_prompt = JUDGE_EVAL_PROMPT.format(
        project_profile=project_profile,
        grant_brief=grant_brief,
        proposal=proposal,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=eval_prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=JUDGE_SYSTEM_PROMPT,
            ),
        )
    except Exception as error:
        _raise_agent_error("Judge", error)

    raw = response.text.strip().replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "scores": {
                "grant_alignment":  {"score": 0, "reasoning": "Could not parse"},
                "problem_clarity":  {"score": 0, "reasoning": "Could not parse"},
                "methodology":      {"score": 0, "reasoning": "Could not parse"},
                "impact_outcomes":  {"score": 0, "reasoning": "Could not parse"},
                "budget_rationale": {"score": 0, "reasoning": "Could not parse"},
            },
            "overall_score": 0,
            "summary": "Judge response could not be parsed.",
            "top_strength": "N/A",
            "top_improvement": "N/A",
        }

    if log_step:
        log_step(f"Judge: overall score = {result.get('overall_score', '?')}/5")
    return result
