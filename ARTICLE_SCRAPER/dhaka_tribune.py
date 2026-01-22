from bs4 import BeautifulSoup
import requests
import json
import os
from time import sleep 

from DATASAVER import save_data, get_completed

"""schema:

title , body , url , date , language (required)
tokens (count), word_embeddings (optional but recommended)
named_entities (optional)

"""

output_path = "dhaka_tribune.jsonl"
input_path = "./urls/dhaka_tribune.txt"


def scrape_article_data(base_url):
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("h1").text
        date = soup.find("span", class_="modified_time").get("content")

        body = soup.find("div", class_="detail_inner").text
        

        save_data(output_path, title, body, base_url, date, "en")        

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {base_url}: {e}")


if __name__ == "__main__":

    COMPLETED = get_completed(output_path)

    print(len(COMPLETED), " problems completed")

    with open(input_path, "r", encoding="utf-8") as f:
        COUNT = 0
        for line in f:
            print(COUNT)
            COUNT += 1
            url = line.strip()
            if url:
                if url not in COMPLETED:
                    print("Start scraping " + url)
                    scrape_article_data(url)
                    print("Start sleep")
                    sleep(1)
                    print("End sleep")
            else:
                break
