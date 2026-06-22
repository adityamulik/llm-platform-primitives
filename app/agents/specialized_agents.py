from app.custom_llm_agent import CustomLlmAgent

SPECIALIZED_AGENTS = [
    CustomLlmAgent(
        id="agent_special_001",
        name="multi_domain_orchestrator",
        description="Coordinates complex workflows across multiple domains",
        category="orchestration",
        specialization="Workflow Orchestration",
        mcp_functions=[
            "model_training_orchestration", "container_orchestration",
            "product_roadmap_optimization"
        ],
        capabilities=["workflow orchestration", "coordination", "monitoring"],
        input_types=["workflow_spec", "configuration"],
        output_types=["execution_plan", "monitoring", "results"],
        max_conversation_turns=20
    ),
    CustomLlmAgent(
        id="agent_special_002",
        name="executive_insights_dashboard",
        description="Provides executive-level insights and reporting",
        category="business",
        specialization="Executive Reporting",
        mcp_functions=[
            "generate_summary_report", "revenue_forecasting",
            "market_segmentation_analysis", "competitive_intelligence"
        ],
        capabilities=["report generation", "KPI tracking", "insight synthesis"],
        input_types=["business_data", "metrics"],
        output_types=["executive_report", "dashboards", "alerts"],
        max_conversation_turns=16
    ),
    CustomLlmAgent(
        id="agent_special_003",
        name="cross_functional_advisor",
        description="Provides advice across technical and business domains",
        category="advisory",
        specialization="Strategic Advisory",
        mcp_functions=[
            "code_review_static_analysis", "market_segmentation_analysis",
            "infrastructure_as_code_validation", "hypothesis_generation"
        ],
        capabilities=["cross-functional analysis", "strategic recommendations"],
        input_types=["business_case", "technical_specs"],
        output_types=["recommendations", "analysis", "roadmap"],
        max_conversation_turns=18
    ),
    CustomLlmAgent(
        id="agent_special_004",
        name="incident_response_coordinator",
        description="Coordinates response to incidents across systems",
        category="operations",
        specialization="Incident Management",
        mcp_functions=[
            "incident_response_automation", "monitor_system_health",
            "log_aggregation_query", "disaster_recovery_plan"
        ],
        capabilities=["incident coordination", "response planning", "resolution"],
        input_types=["incident_data", "system_state"],
        output_types=["response_plan", "actions", "status_updates"],
        max_conversation_turns=15
    ),
]
