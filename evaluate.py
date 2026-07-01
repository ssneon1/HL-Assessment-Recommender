import json
import urllib.request
import os
from run_zero_dependency import ZeroDependencyHandler

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Load from .env if needed
if not GEMINI_API_KEY and os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                if key == "GEMINI_API_KEY":
                    GEMINI_API_KEY = val.strip()
                    os.environ[key] = GEMINI_API_KEY

def evaluate_with_llm(scenario, response_data):
    if not GEMINI_API_KEY:
        print("API key missing. Cannot evaluate.")
        return None
        
    eval_prompt = f"""
    You are an impartial evaluator grading an AI Assessment Recommender system.
    
    User Query: {scenario['messages'][-1]['content']}
    
    System Response: {response_data['reply']}
    System Recommendations: {[r['name'] for r in response_data.get('recommendations', [])]}
    
    Evaluate the response on the following 3 criteria on a scale of 1 to 5:
    1. Retrieval Quality (1-5): Are the recommended assessments highly relevant to the user query?
    2. Recommendation Relevance (1-5): Did the system clearly explain WHY these are recommended and address the user's constraints?
    3. Groundedness (1-5): Is the response completely grounded in the recommendations? (Score 5 if no hallucinated tests are mentioned).
    
    Return ONLY a JSON object with these keys: retrieval_score, relevance_score, groundedness_score, reasoning.
    """
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "retrieval_score": {"type": "INTEGER"},
            "relevance_score": {"type": "INTEGER"},
            "groundedness_score": {"type": "INTEGER"},
            "reasoning": {"type": "STRING"}
        }
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": eval_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
    except Exception as e:
        print(f"Eval Error: {e}")
        return None

def main():
    scenarios = [
        {
            "name": "Java Developer",
            "messages": [{"role": "user", "content": "I am hiring a mid-level Java developer."}]
        },
        {
            "name": "Leadership",
            "messages": [{"role": "user", "content": "We need an assessment for an executive leadership role focusing on personality and competencies."}]
        },
        {
            "name": "Vague Request",
            "messages": [{"role": "user", "content": "I need a test."}]
        }
    ]
    
    # We will instantiate the handler to use its logic without running a full server
    # We pass dummy request/client_address/server arguments
    class DummyServer: pass
    try:
        # Just create the object without initializing the socketserver by bypassing __init__
        handler = ZeroDependencyHandler.__new__(ZeroDependencyHandler)
    except Exception:
        pass
        
    results = []
    
    for s in scenarios:
        print(f"Evaluating Scenario: {s['name']}...")
        # Process chat
        response_data = handler.process_chat(s)
        
        # Evaluate
        eval_scores = evaluate_with_llm(s, response_data)
        if eval_scores:
            s['eval'] = eval_scores
            s['response'] = response_data
            results.append(s)
            
            print(f"  Retrieval: {eval_scores['retrieval_score']}/5 | Relevance: {eval_scores['relevance_score']}/5 | Groundedness: {eval_scores['groundedness_score']}/5")
            print(f"  Reasoning: {eval_scores['reasoning']}\n")
            
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Saved detailed evaluation to evaluation_results.json")

if __name__ == "__main__":
    main()
