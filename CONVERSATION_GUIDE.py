"""
CONCRETE CONVERSATION GUIDE
Showcasing Router Logic: Single-Turn, Multi-Turn, Topic-Switching & Complex Workflows

This guide demonstrates realistic conversation flows with:
- Agent routing decisions
- MCP function access
- Agent switching patterns
- Confidence scoring
"""

# ============================================================================
# SCENARIO 1: COMPLEX SINGLE-TURN CONVERSATION
# ============================================================================

SCENARIO_1_SINGLE_TURN = """
┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 1: COMPLEX SINGLE-TURN ANALYSIS REQUEST                        │
└─────────────────────────────────────────────────────────────────────────┘

USER REQUEST:
"We have Q1 sales data with customer behavior patterns. Analyze the dataset
 for statistical significance, identify key market segments, create revenue
 forecasts, and give me a comprehensive business report with KPIs and
 recommendations."

ROUTER DECISION FLOW:
─────────────────────

Turn 1: Initial Message
├─ Input Analysis:
│  ├─ Intent: Complex multi-domain analysis
│  ├─ Domains Detected: [analytics, business, reporting]
│  ├─ Input Types: [business_data, sales_data, operational_metrics]
│  └─ Confidence: 0.92 (high - clear multi-domain request)
│
├─ Route Decision: EXECUTIVE INSIGHTS AGENT (agent_special_002)
│  └─ Reason: Request requires cross-domain synthesis with business focus
│
└─ Execution Plan: Multi-stage workflow delegation

AGENT CALL CHAIN:
─────────────────

┌──────────────────────────────────────────────────────────────┐
│ AGENT: Executive Insights Dashboard (agent_special_002)      │
│ Specialization: Executive Reporting                          │
├──────────────────────────────────────────────────────────────┤
│ Status: PRIMARY ORCHESTRATOR                                 │
│ Available MCP Functions:                                     │
│   1. generate_summary_report                                 │
│   2. revenue_forecasting                                     │
│   3. market_segmentation_analysis                            │
│   4. competitive_intelligence                                │
└──────────────────────────────────────────────────────────────┘

EXECUTION SEQUENCE:
───────────────────

PHASE 1: STATISTICAL VALIDATION (Subtask Delegation)
└─ agent_special_002 delegates to: agent_analytics_001
   ├─ Agent: Data Statistician
   ├─ Access MCP Functions:
   │  ├─ analyze_dataset_statistics (INPUT: Q1 sales data)
   │  ├─ hypothesis_testing (PARAM: H0=no significant difference)
   │  ├─ correlation_analysis (PARAM: find correlations)
   │  └─ normalize_data (PARAM: standardize for modeling)
   ├─ Processing:
   │  ├─ Statistical Tests: p-value < 0.05 ✓
   │  ├─ Correlation: 0.78 customer_spend ↔ visit_frequency
   │  └─ Mean: $427.50, Std Dev: $89.30, Outliers: 2.1%
   └─ Return: {"status": "CONTINUE", "next_agent": "market_segmentation"}

PHASE 2: MARKET SEGMENTATION (Subtask Delegation)
└─ agent_special_002 delegates to: agent_business_001
   ├─ Agent: Market Segmentation Analyst
   ├─ Access MCP Functions:
   │  ├─ market_segmentation_analysis (INPUT: behavioral_data)
   │  ├─ customer_lifetime_value (PARAM: compute CLV per segment)
   │  └─ ab_test_design (PARAM: design validation tests)
   ├─ Processing:
   │  ├─ Segments Identified: 5
   │  │  ├─ Premium High-Value (18%): CLV=$2,450
   │  │  ├─ Growing Engaged (31%): CLV=$892
   │  │  ├─ Occasional Buyers (35%): CLV=$310
   │  │  ├─ At-Risk Churners (12%): CLV=$145
   │  │  └─ New Explorers (4%): CLV=$89
   │  └─ Recommendations: Focus on At-Risk retention
   └─ Return: {"status": "CONTINUE", "next_agent": "revenue_forecast"}

PHASE 3: REVENUE FORECASTING (Subtask Delegation)
└─ agent_special_002 delegates to: agent_business_002
   ├─ Agent: Revenue Forecaster
   ├─ Access MCP Functions:
   │  ├─ revenue_forecasting (INPUT: historical Q1 data)
   │  ├─ customer_lifetime_value (already computed)
   │  └─ ab_test_design (PARAM: test revenue impact)
   ├─ Processing:
   │  ├─ Q2 Forecast: $1.24M (95% CI: $1.15M - $1.33M)
   │  ├─ Q3 Forecast: $1.31M (95% CI: $1.18M - $1.44M)
   │  ├─ Q4 Forecast: $1.52M (trend: +22.6% YoY)
   │  ├─ Seasonality: High in Q4 (+34%), Low in Q1 (-12%)
   │  └─ Growth Rate: 2.1% QoQ average
   └─ Return: {"status": "COMPILE_REPORT"}

PHASE 4: EXECUTIVE REPORT COMPILATION (Primary Task)
└─ agent_special_002 executes:
   ├─ MCP Function: generate_summary_report
   ├─ Compile All Results:
   │  ├─ Statistical Validation: ✓ Data quality: 98.5%
   │  ├─ Market Segments: 5 segments identified with CLV
   │  ├─ Revenue Forecast: Q2-Q4 projections with confidence intervals
   │  ├─ KPI Dashboard:
   │  │  ├─ Avg Customer Value: $427.50
   │  │  ├─ Customer Lifetime Value: $735 (across all segments)
   │  │  ├─ Churn Risk: 12% (At-Risk segment)
   │  │  ├─ Growth Rate: +2.1% QoQ
   │  │  └─ Revenue Growth: +22.6% YoY forecast
   │  └─ Strategic Recommendations:
   │     ├─ 1. Implement retention program for At-Risk segment (12%)
   │     ├─ 2. Expand offerings for Growing Engaged segment (31%)
   │     ├─ 3. Develop premium services for High-Value segment (18%)
   │     └─ 4. Launch acquisition for New Explorers pipeline (4%)
   └─ Return: Comprehensive Executive Report

FINAL OUTPUT:
─────────────
✓ Single Agent Call: YES (agent_special_002)
✓ Multi-Agent Orchestration: 3 agents coordinated
✓ MCP Functions Accessed: 10 functions across 3 agents
✓ Total Processing Time: ~2.3 seconds
✓ Report Quality: 98.5%

CONVERSATION TURNS USED: 1 / unlimited (SINGLE-TURN COMPLETE)
"""

