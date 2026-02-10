# Task_Pilot_LLM

AI Orchestration Service for Task-Pilot  
Handles AI reasoning, planning, subtasks, and AI memory.

---

## 🧩 Responsibilities

This service is **NOT** the database and **NOT** the UI.

It is responsible for:

• Turning user prompts into structured AI output  
• Understanding tasks + subtasks  
• Planning days  
• Generating subtasks  
• Returning AI-readable JSON  
• Enforcing response schema  
• No persistence (delegated to UI backend + DB)

---

## 🏗 Architecture

UI Backend → LLM Service → Groq / OpenAI  
                     ↳ Receives Tasks + Context  
                     ↳ Returns Structured JSON

---

## 🧠 Supported AI Types

The LLM returns different response formats depending on the user intent.

| Type | Purpose |
|------|--------|
| `plan` | Create daily plan |
| `subtasks` | Break a task into subtasks |
| `focus` | Tell what to work on |

---

## 🧪 Example Request

`POST /assist`

```json
{
  "prompt": "Plan my day",
  "tasks": [
    { "id": 44, "title": "Learn Angular", "priority": "High" }
  ],
  "context": [
    { "type": "plan", "summary": "Yesterday's plan" }
  ]
}
