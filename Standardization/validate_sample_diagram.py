
import sys
import os

# Add lib path
sys.path.append('/storage/emulated/0/dev/lib/py')

try:
    from lib_bejson_validator_diagram import bejson_validator_diagram_validate_file
    
    test_file = "/storage/emulated/0/dev/lib/sample_diagram.104db.bejson"
    print(f"[*] Validating diagram: {test_file}")
    
    if bejson_validator_diagram_validate_file(test_file):
        print("[+] Diagram Validation: SUCCESS")
    else:
        print("[-] Diagram Validation: FAILED")
except Exception as e:
    print(f"[!] ERROR: {e}")
    sys.exit(1)
