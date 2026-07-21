import asyncio

from agentlens import trace


@trace
async def hello():
    await asyncio.sleep(1)
    return "AgentLens"


async def main():
    print(await hello())


asyncio.run(main())