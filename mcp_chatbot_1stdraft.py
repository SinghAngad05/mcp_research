import arxiv
import json
import os
from typing import List, Dict
from dotenv import load_dotenv
import ollama
import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters,types
from mcp.client.stdio import stdio_client

nest_asyncio.apply()

load_dotenv()
OLLAMA_MODEL = 'mistral'

class MCP_Chatbot:
    def __init__(self):
        self.session: ClientSession = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict] = []

    async def process_query(query):
        """
        Process user query with tool use capability.
        The AI can decide to call search_papers or extract_info tools.
        """
        try:
            if not query or query.strip() == "":
                print("Please enter a valid query")
                return
            
            # Build system prompt that tells Ollama about available tools
            system_prompt = """You are an AI assistant specialized in searching and analyzing academic papers on arXiv.

    You have access to the following tools:
    1. search_papers(topic: str, max_results: int = 5) - Search for papers on arXiv by topic
    2. extract_info(paper_id: str) - Get detailed info about a specific paper

    When the user asks you to search for papers, use the search_papers tool.
    When the user asks about a specific paper, use the extract_info tool.

    If you decide to use a tool, respond in this exact format:
    TOOL_CALL: [tool_name] | {json_with_args}

    For example:
    TOOL_CALL: search_papers | {"topic": "machine learning", "max_results": 5}

    After getting tool results, provide a helpful response to the user."""

            # First, ask Ollama what it thinks it should do
            full_prompt = f"{system_prompt}\n\nUser: {query}"
            
            response = ollama.generate(
                model=OLLAMA_MODEL, 
                prompt=full_prompt,
                stream=False
            )
            
            if not response or 'response' not in response:
                print("Could not generate a response. Try a different query.")
                return
            
            assistant_response = response['response'].strip()
            
            # Check if the assistant wants to call a tool
            if "TOOL_CALL:" in assistant_response:
                # Extract the tool call
                tool_call_idx = assistant_response.find("TOOL_CALL:")
                tool_section = assistant_response[tool_call_idx:].split('\n')[0]
                
                try:
                    # Parse: TOOL_CALL: search_papers | {"topic": "algebra"}
                    parts = tool_section.replace("TOOL_CALL:", "").strip().split("|")
                    if len(parts) == 2:
                        tool_name = parts[0].strip()
                        tool_args = json.loads(parts[1].strip())
                        
                        print(f"\n Using tool: {tool_name}")
                        print(f"   Args: {tool_args}\n")
                        
                        # Execute the tool
                        tool_result = execute_tool(tool_name, tool_args)
                        
                        print(f" Tool result:\n{tool_result}\n")
                        
                        # Now ask Ollama to provide a helpful response based on the tool result
                        followup_prompt = f"{system_prompt}\n\nUser: {query}\n\nTool used: {tool_name}\nTool result:\n{tool_result}\n\nProvide a helpful summary for the user:"
                        
                        followup_response = ollama.generate(
                            model=OLLAMA_MODEL,
                            prompt=followup_prompt,
                            stream=False
                        )
                        
                        if followup_response and 'response' in followup_response:
                            print(f" Assistant: {followup_response['response'].strip()}")
                        return
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Could not parse tool call: {e}")
                    print(f"Response: {assistant_response}")
                    return
            
            # No tool call, just print the response
            print(f" Assistant: {assistant_response}")
                
        except ConnectionError:
            print("❌ Error: Ollama is not running!")
            print("Start Ollama with: & \"C:\\Users\\geek9\\AppData\\Local\\Programs\\Ollama\\ollama.exe\" serve")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    async def chat_loop():
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
        
                process_query(query)
                print("\n")
            except Exception as e:
                print(f"\nError: {str(e)}")    
    
     async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "research_server.py"],  # Optional command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()
    
                # List available tools
                response = await session.list_tools()
                
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])
                
                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]
    
                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()
  

if __name__ == "__main__":
    asyncio.run(main())