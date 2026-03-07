import os
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions
from dotenv import load_dotenv
from app.llm.schemas import ParsedConstraints, merge_constraints
from app.llm.errors import LLMError
from app.trace.tracer import log_event

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

SYSTEM_PROMPT = """
You are a JSON-only information extraction engine.
You must output a single valid JSON object and nothing else.
No markdown, no comments, no trailing text.
If you are uncertain, use null. Never fabricate facts.
"""

DEVELOPER_PROMPT = """
Task: Extract structured trip constraints from the user's query and optional existing constraints.
Output MUST be a single JSON object that conforms to this schema (all fields optional, use null if unknown):

{
  "destination": string | null,
  "days": integer | null,                       // must be > 0 if provided
  "date_range": { "start": string, "end": string } | null,  // ISO date "YYYY-MM-DD" if explicitly stated; else null
  "budget": { "currency": string, "total": number } | null, // currency like "USD"; total >= 0
  "interests": array of strings | null,         // short tags like ["food","anime","museums"]
  "style": string | null,                       // one of: "budget","mid","luxury"
  "pace": string | null,                        // one of: "relaxed","normal","packed"
  "limit": integer | null                       // number of place suggestions; >0 if provided
}

Rules:
- Only extract what is explicitly stated or can be reasonably inferred from standard phrasing.
- If something is missing or ambiguous, set it to null.
- Do not invent specific attractions, hotels, or prices.
- If multiple destinations are mentioned, pick the primary one; otherwise null.
- If the user says "X days" or "X-day trip", set days=X.
- If the user mentions a month/season without exact dates, do NOT fabricate dates; keep date_range=null.
- Normalize common currency symbols: "$" -> "USD" (only if user context strongly implies USD; otherwise null).
- Normalize style keywords: cheap/省钱 -> "budget"; normal/一般/中等 -> "mid"; luxury/奢华 -> "luxury".
- Normalize pace keywords: slow/悠闲 -> "relaxed"; normal -> "normal"; tight/特种兵/packed -> "packed".
- interests should be lower_snake_case or simple lowercase tokens without spaces (e.g. "street_food", "anime", "hiking").
- limit: if user says "give me 5 spots" or similar, set limit=5; else null.

Output requirements:
- Output JSON only, no additional keys beyond the schema above.
- Use null instead of empty string when unknown.
- Validate types: days/limit must be integers; total must be a number.
- If days/limit is mentioned but not a valid positive integer, set it to null.

Examples:

Input query: "3月去东京玩5天，预算2000刀，喜欢美食和动漫"
Output:
{"destination":"Tokyo","days":5,"date_range":null,"budget":{"currency":null,"total":2000},"interests":["food","anime"],"style":null,"pace":null,"limit":null}

Input query: "Weekend trip to SF, want it relaxed, keep it cheap"
Output:
{"destination":"San Francisco","days":null,"date_range":null,"budget":null,"interests":null,"style":"budget","pace":"relaxed","limit":null}

Input query: "Plan a 7-day trip, not sure where yet"
Output:
{"destination":null,"days":7,"date_range":null,"budget":null,"interests":null,"style":null,"pace":null,"limit":null}
"""


class LLMClient:
    def __init__(self, llm):
        self.llm = llm
    
    async def parse_constraints(self, *, query: str, constraints_hint: dict | None) -> dict:
        try:
            response = self.llm.generate_content(
                model="gemini-3-flash-preview",
                contents=query,
                config=GenerateContentConfig(
                    system_instruction=[
                        SYSTEM_PROMPT,
                        DEVELOPER_PROMPT,
                    ],
                    response_mime_type="application/json",
                    response_json_schema=ParsedConstraints.model_json_schema(),
                ),
            )
            parsed_constraints = ParsedConstraints.model_validate_json(response.text)
        except Exception as e:
            log_event({"query": query, "error": str(e)})
            raise LLMError(f"LLM call failed: {str(e)}", type="llm_failure", retryable=True) from e
        merged_constraints = merge_constraints(api_constraints=constraints_hint, parsed=parsed_constraints)
        log_event({"query": query, "response": response.text})
        return merged_constraints

def get_llm_client() -> LLMClient:
    """
    Factory function to create an LLMClient instance.
    This is where you would initialize your actual LLM (e.g., OpenAI, Hugging Face) and pass it to the client.
    For testing purposes, you can return a mock or dummy client.
    """
    return LLMClient(gemini)