from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Minimal observability via Arize/OpenInference (optional)
try:
    from arize.otel import register
    from openinference.instrumentation.langchain import LangChainInstrumentor
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from openinference.instrumentation import using_prompt_template, using_metadata, using_attributes
    from opentelemetry import trace
    _TRACING = True
    print("[Arize] OpenInference packages loaded successfully")
except Exception as e:
    print(f"[Arize] OpenInference packages not available: {e}")
    def using_prompt_template(**kwargs):  # type: ignore
        from contextlib import contextmanager
        @contextmanager
        def _noop():
            yield
        return _noop()
    def using_metadata(*args, **kwargs):  # type: ignore
        from contextlib import contextmanager
        @contextmanager
        def _noop():
            yield
        return _noop()
    def using_attributes(*args, **kwargs):  # type: ignore
        from contextlib import contextmanager
        @contextmanager
        def _noop():
            yield
        return _noop()
    _TRACING = False

# LangGraph + LangChain
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import httpx
import re


# ========================================
# Request/Response Models
# ========================================

class CardSearchRequest(BaseModel):
    query: str
    game: Optional[str] = "all"


class CardPrice(BaseModel):
    low: float
    market: float
    high: float


class MarketplacePrice(BaseModel):
    name: str
    price: float
    url: str


class CardResponse(BaseModel):
    id: str
    name: str
    set: Optional[str] = None
    rarity: Optional[str] = None
    game: str
    image: Optional[str] = None
    prices: Dict[str, CardPrice]
    marketplaces: List[MarketplacePrice]
    summary: str


class CardSearchResponse(BaseModel):
    card: Optional[CardResponse] = None
    error: Optional[str] = None


# ========================================
# eBay API Integration
# ========================================

class EbayClient:
    """Client for eBay Browse API."""
    
    TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    # Trading card category IDs on eBay
    CATEGORY_IDS = {
        "all": "183454",  # Trading Card Games
        "mtg": "19107",   # MTG
        "pokemon": "183454",  # Pokemon
        "yugioh": "183454",  # Yu-Gi-Oh
        "sports": "212",  # Sports Trading Cards
    }
    
    def __init__(self):
        self.client_id = os.getenv("EBAY_CLIENT_ID")
        self.client_secret = os.getenv("EBAY_CLIENT_SECRET")
        self._access_token = None
        self._token_expiry = 0
    
    @property
    def is_configured(self) -> bool:
        """Check if eBay credentials are configured."""
        return bool(self.client_id and self.client_secret and 
                   self.client_id != "your_ebay_client_id_here")
    
    def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token from eBay."""
        import time
        
        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expiry - 60:
            return self._access_token
        
        if not self.is_configured:
            return None
        
        # Create Basic auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self.TOKEN_URL,
                    headers={
                        "Authorization": f"Basic {encoded}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "grant_type": "client_credentials",
                        "scope": "https://api.ebay.com/oauth/api_scope"
                    }
                )
                response.raise_for_status()
                data = response.json()
                self._access_token = data["access_token"]
                self._token_expiry = time.time() + data.get("expires_in", 7200)
                return self._access_token
        except Exception as e:
            print(f"[eBay] Failed to get access token: {e}")
            return None
    
    def search(self, query: str, game: str = "all", limit: int = 10) -> Dict[str, Any]:
        """Search eBay for trading card listings."""
        token = self._get_access_token()
        
        if not token:
            return {"error": "eBay API not configured. Please add EBAY_CLIENT_ID and EBAY_CLIENT_SECRET to .env"}
        
        category_id = self.CATEGORY_IDS.get(game, self.CATEGORY_IDS["all"])
        
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    self.BROWSE_URL,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                        "Content-Type": "application/json",
                    },
                    params={
                        "q": query,
                        "category_ids": category_id,
                        "limit": limit,
                        "sort": "price",
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"[eBay] API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"eBay API error: {e.response.status_code}"}
        except Exception as e:
            print(f"[eBay] Request failed: {e}")
            return {"error": str(e)}
    
    def get_sold_listings(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Note: eBay Browse API doesn't directly support sold listings.
        This searches current listings and estimates market value.
        For true sold data, you'd need eBay's Finding API or a service like SerpAPI.
        """
        return self.search(query, limit=limit)


