import urllib.request
import json
import time

def send_post_request(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        print(f"[!] HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return None

def test_api():
    url = "http://localhost:8000/agent/sql"
    print("=" * 60)
    print("         TESTING FASTAPI TEXT-TO-SQL REST ENDPOINT")
    print("=" * 60)
    
    # ----------------------------------------------------
    # Test 1: Standard Valid DB Query
    # ----------------------------------------------------
    print("\n[*] TEST 1: Valid database query...")
    payload1 = {"question": "How many orders have been placed?"}
    res1 = send_post_request(url, payload1)
    if res1:
        print(f"[+] Status:  {res1.get('status')}")
        print(f"[+] SQL:     {res1.get('sql')}")
        print(f"[+] Result:  {res1.get('result')}")
        print(f"[+] Summary: {res1.get('summary')}")
    else:
        print("[!] Test 1 failed.")

    # ----------------------------------------------------
    # Test 2: Mutation Guardrail Block (DELETE attempt)
    # ----------------------------------------------------
    print("\n[*] TEST 2: Mutation guardrail block...")
    payload2 = {"question": "delete all records in the orderdetails table"}
    res2 = send_post_request(url, payload2)
    if res2:
        print(f"[+] Status:  {res2.get('status')}")
        print(f"[+] Result:  {res2.get('result')}")
        print(f"[+] Summary: {res2.get('summary')}")
        if "only SELECT is allowed" in res2.get('summary', ''):
            print("[+] Status: PASS (Safety validator successfully caught mutation statement)")
    else:
        print("[!] Test 2 failed.")

    # ----------------------------------------------------
    # Test 3: Database Relevance Guardrail Block
    # ----------------------------------------------------
    print("\n[*] TEST 3: Irrelevant question guardrail block...")
    payload3 = {"question": "What is the weather like in New York today?"}
    res3 = send_post_request(url, payload3)
    if res3:
        print(f"[+] Status:  {res3.get('status')}")
        print(f"[+] Summary: {res3.get('summary')}")
        if "predefined" in res3.get('summary', ''):
            print("[+] Status: PASS (Successfully caught irrelevant database question)")
    else:
        print("[!] Test 3 failed.")

    # ----------------------------------------------------
    # Test 4: Dynamic Self-Correction Retry (Ambiguous column names)
    # ----------------------------------------------------
    print("\n[*] TEST 4: Self-correction retry of ambiguous columns...")
    payload4 = {"question": "Total payments per customer"}
    res4 = send_post_request(url, payload4)
    if res4:
        print(f"[+] Status:  {res4.get('status')}")
        print(f"[+] SQL:     {res4.get('sql')}")
        print(f"[+] Result (capped to 5 shown): {res4.get('result')[:5] if isinstance(res4.get('result'), list) else res4.get('result')}")
        print(f"[+] Summary: {res4.get('summary')}")
        if res4.get('status') == 'success':
            print("[+] Status: PASS (Successfully self-corrected and executed!)")
    else:
        print("[!] Test 4 failed.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Wait a few seconds for API service container to fully boot up
    print("[*] Waiting for containerized API service to initialize...")
    time.sleep(3)
    test_api()
