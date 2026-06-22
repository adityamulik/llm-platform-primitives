
from app.custom_llm_agent import CustomLlmAgent
from google.adk.models.lite_llm import LiteLlm
from prompt_registry import get_prompt

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

DEV_AGENTS = [
    CustomLlmAgent(
        id="agent_dev_001",
        name="code_quality_reviewer",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("code_quality_reviewer"),
        description="Reviews code for quality, complexity, and best practices",
        category="development",
        specialization="Code Review",
        mcp_functions=[
            "code_review_static_analysis", "lint_code_style", "extract_ast_metrics",
            "detect_code_clones"
        ],
        capabilities=["static analysis", "complexity assessment", "quality scoring"],
        input_types=["source_code", "codebase"],
        output_types=["review_report", "issues", "recommendations"],
        max_conversation_turns=15
    ),
    CustomLlmAgent(
        id="agent_dev_002",
        name="security_vulnerability_scanner",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("security_vulnerability_scanner"),
        description="Scans code for security vulnerabilities and compliance issues",
        category="development",
        specialization="Security & Compliance",
        mcp_functions=[
            "security_vulnerability_scan", "code_review_static_analysis",
            "dependency_analysis"
        ],
        capabilities=["vulnerability detection", "OWASP scanning", "compliance check"],
        input_types=["source_code", "dependencies"],
        output_types=["security_report", "vulnerability_list", "remediation"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        id="agent_dev_003",
        name="test_coverage_analyzer",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("test_coverage_analyzer"),
        description="Analyzes test coverage and recommends test improvements",
        category="development",
        specialization="Testing & QA",
        mcp_functions=[
            "test_coverage_analysis", "code_review_static_analysis",
            "extract_ast_metrics"
        ],
        capabilities=["coverage analysis", "test optimization", "gap identification"],
        input_types=["test_results", "coverage_data"],
        output_types=["coverage_report", "test_gaps", "recommendations"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_dev_004",
        name="performance_profiler",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("performance_profiler"),
        description="Profiles code performance and identifies bottlenecks",
        category="development",
        specialization="Performance Optimization",
        mcp_functions=[
            "performance_profiling", "extract_ast_metrics",
            "code_refactoring_suggestions"
        ],
        capabilities=["bottleneck identification", "optimization", "benchmarking"],
        input_types=["profiling_data", "source_code"],
        output_types=["profile_report", "bottlenecks", "optimization_plan"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_dev_005",
        name="api_documentation_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("api_documentation_specialist"),
        description="Generates comprehensive API documentation from code",
        category="development",
        specialization="Documentation",
        mcp_functions=[
            "generate_documentation", "extract_ast_metrics", "lint_code_style"
        ],
        capabilities=["doc generation", "API documentation", "example creation"],
        input_types=["source_code", "docstrings"],
        output_types=["documentation", "API_spec", "examples"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_dev_006",
        name="refactoring_strategist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("refactoring_strategist"),
        description="Suggests and plans code refactoring improvements",
        category="development",
        specialization="Code Refactoring",
        mcp_functions=[
            "code_refactoring_suggestions", "detect_code_clones",
            "extract_ast_metrics", "lint_code_style"
        ],
        capabilities=["refactoring planning", "duplication removal", "structure improvement"],
        input_types=["source_code", "metrics"],
        output_types=["refactoring_plan", "before_after", "impact_analysis"],
        max_conversation_turns=16
    ),
    CustomLlmAgent(
        id="agent_dev_007",
        name="dependency_manager",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("dependency_manager"),
        description="Manages dependencies and checks for outdated packages",
        category="development",
        specialization="Dependency Management",
        mcp_functions=[
            "dependency_analysis", "security_vulnerability_scan",
            "migration_compatibility_check"
        ],
        capabilities=["version checking", "vulnerability detection", "upgrade planning"],
        input_types=["requirements_files", "manifest"],
        output_types=["dependency_report", "upgrade_plan", "risks"],
        max_conversation_turns=11
    ),
    CustomLlmAgent(
        id="agent_dev_008",
        name="git_analytics_engineer",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("git_analytics_engineer"),
        description="Analyzes git history and development patterns",
        category="development",
        specialization="Version Control Analytics",
        mcp_functions=[
            "git_log_analysis", "generate_changelog", "detect_code_clones"
        ],
        capabilities=["commit analysis", "contributor tracking", "changelog generation"],
        input_types=["git_history", "repository"],
        output_types=["git_analytics", "changelog", "trends"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        id="agent_dev_009",
        name="database_schema_architect",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("database_schema_architect"),
        description="Analyzes and optimizes database schemas",
        category="development",
        specialization="Database Design",
        mcp_functions=[
            "database_schema_analysis", "api_contract_validation",
            "performance_profiling"
        ],
        capabilities=["schema optimization", "index recommendations", "performance tuning"],
        input_types=["schema_definition", "query_logs"],
        output_types=["optimization_report", "schema_changes", "performance_gains"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_dev_010",
        name="api_contract_validator",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("api_contract_validator"),
        description="Validates API contracts and specifications",
        category="development",
        specialization="API Design",
        mcp_functions=[
            "api_contract_validation", "lint_code_style",
            "code_review_static_analysis", "migration_compatibility_check"
        ],
        capabilities=["contract validation", "spec compliance", "test generation"],
        input_types=["API_spec", "test_cases"],
        output_types=["validation_report", "issues", "recommendations"],
        max_conversation_turns=13
    ),
]
