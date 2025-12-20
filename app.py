from fastapi import FastAPI  # FastAPI framework for creating the web application
from pydantic import BaseModel  # BaseModel for structured data data models
from typing import List  # List type hint for type annotations
from langchain_community.tools.tavily_search import TavilySearchResults  # TavilySearchResults tool for handling search results from Tavily
import os  # os module for environment variable handling
from langgraph.prebuilt import create_react_agent  # Function to create a ReAct agent
from langchain_groq import ChatGroq  # ChatGroq class for interacting with LLMs
import uvicorn  # Import Uvicorn server for running the FastAPI app


groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

if not groq_api_key or not os.environ["TAVILY_API_KEY"]:
    print("Error: API Keys missing in environment variables!") 

MODEL_NAMES = [
    "llama-3.3-70b-versatile", 
    "mixtral-8x7b-32768"
]

tool_tavily = TavilySearchResults(max_results=2)  


tools = [tool_tavily, ]

app = FastAPI(title='LangGraph AI Agent')

class RequestState(BaseModel):
    system_prompt: str  
    model_name: str  
    messages: List[str]  

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API endpoint to interact with the chatbot using LangGraph and tools.
    Dynamically selects the model specified in the request.
    """
    if request.model_name not in MODEL_NAMES:
        return {"error": "Invalid model name. Please select a valid model."}

    llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)

    agent = create_react_agent(llm, tools=tools)    
    state = {"messages": request.messages}

    result = agent.invoke(state) 

    return result

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)  