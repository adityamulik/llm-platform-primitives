
import logging
from app.custom_llm_agent import CustomLlmAgent
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

from prompt_registry import get_prompt

ANALYTICS_AGENTS = [
    CustomLlmAgent(
        id="agent_analytics_001",
        name="data_statistician",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Analyzes data distributions, correlations, and statistical properties",
        category="analytics",
        specialization="Statistical Analysis",
        mcp_functions=[
            "analyze_dataset_statistics", "correlation_analysis", "distribution_fitting",
            "hypothesis_testing", "normalize_data", "percentiles_calculation"
        ],
        capabilities=["distribution analysis", "correlation detection", "outlier identification"],
        input_types=["numeric_data", "timeseries"],
        output_types=["statistical_report", "insights", "recommendations"],
        max_conversation_turns=15
    ),
    CustomLlmAgent(
        id="agent_analytics_002",
        name="time_series_forecaster",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Forecasts future trends and patterns in time series data",
        category="analytics",
        specialization="Time Series Analysis",
        mcp_functions=[
            "forecast_trends", "extract_time_series_features", "detect_anomalies",
            "correlation_analysis"
        ],
        capabilities=["trend forecasting", "seasonality detection", "anomaly detection"],
        input_types=["timeseries", "sequential_data"],
        output_types=["forecast", "trend_analysis", "anomaly_alerts"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        # id="agent_analytics_003",
        name="data_clustering_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Segments data into meaningful clusters and groups",
        category="analytics",
        specialization="Data Clustering",
        mcp_functions=[
            "segment_data_clusters", "extract_time_series_features",
            "calculate_percentiles"
        ],
        capabilities=["customer segmentation", "cluster analysis", "group identification"],
        input_types=["multidimensional_data", "feature_vectors"],
        output_types=["cluster_report", "segment_profiles", "labels"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        # id="agent_analytics_004",
        name="comparative_analytics_expert",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
    # tools=[_context7_toolset],
        description="Compares datasets and identifies key differences and patterns",
        category="analytics",
        specialization="Comparative Analysis",
        mcp_functions=[
            "compare_datasets", "correlation_analysis", "hypothesis_testing",
            "regression_analysis"
        ],
        capabilities=["dataset comparison", "A/B analysis", "benchmark comparison"],
        input_types=["multiple_datasets", "experimental_data"],
        output_types=["comparison_report", "statistical_tests", "conclusions"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        # id="agent_analytics_005",
        name="business_intelligence_analyst",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
    # tools=[_context7_toolset],
        description="Generates comprehensive analytics reports and business insights",
        category="analytics",
        specialization="BI & Reporting",
        mcp_functions=[
            "generate_summary_report", "pivot_table_analysis", "correlation_analysis",
            "forecast_trends"
        ],
        capabilities=["report generation", "KPI tracking", "insight extraction"],
        input_types=["business_data", "sales_data", "operational_metrics"],
        output_types=["BI_report", "dashboard_data", "executive_summary"],
        max_conversation_turns=20
    ),
    CustomLlmAgent(
        # id="agent_analytics_006",
        name="regression_analysis_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Performs regression analysis and predictive modeling",
        category="analytics",
        specialization="Regression & Prediction",
        mcp_functions=[
            "regression_analysis", "distribution_fitting", "normalize_data",
            "hypothesis_testing"
        ],
        capabilities=["linear regression", "polynomial fitting", "prediction"],
        input_types=["labeled_data", "features"],
        output_types=["regression_model", "predictions", "coefficients"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        # id="agent_analytics_007",
        name="matrix_operations_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Performs complex matrix operations and linear algebra computations",
        category="analytics",
        specialization="Linear Algebra",
        mcp_functions=[
            "matrix_operations", "regression_analysis", "normalize_data"
        ],
        capabilities=["matrix multiplication", "eigen decomposition", "transformations"],
        input_types=["matrices", "tensor_data"],
        output_types=["matrix_results", "transformed_data", "decomposition"],
        max_conversation_turns=8
    ),
    CustomLlmAgent(
        # id="agent_analytics_008",
        name="anomaly_detection_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
    # tools=[_context7_toolset],
        description="Detects statistical anomalies and outliers in data",
        category="analytics",
        specialization="Anomaly Detection",
        mcp_functions=[
            "detect_anomalies", "calculate_percentiles", "analyze_dataset_statistics",
            "correlation_analysis"
        ],
        capabilities=["outlier detection", "fraud detection", "anomaly alerts"],
        input_types=["streaming_data", "historical_data"],
        output_types=["anomaly_alerts", "score_distribution", "recommendations"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        # id="agent_analytics_009",
        name="data_normalization_expert",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Normalizes and scales data for machine learning and analysis",
        category="analytics",
        specialization="Data Preprocessing",
        mcp_functions=[
            "normalize_data", "matrix_operations", "analyze_dataset_statistics"
        ],
        capabilities=["standardization", "scaling", "transformation"],
        input_types=["raw_data", "features"],
        output_types=["normalized_data", "scaling_params", "quality_report"],
        max_conversation_turns=8
    ),
    CustomLlmAgent(
        # id="agent_analytics_010",
        name="advanced_analytics_architect",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("docs_agent"),
        # tools=[_context7_toolset],
        description="Designs and orchestrates complex analytical workflows",
        category="analytics",
        specialization="Analytics Architecture",
        mcp_functions=[
            "analyze_dataset_statistics", "forecast_trends", "segment_data_clusters",
            "pivot_table_analysis", "regression_analysis", "correlation_analysis"
        ],
        capabilities=["workflow design", "multi-stage analysis", "complex pipelines"],
        input_types=["complex_datasets", "requirements"],
        output_types=["analysis_plan", "workflow", "results"],
        max_conversation_turns=20
    ),
]
