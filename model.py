import asyncio
import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient, MCPAgent

from enum import Enum

class ToolAccess(Enum):
    NONE = 0
    ALL = 1
    WEB_ONLY = 2
    NEWS_ONLY = 3


class QueryService:
  def __init__(self):
    load_dotenv()
    self.change_tool_access(ToolAccess.ALL)
    self.json = {}
    
  
  def change_tool_access(self, tool_access: ToolAccess):
    """
    Change the tool access level for the agent.

    Args:
        tool_access (ToolAccess): The new tool access level.
    """
    if tool_access == ToolAccess.NONE:
      self.config =  {
      "mcpServers": {}}
    elif tool_access == ToolAccess.ALL:
      self.config = {
      "mcpServers": {
        "playwright": {
          "command": "npx",
          "args": ["@playwright/mcp@latest"],
          "env": {
            "DISPLAY": ":1"
          }
        },
      }
    }
    elif tool_access == ToolAccess.WEB_ONLY:
      self.config = {
      "mcpServers": {
        "playwright": {
          "command": "npx",
          "args": ["@playwright/mcp@latest"],
          "env": {
            "DISPLAY": ":1"
          }
        },
      }
    }
    else:
      raise ValueError("Invalid tool access level")
    self.client = MCPClient.from_dict(self.config)
    self.llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7)
    self.agent = MCPAgent(llm=self.llm, client=self.client, max_steps=20)
    

  async def query(self, company: str, prompt:str, additional_info = None) -> str:
    # 1) Ask the weather service
    if(additional_info is None):
      additional_info = """
          "Any time you finish your search, you MUST output a single JSON object "
          "and nothing else.  "
          "Your JSON MUST match the schema:\n"
          "{
    "founder_name": "",
    "founder_experience": "",
    "founder_press_mentions": "",
    "startup_name": "",
    "pitch": "",
    "business_model": "",
    "market_size": "",
    "competition": "",
    "innovation_score": ""
  } if you dont have the information, write "NONE" EXAMPLE:

  {
    "founder_name": "John Doe",
    "founder_experience": "5 years in tech startups",
    "founder_press_mentions": 10,
    "startup_name": "TechNova",
    "pitch": "TechNova is revolutionizing the way AI is applied in healthcare.",
    "business_model": "SaaS",
    "market_size": "global healthcare",
    "competition": "XYZ Corp",
    "innovation_score": 9
  }
      )"""
    #prompt = "Look up on the web who the founder of ACE Alternatives is. Look it up also in news articles."
    result = await self.agent.run(
      prompt+additional_info,
      max_steps=10,
    )
    self.json = self.parse_json(result)
    return result
  
  async def query_raw(self, company: str, prompt:str, additional_info = None) -> str:
    # 1) Ask the weather service
    if(additional_info is None):
      additional_info = """
          "Any time you finish your search, you MUST output a single JSON object "
          "and nothing else.  "
          "Your JSON MUST match the schema:\n"
          "{
    "founder_name": "",
    "founder_experience": "",
    "founder_press_mentions": "",
    "startup_name": "",
    "pitch": "",
    "business_model": "",
    "market_size": "",
    "competition": "",
    "innovation_score": ""
  } if you dont have the information, write "NONE" EXAMPLE:

  {
    "founder_name": "John Doe",
    "founder_experience": "5 years in tech startups",
    "founder_press_mentions": 10,
    "startup_name": "TechNova",
    "pitch": "TechNova is revolutionizing the way AI is applied in healthcare.",
    "business_model": "SaaS",
    "market_size": "global healthcare",
    "competition": "XYZ Corp",
    "innovation_score": 9
  }
      )"""
    #prompt = "Look up on the web who the founder of ACE Alternatives is. Look it up also in news articles."
    result = await self.llm.invoke(
      prompt+additional_info)
    self.json = self.parse_json(result)
    return result
  
  def parse_json(self, text: str) -> dict:
    """
    Parses a JSON string and returns a dictionary.

    Args:
      text (str): The JSON string to parse.

    Returns:
      dict: The parsed JSON as a dictionary.
    """
    try:
      return json.loads(text)
    except json.JSONDecodeError as e:
      print(f"Error parsing JSON: {e}")
      return {}

async def main():
  service = QueryService()
  company = "lanch"  # Replace with actual company if needed
  prompt =       f"""You are a competent Analyst that scoutes for startup companies. I need you the evaluate the startup company {company}.I need you to give a final verdict with a detailed report on them and how you would value them as a company.Start what should be said to the user with FINAL_RESULT. You may check the online sources.I need especially the following information: 1) What is the company doing? 2) How are they doing it? 3) How are they different from their competitors? 4) What is their business model? 5) What is their target market? 6) What is their current valuation? 7) What are their future plans? 8) What are the risks associated with this company? 9) What is your final verdict on this company? Give me also the KPI's of their: growth rate
product stage
revenue growth
funding stage
amount. You need to dig deep. You can also check any website you want. You need to be very detailed and give me a final verdict."""
  service.change_tool_access(ToolAccess.ALL)
  await service.query(company,prompt)
  print(service.json)


if __name__ == "__main__":
  asyncio.run(main())
