from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import uvicorn
import traceback
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage

groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

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
    try:
        if not groq_api_key or not os.environ.get("TAVILY_API_KEY"):
            raise ValueError("API Keys are missing!")

        llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)
        
        agent = create_react_agent(llm, tools=tools, checkpointer=memory)
        
        config = {"configurable": {"thread_id": request.thread_id}}

        input_messages = [SystemMessage(content=request.system_prompt)]
        for m in request.messages:
            input_messages.append(HumanMessage(content=m))

        state = {"messages": input_messages}

        result = agent.invoke(state, config=config)
        
        serializable_messages = []
        for msg in result["messages"]:
            role = "assistant" if hasattr(msg, 'type') and msg.type == 'ai' else "user"
            serializable_messages.append({
                "role": role,
                "content": str(msg.content)
            })

        return {"messages": serializable_messages}
        
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)