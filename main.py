import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
import requests, json
from models import AiAskRequest, AIContextItem
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import OpenAIEmbeddings

groq_api_key = os.getenv("GROQ_API_KEY")

app = FastAPI()


SYSTEM_PROMPT = """

You are an AI task assistant embedded inside a productivity application.

Your job is to analyze the user's intent and return a SINGLE structured JSON response.

IMPORTANT RULES:
- You MUST choose exactly ONE response type.
- You MUST return valid JSON only. No markdown. No explanations.
- You MUST strictly follow the schema for the chosen type.
- You MUST be concise, decisive, and actionable.
- You MUST NOT invent tasks that do not exist unless explicitly asked.
- You MUST prioritize unfinished and high-priority tasks.

Allowed response types:
- plan       → planning the day
- subtasks   → breaking tasks into smaller steps
- focus      → selecting the single best task to work on

If the user intent does not clearly match a type, choose the closest one.

You MUST always include follow-up questions.

Rules for followUps:
- followUps MUST contain 3 to 5 questions [Strictly Not more than 6 words] the user can ask next to the LLM.
- followUps MUST be actionable.
- followUps MUST be directly related to the selected response type.
- followUps MUST be phrased only as questions.

You are NOT a chatbot.
You are a decision engine that outputs structured instructions.

"""

DEVELOPER_PROMPT = """
Each response MUST follow this base structure:

{{
  "type": "<one of: plan | subtasks | focus>",
  "title": "<short descriptive title>",
  "items": [],
  "tip": "<string or null>",
  "followUps": []
}}

--------------------------------
TYPE: plan

items format:
[
  {{
    "taskId": number,
    "title": string,
    "meta": string
  }}
]

--------------------------------
TYPE: subtasks

items format:
[
  {{
    "parentTaskId": number,
    "parentTitle": string,
    "subtasks": [
      {{
        "title": string,
        "estimate": string,
        "priority": "High" | "Medium" | "Low"
      }}
    ]
  }}
]

--------------------------------
TYPE: focus

items format:
[
  {{
    "taskId": number,
    "title": string,
    "reason": string
  }}
]

--------------------------------
FOLLOW-UP RULES (MANDATORY)

Each response MUST include 3-5 followUps.

--------------------------------

Example output :

response = {{
        "type": "plan",
        "title": "Your plan for today",
        "items": items,
        "tip": "Focus on one task at a time to stay productive.",
        "followUps": [
            "What should I do first?",
            "Can you reorder my tasks?",
            "What can I finish today?",
            "Break these tasks into smaller steps"
        ]
    }}

"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", DEVELOPER_PROMPT),
    ("user", """

User request:
"{user_prompt}"
     
Context [ Your previous response]:
"{context}"

User tasks:
{tasks}

""")
])


llm = ChatGroq(model="openai/gpt-oss-120b", api_key=groq_api_key)

outputParser = JsonOutputParser()

chain = prompt | llm | outputParser

def build_context_text(context: list[AIContextItem]) -> str:
    if not context:
        return "No prior context."

    lines = []
    for i, c in enumerate(context, start=1):
        lines.append(
            f"{i}. Type: {c.previousAIresponse.type if c.previousAIresponse else 'No type'}\n"
            f"   User asked: {c.prompt}\n"
            f"   YourPreviousResponse: {c.previousAIresponse or 'No previous conversation'}"
        )
    return "\n".join(lines)



@app.post("/assist")
def assist(payload : AiAskRequest):
    
    print(f"Received payload : {payload}")
    tasks = payload.tasks
    prompt = payload.prompt
    context = build_context_text(payload.context)

    if tasks:
        response = chain.invoke({
            "user_prompt" : prompt,
            "context" : context,
            "tasks" : tasks
        })
        print(response)
        return response
    return {"message":"LLM received empty Tasks list"}

if __name__=="__main__":
    
    uvicorn.run(app,host="localhost",port=7000)