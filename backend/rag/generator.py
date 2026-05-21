import logging
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_response(system_prompt: str, user_prompt: str) -> str:
    response = _client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1200,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    logger.info("Response generated (%d chars)", len(response.content[0].text))
    return response.content[0].text
