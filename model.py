import vertexai
from groq import Groq
from vertexai.generative_models import GenerationConfig, GenerativeModel, SafetySetting

import config
import persona

vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)

SAFETY_CONFIG = [
    SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
    SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
]

model = GenerativeModel(
    model_name=config.TUNED_MODEL_ENDPOINT,
    system_instruction=persona.SYSTEM_INSTRUCTION,
    safety_settings=SAFETY_CONFIG,
)

groq_client = Groq(api_key=config.GROQ_API_KEY)

GIF_GEN_CONFIG = GenerationConfig(max_output_tokens=150)
