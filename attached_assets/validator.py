# validator.py - Validates core soul-brain connections

def validate_core_link(soul):
    if hasattr(soul, 'core_memory'):
        print("Soul-Brain Link: ✅ Memory check passed.")
    else:
        print("Soul-Brain Link: ❌ Memory missing.")
