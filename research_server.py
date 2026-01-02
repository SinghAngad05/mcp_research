import arxiv
import json
import os
from typing import List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


PAPERS_DIR = "papers"

mcp = FastMCP("research")

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """Search for papers on arXiv related to the given topic."""

    client = arxiv.Client()

    # Search for most relevant articles matching the query topics.
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = client.results(search)

    # Creating directory of the topic.
    path = os.path.join(PAPERS_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "papers.json")

    # Try to load existing paper info.
    papers_info = {}
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info

    # Save updated papers into JSON file.
    with open(file_path, 'w') as json_file:
        json.dump(papers_info, json_file, indent=2)
    print(f"Results are saved to {file_path}")
    return paper_ids


@mcp.tool()
def extract_info(paper_id: str) -> str:
    """Extract title and abstract from a paper given its arXiv ID."""
    for item in os.listdir(PAPERS_DIR):
        item_path = os.path.join(PAPERS_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

    return f"There is no information found for paper ID {paper_id}."

# if __name__ == "__main__":
#     mcp.run(transport="sse") # It's stdio for local. 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )



