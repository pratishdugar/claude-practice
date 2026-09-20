import anthropic
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

client = anthropic.Anthropic()


def coordinator(topic:str) -> str:
    system_prompt = f"""You are a research coordinator.
      1. Your task is to break down the research topic into a comprehensive subtopics
        2. DElegate research to specialist subagents
        3. Evaluate coverage and identify gaps
         4. Refine unit optic is fully covered

         Always ensure braod coverage - never miss major categories
          """

    response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": f"Research topic: {topic} Please research it comprehensively"}],
                system=system_prompt,
                max_tokens=1024,
            )

    return response.content[0].text