# ============================================================================
# SCENARIO 2: MULTI-TURN CONVERSATION (SAME AGENT)
# ============================================================================

SCENARIO_2_MULTI_TURN = """
┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 2: MULTI-TURN CONVERSATION (SAME AGENT CONTINUATION)          │
└─────────────────────────────────────────────────────────────────────────┘

CONTEXT: User is working with a Code Quality Reviewer on comprehensive
         codebase analysis. Each turn adds more detailed analysis.

═══════════════════════════════════════════════════════════════════════════

TURN 1: Initial Code Review Request
─────────────────────────────────────

USER: "Can you review the payment module in our codebase for code quality
       and potential issues?"

ROUTER ANALYSIS:
├─ Domain: development/code_review
├─ Input Type: source_code
├─ Intent Confidence: 0.95 (clear code review request)
└─ Route Decision: SWITCH to agent_dev_001 (Code Quality Reviewer)
   └─ Reason: Clear development domain, static analysis required

AGENT EXECUTION:
┌──────────────────────────────────────────────────────────────┐
│ AGENT: Code Quality Reviewer (agent_dev_001)                 │
│ Turn Count: 1/15 max                                         │
├──────────────────────────────────────────────────────────────┤
│ MCP Functions Called:                                        │
│  ├─ code_review_static_analysis (payment.py)                │
│  ├─ lint_code_style (check PEP 8)                           │
│  ├─ extract_ast_metrics (complexity analysis)               │
│  └─ detect_code_clones (duplication check)                  │
├──────────────────────────────────────────────────────────────┤
│ Results:                                                     │
│  ├─ Issues Found: 7                                         │
│  │  ├─ 2 Critical (exception handling, SQL injection risk)   │
│  │  ├─ 3 Major (complexity, missing type hints)             │
│  │  └─ 2 Minor (naming conventions, docstrings)             │
│  ├─ Code Complexity: 8.2/10 (HIGH - refactoring needed)     │
│  ├─ Duplicated Blocks: 12% of code                          │
│  └─ Style Violations: 3 (PEP 8)                             │
└──────────────────────────────────────────────────────────────┘

RESPONSE: "Found 7 issues in payment module. Main concerns: SQL injection
          risk, high complexity (8.2/10), and 12% code duplication. Would
          you like me to go deeper on any specific issue?"

═══════════════════════════════════════════════════════════════════════════

TURN 2: Follow-up on Security
──────────────────────────────

USER: "Wait, let's focus on that SQL injection risk. What exactly needs
       to be fixed?"

ROUTER ANALYSIS:
├─ Session State: agent_dev_001 active
├─ Domain Shift: development → development/security (same agent category)
├─ Input Type: code_review_context
├─ Continuation Check: YES - staying within same specialization
├─ Intent Confidence: 0.88 (follow-up clarification)
└─ Route Decision: CONTINUE with agent_dev_001
   └─ Reason: Same domain, follow-up question, agent already context-aware

AGENT EXECUTION:
┌──────────────────────────────────────────────────────────────┐
│ AGENT: Code Quality Reviewer (agent_dev_001)                 │
│ Turn Count: 2/15 max                                         │
├──────────────────────────────────────────────────────────────┤
│ MCP Functions Called:                                        │
│  ├─ code_review_static_analysis (FOCUS: SQL injection)       │
│  ├─ security_vulnerability_scan [DELEGATION]                │
│  └─ lint_code_style (parametrized queries check)            │
├──────────────────────────────────────────────────────────────┤
│ Analysis Results:                                            │
│  ├─ Vulnerable Code Location: payment.py:45-52              │
│  │  ```                                                      │
│  │  query = f"SELECT * FROM orders WHERE user_id={user_id}" │
│  │  ```                                                      │
│  ├─ Risk Level: CRITICAL (CVSS 9.1)                         │
│  ├─ Fix: Use parameterized queries                          │
│  │  ```                                                      │
│  │  query = "SELECT * FROM orders WHERE user_id=%s"         │
│  │  cursor.execute(query, (user_id,))                       │
│  │  ```                                                      │
│  └─ Similar Issues: 2 other locations found                 │
└──────────────────────────────────────────────────────────────┘

RESPONSE: "SQL injection on line 45-52. You're using f-string interpolation
          directly into query. Should use parameterized queries instead. I
          found 2 similar issues elsewhere. Want me to identify all three?"

═══════════════════════════════════════════════════════════════════════════

TURN 3: Request for Full Security Audit
────────────────────────────────────────

USER: "Yes, please identify all three. And after that, can you also check
       our dependency vulnerabilities?"

ROUTER ANALYSIS:
├─ Session State: agent_dev_001 active
├─ Domain Shift: code_review → dependency_management (DIFFERENT category!)
├─ Input Type: [security_context, requirements_files]
├─ Continuation Check: NO - moving from code review to dependency analysis
├─ Intent Confidence: 0.72 (compound request with topic shift)
├─ Multi-Part Request: YES - handle current then switch
└─ Route Decision: COMPLETE CURRENT TASK, THEN SWITCH
   ├─ Part 1: CONTINUE with agent_dev_001 (finish SQL injection audit)
   └─ Part 2: SWITCH to agent_dev_007 (Dependency Manager) [separate turn]

AGENT EXECUTION (PART 1):
┌──────────────────────────────────────────────────────────────┐
│ AGENT: Code Quality Reviewer (agent_dev_001)                 │
│ Turn Count: 3/15 max                                         │
├──────────────────────────────────────────────────────────────┤
│ MCP Functions Called:                                        │
│  ├─ code_review_static_analysis (full security audit)        │
│  ├─ extract_ast_metrics (security patterns)                 │
│  └─ lint_code_style (security best practices)               │
├──────────────────────────────────────────────────────────────┤
│ SQL Injection Findings:                                      │
│  ├─ Location 1: payment.py:45-52 (CRITICAL)                │
│  ├─ Location 2: reports.py:103-110 (CRITICAL)              │
│  ├─ Location 3: dashboard.py:234-241 (CRITICAL)            │
│  └─ All 3 Locations: Use parameterized queries              │
└──────────────────────────────────────────────────────────────┘

RESPONSE (PART 1): "All 3 SQL injection points identified. [Shows code
                    locations]. Now switching to dependency analysis..."

═══════════════════════════════════════════════════════════════════════════

TURN 4: Dependency Vulnerability Check [NEW AGENT]
───────────────────────────────────────────────────

ROUTER ANALYSIS:
├─ Previous Agent: agent_dev_001 (finished)
├─ Domain Shift: code_review → dependency_management
├─ Input Type: requirements_files
├─ Continuation Check: NO - new domain
├─ Intent Confidence: 0.85 (clear dependency analysis request)
└─ Route Decision: SWITCH to agent_dev_007
   └─ Reason: Topic shift detected, new domain requires different agent

AGENT EXECUTION (PART 2):
┌──────────────────────────────────────────────────────────────┐
│ AGENT: Dependency Manager (agent_dev_007)                    │
│ Turn Count: 1/11 max (new agent session)                     │
├──────────────────────────────────────────────────────────────┤
│ MCP Functions Called:                                        │
│  ├─ dependency_analysis (requirements.txt, poetry.lock)      │
│  ├─ security_vulnerability_scan (check CVEs)                │
│  └─ migration_compatibility_check (upgrade paths)           │
├──────────────────────────────────────────────────────────────┤
│ Findings:                                                    │
│  ├─ Total Dependencies: 47                                  │
│  ├─ Vulnerable Packages: 3                                  │
│  │  ├─ django==3.2.0 (CRITICAL: CVE-2021-35042, upgrade to 3.2.13)
│  │  ├─ pillow==8.0.0 (HIGH: CVE-2022-3570, upgrade to 9.0.0)
│  │  └─ requests==2.27.0 (MEDIUM: upgrade to 2.28.0)        │
│  ├─ Outdated Packages: 8                                    │
│  └─ Compatible Updates Available: YES                       │
└──────────────────────────────────────────────────────────────┘

RESPONSE (PART 2): "Found 3 vulnerable packages. Django is critical - update
                    to 3.2.13+. Pillow and requests have medium/high CVEs."

CONVERSATION SUMMARY:
─────────────────────
✓ Agent Sessions: 2 agents across 4 turns
  ├─ agent_dev_001 (Code Quality Reviewer): Turns 1-3 (3/15 max)
  └─ agent_dev_007 (Dependency Manager): Turn 4 (1/11 max)
✓ Topic Shifts: 1 (code review → dependencies)
✓ MCP Functions Used: 9 total
✓ Conversation Complexity: Medium-High
"""

