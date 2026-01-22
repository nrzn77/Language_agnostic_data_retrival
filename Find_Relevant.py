import json

# Load your data
data = []
for filename in ['prothom_alo.jsonl', 'dhaka_tribune.jsonl']:
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))

print(f"Loaded {len(data)} articles.")

while True:
    keyword = input("\nEnter keyword to find URLs (or 'q' to quit): ").lower()
    if keyword == 'q':
        break
    
    found_count = 0
    print(f"\n--- URLS for '{keyword}' ---")
    for doc in data:
        # Check if keyword is in title or body
        if keyword in doc.get('title', '').lower() or keyword in doc.get('body', '').lower():
            print(f"{doc['url']}")
            found_count += 1
            
    print(f"-----------------------------")
    print(f"Found {found_count} articles. Copy these to your CSV if they are relevant!")