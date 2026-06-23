---
name: workflow-skill
description: Multi-agent workflow orchestration skill that routes user requests to specialized agents across 8 categories (Analytics, Development, DevOps, Content, Research, ML, Business, Specialized).
metadata:
  adk_additional_tools:
    - classify_intent
    - analyze_dataset_statistics
    - code_review_static_analysis
    - security_vulnerability_scan
    - forecast_trends
    - generate_documentation
    - generate_summary_report
  agent_categories:
    - analytics
    - development
    - devops
    - content
    - research
    - ml
    - business
    - specialized
  total_agents: 60
---

## Workflow Steps

### Step 1: Intent Classification
Identify the user's intent using the intent classifier module:
- Load intent rules from `intent_classifier/intent_rules.yml`
- Use `classify_intent()` function from `router.intent_classifier.classifier`
- Extract primary domain and specialized keywords
- Map to agent category and specific agent

### Step 2: Agent Selection
Select the appropriate agent(s) from available categories:
- **Analytics Agents** (10): Statistical analysis, forecasting, clustering, regression, anomaly detection
- **Development Agents** (10): Code quality, security, testing, performance, documentation, refactoring, dependencies, git analytics, database schema, API validation
- **DevOps Agents** (8): System monitoring, container orchestration, infrastructure validation, disaster recovery, networking, cost optimization, compliance, database replication
- **Content Agents** (8): Blog creation, sentiment analysis, summarization, grammar checking, plagiarism detection, translation, strategy, voice/tone
- **Research Agents** (8): Literature review, knowledge graphs, competitive intelligence, hypothesis generation, experiment design, meta-analysis, data quality, citations
- **ML Agents** (6): Model training, hyperparameter tuning, model interpretation, data augmentation, ensemble building, MLOps
- **Business Agents** (6): Market segmentation, revenue forecasting, product roadmap, pricing strategy, customer journey, partnerships
- **Specialized Agents** (4): Multi-domain orchestration, executive insights, cross-functional advisory, incident response

### Step 3: Task Planning
Create a TODO list of sequential tasks:
- Break down user request into subtasks
- Identify required agents and their capabilities
- Determine data flow between agents
- Plan tool access and function calls
- Establish success criteria

### Step 4: Agent Workflow Execution
Execute each selected agent in sequence:
- Load agent from `app.agents` module
- Initialize agent with request context
- Provide agent with access to MCP functions
- Execute agent workflow
- Collect results and metadata
- Pass results to next agent if multi-step

### Step 5: Tool Invocation
If an agent requires specific tools not directly available:
- Call MCP functions from `mcp_server.custom_mcp_server`
- Access specialized tools by agent category
- Aggregate results for downstream processing
- Log tool calls and responses

### Step 6: Result Aggregation
Combine outputs from all agents:
- Merge analysis results
- Validate completeness
- Format response for user
- Track token usage via TokenCostCalculator callbacks
- Return formatted result with agent metadata
 