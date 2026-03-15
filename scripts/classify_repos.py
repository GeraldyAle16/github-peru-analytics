import os
import sys
import json
import pandas as pd
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.classification.industry_classifier import IndustryClassifier

def main():
    repos_json_path = "data/raw/repos/top_repos_enriched.json"
    output_path = "data/processed/classifications.csv"
    
    if not os.path.exists(repos_json_path):
        logger.error(f"Cannot find {repos_json_path}. Ensure extract_data.py has finished running.")
        return

    logger.info("Loading extracted repositories...")
    with open(repos_json_path, "r", encoding="utf-8") as f:
        repos_data = json.load(f)

    logger.info(f"Loaded {len(repos_data)} repositories total.")
    
    classifications = []
    if os.path.exists(output_path):
        try:
            classifications = pd.read_csv(output_path).to_dict('records')
            logger.info(f"Loaded {len(classifications)} existing classifications. Resuming from here...")
        except BaseException as e:
            logger.warning(f"Could not read existing CSV, starting fresh. {e}")
            pass
            
    processed_ids = {c["repo_id"] for c in classifications}
    repos_to_process = [r for r in repos_data if r["id"] not in processed_ids]
    
    if not repos_to_process:
        logger.info("All repositories have already been classified!")
        return
        
    logger.info(f"{len(repos_to_process)} repositories remaining to classify via GPT-4...")
    classifier = IndustryClassifier()
    
    batch_size = 10
    os.makedirs("data/processed", exist_ok=True)
    
    for i in range(0, len(repos_to_process), batch_size):
        batch = repos_to_process[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} of {(len(repos_to_process) + batch_size - 1)//batch_size}...")
        
        batch_results = classifier.batch_classify(batch, batch_size=batch_size)
        classifications.extend(batch_results)
        
        df = pd.DataFrame(classifications)
        df.to_csv(output_path, index=False)
        logger.info(f"-> Progress saved. ({len(classifications)} / {len(repos_data)} completed)")
        
    logger.info(f"Classification Complete! Saved {len(classifications)} total classifications to {output_path}")

if __name__ == "__main__":
    main()
