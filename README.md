# Multilingual News Search Engine

This project is a multilingual (English & Bangla) news search engine that supports cross-lingual and code-switched queries. It uses BM25, semantic embeddings, and fuzzy matching for robust retrieval.

## Project Structure
- `prothom_alo.jsonl` — Bangla news articles (JSONL format)
- `dhaka_tribune.jsonl` — English news articles (JSONL format)
- `Document_Indexing.py` — Builds the search index (BM25, embeddings, metadata)
- `Querying.py` — Handles query normalization, language detection, translation, and entity extraction
- `hybrid_retrival_test.py` — Interactive script to test the hybrid retrieval pipeline
- `search_index/` — Folder where all indices and models are saved
- `Installation_commands.txt` — All required installation commands

## Getting Started

### 1. Prepare Data
Place your news data in JSONL format:
- Each line should be a JSON object with at least `title`, `body`, `url`, and `language` fields.
- Example files: `prothom_alo.jsonl` (Bangla), `dhaka_tribune.jsonl` (English)

### 2. Install Dependencies
Run the following commands (see `Installation_commands.txt` for details):

```sh
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Build the Index
Run the indexing script to process your articles and build the search index:

```sh
python Document_Indexing.py
```
This will create the `search_index/` folder with all necessary files.

### 4. Querying
You can use `Querying.py` to test query normalization, language detection, translation, and entity extraction. Example usage is provided in the script.

### 5. Hybrid Retrieval Test
Run the interactive test script to search for news articles using the hybrid retrieval pipeline:

```sh
python hybrid_retrival_test.py
```
This will print ranked search results for sample queries in English, Bangla, and code-switched forms.

## Notes
- Make sure your JSONL files are properly formatted and contain both English and Bangla articles for best results.
- The retrieval system ensures a balanced candidate pool from both languages.
- All installation commands are in `Installation_commands.txt` for convenience.

## License
This project is for academic and research purposes.

## Appendix
The code to scrape articles is inside [ARTICLE_SCRAPER](ARTICLE_SCRAPER).