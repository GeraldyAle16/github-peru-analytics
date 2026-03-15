import json
import pandas as pd
import os
from loguru import logger

def main():
    users_path = "data/raw/users/users_detailed.json"
    
    if not os.path.exists(users_path):
        logger.error(f"Cannot find {users_path}. The extraction script hasn't saved anything yet.")
        return
        
    with open(users_path, "r", encoding="utf-8") as f:
        users = json.load(f)
        
    logger.info(f"Found {len(users)} users that have been extracted so far.")
    
    df = pd.DataFrame(users)
    
    # Select the exact variables requested in section 6.4 Data to Extract 
    columns_to_keep = [
        "id", "login", "name", "location", "bio", "company", 
        "blog", "email", "followers", "following", "public_repos", 
        "created_at", "updated_at"
    ]
    
    available_cols = [c for c in columns_to_keep if c in df.columns]
    df_filtered = df[available_cols]
    
    out_path = "1000_usuarios_extraidos.csv"
    df_filtered.to_csv(out_path, index=False, encoding="utf-8-sig")
    
    logger.info(f"Successfully saved progress to: {out_path}")

if __name__ == "__main__":
    main()
