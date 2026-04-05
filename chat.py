"""
Locum Genius AI — RAG Chat Backend
Queries the Gemini File Search Store containing UK locum guide PDFs.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Check your .env file in the project root.")

client = genai.Client(api_key=api_key)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")

# ─── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are "Locum Genius AI", a world-class expert assistant specifically built for UK locum optometrists.

Your knowledge base contains the following documents:
- **Boots Opticians Locum Guide v2.1** — policies, procedures, clinical workflows at Boots
- **Costco Locum Guide** — specific requirements, equipment, and processes at Costco Optical
- **The Green Locum Guide** — comprehensive locum guidance for this chain
- **The Light Green Locum Guide** — guidance for this chain
- **The Purple Optician Locum Guide** — guidance for this chain
- **COO Clinical Management Guidelines (CMGs) — March 2026** — College of Optometrists evidence-based clinical protocols

Your role is to help locum optometrists:
1. Understand the SPECIFIC procedures, policies, and requirements of each optical chain
2. Apply College of Optometrists Clinical Management Guidelines accurately
3. Navigate the practicalities of locum work: equipment, referral pathways, paperwork, charging, recalls
4. Know their rights, responsibilities, and expectations at each practice

STRICT RULES — You MUST follow these at all times:
1. ONLY use information found in the file search results. Do NOT rely on general training knowledge.
2. If the answer is not in the documents, respond EXACTLY: "I cannot find this in the current Locum Guides. Please verify directly with the practice manager or the relevant optical chain's locum team."
3. ALWAYS cite which specific guide your answer comes from (e.g., "According to the Boots Opticians Locum Guide v2.1..." or "The COO CMGs state that...").
4. Be PRACTICAL and PRECISE — locums need actionable, specific answers, not vague generalities.
5. If a question spans multiple chains, compare them clearly (e.g., "At Boots... whereas at Costco...").
6. NEVER hallucinate or fabricate procedures, rates, or policies.
7. Format responses clearly with headers and bullet points where appropriate.
"""


@lru_cache(maxsize=1)
def load_store_name() -> str | None:
    """Load the Gemini File Search Store name from config.txt."""
    if not os.path.exists(CONFIG_FILE):
        print("ERROR: config.txt not found. Please run indexer.py first.")
        return None
    with open(CONFIG_FILE, "r") as f:
        return f.read().strip()


def query_rag(question: str) -> object | None:
    """
    Send a question to the Locum Genius AI RAG and return the full Gemini response.
    Returns None on error.
    """
    store_name = load_store_name()
    if not store_name:
        return None

    print(f"🔍 Querying store: {store_name}")
    print(f"   Question: {question[:100]}...")

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT.strip(),
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store_name]
                        )
                    )
                ]
            )
        )
        return response

    except Exception as e:
        print(f"❌ RAG query error: {e}")
        return None


def extract_citations(response) -> list[dict]:
    """
    Extract cited document names from the grounding metadata.
    Returns a list of dicts: [{"title": str}, ...]
    """
    citations = []
    seen = set()

    try:
        if response.candidates and hasattr(response.candidates[0], "grounding_metadata"):
            gm = response.candidates[0].grounding_metadata
            if gm and hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                for chunk in gm.grounding_chunks:
                    if hasattr(chunk, "retrieved_context"):
                        ctx = chunk.retrieved_context
                        title = getattr(ctx, "title", "Unknown Document")
                        if title not in seen:
                            seen.add(title)
                            citations.append({"title": title})
    except Exception:
        pass

    return citations


# ─── CLI Mode ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Usage: python chat.py "Your question here"')
        sys.exit(1)

    q = sys.argv[1]
    resp = query_rag(q)
    if resp:
        print("\n─── Answer ───────────────────────────────────────────────")
        print(resp.text)
        cites = extract_citations(resp)
        if cites:
            print("\n─── Sources ──────────────────────────────────────────────")
            for c in cites:
                print(f"  📄 {c['title']}")
    else:
        print("No response received. Check config.txt and your API key.")
