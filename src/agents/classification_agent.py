import os
import json
import sys
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.extraction.github_client import GitHubClient
from src.extraction.repo_extractor import RepoExtractor

load_dotenv()

class ClassificationAgent:
    """
    Option B: Classification Agent (Requirement 10)
    An autonomous agent that reads repository info, decides if it needs more 
    context (README, languages, commits), and classifies into industries.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        self.client = OpenAI(api_key=self.api_key)
        
        # Tools initialized for internal use
        self.github_client = GitHubClient()
        self.repo_extractor = RepoExtractor(self.github_client)
        
        self.industries = {
            "A": "Agriculture, forestry and fishing",
            "B": "Mining and quarrying",
            "C": "Manufacturing",
            "D": "Electricity, gas, steam supply",
            "E": "Water supply; sewerage",
            "F": "Construction",
            "G": "Wholesale and retail trade",
            "H": "Transportation and storage",
            "I": "Accommodation and food services",
            "J": "Information and communication (Generic Tech/Software)",
            "K": "Financial and insurance activities",
            "L": "Real estate activities",
            "M": "Professional, scientific activities",
            "N": "Administrative and support activities",
            "O": "Public administration and defense",
            "P": "Education",
            "Q": "Human health and social work",
            "R": "Arts, entertainment and recreation",
            "S": "Other service activities",
            "T": "Activities of households",
            "U": "Extraterritorial organizations"
        }

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_readme",
                    "description": "Fetch the README content of a repository for more context.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_languages",
                    "description": "Get the programming languages used in a repository.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recent_commits",
                    "description": "Get recent commit messages to understand development activity.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "classify_industry",
                    "description": "FINAL STEP: Classify the repository into an industry category.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_name": {"type": "string"},
                            "industry_code": {"type": "string", "description": "The code (A-U) from the industries list."},
                            "industry_name": {"type": "string"},
                            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                            "reasoning": {"type": "string", "description": "Explain WHY this industry fits based on the info found."}
                        },
                        "required": ["repo_name", "industry_code", "industry_name", "confidence", "reasoning"]
                    }
                }
            }
        ]

    def _get_commits(self, owner, repo):
        try:
            commits = self.github_client.make_request(f"repos/{owner}/{repo}/commits?per_page=5")
            if not commits: return "No commits found."
            return [c.get('commit', {}).get('message', '') for c in commits]
        except Exception as e:
            return f"Error fetching commits: {str(e)}"

    def run(self, repository: dict) -> dict:
        repo_name = repository.get('name', 'Unknown')
        owner = repository.get('owner_login', '')
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an autonomous AI Agent classifying repos into Peruvian industries.
Goal: Use tools if the basic Name/Description is not enough to be 100% sure of the industry.

INDUSTRY LIST (CIIU):
{json.dumps(self.industries, indent=2)}

INSTRUCTIONS:
1. Start by thinking if the Name and Description are enough.
2. If uncertain, call 'get_readme', 'get_languages', or 'get_recent_commits'.
3. Finally, use 'classify_industry' to provide the result.
"""
            },
            {
                "role": "user",
                "content": f"Please analyze and classify this repository: {repo_name}. Description: {repository.get('description', 'None')}. Owner: {owner}"
            }
        ]

        # Autonomous loop (Max 5 steps to fulfill requirement while keeping costs sane)
        for step in range(5):
            logger.info(f"Agent Loop Step {step+1} for {repo_name}...")
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0
            )

            message = response.choices[0].message
            messages.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"-> Agent Decided Action: {fn_name}")
                    
                    result_content = ""
                    if fn_name == "get_readme":
                        result_content = self.repo_extractor.get_repo_readme(args.get("owner", owner), args.get("repo", repo_name))
                        result_content = result_content[:1500] if result_content else "No README."
                    elif fn_name == "get_languages":
                        result_content = str(self.repo_extractor.get_repo_languages(args.get("owner", owner), args.get("repo", repo_name)))
                    elif fn_name == "get_recent_commits":
                        result_content = str(self._get_commits(args.get("owner", owner), args.get("repo", repo_name)))
                    elif fn_name == "classify_industry":
                        logger.success(f"-> Agent Final Decision: {args['industry_name']} ({args['industry_code']})")
                        return args

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_content or "No result available from tool."
                    })
            else:
                # Fallback if it doesn't use a tool but replies
                break
                
        return {"industry_code": "J", "industry_name": "Information and communication", "confidence": "low", "reasoning": "Fallback reached limit"}

if __name__ == "__main__":
    agent = ClassificationAgent()
    print(agent.run({"name": "django-peru", "description": "Comunidad Django", "owner_login": "django-peru"}))
