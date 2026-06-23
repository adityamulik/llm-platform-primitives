from app.custom_llm_agent import CustomLlmAgent
from google.adk.models.lite_llm import LiteLlm
from prompt_registry import get_prompt

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

CONTENT_AGENTS = [
    CustomLlmAgent(
        id="agent_content_001",
        name="blog_content_creator",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Creates SEO-optimized blog post content",
        category="content",
        specialization="Blog Writing",
        mcp_functions=[
            "generate_blog_post", "keyword_extraction", "seo_optimization"
        ],
        capabilities=["blog generation", "SEO optimization", "content planning"],
        input_types=["topic", "keywords"],
        output_types=["blog_post", "outline", "metadata"],
        max_conversation_turns=16
    ),
    CustomLlmAgent(
        id="agent_content_002",
        name="sentiment_analyzer",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Analyzes sentiment and emotional tone of content",
        category="content",
        specialization="Sentiment Analysis",
        mcp_functions=[
            "sentiment_analysis", "content_categorization", "voice_tone_analysis"
        ],
        capabilities=["sentiment scoring", "emotion detection", "tone analysis"],
        input_types=["text", "social_media"],
        output_types=["sentiment_report", "emotions", "insights"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_content_003",
        name="content_summarizer",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Summarizes long-form content efficiently",
        category="content",
        specialization="Text Summarization",
        mcp_functions=[
            "text_summarization", "keyword_extraction", "content_categorization"
        ],
        capabilities=["summarization", "key point extraction", "condensing"],
        input_types=["long_text", "documents"],
        output_types=["summary", "keypoints", "metadata"],
        max_conversation_turns=8
    ),
    CustomLlmAgent(
        id="agent_content_004",
        name="grammar_spell_checker",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Checks grammar, spelling, and writing quality",
        category="content",
        specialization="Proofreading",
        mcp_functions=[
            "grammar_spell_check", "content_categorization", "voice_tone_analysis"
        ],
        capabilities=["grammar checking", "spell correction", "readability scoring"],
        input_types=["text", "documents"],
        output_types=["corrected_text", "suggestions", "readability_score"],
        max_conversation_turns=9
    ),
    CustomLlmAgent(
        id="agent_content_005",
        name="plagiarism_detector",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Detects plagiarism and checks content originality",
        category="content",
        specialization="Originality Checking",
        mcp_functions=[
            "plagiarism_detection", "content_categorization",
            "sentiment_analysis"
        ],
        capabilities=["plagiarism detection", "source matching", "originality scoring"],
        input_types=["content", "document"],
        output_types=["plagiarism_report", "matched_sources", "score"],
        max_conversation_turns=8
    ),
    CustomLlmAgent(
        id="agent_content_006",
        name="translator",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Translates content between languages",
        category="content",
        specialization="Translation",
        mcp_functions=[
            "translation_service", "grammar_spell_check",
            "content_personalization"
        ],
        capabilities=["translation", "localization", "cultural adaptation"],
        input_types=["text", "source_language", "target_language"],
        output_types=["translated_text", "alternatives", "quality_score"],
        max_conversation_turns=10
    ),
    CustomLlmAgent(
        id="agent_content_007",
        name="content_strategist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Develops content strategy and identifies gaps",
        category="content",
        specialization="Content Strategy",
        mcp_functions=[
            "content_gap_analysis", "keyword_extraction", "generate_blog_post",
            "content_personalization"
        ],
        capabilities=["gap analysis", "strategy planning", "content mapping"],
        input_types=["existing_content", "competitor_analysis"],
        output_types=["strategy_plan", "gap_report", "recommendations"],
        max_conversation_turns=14
    ),
    CustomLlmAgent(
        id="agent_content_008",
        name="voice_tone_specialist",
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=get_prompt("execution_agent"),
        description="Analyzes and maintains consistent voice and tone",
        category="content",
        specialization="Brand Voice",
        mcp_functions=[
            "voice_tone_analysis", "grammar_spell_check",
            "content_personalization", "sentiment_analysis"
        ],
        capabilities=["tone consistency", "brand voice modeling", "adaptation"],
        input_types=["content_samples", "brand_guidelines"],
        output_types=["tone_report", "adjustments", "consistency_score"],
        max_conversation_turns=12
    ),
]
