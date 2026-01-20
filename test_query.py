# Import the pipeline function from Querying.py
from Querying import module_b_pipeline

# Ensure UTF-8 output for Windows console
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# List of test queries including English, Bangla, and Mixed (Code-switching)
test_queries = [
    "Climate change in Bangladesh",           # Standard English
    "বাংলাদেশের জলবায়ু পরিবর্তন",              # Standard Bangla
    "Dhaka education system",                 # English with NE (Dhaka)
    "শেখ হাসিনার ভাষণ",                        # Bangla with NE
    "Latest news on cricket in বাংলাদেশ"      # Code-switching (English + Bangla)
]

print(f"{'Original':<35} | {'SourceLang':<10} | {'Translated':<35} | {'Entities'}")
print("-" * 110)

for q in test_queries:
    result = module_b_pipeline(q)
    entities_str = ", ".join(result['entities'])
    print(f"{result['query']:<35} | {result['source_lang']:<10} | {result['translated']:<35} | {entities_str}")