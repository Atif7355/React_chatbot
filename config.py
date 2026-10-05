# Configuration settings for the AI Backend App

MODEL_NAME = "gpt-4-dummy"
ALLOW_SYSTEM_OVERRIDE = True  # Vulnerability: Allows prompt injection via user controls
AUTO_EXECUTE_TOOLS = True     # Vulnerability: Excessive agency (executing tools without confirmation)
MAX_TOKENS = 1000