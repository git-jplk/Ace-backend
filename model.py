import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPClient, MCPAgent

class QueryService:
  def __init__(self):
    load_dotenv()
    self.config = {
      "mcpServers": {
        "playwright": {
          "command": "npx",
          "args": ["@playwright/mcp@latest"],
          "env": {
            "DISPLAY": ":1"
          }
        }
      }
    }
    self.client = MCPClient.from_dict(self.config)
    self.llm = ChatGroq(
      model="meta-llama/llama-4-maverick-17b-128e-instruct",
      api_key=os.getenv("GROQ_API_KEY")
    )
    self.weather_agent = MCPAgent(llm=self.llm, client=self.client, max_steps=30)

  async def query(self, company: str):
    # 1) Ask the weather service
    result = await self.weather_agent.run(
      f"You are a competent Analyst that scoutes for startup companies. I need you the evaluate the startup company {company}.I need you to give a final verdict with a detailed report on them and how you would value them as a company.Start what should be said to the user with FINAL_RESULT. You may check the online sources.",
      max_steps=50,
    )
    #parse everything after FINAL_RESULT
    result = result.split("FINAL_RESULT:")[-1].strip()

    return result

async def main():
  service = QueryService()
  company = "Example Company"  # Replace with actual company if needed
  await service.query(company)

if __name__ == "__main__":
  asyncio.run(main())
