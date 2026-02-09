# Trading Card Price Checker – Product Requirements Document

## 1. Summary

**Objective:** Build a **Trading Card Price Checker** that allows users to search for trading cards by name and retrieve current market prices from multiple sources.

**Approach:** Create a FastAPI backend with AI-powered card identification and price aggregation, paired with a clean, responsive frontend UI. Integrate Arize AX for full observability and tracing of the AI agent workflow.

**Target Users:** Trading card collectors, resellers, and enthusiasts who want quick, accurate pricing information.

---

## 2. Problem & Goals

### Problem

Trading card collectors face challenges when trying to determine fair market value:

- Prices vary significantly across marketplaces (TCGPlayer, eBay, CardMarket, etc.)
- Card names can be ambiguous (multiple editions, variants, conditions)
- Manual price checking across multiple sites is time-consuming
- Identifying the exact card from a partial name is difficult

### Primary Goal

Enable users to **search for any trading card by name** and instantly see aggregated pricing data with AI-assisted card identification.

### Secondary Goals

- Provide price ranges across different conditions (Near Mint, Lightly Played, etc.)
- Show price trends and recent sales data
- Support multiple trading card games (Magic: The Gathering, Pokémon, Yu-Gi-Oh!, etc.)
- Demonstrate AI agent tracing with Arize AX for educational purposes

### Out of Scope (v1)

- User accounts and saved searches
- Price alerts and notifications
- Direct purchase integration
- Card scanning/image recognition

---

## 3. Users & Use Cases

### Primary Users

| Role | Description |
|------|-------------|
| **Collectors** | Check value of cards in their collection |
| **Buyers** | Research fair prices before purchasing |
| **Sellers** | Price cards competitively for resale |
| **Traders** | Evaluate trade fairness |

### Key Use Cases

| ID | Use Case | Description |
|----|----------|-------------|
| UC1 | **Search by card name** | Enter partial or full card name to find matches |
| UC2 | **View price breakdown** | See prices across conditions and marketplaces |
| UC3 | **Select card variant** | Choose specific edition/set when multiple exist |
| UC4 | **Compare prices** | View side-by-side pricing from different sources |
| UC5 | **View price history** | See recent price trends (if available) |

---

## 4. Functional Requirements

### 4.1 Frontend UI

#### FR1 – Search Interface

- **Search input** with autocomplete suggestions
- Support for partial name matching (e.g., "Black Lotus" or "Charizard")
- Game selector dropdown (MTG, Pokémon, Yu-Gi-Oh!, Sports, etc.)
- Search button with keyboard shortcut (Enter)

#### FR2 – Card Results Display

- **Card preview card** showing:
  - Card image (if available)
  - Full card name
  - Set/Edition name
  - Rarity indicator
  - Card number

#### FR3 – Price Display Widget

- **Price breakdown table** showing:
  | Condition | Low | Market | High |
  |-----------|-----|--------|------|
  | Near Mint | $X  | $Y     | $Z   |
  | Lightly Played | ... | ... | ... |
  | Moderately Played | ... | ... | ... |

- **Marketplace comparison:**
  - TCGPlayer price
  - eBay recent sales
  - CardMarket (EU)
  - Other sources as available

#### FR4 – Multiple Results Handling

- When search returns multiple cards:
  - Display card grid/list with thumbnails
  - Allow user to select specific card
  - Show set/edition to differentiate variants

#### FR5 – Error States

| State | Display |
|-------|---------|
| No results | "No cards found matching '[query]'. Try a different search term." |
| API error | "Unable to fetch prices. Please try again." |
| Loading | Skeleton loader with spinner |

---

### 4.2 Backend / API

#### FR6 – Search Endpoint

```
GET /api/cards/search?q={query}&game={game}
```

**Response:**
```json
{
  "cards": [
    {
      "id": "card-123",
      "name": "Black Lotus",
      "set": "Alpha",
      "set_code": "LEA",
      "rarity": "Rare",
      "image_url": "https://...",
      "game": "mtg"
    }
  ],
  "total": 5
}
```

#### FR7 – Price Endpoint

```
GET /api/cards/{card_id}/prices
```

**Response:**
```json
{
  "card_id": "card-123",
  "name": "Black Lotus",
  "prices": {
    "near_mint": { "low": 10000, "market": 25000, "high": 50000 },
    "lightly_played": { "low": 8000, "market": 20000, "high": 40000 }
  },
  "sources": [
    { "name": "TCGPlayer", "price": 25000, "url": "https://..." },
    { "name": "eBay", "price": 28000, "url": "https://..." }
  ],
  "last_updated": "2026-01-29T12:00:00Z"
}
```

#### FR8 – AI Agent for Card Identification

- Use LLM to disambiguate card names
- Agent workflow:
  1. **Search Agent**: Find matching cards from database/API
  2. **Identification Agent**: Determine most likely card user is looking for
  3. **Price Agent**: Aggregate prices from multiple sources
  4. **Summary Agent**: Generate human-readable price summary

---

### 4.3 AI Agent Architecture

#### FR9 – Multi-Agent Graph (LangGraph)

```
┌─────────────────────────────────────────────────────┐
│                      START                          │
│                        │                            │
│                        ▼                            │
│              ┌─────────────────┐                    │
│              │  Search Agent   │                    │
│              │ (Find matches)  │                    │
│              └────────┬────────┘                    │
│                       │                             │
│         ┌─────────────┼─────────────┐              │
│         ▼             ▼             ▼              │
│  ┌────────────┐ ┌───────────┐ ┌───────────┐       │
│  │ TCGPlayer  │ │   eBay    │ │ CardMarket│       │
│  │   Tool     │ │   Tool    │ │   Tool    │       │
│  └─────┬──────┘ └─────┬─────┘ └─────┬─────┘       │
│        └──────────────┼─────────────┘              │
│                       ▼                             │
│              ┌─────────────────┐                    │
│              │  Price Agent    │                    │
│              │ (Aggregate)     │                    │
│              └────────┬────────┘                    │
│                       ▼                             │
│              ┌─────────────────┐                    │
│              │ Summary Agent   │                    │
│              │ (Format output) │                    │
│              └────────┬────────┘                    │
│                       ▼                             │
│                      END                            │
└─────────────────────────────────────────────────────┘
```

