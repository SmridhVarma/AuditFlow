"""
Evaluation script for testing routing accuracy
"""

import json
import os
import asyncio
from typing import Dict, List

import httpx


async def evaluate_routing(router_url: str = "http://localhost:8001"):
    """Evaluate routing accuracy against synthetic claims"""
    
    # Load synthetic claims
    claims_path = os.path.join(
        os.path.dirname(__file__),
        "..", "data", "evaluation", "synthetic_claims.json"
    )
    
    with open(claims_path, "r") as f:
        data = json.load(f)
    
    claims = data["claims"]
    
    results = {
        "total": len(claims),
        "correct_region": 0,
        "correct_category": 0,
        "correct_both": 0,
        "details": [],
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for claim in claims:
            try:
                response = await client.post(
                    f"{router_url}/classify",
                    json={"claim_text": claim["text"], "include_reasoning": True},
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    region_match = result["region"] == claim["expected_region"]
                    category_match = result["category"] == claim["expected_category"]
                    
                    if region_match:
                        results["correct_region"] += 1
                    if category_match:
                        results["correct_category"] += 1
                    if region_match and category_match:
                        results["correct_both"] += 1
                    
                    results["details"].append({
                        "id": claim["id"],
                        "expected_region": claim["expected_region"],
                        "predicted_region": result["region"],
                        "region_correct": region_match,
                        "expected_category": claim["expected_category"],
                        "predicted_category": result["category"],
                        "category_correct": category_match,
                        "confidence": result["confidence"],
                    })
                else:
                    print(f"Error for {claim['id']}: {response.status_code}")
                    
            except Exception as e:
                print(f"Error for {claim['id']}: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("ROUTING EVALUATION RESULTS")
    print("="*60)
    print(f"Total Claims: {results['total']}")
    print(f"Region Accuracy: {results['correct_region']}/{results['total']} ({100*results['correct_region']/results['total']:.1f}%)")
    print(f"Category Accuracy: {results['correct_category']}/{results['total']} ({100*results['correct_category']/results['total']:.1f}%)")
    print(f"Both Correct: {results['correct_both']}/{results['total']} ({100*results['correct_both']/results['total']:.1f}%)")
    print("="*60)
    
    # Print failures
    failures = [d for d in results["details"] if not (d["region_correct"] and d["category_correct"])]
    if failures:
        print("\nMisclassified Claims:")
        for f in failures:
            print(f"  {f['id']}: Expected {f['expected_region']}/{f['expected_category']}, "
                  f"Got {f['predicted_region']}/{f['predicted_category']} "
                  f"(conf: {f['confidence']:.2f})")
    
    return results


if __name__ == "__main__":
    asyncio.run(evaluate_routing())
