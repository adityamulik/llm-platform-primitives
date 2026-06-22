
from app.custom_llm_agent import CustomLlmAgent

DEVOPS_AGENTS = [
    CustomLlmAgent(
        id="agent_devops_001",
        name="system_health_monitor",
        description="Monitors system health and generates alerts",
        category="devops",
        specialization="System Monitoring",
        mcp_functions=[
            "monitor_system_health", "log_aggregation_query",
            "incident_response_automation"
        ],
        capabilities=["health monitoring", "metric collection", "alerting"],
        input_types=["metrics", "logs"],
        output_types=["health_report", "alerts", "recommendations"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_devops_002",
        name="container_orchestration_manager",
        description="Manages containerized deployments and scaling",
        category="devops",
        specialization="Container Management",
        mcp_functions=[
            "container_orchestration", "monitor_system_health",
            "cost_optimization_analysis"
        ],
        capabilities=["container management", "auto-scaling", "deployment"],
        input_types=["container_config", "metrics"],
        output_types=["deployment_status", "scaling_actions", "logs"],
        max_conversation_turns=12
    ),
    CustomLlmAgent(
        id="agent_devops_003",
        name="infrastructure_code_validator",
        description="Validates Infrastructure as Code configurations",
        category="devops",
        specialization="IaC Validation",
        mcp_functions=[
            "infrastructure_as_code_validation", "security_compliance_audit",
            "cost_optimization_analysis"
        ],
        capabilities=["IaC validation", "syntax checking", "best practice verification"],
        input_types=["IaC_files", "configurations"],
        output_types=["validation_report", "issues", "cost_estimate"],
        max_conversation_turns=11
    ),
    CustomLlmAgent(
        id="agent_devops_004",
        name="disaster_recovery_planner",
        description="Plans and validates disaster recovery procedures",
        category="devops",
        specialization="DR & Business Continuity",
        mcp_functions=[
            "disaster_recovery_plan", "backup_restore_management",
            "database_replication_monitoring"
        ],
        capabilities=["DR planning", "backup management", "recovery testing"],
        input_types=["infrastructure", "requirements"],
        output_types=["DR_plan", "RTO_RPO", "test_results"],
        max_conversation_turns=13
    ),
    CustomLlmAgent(
        id="agent_devops_005",
        name="network_operations_engineer",
        description="Analyzes network traffic and configuration",
        category="devops",
        specialization="Network Operations",
        mcp_functions=[
            "network_traffic_analysis", "dns_configuration_validation",
            "load_balancer_configuration"
        ],
        capabilities=["traffic analysis", "DNS management", "load balancing"],
        input_types=["network_data", "configuration"],
        output_types=["network_report", "anomalies", "recommendations"],
        max_conversation_turns=11
    ),
    CustomLlmAgent(
        id="agent_devops_006",
        name="cost_optimization_analyst",
        description="Analyzes cloud costs and recommends optimizations",
        category="devops",
        specialization="Cost Management",
        mcp_functions=[
            "cost_optimization_analysis", "monitor_system_health",
            "infrastructure_as_code_validation"
        ],
        capabilities=["cost analysis", "optimization planning", "budget forecasting"],
        input_types=["billing_data", "infrastructure"],
        output_types=["cost_report", "recommendations", "savings_estimate"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_devops_007",
        name="security_compliance_auditor",
        description="Audits infrastructure security and compliance",
        category="devops",
        specialization="Security Compliance",
        mcp_functions=[
            "security_compliance_audit", "ssl_certificate_management",
            "infrastructure_as_code_validation"
        ],
        capabilities=["compliance auditing", "security assessment", "certificate management"],
        input_types=["infrastructure", "standards"],
        output_types=["audit_report", "issues", "remediation_plan"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_devops_008",
        name="database_replication_manager",
        description="Manages database replication and synchronization",
        category="devops",
        specialization="Database Operations",
        mcp_functions=[
            "database_replication_monitoring", "backup_restore_management",
            "infrastructure_as_code_validation"
        ],
        capabilities=["replication monitoring", "sync management", "backup verification"],
        input_types=["database_config", "replication_logs"],
        output_types=["replication_status", "alerts", "actions"],
        max_conversation_turns=12
    ),
]