# ============================================================================
# SCENARIO 3: RAPID TOPIC SWITCHING
# ============================================================================

SCENARIO_3_TOPIC_SWITCHING = """
┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 3: RAPID TOPIC SWITCHING (4 DIFFERENT AGENTS IN 5 TURNS)      │
└─────────────────────────────────────────────────────────────────────────┘

CONTEXT: Product manager needs to navigate multiple aspects of a product
         launch in quick succession, requiring rapid agent switching.

═══════════════════════════════════════════════════════════════════════════

TURN 1: Content Planning
────────────────────────

USER: "Help me plan the marketing content strategy for our new product launch."

ROUTER ANALYSIS:
├─ Domain: content
├─ Route Decision: agent_content_007 (Content Strategist)
└─ Confidence: 0.94

EXECUTION:
┌─────────────────────────────────────────────┐
│ AGENT: agent_content_007                    │
│ Specialization: Content Strategy            │
├─────────────────────────────────────────────┤
│ MCP Functions:                              │
│  ├─ content_gap_analysis                    │
│  ├─ keyword_extraction                      │
│  ├─ generate_blog_post                      │
│  └─ content_personalization                 │
├─────────────────────────────────────────────┤
│ Deliverables:                               │
│  ├─ Content Calendar: 12-week plan          │
│  ├─ Key Topics: 23 identified               │
│  ├─ Gaps: Email sequences, case studies     │
│  └─ Recommendations: Launch 8-piece series  │
└─────────────────────────────────────────────┘

RESPONSE: "Created 12-week content plan. 8-piece launch series recommended.
          Identified gaps in email sequences and case studies. Ready?"

TURN COUNT USED: 1/14

═══════════════════════════════════════════════════════════════════════════

TURN 2: Competitor Pricing Analysis
───────────────────────────────────

USER: "Actually, before we finalize content, I need to understand what
       competitors are charging and how we should price."

ROUTER ANALYSIS:
├─ Domain Shift: content → business/pricing
├─ Topic Change: YES - completely different domain
├─ Confidence: 0.89
├─ Route Decision: SWITCH to agent_business_004 (Pricing Strategist)
└─ Reason: Topic shift to pricing/competitive analysis

EXECUTION:
┌─────────────────────────────────────────────┐
│ AGENT: agent_business_004                   │
│ Specialization: Pricing                     │
├─────────────────────────────────────────────┤
│ MCP Functions:                              │
│  ├─ competitive_pricing_analysis            │
│  ├─ market_segmentation_analysis            │
│  └─ revenue_forecasting                     │
├─────────────────────────────────────────────┤
│ Findings:                                   │
│  ├─ Competitor Prices: $49-$199/month       │
│  ├─ Market Gap: $89/month (sweet spot)      │
│  ├─ Revenue Impact: +18% vs $99 pricing     │
│  └─ Elasticity: -1.2 (moderate price sens) │
└─────────────────────────────────────────────┘

RESPONSE: "Competitors range $49-$199. Recommend $89/month - that's 18%
          more revenue than $99 while staying competitive. Market sweet spot."

TURN COUNT USED: 1/12

═══════════════════════════════════════════════════════════════════════════

TURN 3: Market Segment Analysis
───────────────────────────────

USER: "What are my customer segments? Who should I target first?"

ROUTER ANALYSIS:
├─ Domain Shift: pricing → business/segmentation
├─ Topic Change: YES - moving to customer analysis
├─ Confidence: 0.91
├─ Route Decision: SWITCH to agent_business_001 (Market Segmentation Analyst)
└─ Reason: Segment analysis, customer targeting focus

EXECUTION:
┌─────────────────────────────────────────────┐
│ AGENT: agent_business_001                   │
│ Specialization: Market Segmentation         │
├─────────────────────────────────────────────┤
│ MCP Functions:                              │
│  ├─ market_segmentation_analysis            │
│  ├─ customer_lifetime_value                 │
│  └─ ab_test_design                          │
├─────────────────────────────────────────────┤
│ Segments Identified:                        │
│  ├─ Enterprise (8%, CLV: $8,400/yr)         │
│  ├─ Mid-Market (22%, CLV: $2,100/yr)        │
│  ├─ Small Biz (45%, CLV: $540/yr)           │
│  └─ Individuals (25%, CLV: $120/yr)         │
│ Priority: Enterprise 1st, then Mid-Market   │
└─────────────────────────────────────────────┘

RESPONSE: "4 segments identified. Target Enterprise first (8%, high CLV),
          then Mid-Market (22%). Small Biz represents volume but lower LTV."

TURN COUNT USED: 1/14

═══════════════════════════════════════════════════════════════════════════

TURN 4: Product Roadmap Integration
────────────────────────────────────

USER: "Now I need to map this all into our product roadmap. Content
       strategy, pricing model, and feature priorities by segment."

ROUTER ANALYSIS:
├─ Domain Shift: segmentation → orchestration
├─ Topic Change: YES - meta-level orchestration
├─ Request Complexity: HIGH (requires cross-domain synthesis)
├─ Confidence: 0.85
├─ Route Decision: SWITCH to agent_special_001 (Multi-Domain Orchestrator)
└─ Reason: Complex cross-domain workflow requiring coordination

EXECUTION:
┌─────────────────────────────────────────────┐
│ AGENT: agent_special_001                    │
│ Specialization: Workflow Orchestration      │
├─────────────────────────────────────────────┤
│ MCP Functions:                              │
│  ├─ model_training_orchestration            │
│  ├─ container_orchestration                 │
│  └─ product_roadmap_optimization            │
├─────────────────────────────────────────────┤
│ Orchestration Actions:                      │
│  ├─ Retrieve content strategy (agent #1)    │
│  ├─ Integrate pricing ($89/mo) (agent #2)   │
│  ├─ Apply segment priorities (agent #3)     │
│  └─ Generate unified roadmap                │
├─────────────────────────────────────────────┤
│ Output:                                     │
│  ├─ Phase 1 (Q2): Enterprise features       │
│  ├─ Phase 2 (Q3): Mid-Market features       │
│  ├─ Pricing: $89/month base                 │
│  ├─ Content: Launch series aligned to phases│
│  └─ Go-Live: Week 1 of Q2                   │
└─────────────────────────────────────────────┘

RESPONSE: "Coordinated all inputs into roadmap. Phase 1 targets Enterprise
          with premium content. Q2 launch at $89/month. Full roadmap ready."

TURN COUNT USED: 1/20

═══════════════════════════════════════════════════════════════════════════

TURN 5: Validation & A/B Testing
────────────────────────────────

USER: "Before we commit, how should we validate this? Any A/B testing
       recommendations?"

ROUTER ANALYSIS:
├─ Domain Shift: orchestration → business/testing
├─ Topic Change: YES - validation methodology
├─ Confidence: 0.88
├─ Route Decision: SWITCH to agent_business_001 (Market Segmentation Analyst)
└─ Reason: A/B test design capability, customer segment focus

EXECUTION:
┌─────────────────────────────────────────────┐
│ AGENT: agent_business_001 (NEW SESSION)     │
│ Specialization: Market Segmentation         │
├─────────────────────────────────────────────┤
│ MCP Functions:                              │
│  ├─ ab_test_design                          │
│  ├─ customer_lifetime_value                 │
│  └─ market_segmentation_analysis            │
├─────────────────────────────────────────────┤
│ A/B Test Design:                            │
│  ├─ Test 1: Price sensitivity ($79 vs $89)  │
│  │  ├─ Sample: 2,000 per variant            │
│  │  ├─ Duration: 2 weeks                    │
│  │  └─ Success Metric: Conversion rate      │
│  ├─ Test 2: Content messaging (2 variants)  │
│  │  ├─ Sample: 5,000 per variant            │
│  │  ├─ Duration: 3 weeks                    │
│  │  └─ Success Metric: Engagement           │
│  └─ Success Criteria: 95% confidence        │
└─────────────────────────────────────────────┘

RESPONSE: "Recommend two A/B tests: price sensitivity ($79 vs $89) and
          content messaging. 2-3 week test windows needed for statistical power."

TURN COUNT USED: 1/14 (new session)

═══════════════════════════════════════════════════════════════════════════

CONVERSATION ANALYTICS:
───────────────────────
Total Turns: 5
Agent Switches: 5 (every turn!)
├─ Turn 1: agent_content_007 (Content Strategist)
├─ Turn 2: agent_business_004 (Pricing Strategist)
├─ Turn 3: agent_business_001 (Market Segmentation Analyst)
├─ Turn 4: agent_special_001 (Multi-Domain Orchestrator)
└─ Turn 5: agent_business_001 (Market Segmentation Analyst - return)

Domains Traversed: 4
├─ content (1 turn)
├─ business/pricing (1 turn)
├─ business/segmentation (2 turns)
└─ orchestration (1 turn)

MCP Functions Used: 15 total
Router Decisions: 5/5 correct (100% accuracy)
Average Switch Confidence: 0.89

KEY PATTERN: Rapid topic switching with high semantic understanding
             required. Router correctly identified each domain shift
             and routed to appropriate specialist.
"""

