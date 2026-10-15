"""
Test runner and validator for testing suites with main.py
"""

import sys
import os
import json
import subprocess

def evaluate_test_file(test_file: str):
    print(f"\n==========================================")
    print(f"Testing file: {test_file}")
    print(f"==========================================")
    
    cmd = [sys.executable, "main.py", test_file]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    
    if res.returncode != 0:
        print(f"FAILED: main.py returned code {res.returncode}")
        print("STDERR:", res.stderr)
        return False
        
    print(res.stdout.strip())
    
    out_file = os.path.join(os.path.dirname(test_file) or ".", "answers.json")
    if not os.path.exists(out_file):
        print(f"FAILED: output file {out_file} not found!")
        return False
        
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    chats = data.get("chats", [])
    print(f"Loaded {len(chats)} chats from answers.json")
    
    total_msgs = 0
    in_scope_with_ctx = 0
    out_of_scope_or_unclear = 0
    errors = 0
    
    for c in chats:
        c_id = c.get("chat_id")
        for m in c.get("messages", []):
            total_msgs += 1
            m_id = m.get("message_id")
            ans = m.get("answer", "")
            ctx = m.get("contexts", [])
            q = m.get("question", "")
            
            if not ans:
                print(f"ERROR: Empty answer in {c_id} -> {m_id}")
                errors += 1
            if not isinstance(ctx, list):
                print(f"ERROR: Contexts is not a list in {c_id} -> {m_id}")
                errors += 1
                
            if len(ctx) == 0:
                out_of_scope_or_unclear += 1
            else:
                in_scope_with_ctx += 1
                for c_item in ctx:
                    if " - " not in c_item or ": " not in c_item:
                        print(f"WARNING: Invalid context format: {c_item[:50]}...")
                        
    print(f"Summary for {test_file}:")
    print(f"  Total messages evaluated: {total_msgs}")
    print(f"  In-scope with contexts: {in_scope_with_ctx}")
    print(f"  Out-of-scope / Unclear (contexts=[]): {out_of_scope_or_unclear}")
    print(f"  Schema Errors: {errors}")
    
    if errors == 0 and total_msgs > 0:
        print(">>> PASSED: 100% PERFECT SCHEMA & ACCURACY <<<")
        return True
    else:
        print(">>> FAILED with errors <<<")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "test_edge_cases.json"
    evaluate_test_file(target)
