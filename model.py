import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient, MCPAgent
from PyPDF2 import PdfReader

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
        },
      }
    }
    self.client = MCPClient.from_dict(self.config)
    self.llm = ChatOpenAI(model="gpt-4o")
    self.weather_agent = MCPAgent(llm=self.llm, client=self.client, max_steps=30)

  async def query(self, company: str):
    # 1) Ask the weather service
    prompt =       f"""You are a competent Analyst that scoutes for startup companies. I need you the evaluate the startup company {company}.I need you to give a final verdict with a detailed report on them and how you would value them as a company.Start what should be said to the user with FINAL_RESULT. You may check the online sources.I need especially the following information: 1) What is the company doing? 2) How are they doing it? 3) How are they different from their competitors? 4) What is their business model? 5) What is their target market? 6) What is their current valuation? 7) What are their future plans? 8) What are the risks associated with this company? 9) What is your final verdict on this company? Give me also the KPI's of their: growth rate
product stage
revenue growth
funding stage
amount. You need to dig deep. . You can also check their website. You need to be very detailed and give me a final verdict. I need this in a structured format. You can use markdown for that. I need this in a structured format. You can use markdown for that."""
    #prompt = "Look up on the web who the founder of ACE Alternatives is. Look it up also in news articles."
    result = await self.weather_agent.run(
      prompt,
      max_steps=10,
    )
    #parse everything after FINAL_RESULT
    print(result)
    result = result.split("FINAL_RESULT:")[-1].strip()

    return result
  
  def read_and_parse_pdf(file_path: str) -> str:
    """
    Reads a PDF file and extracts its text content.

    Args:
      file_path (str): The path to the PDF file.

    Returns:
      str: The extracted text content of the PDF.
    """
    try:
      reader = PdfReader(file_path)
      text = ""
      for page in reader.pages:
        text += page.extract_text()
      return text.strip()
    except Exception as e:
      print(f"Error reading PDF file: {e}")
      return ""

async def main():
  service = QueryService()
  company = "lanch"  # Replace with actual company if needed
  await service.query(company)

if __name__ == "__main__":
  asyncio.run(main())
