"""
Regional Classifier using DistilBERT + keyword-based fallback
Classifies claims by Region (SG/AU) and Category (Home/Business)
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple

import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    pipeline,
)

logger = logging.getLogger(__name__)


class RegionalClassifier:
    """
    Hybrid classifier combining:
    1. DistilBERT zero-shot classification for semantic understanding
    2. Keyword-based rules for high-confidence regional markers
    """
    
    # Regional keywords with strong association
    REGION_KEYWORDS = {
        "SG": {
            "locations": [
                "singapore", "bedok", "tampines", "jurong", "woodlands",
                "ang mo kio", "toa payoh", "clementi", "orchard", "pasir ris",
                "punggol", "sengkang", "yishun", "hougang", "bishan",
                "bukit", "marine parade", "geylang", "kallang", "serangoon",
                "changi", "hdb", "condo", "flat",
            ],
            "insurers": ["msig", "ntuc", "aia singapore", "great eastern"],
            "terms": ["sgd", "s$", "cpf", "medishield", "eldershield"],
        },
        "AU": {
            "locations": [
                "australia", "sydney", "melbourne", "brisbane", "perth",
                "adelaide", "canberra", "hobart", "darwin", "gold coast",
                "newcastle", "wollongong", "geelong", "cairns", "townsville",
                "nsw", "vic", "qld", "wa", "sa", "tas", "nt", "act",
                "warehouse", "factory", "industrial",
            ],
            "insurers": ["zurich australia", "allianz australia", "qbe", "suncorp"],
            "terms": ["aud", "a$", "abn", "gst australia"],
        },
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        "Home": [
            "home", "house", "flat", "apartment", "condo", "hdb",
            "residential", "dwelling", "water leak", "pipe", "air-con",
            "aircon", "air conditioning", "flood", "fire damage home",
            "burglary home", "personal property", "furniture", "appliance",
            "renovation", "tenant", "landlord", "domestic",
        ],
        "Business": [
            "business", "commercial", "warehouse", "factory", "office",
            "machinery", "equipment", "inventory", "stock", "liability",
            "employee", "workers", "industrial", "manufacturing",
            "retail", "shop", "premises", "commercial property",
            "business interruption", "professional indemnity",
        ],
    }
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        """Initialize the classifier with optional transformer model"""
        import os
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Check if we should use lightweight mode (for Railway free tier)
        use_lightweight = os.getenv("LIGHTWEIGHT_MODE", "true").lower() == "true"
        
        if use_lightweight:
            logger.info("Using lightweight keyword-only classification (LIGHTWEIGHT_MODE=true)")
            self.classifier = None
            self.model_loaded = False
        else:
            # Load zero-shot classification pipeline (requires ~2GB RAM)
            try:
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="typeform/distilbert-base-uncased-mnli",  # Much smaller than BART
                    device=0 if self.device == "cuda" else -1,
                )
                self.model_loaded = True
                logger.info("Zero-shot classifier loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load transformer model: {e}")
                logger.warning("Falling back to keyword-only classification")
                self.classifier = None
                self.model_loaded = False
    
    def _keyword_match(self, text: str) -> Tuple[Optional[str], Optional[str], float, str]:
        """
        Perform keyword-based classification.
        Returns: (region, category, confidence, reasoning)
        """
        text_lower = text.lower()
        
        # Count regional keyword matches
        region_scores = {"SG": 0, "AU": 0}
        region_matches = {"SG": [], "AU": []}
        
        for region, keyword_groups in self.REGION_KEYWORDS.items():
            for group_name, keywords in keyword_groups.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        region_scores[region] += 1
                        region_matches[region].append(keyword)
        
        # Count category keyword matches
        category_scores = {"Home": 0, "Business": 0}
        category_matches = {"Home": [], "Business": []}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    category_scores[category] += 1
                    category_matches[category].append(keyword)
        
        # Determine region
        region = None
        region_confidence = 0.0
        if region_scores["SG"] > region_scores["AU"]:
            region = "SG"
            region_confidence = min(0.5 + region_scores["SG"] * 0.15, 0.95)
        elif region_scores["AU"] > region_scores["SG"]:
            region = "AU"
            region_confidence = min(0.5 + region_scores["AU"] * 0.15, 0.95)
        
        # Determine category
        category = None
        category_confidence = 0.0
        if category_scores["Home"] > category_scores["Business"]:
            category = "Home"
            category_confidence = min(0.5 + category_scores["Home"] * 0.1, 0.95)
        elif category_scores["Business"] > category_scores["Home"]:
            category = "Business"
            category_confidence = min(0.5 + category_scores["Business"] * 0.1, 0.95)
        
        # Build reasoning
        reasoning_parts = []
        if region and region_matches[region]:
            reasoning_parts.append(
                f"Region {region} detected via keywords: {', '.join(region_matches[region][:5])}"
            )
        if category and category_matches[category]:
            reasoning_parts.append(
                f"Category {category} detected via keywords: {', '.join(category_matches[category][:5])}"
            )
        
        combined_confidence = (region_confidence + category_confidence) / 2 if region and category else 0.0
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No strong keyword indicators found"
        
        return region, category, combined_confidence, reasoning
    
    def _transformer_classify(self, text: str) -> Tuple[str, str, float, str]:
        """
        Use zero-shot classification for semantic understanding.
        Returns: (region, category, confidence, reasoning)
        """
        if not self.classifier:
            return None, None, 0.0, "Transformer model not available"
        
        # Classify region (orthogonal labels - no category bias)
        region_result = self.classifier(
            text,
            candidate_labels=[
                "This is an insurance claim from Singapore",
                "This is an insurance claim from Australia",
            ],
        )
        
        region_label = region_result["labels"][0]
        region_score = region_result["scores"][0]
        
        if "Singapore" in region_label:
            region = "SG"
        else:
            region = "AU"
        
        # Classify category (orthogonal labels - no region bias)
        category_result = self.classifier(
            text,
            candidate_labels=[
                "This is a residential home property insurance claim",
                "This is a commercial business property insurance claim",
            ],
        )
        
        category_label = category_result["labels"][0]
        category_score = category_result["scores"][0]
        
        if "residential" in category_label or "home" in category_label:
            category = "Home"
        else:
            category = "Business"
        
        combined_confidence = (region_score + category_score) / 2
        reasoning = (
            f"Semantic analysis: {region_label} ({region_score:.2f}), "
            f"{category_label} ({category_score:.2f})"
        )
        
        return region, category, combined_confidence, reasoning
    
    def classify(
        self,
        text: str,
        include_reasoning: bool = True,
    ) -> Dict[str, Any]:
        """
        Classify a claim by region and category using hybrid approach.
        
        Strategy:
        1. First check for strong keyword matches
        2. If keywords are ambiguous, use transformer classification
        3. Combine results with weighted confidence
        """
        # Get keyword-based classification
        kw_region, kw_category, kw_confidence, kw_reasoning = self._keyword_match(text)
        
        # If keywords are strong enough (confidence > 0.5), use them
        # This ensures strong regional markers like "Bedok" always win
        if kw_confidence > 0.5 and kw_region and kw_category:
            result = {
                "region": kw_region,
                "category": kw_category,
                "confidence": kw_confidence,
            }
            if include_reasoning:
                result["reasoning"] = f"[Keyword Match] {kw_reasoning}"
            return result
        
        # Try transformer classification
        tf_region, tf_category, tf_confidence, tf_reasoning = self._transformer_classify(text)
        
        # Combine results
        if tf_region and tf_confidence > kw_confidence:
            final_region = tf_region
            final_category = tf_category or kw_category or "Home"  # Default to Home
            final_confidence = tf_confidence
            final_reasoning = tf_reasoning
        elif kw_region:
            final_region = kw_region
            final_category = kw_category or "Home"
            final_confidence = kw_confidence
            final_reasoning = kw_reasoning
        else:
            # Default fallback
            final_region = "SG"  # Default region
            final_category = "Home"  # Default category
            final_confidence = 0.3
            final_reasoning = "Low confidence classification - defaulting to SG/Home"
        
        result = {
            "region": final_region,
            "category": final_category,
            "confidence": final_confidence,
        }
        
        if include_reasoning:
            result["reasoning"] = final_reasoning
        
        return result
