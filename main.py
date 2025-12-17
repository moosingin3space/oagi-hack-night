import asyncio

from oagi import AsyncScreenshotMaker
from oagi import AsyncPyautoguiActionHandler
from oagi import TaskerAgent

import dotenv

async def main():
    dotenv.load_dotenv()
    agent = TaskerAgent(model="lux-actor-1")
    agent.set_task(
        task = "Use the already-open Weather app to find the current temperature",
        todos = [
            "Click 'Search for a city or country'",
            "Choose San Francisco",
            "Look at the temperature"
        ]
    )

    await agent.execute(
        instruction="Use the already-open Weather app to find the current temperature",
        action_handler=AsyncPyautoguiActionHandler(),
        image_provider=AsyncScreenshotMaker(),
    )


if __name__ == "__main__":
    asyncio.run(main())