# Initialize eBay client
ebay_client = EbayClient()


# ========================================
# LLM Initialization
# ========================================

def _init_llm():
    """Initialize LLM with fallback for test mode."""
    class _Fake:
        def __init__(self):
            pass
        def bind_tools(self, tools):
            return self
        def invoke(self, messages):
            class _Msg:
                content = "Test card price response"
                tool_calls: List[Dict[str, Any]] = []
            return _Msg()

    if os.getenv("TEST_MODE"):
        return _Fake()
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=1000)
    elif os.getenv("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            temperature=0.3,
        )
    else:
        raise ValueError("Please set OPENAI_API_KEY or OPENROUTER_API_KEY in your .env")


llm = _init_llm()


# ========================================
# Card Search Tools (eBay Integration)
# ========================================

@tool
def search_ebay_cards(card_name: str, game: str = "all") -> str:
    """
    Search eBay for trading card listings.
    Returns current listings with prices.
    
    Args:
        card_name: Name of the trading card to search for
        game: Game type filter (all, mtg, pokemon, yugioh, sports)
    """
    result = ebay_client.search(card_name, game=game, limit=15)
    
    if "error" in result:
        return json.dumps(result)
    
    items = result.get("itemSummaries", [])
    
    if not items:
        return json.dumps({
            "found": False,
            "message": f"No listings found for '{card_name}' on eBay"
        })
    
    # Extract pricing data
    prices = []
    listings = []
    
    for item in items:
        price_info = item.get("price", {})
        price_value = float(price_info.get("value", 0))
        
        if price_value > 0:
            prices.append(price_value)
            listings.append({
                "title": item.get("title", ""),
                "price": price_value,
                "currency": price_info.get("currency", "USD"),
                "condition": item.get("condition", "Unknown"),
                "url": item.get("itemWebUrl", ""),
                "image": item.get("image", {}).get("imageUrl", ""),
                "seller": item.get("seller", {}).get("username", "Unknown")
            })
    
    if not prices:
        return json.dumps({
            "found": False,
            "message": f"No priced listings found for '{card_name}'"
        })
    
    # Calculate price statistics
    prices.sort()
    low = prices[0]
    high = prices[-1]
    market = sum(prices) / len(prices)
    median = prices[len(prices) // 2]
    
    return json.dumps({
        "found": True,
        "card_name": card_name,
        "total_listings": len(listings),
        "price_stats": {
            "low": round(low, 2),
            "high": round(high, 2),
            "average": round(market, 2),
            "median": round(median, 2)
        },
        "sample_listings": listings[:5],  # Top 5 listings
        "source": "eBay"
    })


@tool
def get_card_details(card_name: str) -> str:
    """
    Get detailed information about a trading card using the LLM's knowledge.
    
    Args:
        card_name: Name of the trading card
    """
    # Use LLM to provide card details since eBay doesn't have card metadata
    prompt = f"""Provide brief factual details about the trading card "{card_name}":
    - Game (MTG, Pokemon, Yu-Gi-Oh, etc.)
    - Rarity (if known)
    - Set/Edition (most valuable version)
    - Why collectors value it
    
    Keep response under 100 words. If you don't know the card, say so."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return json.dumps({
        "card_name": card_name,
        "details": response.content if hasattr(response, "content") else str(response)
    })


# ========================================
# Agent State
# ========================================

class CardSearchState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    game_filter: str
    ebay_data: Optional[Dict[str, Any]]
    card_details: Optional[str]
    summary: Optional[str]
    tool_calls: Annotated[List[Dict[str, Any]], operator.add]


# ========================================
# Agent Nodes
# ========================================

def search_agent(state: CardSearchState) -> CardSearchState:
    """Agent that searches eBay for card listings."""
    query = state["query"]
    game = state.get("game_filter", "all")
    
    system_prompt = (
        "You are a trading card price search assistant. "
        "You MUST use the search_ebay_cards tool to find current listings and prices. "
        "Always call the tool with the card name provided."
    )
    prompt_t = "Search for the trading card: {query} (Game filter: {game})"
    vars_ = {"query": query, "game": game}
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_t.format(**vars_))
    ]
    tools = [search_ebay_cards]
    agent = llm.bind_tools(tools)
    
    calls: List[Dict[str, Any]] = []
    ebay_data = None
    
    with using_attributes(tags=["search", "ebay_lookup"]):
        if _TRACING:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("metadata.agent_type", "search")
                current_span.set_attribute("metadata.query", query)
        
        with using_prompt_template(template=prompt_t, variables=vars_, version="v1"):
            res = agent.invoke(messages)
    
    # Execute tool calls
    if getattr(res, "tool_calls", None):
        for c in res.tool_calls:
            calls.append({"agent": "search", "tool": c["name"], "args": c.get("args", {})})
        
        tool_node = ToolNode(tools)
        tr = tool_node.invoke({"messages": [res]})
        
        # Parse result
        if tr["messages"]:
            result = tr["messages"][0].content
            try:
                ebay_data = json.loads(result)
            except:
                ebay_data = {"raw": result}
    
    # Fallback: direct eBay search (only if eBay is configured)
    if not ebay_data and ebay_client.is_configured:
        result = ebay_client.search(query, game=game, limit=15)
        if "itemSummaries" in result:
            items = result["itemSummaries"]
            prices = [float(i.get("price", {}).get("value", 0)) for i in items if i.get("price")]
            prices = [p for p in prices if p > 0]
            
            if prices:
                prices.sort()
                ebay_data = {
                    "found": True,
                    "card_name": query,
                    "total_listings": len(items),
                    "price_stats": {
                        "low": round(prices[0], 2),
                        "high": round(prices[-1], 2),
                        "average": round(sum(prices) / len(prices), 2),
                        "median": round(prices[len(prices) // 2], 2)
                    },
                    "sample_listings": [
                        {
                            "title": i.get("title", ""),
                            "price": float(i.get("price", {}).get("value", 0)),
                            "url": i.get("itemWebUrl", ""),
                            "image": i.get("image", {}).get("imageUrl", "")
                        }
                        for i in items[:5]
                    ],
                    "source": "eBay"
                }
            else:
                ebay_data = {"found": False, "message": f"No priced listings for '{query}'"}
        else:
            ebay_data = result  # Contains error
    
    # Final fallback: LLM-based price estimate when eBay is unavailable
    if not ebay_data or not ebay_data.get("found"):
        estimate_messages = [
            SystemMessage(content=(
                "You are a trading card pricing expert. "
                "Respond with ONLY a valid JSON object, no markdown fences, no extra text."
            )),
            HumanMessage(content=(
                f'Estimate the current market price range for: "{query}" (Game: {game}).\n\n'
                "Return ONLY this JSON:\n"
                '{"found": true, "card_name": "' + query + '", "estimated": true, '
                '"total_listings": 0, "price_stats": {"low": <number>, "high": <number>, '
                '"average": <number>, "median": <number>}, "sample_listings": [], '
                '"source": "AI Estimate"}\n\n'
                'If you don\'t recognize this card, return: '
                '{"found": false, "message": "Card not recognized"}'
            ))
        ]
        try:
            estimate_res = llm.invoke(estimate_messages)
            estimate_text = estimate_res.content if hasattr(estimate_res, "content") else str(estimate_res)
            json_match = re.search(r'\{[\s\S]*\}', estimate_text)
            if json_match:
                ebay_data = json.loads(json_match.group())
        except Exception as e:
            print(f"[LLM Estimate] Failed: {e}")
    
    return {
        "messages": [SystemMessage(content=f"Search complete: {json.dumps(ebay_data)[:500]}" if ebay_data else "Search failed")],
        "ebay_data": ebay_data,
        "tool_calls": calls
    }


def details_agent(state: CardSearchState) -> CardSearchState:
    """Agent that fetches card details using LLM knowledge."""
    query = state["query"]
    
    system_prompt = (
        "You are a trading card expert. "
        "Use the get_card_details tool to look up information about trading cards."
    )
    prompt_t = "Get details about this trading card: {query}"
    vars_ = {"query": query}
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt_t.format(**vars_))
    ]
    tools = [get_card_details]
    agent = llm.bind_tools(tools)
    
    calls: List[Dict[str, Any]] = []
    card_details = None
    
    with using_attributes(tags=["details", "card_info"]):
        if _TRACING:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("metadata.agent_type", "details")
        
        with using_prompt_template(template=prompt_t, variables=vars_, version="v1"):
            res = agent.invoke(messages)
    
    if getattr(res, "tool_calls", None):
        for c in res.tool_calls:
            calls.append({"agent": "details", "tool": c["name"], "args": c.get("args", {})})
        
        tool_node = ToolNode(tools)
        tr = tool_node.invoke({"messages": [res]})
        
        if tr["messages"]:
            card_details = tr["messages"][0].content
    
    # Fallback: use the LLM response directly if no tool was called
    if not card_details and hasattr(res, "content") and res.content:
        card_details = res.content
    
    return {
        "messages": [SystemMessage(content=f"Card details: {card_details}")],
        "card_details": card_details,
        "tool_calls": calls
    }


def summary_agent(state: CardSearchState) -> CardSearchState:
    """Agent that generates a price summary."""
    query = state["query"]
    ebay_data = state.get("ebay_data", {})
    card_details = state.get("card_details", "")
    
    if not ebay_data or not ebay_data.get("found"):
        return {
            "messages": [SystemMessage(content="No data to summarize")],
            "summary": f"No listings found for '{query}' on eBay. Try a different search term or check spelling.",
            "tool_calls": []
        }
    
    price_stats = ebay_data.get("price_stats", {})
    total_listings = ebay_data.get("total_listings", 0)
    is_estimated = ebay_data.get("estimated", False)
    source = ebay_data.get("source", "eBay")
    source_note = " Note: These prices are AI estimates, not live market data." if is_estimated else ""
    
    prompt_t = (
        "You are a trading card price analyst. Write a brief 2-3 sentence summary.\n"
        "Card: {query}\n"
        "Data Source: {source}\n"
        "Listings Found: {total_listings}\n"
        "Price Range: ${low} - ${high}\n"
        "Average Price: ${average}\n"
        "Card Details: {details}\n"
        "{source_note}\n"
        "Provide a helpful summary for a collector considering this purchase."
    )
    vars_ = {
        "query": query,
        "source": source,
        "total_listings": total_listings,
        "low": price_stats.get("low", "N/A"),
        "high": price_stats.get("high", "N/A"),
        "average": price_stats.get("average", "N/A"),
        "details": card_details[:200] if card_details else "No additional details",
        "source_note": source_note
    }
    
    with using_attributes(tags=["summary", "final_output"]):
        if _TRACING:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("metadata.agent_type", "summary")
        
        with using_prompt_template(template=prompt_t, variables=vars_, version="v1"):
            res = llm.invoke([SystemMessage(content=prompt_t.format(**vars_))])
    
    summary = res.content if hasattr(res, "content") else str(res)
    
    return {
        "messages": [SystemMessage(content=summary)],
        "summary": summary,
        "tool_calls": []
    }


# ========================================
# Build Agent Graph
# ========================================

def build_card_search_graph():
    """Build the LangGraph for card search."""
    g = StateGraph(CardSearchState)
    
    g.add_node("search_node", search_agent)
    g.add_node("details_node", details_agent)
    g.add_node("summary_node", summary_agent)
    
    # Sequential flow: search -> details -> summary
    g.add_edge(START, "search_node")
    g.add_edge("search_node", "details_node")
    g.add_edge("details_node", "summary_node")
    g.add_edge("summary_node", END)
    
    return g.compile()


# ========================================
# FastAPI Application
# ========================================

app = FastAPI(title="Trading Card Price Checker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend directory
_frontend_dir = Path(__file__).parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


@app.get("/")
def serve_frontend():
    """Serve the main UI."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "frontend", "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"message": "frontend/index.html not found"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "trading-card-price-checker",
        "ebay_configured": ebay_client.is_configured
    }