#### FR10 – Agent Tools

| Tool | Purpose |
|------|---------|
| `search_cards` | Query card database by name |
| `get_tcgplayer_price` | Fetch TCGPlayer pricing |
| `get_ebay_sales` | Fetch recent eBay sold listings |
| `get_cardmarket_price` | Fetch CardMarket (EU) pricing |
| `identify_card` | Use LLM to disambiguate similar cards |

---

### 4.4 Observability (Arize AX)

#### FR11 – Tracing Requirements

- **Full trace visibility** for each price check request
- Track each agent node execution
- Capture tool calls and responses
- Log LLM prompts and completions
- Session and user tracking (optional)

#### FR12 – Instrumentation

```python
from arize.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# Initialize at startup
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),
    api_key=os.getenv("ARIZE_API_KEY"),
    project_name="trading-card-price-checker",
    log_to_console=True,
)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
```

---

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | **Response time** | Search results < 2 seconds |
| NFR2 | **Price freshness** | Data no older than 1 hour |
| NFR3 | **Availability** | 99% uptime for API |
| NFR4 | **Observability** | 100% of requests traced in Arize |
| NFR5 | **Mobile responsive** | UI works on mobile devices |

---

## 6. Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **AI Framework** | LangGraph + LangChain |
| **LLM** | OpenAI GPT-4o-mini (or OpenRouter) |
| **Frontend** | HTML + Tailwind CSS + Vanilla JS |
| **Observability** | Arize AX + OpenTelemetry |
| **Data Sources** | TCGPlayer API, Scryfall API (MTG), PokémonTCG API |

---

## 7. UI Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│  🃏 Trading Card Price Checker                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔍 Enter card name...                    [Search]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Game: [MTG ▼] [Pokémon] [Yu-Gi-Oh!] [Sports] [Other]      │
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │                     │  │  PRICE BREAKDOWN            │  │
│  │    [Card Image]     │  │                             │  │
│  │                     │  │  Condition    Low   Market  │  │
│  │                     │  │  ─────────────────────────  │  │
│  │  Black Lotus        │  │  Near Mint   $20K   $25K   │  │
│  │  Alpha (LEA)        │  │  LP          $15K   $20K   │  │
│  │  ⭐ Rare            │  │  MP          $10K   $15K   │  │
│  │                     │  │                             │  │
│  └─────────────────────┘  │  MARKETPLACE PRICES         │  │
│                           │  TCGPlayer: $25,000         │  │
│                           │  eBay (avg): $28,000        │  │
│                           │  CardMarket: €22,000        │  │
│                           └─────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  💡 AI Summary: Black Lotus from Alpha is one of    │   │
│  │  the most valuable MTG cards. Current market price  │   │
│  │  is approximately $25,000 for Near Mint condition.  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Data Sources

### Primary APIs

| Source | Game Support | Notes |
|--------|--------------|-------|
| [Scryfall](https://scryfall.com/docs/api) | MTG | Free, comprehensive MTG data |
| [PokémonTCG API](https://pokemontcg.io/) | Pokémon | Free, official card data |
| [TCGPlayer API](https://docs.tcgplayer.com/) | All | Requires API key, pricing data |
| [YGOProDeck](https://ygoprodeck.com/api-guide/) | Yu-Gi-Oh! | Free card database |

### Fallback Strategy

If primary API unavailable:
1. Use cached data (if < 24 hours old)
2. Use LLM to estimate price range based on training data
3. Display "Price unavailable" with link to manual search

---

## 9. Environment Variables

```env
# LLM Provider
OPENAI_API_KEY=your_openai_api_key

# Arize Observability
ARIZE_SPACE_ID=your_space_id
ARIZE_API_KEY=your_api_key

# Card Data APIs (optional - enables real pricing)
TCGPLAYER_API_KEY=your_tcgplayer_key
POKEMONTCG_API_KEY=your_pokemon_key
```

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| Search accuracy | 90%+ correct card identification |
| Price accuracy | Within 10% of actual market value |
| Response time | < 2 seconds for 95% of requests |
| Trace coverage | 100% of requests visible in Arize |
| User satisfaction | Can find card price in < 3 interactions |

---

## 11. Future Enhancements

| Priority | Feature | Description |
|----------|---------|-------------|
| High | Price alerts | Notify when card drops below threshold |
| High | Collection tracker | Save and track collection value |
| Medium | Price history charts | Visualize price trends over time |
| Medium | Bulk lookup | Check prices for multiple cards at once |
| Low | Image search | Upload card photo to identify |
| Low | Marketplace links | Direct links to buy/sell listings |

---

## 12. Implementation Phases

### Phase 1: MVP (Current)
- [ ] Basic search UI
- [ ] Single card lookup
- [ ] Mock price data
- [ ] Arize tracing setup

### Phase 2: Real Data
- [ ] Integrate Scryfall API (MTG)
- [ ] Integrate PokémonTCG API
- [ ] Add condition-based pricing

### Phase 3: Enhanced Features
- [ ] Multi-game support
- [ ] Price comparison view
- [ ] AI-generated summaries

---

*Last updated: January 29, 2026*
