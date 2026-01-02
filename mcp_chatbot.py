import asyncio
import json
import re
import ollama
from typing import Optional
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

OLLAMA_MODEL = "mistral"


class MCPChatbot:
    def __init__(self):
        self.session: Optional[ClientSession] = None

    async def connect(self):
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "research_server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()
                tools = await session.list_tools()
                print("Connected. Available tools:", [t.name for t in tools.tools])
                await self.chat_loop()

    async def chat_loop(self):
        while True:
            query = input("\nQuery (or 'quit'): ").strip()
            if query.lower() == "quit":
                break
            await self.handle_query(query)

    async def handle_query(self, query: str):
        # 🔒 CLIENT decides: is this a paper search?
        if self.is_search_request(query):
            topic, count = await self.extract_search_args(query)
            await self.run_search(topic, count)
        else:
            print("💬 Assistant: I can help you search for academic papers on arXiv. Try asking me to find papers on a topic.")

    def is_search_request(self, query: str) -> bool:
        keywords = ["search", "find", "papers", "research", "fetch"]
        return any(k in query.lower() for k in keywords)

    async def extract_search_args(self, query: str):
        # LLM used ONLY for argument extraction
        prompt = f"""
Extract search parameters from the user query.

Return ONLY valid JSON:
{{
  "topic": "<string>",
  "max_results": <integer>
}}

User query:
{query}
"""
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
        )

        try:
            data = json.loads(response["response"])
            topic = data.get("topic", "physics")
            max_results = int(data.get("max_results", 5))
        except Exception:
            # Safe fallback
            topic = "physics"
            max_results = 5

        return topic, max_results

    async def run_search(self, topic: str, max_results: int):
        print(f"Searching arXiv for '{topic}' ({max_results} papers)...")

        result = await self.session.call_tool(
            "search_papers",
            {"topic": topic, "max_results": max_results}
        )

        paper_ids = [
            c.text for c in result.content if hasattr(c, "text")
        ]

        if not paper_ids:
            print("Assistant: No papers found.")
            return

        print(" Papers found:")
        for pid in paper_ids:
            print(f" - {pid}")


async def main():
    bot = MCPChatbot()
    await bot.connect()


if __name__ == "__main__":
    asyncio.run(main())