@app.post("/api/cards/search", response_model=CardSearchResponse)
def search_cards(req: CardSearchRequest):
    """Search for a card and get pricing information from eBay."""
    
    # Run the agent graph (agents handle missing eBay gracefully with LLM estimates)
    graph = build_card_search_graph()
    
    state = {
        "messages": [],
        "query": req.query,
        "game_filter": req.game or "all",
        "tool_calls": [],
    }
    
    with using_attributes(tags=["card_search", "api_request"]):
        if _TRACING:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute("query", req.query)
                current_span.set_attribute("game_filter", req.game or "all")
        
        result = graph.invoke(state)
    
    # Build response
    ebay_data = result.get("ebay_data", {})
    
    if not ebay_data or not ebay_data.get("found"):
        error_msg = ebay_data.get("message") if ebay_data else f"No listings found for '{req.query}'"
        error_msg = ebay_data.get("error", error_msg) if isinstance(ebay_data, dict) else error_msg
        return CardSearchResponse(error=error_msg)
    
    # Build card response from search data
    price_stats = ebay_data.get("price_stats", {})
    sample_listings = ebay_data.get("sample_listings", [])
    is_estimated = ebay_data.get("estimated", False)
    source = ebay_data.get("source", "eBay")
    
    # Get first listing for image
    first_listing = sample_listings[0] if sample_listings else {}
    
    # Build marketplace label
    if is_estimated:
        marketplace_name = f"{source}"
        marketplace_url = "#"
    else:
        listing_count = ebay_data.get("total_listings", 0)
        marketplace_name = f"eBay ({listing_count} listings)"
        marketplace_url = first_listing.get("url", "https://ebay.com")
    
    response_card = CardResponse(
        id=f"card-{req.query.lower().replace(' ', '-')}",
        name=ebay_data.get("card_name", req.query),
        set=None,
        rarity=None,
        game=req.game or "Trading Card",
        image=first_listing.get("image"),
        prices={
            "market": CardPrice(
                low=price_stats.get("low", 0),
                market=price_stats.get("average", 0),
                high=price_stats.get("high", 0)
            )
        },
        marketplaces=[
            MarketplacePrice(
                name=marketplace_name,
                price=price_stats.get("average", 0),
                url=marketplace_url
            )
        ],
        summary=result.get("summary", "Price data retrieved successfully.")
    )
    
    return CardSearchResponse(card=response_card)


# ========================================
# Initialize Tracing
# ========================================

if _TRACING:
    try:
        from arize.otel import Endpoint
        space_id = os.getenv("ARIZE_SPACE_ID")
        api_key = os.getenv("ARIZE_API_KEY")
        if space_id and api_key:
            print(f"[Arize] Initializing tracing for project: trading-card-price-checker (EU endpoint)")
            tp = register(
                space_id=space_id,
                api_key=api_key,
                project_name="trading-card-price-checker",
                endpoint=Endpoint.ARIZE_EUROPE,  # EU endpoint for EU users
                log_to_console=True,
            )
            LangChainInstrumentor().instrument(tracer_provider=tp)
            LiteLLMInstrumentor().instrument(tracer_provider=tp, skip_dep_check=True)
            print("[Arize] Tracing initialized successfully - spans will appear in console and Arize AX (EU)")
        else:
            print("[Arize] Skipping tracing - ARIZE_SPACE_ID or ARIZE_API_KEY not set")
    except Exception as e:
        print(f"[Arize] Failed to initialize tracing: {e}")


# ========================================
# Run Server
# ========================================

if __name__ == "__main__":
    import uvicorn
    print(f"[eBay] API configured: {ebay_client.is_configured}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
