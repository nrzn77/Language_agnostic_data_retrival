import json
import os

def save_data(filename, title, body, url, date, language):
    print("Saving " + title)
    data = {
        "title": title,
        "body": body, 
        "url": url, 
        "date": date, 
        "language": language
    }

    os.makedirs("./outputs", exist_ok=True)
    with open("./outputs/" + filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    print("Saved")

def get_completed(filename):
    COMPLETED = []
    try:
        with open("./outputs/" + filename, "r", encoding="utf-8") as f:
            for line in f:
                COMPLETED.append(json.loads(line)["url"])
    except:
        print("Previously completed problems not found")

    return COMPLETED
        
