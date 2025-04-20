"""Model configuration for multi-model support."""

from google.adk.models.lite_llm import LiteLlm

# Define model constants for easier use
# Gemini Models
GEMINI_PRO_MODEL = "gemini-1.5-pro"
GEMINI_FLASH_MODEL = "gemini-2.0-flash"

# OpenAI Models
GPT_4O_MODEL = "gpt-4o"
GPT_35_TURBO_MODEL = "gpt-3.5-turbo"

# Anthropic Models
CLAUDE_SONNET_MODEL = "claude-3-sonnet-20240229"
CLAUDE_OPUS_MODEL = "claude-3-opus-20240229"

# Create LiteLLM instances for each model
gemini_pro = LiteLlm(model=GEMINI_PRO_MODEL, provider="google")
gemini_flash = LiteLlm(model=GEMINI_FLASH_MODEL, provider="google")

# Note: Uncomment these lines when you have the respective API keys configured
# gpt_4o = LiteLlm(model=GPT_4O_MODEL, provider="openai")
# gpt_35_turbo = LiteLlm(model=GPT_35_TURBO_MODEL, provider="openai")
# claude_sonnet = LiteLlm(model=CLAUDE_SONNET_MODEL, provider="anthropic")
# claude_opus = LiteLlm(model=CLAUDE_OPUS_MODEL, provider="anthropic")

# Default model to use if not specified
DEFAULT_MODEL = gemini_flash 