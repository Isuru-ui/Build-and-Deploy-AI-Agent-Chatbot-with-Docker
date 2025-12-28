from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import uvicorn
from langgraph.checkpoint.memory import MemorySaver


groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

<<<<<<< HEAD
if not groq_api_key or not os.environ["TAVILY_API_KEY"]:
    print("Error: API Keys missing in environment variables!") 
=======
# Predefined list of supported model names
MODEL_NAMES = [
    "llama-3.3-70b-versatile", 
    "mixtral-8x7b-32768"
]
>>>>>>> 5e04c61b829d5ae73f66c472ffe14680f4b2d3fb

MODEL_NAMES = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

tool_tavily = TavilySearchResults(max_results=2)  
tools = [tool_tavily]

memory = MemorySaver()

app = FastAPI(title='LangGraph AI Agent')

class RequestState(BaseModel):
    system_prompt: str  
    model_name: str  
    messages: List[str]
    thread_id: str  

@app.post("/chat")
def chat_endpoint(request: RequestState):
    if request.model_name not in MODEL_NAMES:
        return {"error": "Invalid model name."}

    llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)

    agent = create_react_agent(llm, tools=tools, checkpointer=memory)    
    
    config = {"configurable": {"thread_id": request.thread_id}}

    state = {"messages": request.messages}

    result = agent.invoke(state, config=config) 

    return result

if __name__ == '__main__':
<<<<<<< HEAD
    uvicorn.run(app, host='0.0.0.0', port=8000)
=======
    uvicorn.run(app, host='127.0.0.1', port=8000)  # Start the app on localhost with port 8000
>>>>>>> 5e04c61b829d5ae73f66c472ffe14680f4b2d3fb