# ============================================================================
# SCENARIO 4: COMPLEX MULTI-AGENT WORKFLOW
# ============================================================================

SCENARIO_4_COMPLEX_WORKFLOW = """
┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 4: COMPLEX MULTI-AGENT WORKFLOW (RESEARCH TO IMPLEMENTATION)  │
└─────────────────────────────────────────────────────────────────────────┘

CONTEXT: User is conducting research on implementing a new ML model for
         fraud detection, spanning research, security, architecture, and
         implementation planning across 8 turns.

═══════════════════════════════════════════════════════════════════════════

TURN 1: Research Foundation
────────────────────────────

USER: "I need to build a fraud detection system. Let me start with current
       research on state-of-the-art approaches."

ROUTER → agent_research_001 (Literature Reviewer)
MCP Functions: literature_review, citation_network_analysis, trend_forecasting
Output: 45 key papers, 3 trending approaches identified
Turn Count: 1/18

═══════════════════════════════════════════════════════════════════════════

TURN 2: Hypothesis Development
───────────────────────────────

USER: "Based on those papers, what approach would work best for our
       specific use case? We have transactional data with ~2% fraud rate."

ROUTER → agent_research_004 (Hypothesis Generator)
MCP Functions: hypothesis_generation, data_quality_assessment, literature_review
Output: 3 candidate hypotheses, recommended: ensemble approach
Turn Count: 1/13

═══════════════════════════════════════════════════════════════════════════

TURN 3: Research Methodology
─────────────────────────────

USER: "How should we validate which approach works best? What's the ideal
       experimental design?"

ROUTER → agent_research_005 (Experiment Designer)
MCP Functions: experiment_design_optimization, research_methodology_recommendation, hypothesis_generation
Output: Experimental protocol, sample size: 50K transactions, test duration: 4 weeks
Turn Count: 1/14

═══════════════════════════════════════════════════════════════════════════

TURN 4: Security Architecture Review
─────────────────────────────────────

USER: "Now I need to think about security. ML models can be attacked.
       What are the security implications?"

ROUTER → agent_dev_002 (Security Vulnerability Scanner)
MCP Functions: security_vulnerability_scan, code_review_static_analysis, dependency_analysis
Output: 5 security vectors identified, model poisoning risk: HIGH
Turn Count: 1/12

═══════════════════════════════════════════════════════════════════════════

TURN 5: Cross-Functional Strategic Planning
─────────────────────────────────────────────

USER: "I need to integrate this into our product roadmap, consider ROI,
       implementation timeline, and cross-functional impacts."

ROUTER → agent_special_003 (Cross-Functional Advisor)
MCP Functions: code_review_static_analysis, market_segmentation_analysis,
              infrastructure_as_code_validation, hypothesis_generation
Output: Strategic recommendation, implementation phases, ROI: +24% first year
Turn Count: 1/18

═══════════════════════════════════════════════════════════════════════════

TURN 6: ML Model Approach Selection
────────────────────────────────────

USER: "For the actual ML model, should we use ensemble methods or
       single models? What's the best approach for fraud detection?"

ROUTER → agent_ml_005 (Model Ensemble Builder)
MCP Functions: model_ensemble_creation, model_evaluation_metrics, model_drift_detection
Output: Ensemble recommended, 3-model stack: Random Forest + XGBoost + Neural Net
Turn Count: 1/13

═══════════════════════════════════════════════════════════════════════════

TURN 7: Implementation Planning & Infrastructure
─────────────────────────────────────────────────

USER: "How should we deploy this? Infrastructure requirements?
       Monitoring strategy?"

ROUTER → agent_devops_002 (Container Orchestration Manager)
MCP Functions: container_orchestration, monitor_system_health, cost_optimization_analysis
Output: Kubernetes deployment, auto-scaling rules, monitoring dashboard, cost: $3.2K/month
Turn Count: 1/12

═══════════════════════════════════════════════════════════════════════════

TURN 8: End-to-End Workflow Orchestration
───────────────────────────────────────────

USER: "Pull all of this together. I need a complete implementation plan
       that includes research findings, security, architecture, ML model,
       deployment, and go-live timeline."

ROUTER → agent_special_001 (Multi-Domain Orchestrator)
MCP Functions: model_training_orchestration, container_orchestration, product_roadmap_optimization

ORCHESTRATION FLOW:
┌─────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR RETRIEVES & SYNTHESIZES:                           │
├─────────────────────────────────────────────────────────────────┤
│ FROM Turn 1 (Literature Reviewer):                              │
│  └─ State-of-the-art approaches (3 options)                     │
│                                                                 │
│ FROM Turn 2 (Hypothesis Generator):                             │
│  └─ Recommended: Ensemble fraud detection model                 │
│                                                                 │
│ FROM Turn 3 (Experiment Designer):                              │
│  └─ Validation protocol: 50K transactions, 4 weeks              │
│                                                                 │
│ FROM Turn 4 (Security Scanner):                                 │
│  └─ Security measures: Model poisoning protection              │
│                                                                 │
│ FROM Turn 5 (Strategic Advisor):                                │
│  └─ ROI: +24% first year, 18-month payback                     │
│                                                                 │
│ FROM Turn 6 (ML Ensemble Builder):                              │
│  └─ Model Architecture: RF + XGBoost + NN ensemble              │
│                                                                 │
│ FROM Turn 7 (DevOps Manager):                                   │
│  └─ Infrastructure: K8s, auto-scaling, $3.2K/month             │
│                                                                 │
│ SYNTHESIZED OUTPUT:                                             │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│ 🎯 FRAUD DETECTION SYSTEM - IMPLEMENTATION ROADMAP             │
│                                                                 │
│ PHASE 1: RESEARCH & VALIDATION (Weeks 1-4)                     │
│  ├─ Finalize hypothesis (ensemble approach)                    │
│  ├─ Run A/B experiments on training data                       │
│  ├─ Security threat modeling                                   │
│  └─ Expected Output: Validated model, security plan            │
│                                                                 │
│ PHASE 2: MODEL DEVELOPMENT (Weeks 5-12)                        │
│  ├─ Train 3-model ensemble (RF, XGBoost, NN)                   │
│  ├─ Implement model poisoning defenses                         │
│  ├─ Target Performance: 95%+ precision on fraud                │
│  └─ Expected Output: Production-ready model                    │
│                                                                 │
│ PHASE 3: INFRASTRUCTURE SETUP (Weeks 9-14)                     │
│  ├─ Deploy K8s cluster with auto-scaling                       │
│  ├─ Configure monitoring & alerting                            │
│  ├─ Set up model versioning & rollback                         │
│  └─ Expected Output: Production infrastructure                 │
│                                                                 │
│ PHASE 4: INTEGRATION & TESTING (Weeks 13-16)                   │
│  ├─ Integrate model into payment pipeline                      │
│  ├─ Run security penetration testing                           │
│  ├─ Performance validation at scale                            │
│  └─ Expected Output: Tested, hardened system                   │
│                                                                 │
│ PHASE 5: PILOT & MONITORING (Weeks 17-20)                      │
│  ├─ Deploy to 10% of traffic (canary)                          │
│  ├─ Monitor model drift & false positives                      │
│  ├─ Collect feedback from fraud team                           │
│  └─ Expected Output: Validated in production                   │
│                                                                 │
│ PHASE 6: FULL ROLLOUT (Week 21)                                │
│  ├─ Gradual ramp to 100% traffic                               │
│  ├─ Continuous model retraining (weekly)                       │
│  ├─ Ongoing security monitoring                                │
│  └─ Expected Output: Live fraud detection (24/7)               │
│                                                                 │
│ 📊 KEY METRICS & SUCCESS CRITERIA:                              │
│  ├─ Model Precision: ≥95% (minimize false positives)           │
│  ├─ Model Recall: ≥90% (catch real fraud)                      │
│  ├─ Latency: <100ms per prediction                             │
│  ├─ Uptime: 99.99%                                             │
│  ├─ Model Drift Alert: Enabled                                 │
│  └─ Security Status: All controls in place                     │
│                                                                 │
│ 💰 ROI PROJECTION:                                              │
│  ├─ Fraud Loss Reduction: $850K/year (2% of current fraud)    │
│  ├─ Infrastructure Cost: $38.4K/year                           │
│  ├─ Development Cost (amortized): $120K/year                   │
│  ├─ Net Benefit: +$692K first year                             │
│  └─ Payback Period: 2.4 months                                 │
│                                                                 │
│ 🔒 SECURITY MEASURES:                                           │
│  ├─ Model poisoning detection                                  │
│  ├─ Adversarial robustness testing (quarterly)                │
│  ├─ Input validation on all features                           │
│  ├─ Encrypted model storage                                    │
│  └─ Security audit: Passed (no critical issues)                │
│                                                                 │
│ ⏱️ TIMELINE: 20-week end-to-end deployment                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Output: Comprehensive 20-week implementation roadmap with all components
Turn Count: 1/20

═══════════════════════════════════════════════════════════════════════════

WORKFLOW ANALYTICS:
───────────────────
Total Turns: 8
Agent Utilization: 8 different agents
Domains Covered: 5 (research, security, business, ML, DevOps)

Agent Call Sequence:
  1. agent_research_001 (Literature Reviewer) [turn 1]
  2. agent_research_004 (Hypothesis Generator) [turn 2]
  3. agent_research_005 (Experiment Designer) [turn 3]
  4. agent_dev_002 (Security Vulnerability Scanner) [turn 4]
  5. agent_special_003 (Cross-Functional Advisor) [turn 5]
  6. agent_ml_005 (Model Ensemble Builder) [turn 6]
  7. agent_devops_002 (Container Orchestration Manager) [turn 7]
  8. agent_special_001 (Multi-Domain Orchestrator) [turn 8]

MCP Functions Accessed: 21 total
├─ Research Functions: 6
├─ Development Functions: 3
├─ Business Functions: 2
├─ ML Functions: 4
├─ DevOps Functions: 3
└─ Orchestration Functions: 3

Router Decisions: 8/8 correct (100%)
Average Confidence: 0.91
Workflow Completion: 100%

KEY SUCCESS FACTOR: Progressive specialization with end-to-end orchestration.
                   Each turn added deeper domain expertise, culminating in
                   comprehensive cross-functional strategy.
"""

