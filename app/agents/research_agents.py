from app.custom_llm_agent import CustomLlmAgent

RESEARCH_AGENTS = [
    CustomLlmAgent(
        id="agent_research_001",
        name="literature_reviewer",
        description="Conducts comprehensive literature reviews",
        category="research",
        specialization="Literature Analysis",
        mcp_functions=[
            "literature_review", "citation_network_analysis",
            "trend_forecasting"
        ],
        capabilities=["literature search", "paper analysis", "synthesis"],
        input_types=["topic", "research_question"],
        output_types=["review_report", "key_papers", "trends"],
        max_conversation_turns=18
    ),
    CustomLlmAgent(
        id="agent_research_002",
        name="knowledge_graph_constructor",
        description="Builds knowledge graphs from unstructured data",
        category="research",
        specialization="Knowledge Graphs",
        mcp_functions=[
            "knowledge_graph_construction", "data_source_discovery",
            "entity_relation_extraction"
        ],
        capabilities=["graph building", "relationship mapping", "entity linking"],
        input_types=["documents", "data_sources"],
        output_types=["knowledge_graph", "entities", "relations"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_research_003",
        name="competitive_intelligence_agent",
        description="Gathers and analyzes competitive intelligence",
        category="research",
        specialization="Competitive Analysis",
        mcp_functions=[
            "competitive_intelligence", "trend_forecasting",
            "data_source_discovery"
        ],
        capabilities=["competitor tracking", "market analysis", "trend detection"],
        input_types=["competitor_list", "market_data"],
        output_types=["intelligence_report", "opportunities", "threats"],
        max_conversation_turns=15
    ),
    CustomLlmAgent(
        id="agent_research_004",
        name="hypothesis_generator",
        description="Generates research hypotheses based on data",
        category="research",
        specialization="Hypothesis Development",
        mcp_functions=[
            "hypothesis_generation", "data_quality_assessment",
            "literature_review"
        ],
        capabilities=["hypothesis creation", "testing design", "validation"],
        input_types=["observations", "research_context"],
        output_types=["hypotheses", "supporting_evidence", "test_plan"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_research_005",
        name="experiment_designer",
        description="Designs optimal experiments and studies",
        category="research",
        specialization="Research Design",
        mcp_functions=[
            "experiment_design_optimization", "research_methodology_recommendation",
            "hypothesis_generation"
        ],
        capabilities=["experiment design", "power analysis", "sample sizing"],
        input_types=["research_question", "constraints"],
        output_types=["experiment_design", "protocol", "sample_size"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_research_006",
        name="meta_analysis_conductor",
        description="Conducts meta-analyses and systematic reviews",
        category="research",
        specialization="Meta-Analysis",
        mcp_functions=[
            "meta_analysis_synthesis", "data_quality_assessment",
            "trend_forecasting"
        ],
        capabilities=["meta-analysis", "effect size calculation", "heterogeneity assessment"],
        input_types=["studies", "effect_sizes"],
        output_types=["meta_analysis_report", "conclusions", "recommendations"],
        max_conversation_turns=16
    ),
    CustomLlmAgent(
        id="agent_research_007",
        name="data_quality_assessor",
        description="Assesses data quality and integrity",
        category="research",
        specialization="Data Quality",
        mcp_functions=[
            "data_quality_assessment", "data_source_discovery",
            "institutional_repository_indexing"
        ],
        capabilities=["quality assessment", "validation", "cleaning"],
        input_types=["dataset", "quality_criteria"],
        output_types=["quality_report", "issues", "recommendations"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_research_008",
        name="repository_citation_manager",
        description="Manages institutional repositories and citations",
        category="research",
        specialization="Repository Management",
        mcp_functions=[
            "institutional_repository_indexing", "citation_network_analysis",
            "data_source_discovery"
        ],
        capabilities=["indexing", "citation management", "discoverability"],
        input_types=["documents", "metadata"],
        output_types=["indexed_content", "citation_metrics", "recommendations"],
        max_conversation_turns=11
    ),
]
