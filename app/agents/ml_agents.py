from app.custom_llm_agent import CustomLlmAgent
from google.adk.models.lite_llm import LiteLlm
from prompt_registry import get_prompt

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

ML_AGENTS = [
    CustomLlmAgent(
        id="agent_ml_001",
        name="model_training_orchestrator",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Orchestrates distributed model training",
        category="ml",
        specialization="Model Training",
        mcp_functions=[
            "model_training_orchestration", "hyperparameter_optimization",
            "model_evaluation_metrics"
        ],
        capabilities=["training orchestration", "GPU management", "monitoring"],
        input_types=["training_config", "dataset"],
        output_types=["trained_model", "metrics", "checkpoints"],
        max_conversation_turns=15
    ),
    CustomLlmAgent(
        id="agent_ml_002",
        name="hyperparameter_tuner",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Optimizes hyperparameters for machine learning models",
        category="ml",
        specialization="Hyperparameter Optimization",
        mcp_functions=[
            "hyperparameter_optimization", "model_evaluation_metrics",
            "feature_importance_analysis"
        ],
        capabilities=["parameter search", "optimization", "tuning"],
        input_types=["model", "parameter_space"],
        output_types=["best_params", "results", "convergence"],
        max_conversation_turns=16
    ),
    CustomLlmAgent(
        id="agent_ml_003",
        name="model_interpreter",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Provides interpretability and explanations for models",
        category="ml",
        specialization="Model Interpretability",
        mcp_functions=[
            "model_interpretability_xai", "feature_importance_analysis",
            "adversarial_robustness_testing"
        ],
        capabilities=["SHAP analysis", "LIME explanations", "feature importance"],
        input_types=["model", "predictions"],
        output_types=["explanations", "feature_impact", "visualizations"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        id="agent_ml_004",
        name="data_augmentation_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Generates synthetic data and augmentation strategies",
        category="ml",
        specialization="Data Augmentation",
        mcp_functions=[
            "data_augmentation", "class_imbalance_handling",
            "model_evaluation_metrics"
        ],
        capabilities=["synthetic data generation", "augmentation strategies"],
        input_types=["dataset", "requirements"],
        output_types=["augmented_data", "quality_metrics"],
        max_conversation_turns=11
    ),
    CustomLlmAgent(
        id="agent_ml_005",
        name="model_ensemble_builder",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Creates ensemble models from multiple learners",
        category="ml",
        specialization="Ensemble Methods",
        mcp_functions=[
            "model_ensemble_creation", "model_evaluation_metrics",
            "model_drift_detection"
        ],
        capabilities=["ensemble creation", "stacking", "voting"],
        input_types=["base_models", "data"],
        output_types=["ensemble_model", "performance", "recommendations"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_ml_006",
        name="ml_operations_manager",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Manages ML pipelines and production monitoring",
        category="ml",
        specialization="MLOps",
        mcp_functions=[
            "model_drift_detection", "model_compression_quantization",
            "model_evaluation_metrics"
        ],
        capabilities=["drift monitoring", "model deployment", "performance tracking"],
        input_types=["production_model", "data_stream"],
        output_types=["drift_alerts", "retraining_triggers", "metrics"],
        max_conversation_turns=14
    ),
]