# ============================================================================
# ROUTER DECISION MATRIX
# ============================================================================

ROUTER_DECISION_MATRIX = """
┌─────────────────────────────────────────────────────────────────────────┐
│ ROUTER DECISION LOGIC MATRIX                                            │
└─────────────────────────────────────────────────────────────────────────┘

HOW THE ROUTER MAKES AGENT SELECTION DECISIONS:
════════════════════════════════════════════════

1. COLD START (Turn 1, No Active Session)
   ─────────────────────────────────────────
   Input: User message
   
   Logic:
   ├─ Extract keywords & intent
   ├─ Match to MCP function categories
   ├─ Identify input_types required
   └─ Select agent with best specialization match
   
   Example:
   └─ User: "Analyze sales data and segment customers"
      ├─ Keywords: [analyze, data, segment, customers]
      ├─ Input Types: [business_data, sales_data]
      ├─ Best Specializations: [Statistical Analysis, Market Segmentation]
      ├─ Top Candidates:
      │  ├─ agent_analytics_005 (confidence: 0.92)
      │  ├─ agent_business_001 (confidence: 0.88)
      │  └─ agent_special_002 (confidence: 0.85)
      └─ Decision: SELECT agent_analytics_005 (highest confidence)

2. WARM CONTINUATION (Turn N+1, Same Domain)
   ───────────────────────────────────────────
   Input: User message, active_agent, conversation_history
   
   Logic:
   ├─ Check if new intent matches active_agent specialization
   ├─ Compute semantic similarity to previous turns
   ├─ Check agent's remaining turn budget
   └─ Decide: CONTINUE or SWITCH
   
   Decision Rule:
   ├─ IF similarity > 0.75 AND turns_remaining > 0 → CONTINUE
   ├─ IF similarity > 0.5 AND similarity < 0.75 → DELEGATE (same agent)
   └─ IF similarity < 0.5 → SWITCH
   
   Example:
   └─ Active: agent_analytics_005, Turn: 1/20
      └─ User: "Can you forecast revenue for Q2?"
         ├─ Similarity to Turn 1: 0.82 (SAME DOMAIN)
         ├─ New intent: [forecasting, revenue]
         ├─ Active agent capabilities: [report generation, KPI tracking]
         ├─ Agent has function: "forecast_trends" (MATCH)
         └─ Decision: CONTINUE with agent_analytics_005

3. TOPIC SHIFT DETECTION (Turn N+1, Different Domain)
   ──────────────────────────────────────────────────
   Input: User message, active_agent, conversation_history
   
   Logic:
   ├─ Identify new domain
   ├─ Check if completely different from active_agent
   ├─ Score match to alternative agents
   └─ Switch to best match if confidence > threshold
   
   Decision Rule:
   ├─ IF new_domain != active_domain → ANALYZE SWITCH
   ├─ IF best_match_confidence > 0.80 → SWITCH
   ├─ IF best_match_confidence < 0.70 → DELEGATE to orchestrator
   └─ IF 0.70 < confidence < 0.80 → USER CHOICE PROMPT
   
   Example:
   └─ Active: agent_analytics_005, Turn: 3/20
      └─ User: "I need to review code for security vulnerabilities"
         ├─ Current domain: analytics
         ├─ New domain: development/security
         ├─ Similarity: 0.15 (VERY DIFFERENT)
         ├─ Best alternative: agent_dev_002 (confidence: 0.95)
         ├─ Switch confidence: 0.95 > 0.80 (THRESHOLD)
         └─ Decision: SWITCH to agent_dev_002

4. COMPLEX MULTI-DOMAIN REQUESTS
   ──────────────────────────────
   Input: User message with multiple domains
   
   Logic:
   ├─ Identify all domains in request
   ├─ IF single_domain → route to specialist
   ├─ IF multi_domain AND clear_priority → route to primary
   ├─ IF multi_domain AND equal_complexity → route to orchestrator
   └─ IF multi_domain AND cross_functional → route to cross_functional_advisor
   
   Example:
   └─ User: "Plan content strategy, set pricing, design A/B tests"
      ├─ Domains: [content, business/pricing, business/testing]
      ├─ Complexity: HIGH (3 domains)
      ├─ Integration Needed: YES
      ├─ Best Route: agent_special_002 (Executive Dashboard)
      │  OR agent_special_003 (Cross-Functional Advisor)
      └─ Decision: ROUTE to orchestrator for synthesis

CONFIDENCE SCORING FORMULA:
═════════════════════════════

confidence = (
    0.4 * specialization_match +
    0.3 * capability_match +
    0.2 * input_type_match +
    0.1 * conversation_continuity
)

Where:
├─ specialization_match: How well agent's specialization matches request
├─ capability_match: How many agent capabilities overlap with request
├─ input_type_match: How well input_types align with request data
└─ conversation_continuity: Score bonus if continuing same conversation

Example Calculation:
└─ Agent: agent_analytics_001
   └─ Request: "Analyze dataset for correlations and distribution"
      ├─ Specialization match: 0.95 (Statistical Analysis)
      ├─ Capability match: 0.92 (has correlation, distribution, analysis)
      ├─ Input type match: 0.88 (numeric_data matches)
      ├─ Conversation continuity: 0.50 (first turn, no bonus)
      └─ Final Confidence: 0.87 (HIGH)

WHEN TO INVOKE ORCHESTRATOR AGENTS:
════════════════════════════════════

Invoke agent_special_001 (Multi-Domain Orchestrator) when:
├─ Request spans 3+ domains
├─ Requires coordination between agents
├─ User asks to "pull it all together"
└─ Complex workflow needs sequencing

Invoke agent_special_002 (Executive Dashboard) when:
├─ High-level synthesis needed
├─ Multiple data streams to consolidate
├─ Executive reporting requested
└─ KPI dashboard generation needed

Invoke agent_special_003 (Cross-Functional Advisor) when:
├─ Technical + business decision
├─ Strategic advice needed
├─ Tradeoff analysis required
└─ Multi-stakeholder impact assessment

Invoke agent_special_004 (Incident Response) when:
├─ Production issue detected
├─ Multiple systems affected
├─ Rapid response needed
└─ Coordination across domains required
"""

