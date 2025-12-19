import json
import urllib.request
import urllib.error
import sys

def test_api():
    url = "http://127.0.0.1:8000/analyze"
    print(f"Testing API at {url}...")
    
    try:
        with open("data/sample_request.json", "r") as f:
            data = json.load(f)
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"API Response Status: {response.status}")
            print(f"Signal: {result.get('signal')}")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Reasoning: {result.get('reasoning')[:100]}...")
            print("API Verification Passed!")
            
    except urllib.error.URLError as e:
        print(f"API Request Failed: {e}")
        if hasattr(e, 'read'):
            try:
                print(e.read().decode('utf-8'))
            except:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
