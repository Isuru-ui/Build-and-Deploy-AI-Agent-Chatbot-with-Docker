from fastapi import FastAPI  # FastAPI framework for creating the web application
from pydantic import BaseModel  # BaseModel for structured data data models
from typing import List  # List type hint for type annotations
from langchain_community.tools.tavily_search import TavilySearchResults  # Tavily tool
import os  # os module for environment variable handling
from langgraph.prebuilt import create_react_agent  # Function to create a ReAct agent
from langchain_groq import ChatGroq  # ChatGroq class for interacting with LLMs
import uvicorn  # Import Uvicorn server for running the FastAPI app
from langgraph.checkpoint.memory import MemorySaver # Memory saver for conversation persistence

# API Keys ලබා ගැනීම
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

if not groq_api_key or not os.environ["TAVILY_API_KEY"]:
    print("Error: API Keys missing in environment variables!") 

# පාවිච්චි කළ හැකි Models ලැයිස්තුව
MODEL_NAMES = [
    "llama-3.3-70b-versatile", 
    "mixtral-8x7b-32768"
]

# Tools සැකසීම
tool_tavily = TavilySearchResults(max_results=2)  
tools = [tool_tavily]

# Memory Saver එක initialize කිරීම (මෙය endpoint එකෙන් පිටත තිබිය යුතුය)
memory = MemorySaver()

app = FastAPI(title='LangGraph AI Agent')

# Request එකේ ව්‍යුහය (Thread ID එක ඇතුළත් කර ඇත)
class RequestState(BaseModel):
    system_prompt: str  
    model_name: str  
    messages: List[str]  
    thread_id: str  # Conversation එක වෙන් කර හඳුනාගැනීමට ID එකක්

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API endpoint to interact with the chatbot using LangGraph with Memory.
    """
    if request.model_name not in MODEL_NAMES:
        return {"error": "Invalid model name. Please select a valid model."}

    # LLM එක තේරීම
    llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)

    # Agent එක නිර්මාණය කිරීම (Checkpointer එක ලබා දී ඇත)
    agent = create_react_agent(
        llm, 
        tools=tools, 
        checkpointer=memory,
        state_modifier=request.system_prompt # System prompt එක මෙතනින් ලබා දෙයි
    )    
    
    # දැනට එවන පණිවිඩය state එකට ඇතුළත් කිරීම
    state = {"messages": [("user", m) for m in request.messages]}

    # Thread ID එක සහිතව config එක සැකසීම
    config = {"configurable": {"thread_id": request.thread_id}}

    # Agent එක ක්‍රියාත්මක කිරීම (Config එකත් සමඟ)
    result = agent.invoke(state, config=config) 

    # අවසාන පිළිතුර ලබා දීම
    return result["messages"][-1].content

if __name__ == '__main__':
    # Localhost හි port 8000 ඔස්සේ run කිරීම
    uvicorn.run(app, host='0.0.0.0', port=8000)