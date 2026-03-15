import os
import sys
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.classification_agent import ClassificationAgent

def main():
    logger.info("================================================================")
    logger.info("   DEMO: AUTONOMOUS CLASSIFICATION AGENT (Requirement 10)       ")
    logger.info("================================================================")
    
    agent = ClassificationAgent()
    
    # Simple list of repos for the agent to 'think' about
    test_repos = [
        {
            "name": "react-native-peru", 
            "description": "Comunidad de Facebook React Native en Perú", 
            "owner_login": "react-native-peru"
        },
        {
            "name": "yape-fake", 
            "description": "Just a fun project", 
            "owner_login": "eduardo"
        }
    ]
    
    for repo in test_repos:
        logger.warning(f"TASK: Classify the repository '{repo['name']}'")
        result = agent.run(repo)
        
        print("\n" + "="*50)
        print(f"IDENTIFIED INDUSTRY : {result['industry_name']} ({result['industry_code']})")
        print(f"CONFIDENCE          : {result['confidence'].upper()}")
        print(f"AGENT REASONING     : {result['reasoning']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    main()
