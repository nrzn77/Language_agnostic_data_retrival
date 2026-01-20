import spacy
import re
from langdetect import detect
from deep_translator import GoogleTranslator
from bnlp import BengaliNER

# 1. Setup Models
# Load English model for NER
nlp_en = spacy.load("en_core_web_sm")
# Load Bengali NER model (ensure you have the model file)
bn_ner = BengaliNER()

def module_b_pipeline(raw_query):
    """
    Handles Module B requirements: Detection, Normalization, Translation, and NE Mapping.
    """
    
    clean_query = re.sub(r'\s+', ' ', raw_query.lower().strip())
    
    
    # Identify if query is Bangla or English
    try:
        lang = detect(clean_query)
        lang = 'bn' if 'bn' in lang else 'en'
    except:
        lang = 'en' # Fallback to English
        
   
    # Translate to the target language to facilitate cross-lingual search
    if lang == 'en':
        translated = GoogleTranslator(source='en', target='bn').translate(clean_query)
        source_lang, target_lang = 'en', 'bn'
    else:
        translated = GoogleTranslator(source='bn', target='en').translate(clean_query)
        source_lang, target_lang = 'bn', 'en'
        
    # --- Step 4: Named-Entity Mapping (Recommended) ---
    # Extract entities to prevent mistranslation errors (e.g., 'Chair' vs 'Chairman')
    entities = []
    if lang == 'en':
        doc = nlp_en(clean_query)
        # Extract Geo-political entities, Persons, and Organizations
        entities = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'PERSON', 'ORG']]
    else:
        # Simple extraction for Bangla entities using BNLP
        try:
            bn_entities = bn_ner.tag(clean_query)
            entities = [word for word, tag in bn_entities if tag != 'O']
        except:
            entities = []

    return {
        "query": clean_query,
        "source_lang": source_lang,
        "translated": translated,
        "entities": entities,
        "search_terms": [clean_query, translated] # Use both for higher recall
    }

# Example Test
# query_data = module_b_pipeline("Climate change in Dhaka")
# print(query_data)