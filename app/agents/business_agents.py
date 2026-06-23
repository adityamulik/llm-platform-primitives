from app.custom_llm_agent import CustomLlmAgent
from google.adk.models.lite_llm import LiteLlm
from prompt_registry import get_prompt

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

BUSINESS_AGENTS = [
    CustomLlmAgent(
        id="agent_business_001",
        name="market_segmentation_analyst",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Performs market segmentation and customer analysis",
        category="business",
        specialization="Market Segmentation",
        mcp_functions=[
            "market_segmentation_analysis", "customer_lifetime_value",
            "ab_test_design"
        ],
        capabilities=["segmentation analysis", "profiling", "targeting"],
        input_types=["customer_data", "behavioral_data"],
        output_types=["segments", "profiles", "recommendations"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_business_002",
        name="revenue_forecaster",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Forecasts revenue and business metrics",
        category="business",
        specialization="Revenue Forecasting",
        mcp_functions=[
            "revenue_forecasting", "customer_lifetime_value",
            "ab_test_design"
        ],
        capabilities=["revenue forecasting", "trend analysis", "scenario modeling"],
        input_types=["historical_data", "business_metrics"],
        output_types=["forecast", "confidence_intervals", "scenarios"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_business_003",
        name="product_roadmap_strategist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Optimizes product roadmap and prioritization",
        category="business",
        specialization="Product Strategy",
        mcp_functions=[
            "product_roadmap_optimization", "market_segmentation_analysis",
            "competitive_pricing_analysis"
        ],
        capabilities=["roadmap planning", "prioritization", "impact assessment"],
        input_types=["features", "constraints"],
        output_types=["roadmap", "timeline", "impact_analysis"],
        max_conversation_turns=15
    ),
    CustomLlmAgent(
        id="agent_business_004",
        name="pricing_strategist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Analyzes pricing and recommends strategies",
        category="business",
        specialization="Pricing",
        mcp_functions=[
            "competitive_pricing_analysis", "market_segmentation_analysis",
            "revenue_forecasting"
        ],
        capabilities=["pricing analysis", "competitor benchmarking", "optimization"],
        input_types=["product", "market_data"],
        output_types=["pricing_strategy", "recommendations", "impact"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        id="agent_business_005",
        name="customer_journey_mapper",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Maps and optimizes customer journeys",
        category="business",
        specialization="Customer Experience",
        mcp_functions=[
            "customer_journey_mapping", "market_segmentation_analysis",
            "ab_test_design"
        ],
        capabilities=["journey mapping", "touchpoint analysis", "optimization"],
        input_types=["customer_data", "interactions"],
        output_types=["journey_map", "insights", "improvements"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_business_006",
        name="strategic_partnerships_manager",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("research_agent"),
        description="Identifies and analyzes partnership opportunities",
        category="business",
        specialization="Partnerships",
        mcp_functions=[
            "partnership_opportunity_analysis", "competitive_intelligence",
            "market_entry_risk_assessment"
        ],
        capabilities=["opportunity identification", "fit analysis", "negotiation support"],
        input_types=["company_profile", "market_data"],
        output_types=["opportunities", "recommendations", "partnership_plan"],
        max_conversation_turns=14
    ),
]
