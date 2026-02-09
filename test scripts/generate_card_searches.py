#!/usr/bin/env python3
"""
Synthetic data generator for Trading Card Price Checker - creates traces for Arize Evals.

- Sends crafted card search requests to /api/cards/search
- Tests various card names, games, and edge cases
- Captures responses and flags potential issues
- Saves a JSON report you can correlate with Arize traces

Usage:
  python generate_card_searches.py --base-url http://localhost:8000 --count 20 --outfile synthetic_card_searches.json
"""

import argparse
import json
import os
import random
import time
from datetime import datetime
from typing import Any, Dict, List

import requests


def card_search_scenarios() -> List[Dict[str, Any]]:
    """Curated card search scenarios for testing.

    Each scenario includes the search request, expected behavior,
    and potential issues to watch for in evaluations.
    """
    
    # Popular/common cards - should return good results
    popular_cards = [
        {
            "name": "Popular: Black Lotus",
            "request": {"query": "Black Lotus", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "expect_high_price": True,
            "notes": "Most expensive MTG card",
        },
        {
            "name": "Popular: Charizard Base Set",
            "request": {"query": "Charizard Base Set 1999", "game": "pokemon"},
            "expected_game": "Pokémon",
            "expect_high_price": True,
            "notes": "Iconic Pokemon card",
        },
        {
            "name": "Popular: Blue-Eyes White Dragon",
            "request": {"query": "Blue-Eyes White Dragon LOB", "game": "yugioh"},
            "expected_game": "Yu-Gi-Oh!",
            "expect_high_price": False,
            "notes": "Classic Yu-Gi-Oh card",
        },
        {
            "name": "Popular: Dark Magician",
            "request": {"query": "Dark Magician LOB", "game": "yugioh"},
            "expected_game": "Yu-Gi-Oh!",
            "expect_high_price": False,
            "notes": "Yugi's signature card",
        },
        {
            "name": "Popular: Pikachu Illustrator",
            "request": {"query": "Pikachu Illustrator", "game": "pokemon"},
            "expected_game": "Pokémon",
            "expect_high_price": True,
            "notes": "Rarest Pokemon card",
        },
        {
            "name": "Popular: Mickey Mantle 1952",
            "request": {"query": "Mickey Mantle 1952 Topps", "game": "sports"},
            "expected_game": "Sports",
            "expect_high_price": True,
            "notes": "Most valuable baseball card",
        },
    ]
    
    # Specific set/edition searches
    specific_searches = [
        {
            "name": "Specific: Alpha Black Lotus",
            "request": {"query": "Black Lotus Alpha Edition", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Specific edition search",
        },
        {
            "name": "Specific: 1st Edition Charizard",
            "request": {"query": "Charizard 1st Edition Shadowless", "game": "pokemon"},
            "expected_game": "Pokémon",
            "notes": "Most valuable Charizard variant",
        },
        {
            "name": "Specific: PSA 10 Graded",
            "request": {"query": "Charizard PSA 10 Base Set", "game": "pokemon"},
            "expected_game": "Pokémon",
            "notes": "Graded card search",
        },
        {
            "name": "Specific: Japanese Card",
            "request": {"query": "Pikachu Japanese Promo", "game": "pokemon"},
            "expected_game": "Pokémon",
            "notes": "Region-specific search",
        },
    ]
    
    # Edge cases and potential problem searches
    edge_cases = [
        {
            "name": "Edge: Misspelled Card Name",
            "request": {"query": "Charazard", "game": "pokemon"},
            "expected_game": "Pokémon",
            "notes": "Should handle misspellings",
            "potential_issue": "misspelling",
        },
        {
            "name": "Edge: Partial Name",
            "request": {"query": "Lotus", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Partial name search",
            "potential_issue": "ambiguous",
        },
        {
            "name": "Edge: Very Common Card",
            "request": {"query": "Island", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Basic land - many versions",
            "potential_issue": "too_many_results",
        },
        {
            "name": "Edge: Nonexistent Card",
            "request": {"query": "Super Mega Ultra Dragon XYZ", "game": "all"},
            "expected_game": None,
            "notes": "Should return no results gracefully",
            "potential_issue": "not_found",
        },
        {
            "name": "Edge: Wrong Game Filter",
            "request": {"query": "Charizard", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Pokemon card with MTG filter",
            "potential_issue": "wrong_game",
        },
        {
            "name": "Edge: Special Characters",
            "request": {"query": "Jace, the Mind Sculptor", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Card name with comma",
        },
        {
            "name": "Edge: Very Long Query",
            "request": {"query": "Blue-Eyes White Dragon Legend of Blue Eyes White Dragon 1st Edition LOB-001 Near Mint", "game": "yugioh"},
            "expected_game": "Yu-Gi-Oh!",
            "notes": "Very detailed search query",
        },
    ]
    
    # Price expectation tests
    price_tests = [
        {
            "name": "Price: Budget Card",
            "request": {"query": "Pikachu Base Set", "game": "pokemon"},
            "expected_game": "Pokémon",
            "expect_high_price": False,
            "notes": "Common card, should be cheap",
        },
        {
            "name": "Price: Mid-Range Card",
            "request": {"query": "Liliana of the Veil", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "expect_high_price": False,
            "notes": "Popular but not ultra-rare",
        },
        {
            "name": "Price: Reserved List",
            "request": {"query": "Underground Sea", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "expect_high_price": True,
            "notes": "Reserved list dual land",
        },
    ]
    
    # Game-specific searches
    game_specific = [
        {
            "name": "MTG: Power Nine",
            "request": {"query": "Mox Sapphire", "game": "mtg"},
            "expected_game": "Magic: The Gathering",
            "notes": "Power Nine card",
        },
        {
            "name": "Pokemon: Modern Chase",
            "request": {"query": "Moonbreon VMAX Alt Art", "game": "pokemon"},
            "expected_game": "Pokémon",
            "notes": "Modern valuable card",
        },
        {
            "name": "YuGiOh: Meta Card",
            "request": {"query": "Ash Blossom & Joyous Spring", "game": "yugioh"},
            "expected_game": "Yu-Gi-Oh!",
            "notes": "Competitive staple",
        },
        {
            "name": "Sports: Rookie Card",
            "request": {"query": "Michael Jordan Fleer Rookie", "game": "sports"},
            "expected_game": "Sports",
            "notes": "Iconic sports card",
        },
    ]
    
    return popular_cards + specific_searches + edge_cases + price_tests + game_specific


def post_card_search(base_url: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """Send a card search request to the API."""
    url = f"{base_url.rstrip('/')}/api/cards/search"
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}
        return {"status": r.status_code, "data": data}
    except requests.exceptions.RequestException as e:
        return {"status": 0, "data": {"error": str(e)}}


def evaluate_search_result(
    response: Dict[str, Any],
    scenario: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluate the quality of a search result."""
    
    status = response["status"]
    data = response.get("data", {})
    
    evaluation = {
        "success": status == 200,
        "has_card": data.get("card") is not None,
        "has_error": data.get("error") is not None,
        "issues": [],
        "quality_score": 0,
    }
    
    if status != 200:
        evaluation["issues"].append(f"HTTP error: {status}")
        return evaluation
    
    if data.get("error"):
        # Check if this was expected
        if scenario.get("potential_issue") == "not_found":
            evaluation["expected_no_result"] = True
            evaluation["quality_score"] = 80  # Expected behavior
        else:
            evaluation["issues"].append(f"API error: {data['error']}")
        return evaluation
    
    card = data.get("card", {})
    if not card:
        if scenario.get("potential_issue") == "not_found":
            evaluation["expected_no_result"] = True
            evaluation["quality_score"] = 80
        else:
            evaluation["issues"].append("No card data returned")
        return evaluation
    
    # Evaluate card data quality
    quality_points = 0
    
    # Has name
    if card.get("name"):
        quality_points += 20
    else:
        evaluation["issues"].append("Missing card name")
    
    # Has price data
    if card.get("prices"):
        quality_points += 25
        prices = card["prices"]
        # Check for reasonable prices
        for condition, price_data in prices.items():
            if isinstance(price_data, dict):
                market = price_data.get("market", 0)
                if market > 0:
                    quality_points += 5
    else:
        evaluation["issues"].append("Missing price data")
    
    # Has marketplace info
    if card.get("marketplaces"):
        quality_points += 15
    else:
        evaluation["issues"].append("Missing marketplace data")
    
    # Has summary
    if card.get("summary") and len(card["summary"]) > 20:
        quality_points += 15
    else:
        evaluation["issues"].append("Missing or short summary")
    
    # Has image
    if card.get("image"):
        quality_points += 10
    
    # Check price expectations
    if scenario.get("expect_high_price"):
        prices = card.get("prices", {})
        market_price = 0
        for p in prices.values():
            if isinstance(p, dict):
                market_price = max(market_price, p.get("market", 0))
        if market_price < 100:
            evaluation["issues"].append(f"Expected high price, got ${market_price}")
    
    evaluation["quality_score"] = min(quality_points, 100)
    
    return evaluation


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic card search requests for Arize traces.")
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--count", type=int, default=20, help="Total requests to send")
    parser.add_argument("--outfile", default="synthetic_card_searches.json")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--random", action="store_true", help="Randomize scenario order")
    args = parser.parse_args()

    scenarios = card_search_scenarios()
    
    if args.random:
        random.shuffle(scenarios)
    
    results: List[Dict[str, Any]] = []

    print("🃏 Trading Card Price Checker - Synthetic Data Generator")
    print("=" * 70)
    print(f"Target: {args.base_url}")
    print(f"Scenarios: {len(scenarios)} | Requests: {args.count}")
    print("=" * 70)

    for i in range(args.count):
        # Cycle through scenarios
        scenario = scenarios[i % len(scenarios)]
        payload = scenario["request"].copy()
        
        print(f"\n#{i+1:02d} {scenario['name']}")
        print(f"    Query: \"{payload['query']}\" | Game: {payload.get('game', 'all')}")

        start = time.time()
        resp = post_card_search(args.base_url, payload)
        elapsed = time.time() - start

        status = resp["status"]
        data = resp["data"] if isinstance(resp["data"], dict) else {"raw": resp["data"]}
        
        # Evaluate result
        evaluation = evaluate_search_result(resp, scenario)
        
        # Extract key info for logging
        card = data.get("card", {})
        card_name = card.get("name", "N/A") if card else "N/A"
        
        # Get price if available
        price_str = "N/A"
        if card and card.get("prices"):
            for p in card["prices"].values():
                if isinstance(p, dict) and p.get("market"):
                    price_str = f"${p['market']:.2f}"
                    break
        
        status_icon = "✅" if evaluation["success"] and evaluation["has_card"] else "❌"
        print(f"    {status_icon} HTTP {status} in {elapsed:.1f}s | Card: {card_name} | Price: {price_str}")
        
        if evaluation["issues"]:
            print(f"    ⚠️  Issues: {', '.join(evaluation['issues'][:2])}")

        results.append({
            "id": i + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "scenario": scenario["name"],
            "request": payload,
            "response_status": status,
            "card_found": card_name if card else None,
            "evaluation": evaluation,
            "elapsed_seconds": round(elapsed, 2),
            "notes": scenario.get("notes", ""),
            "arize_trace_hint": "Filter by timestamp in Arize to find this trace.",
        })

        time.sleep(args.delay)

    # Generate summary
    successful = [r for r in results if r["evaluation"]["success"] and r["evaluation"]["has_card"]]
    failed = [r for r in results if not r["evaluation"]["success"] or not r["evaluation"]["has_card"]]
    avg_quality = sum(r["evaluation"]["quality_score"] for r in results) / len(results) if results else 0
    
    summary = {
        "total_requests": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": f"{len(successful)/len(results)*100:.1f}%" if results else "0%",
        "average_quality_score": round(avg_quality, 1),
        "average_response_time": round(sum(r["elapsed_seconds"] for r in results) / len(results), 2) if results else 0,
        "common_issues": list(set(
            issue 
            for r in results 
            for issue in r["evaluation"].get("issues", [])
        ))[:5],
    }

    out = {"summary": summary, "results": results}
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("📦 Results saved to:", args.outfile)
    print("\n📊 Summary:")
    print(f"   Total: {summary['total_requests']} | Success: {summary['successful']} | Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']}")
    print(f"   Avg Quality Score: {summary['average_quality_score']}/100")
    print(f"   Avg Response Time: {summary['average_response_time']}s")
    
    if summary["common_issues"]:
        print(f"\n⚠️  Common Issues: {', '.join(summary['common_issues'][:3])}")
    
    print("\n👉 In Arize: Explore traces to see the agent pipeline for each search.")
    print("   Filter by project 'trading-card-price-checker' and recent timestamps.")


if __name__ == "__main__":
    main()
