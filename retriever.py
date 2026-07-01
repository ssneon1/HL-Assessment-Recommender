import json
import math
from collections import Counter
import re
import os

def map_test_type(keys: list[str]) -> str:
    if not keys:
        return ""
    key = keys[0]
    # Simple mapping to first character based on the expected catalog format
    return key[0].upper()

class CatalogRetriever:
    def __init__(self, catalog_path: str):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f, strict=False)
        
        self.doc_freqs = Counter()
        self.doc_tokens = []
        self.N = len(self.catalog)
        
        for item in self.catalog:
            text = self._extract_text(item)
            tokens = self._tokenize(text)
            self.doc_tokens.append(tokens)
            for token in set(tokens):
                self.doc_freqs[token] += 1

    def _extract_text(self, item: dict) -> str:
        parts = [
            item.get('name', ''),
            item.get('description', ''),
            ' '.join(item.get('job_levels', [])),
            ' '.join(item.get('keys', []))
        ]
        return ' '.join(parts)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        # Extract alphanumeric tokens
        return re.findall(r'\w+', text)

    def search(self, keywords: list[str], specific_names: list[str] = None, top_k: int = 15):
        query_tokens = []
        for kw in keywords:
            query_tokens.extend(self._tokenize(kw))
            
        scores = []
        for i, tokens in enumerate(self.doc_tokens):
            item = self.catalog[i]
            score = 0.0
            
            # TF-IDF scoring for general keywords
            for token in query_tokens:
                if token in tokens:
                    tf = tokens.count(token)
                    idf = math.log((self.N - self.doc_freqs[token] + 0.5) / (self.doc_freqs[token] + 0.5) + 1.5)
                    score += tf * idf
                    
            # Boost if exact specific name is present in the item name
            if specific_names:
                item_name = item.get('name', '').lower()
                for name in specific_names:
                    if name.lower() in item_name:
                        score += 50.0  # Big boost for specific name match
            
            # Ensure we only include valid items with a name and url
            if item.get('name') and item.get('link'):
                scores.append((score, item))
                
        scores.sort(key=lambda x: x[0], reverse=True)
        # Return top items that have a non-zero score (or just top_k if no score filtering)
        # We will return top_k regardless, but prioritize highest scores
        top_items = [x[1] for x in scores[:top_k]]
        return top_items

    def format_for_llm(self, items: list[dict]) -> str:
        formatted = []
        for i, item in enumerate(items):
            test_type = map_test_type(item.get('keys', []))
            s = f"Item {i+1}:\n"
            s += f"Name: {item.get('name')}\n"
            s += f"URL: {item.get('link')}\n"
            s += f"Test Type: {test_type}\n"
            s += f"Keys: {', '.join(item.get('keys', []))}\n"
            s += f"Job Levels: {', '.join(item.get('job_levels', []))}\n"
            s += f"Description: {item.get('description', '')}\n"
            formatted.append(s)
        return "\n".join(formatted)

# Global instance initialized when module is loaded
# Adjust path relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "shl_product_catalog.json")

# Ensure it only loads if the file exists (helpful for tests or initial setup)
retriever_instance = None
if os.path.exists(CATALOG_PATH):
    retriever_instance = CatalogRetriever(CATALOG_PATH)
