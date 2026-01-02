# MCP Research Server (arXiv)

This project is a hands-on implementation of the **Model Context Protocol (MCP)** to demonstrate how an AI client can dynamically discover and call tools exposed by a server.

The server exposes research-related tools backed by **arXiv**, and the client uses an LLM (**Mistral via Ollama**) to decide when and how to call those tools.

This project is intentionally simple and educational, built to understand MCP fundamentals end-to-end.

---

## What is MCP?

**Model Context Protocol (MCP)** is a standard that allows:

- A **server** to expose tools (functions + schemas)
- A **client** (LLM-powered) to discover available tools dynamically
- The LLM to decide *when* to call a tool
- Tool results to be fed back into the model for final reasoning

Think of MCP as a clean contract between:
- Tools
- Schemas
- LLM reasoning
- Execution

---

## Project Architecture

# MCP Research Server (arXiv)

This project is a hands-on implementation of the **Model Context Protocol (MCP)** to demonstrate how an AI client can dynamically discover and call tools exposed by a server.

The server exposes research-related tools backed by **arXiv**, and the client uses an LLM (**Mistral via Ollama**) to decide when and how to call those tools.

This project is intentionally simple and educational, built to understand MCP fundamentals end-to-end.

---

## What is MCP?

**Model Context Protocol (MCP)** is a standard that allows:

- A **server** to expose tools (functions + schemas)
- A **client** (LLM-powered) to discover available tools dynamically
- The LLM to decide *when* to call a tool
- Tool results to be fed back into the model for final reasoning

Think of MCP as a clean contract between:
- Tools
- Schemas
- LLM reasoning
- Execution

---

## Project Architecture


---

## MCP Server (research_server.py)

The MCP server exposes two tools:

### 1. `search_papers`
Searches arXiv for papers by topic and stores metadata locally.

**Inputs**
- topic (string)
- max_results (int)

**Returns**
- List of arXiv paper IDs

### 2. `extract_info`
Fetches stored metadata for a given paper ID.

**Inputs**
- paper_id (string)

**Returns**
- Title, authors, abstract, PDF link, publish date

The server runs using **stdio transport**, which is ideal for local development and MCP inspectors.

---

## MCP Client (mcp_chatbot.py)

The client:
- Connects to the MCP server over stdio
- Discovers available tools dynamically
- Uses **Mistral (via Ollama)** to decide:
  - Whether a tool is needed
  - Which tool to call
  - What arguments to pass
- Calls the tool through MCP
- Feeds the tool result back to the LLM for a final response

The LLM never hardcodes tool logic — it reasons based on tool schemas.

---

## LLM Used

- **Model**: Mistral
- **Runtime**: Ollama (local)
- **Reason**: Fast, local, great for experimentation without API costs

Make sure Ollama is running:
```bash
ollama serve

## Installation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

## Running MCP server
python research_server.py


## Running MCP client
python mcp_chatbot.py


## Example interaction

Query: Can you search papers around physics and find 2 of them?

Searching arXiv for 'physics' (2 papers)...

Papers found:
 - 1910.11775v2
 - hep-ex/9605011v1
