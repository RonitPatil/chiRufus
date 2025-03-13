from Rufus import RufusClient
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('OPENAI_API_KEY') 

client = RufusClient(api_key=key)

instructions = "Tell me about a few features"
print("Scraping website...")

document = client.scrape("https://www.withchima.com/", instructions)

print(document)