# ============================================================================
# PRINT ALL SCENARIOS
# ============================================================================

if __name__ == "__main__":
    print(SCENARIO_1_SINGLE_TURN)
    print("\n" + "="*80 + "\n")
    print(SCENARIO_2_MULTI_TURN)
    print("\n" + "="*80 + "\n")
    print(SCENARIO_3_TOPIC_SWITCHING)
    print("\n" + "="*80 + "\n")
    print(SCENARIO_4_COMPLEX_WORKFLOW)
    print("\n" + "="*80 + "\n")
    print(ROUTER_DECISION_MATRIX)
    
    print("\n" + "="*80)
    print("✓ CONVERSATION GUIDE LOADED")
    print("="*80)
    print("\nScenarios Covered:")
    print("  1. Complex Single-Turn Conversation")
    print("     - 1 primary orchestrator agent")
    print("     - 3 delegated specialist agents")
    print("     - 10 MCP functions accessed")
    print("\n  2. Multi-Turn Conversation (Same Agent)")
    print("     - 4 turns with 2 agents")
    print("     - 1 topic switch (development)")
    print("     - 9 MCP functions accessed")
    print("\n  3. Rapid Topic Switching")
    print("     - 5 turns with 5 agent switches")
    print("     - Every turn = different agent")
    print("     - 15 MCP functions accessed")
    print("\n  4. Complex Multi-Agent Workflow")
    print("     - 8 turns spanning research → implementation")
    print("     - 8 different agents coordinated")
    print("     - 21 MCP functions accessed")
    print("     - 20-week project roadmap synthesized")
    print("\n" + "="*80)
