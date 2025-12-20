from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import uvicorn
from langgraph.checkpoint.memory import MemorySaver

# API Keys ලබා ගැනීම
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

if not groq_api_key or not os.environ["TAVILY_API_KEY"]:
    print("Error: API Keys missing in environment variables!") 

MODEL_NAMES = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

# Tools සකස් කිරීම
tool_tavily = TavilySearchResults(max_results=2)  
tools = [tool_tavily]

# Memory එක හඳුන්වා දීම
memory = MemorySaver()

app = FastAPI(title='LangGraph AI Agent')

# Request එකට thread_id එකතු කිරීම
class RequestState(BaseModel):
    system_prompt: str  
    model_name: str  
    messages: List[str]
    thread_id: str  # Chat එක හඳුනාගැනීමට ID එක

@app.post("/chat")
def chat_endpoint(request: RequestState):
    if request.model_name not in MODEL_NAMES:
        return {"error": "Invalid model name."}

    llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)

    # Agent එක memory (checkpointer) සමඟ නිර්මාණය කිරීම
    agent = create_react_agent(llm, tools=tools, checkpointer=memory)    
    
    # Thread ID එක config එකට ඇතුළත් කිරීම
    config = {"configurable": {"thread_id": request.thread_id}}

    # අවසන් පණිවිඩය පමණක් ලබා දීම (Memory එක නිසා කලින් ඒවා ස්වයංක්‍රීයව එක් වේ)
    state = {"messages": request.messages}

    result = agent.invoke(state, config=config) 

    return result

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)