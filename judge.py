"""
LangChain chain that evaluates the ease of use of steps to achieve a goal.
"""

import os
from pathlib import Path
from typing import Optional

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class EaseOfUseEvaluation(BaseModel):
    """Structured output for ease of use evaluation."""

    summary: str = Field(description="A concise summary of the actions required")
    ease_score: int = Field(
        description="Ease of use score from 1-10 (1 = very difficult, 10 = trivial)",
        ge=1,
        le=10,
    )
    justification: str = Field(description="Detailed justification for the score")


async def evaluate_ease_of_use(
    steps_description: str,
    api_key: Optional[str] = None,
) -> EaseOfUseEvaluation:
    """
    Evaluate the ease of use for a set of steps.

    Args:
        steps_description: Description of steps to achieve a goal
        api_key: OpenRouter API key (optional)

    Returns:
        EaseOfUseEvaluation object with summary, ease_score, and justification
    """
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

    llm = ChatOpenAI(
        api_key=api_key,
        model="openai/gpt-5-nano",
        temperature=0.7,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/moosingin3space/oagi-hack-night",
            "X-Title": "OAGI Hack Night",
        },
    )

    prompt_path = Path(__file__).parent / "judge.md"
    system_prompt = prompt_path.read_text()

    agent = create_agent(
        model=llm,
        response_format=EaseOfUseEvaluation,
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Please evaluate the ease of use for this description:\n\n{steps_description}",
                },
            ],
        }
    )

    return response["structured_response"]


if __name__ == "__main__":
    import asyncio

    import dotenv

    test_steps = """
    To send an email:
    1. Click the "New Email" button in the top left
    2. Enter recipient email address in the "To" field
    3. Click in the "Subject" field and type the subject
    4. Click in the message body area and type the message
    5. Click the "Send" button at the bottom
    """

    dotenv.load_dotenv()
    result = asyncio.run(evaluate_ease_of_use(test_steps))
    print("\nEvaluation Result:")
    print(result.model_dump_json(indent=2))
