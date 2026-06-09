from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List
from typing import TypedDict, List
from app.core.config import settings

# Import tools used by the agent
from app.tools import ALL_TOOLS, get_price, diagnose_pest, get_schemes


class AgentState(TypedDict):
    messages: List[dict]
    user_id: str


# If an OpenAI API key is configured, initialize the real LLM agent.
if settings.OPENAI_API_KEY:
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.2,
        api_key=settings.OPENAI_API_KEY,
    )

    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    async def call_model(state: AgentState):
        response = await llm_with_tools.ainvoke(state["messages"])

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name == "get_price":
                result = await get_price(**tool_args)
            elif tool_name == "diagnose_pest":
                result = await diagnose_pest(**tool_args)
            elif tool_name == "get_schemes":
                result = await get_schemes(**tool_args)
            else:
                result = "I couldn't process that request. Please try again."

            return {"messages": [{"role": "assistant", "content": result}]}

        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    agent = graph.compile(checkpointer=MemorySaver())

    async def get_agent_response(query: str, user_id: str, session_id: str) -> str:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}], "user_id": user_id},
            config={"configurable": {"thread_id": f"{user_id}:{session_id}"}},
        )

        return result["messages"][-1]["content"]

else:
    # Fallback mock responder when OpenAI is not configured. This allows the API
    # to start in development environments without an API key while still
    # returning useful placeholder responses for testing.
    async def get_agent_response(query: str, user_id: str, session_id: str) -> str:
        q = query.lower()
        if "price" in q or "mandi" in q or "msp" in q:
            return "(mock) Current mandi price is not available in offline mode."
        if "pest" in q or "leaves" in q or "disease" in q:
            return "(mock) It looks like a nutrient deficiency — apply balanced NPK and monitor."
        if "scheme" in q or "subsid" in q or "pmkisan" in q:
            return "(mock) Several state and central schemes may apply; provide land details for specifics."
        return "(mock) OpenAI not configured — running in mock mode."


async def get_agent_response_with_key(api_key: str, query: str, user_id: str, session_id: str) -> str:
    """Create an on-the-fly agent using the provided `api_key` and return a response.

    This is used when callers supply their own OpenAI API key so the server
    does not need to be configured with a single global key.
    """
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.2,
        api_key=api_key,
    )

    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    async def call_model(state: AgentState):
        response = await llm_with_tools.ainvoke(state["messages"])

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name == "get_price":
                result = await get_price(**tool_args)
            elif tool_name == "diagnose_pest":
                result = await diagnose_pest(**tool_args)
            elif tool_name == "get_schemes":
                result = await get_schemes(**tool_args)
            else:
                result = "I couldn't process that request. Please try again."

            return {"messages": [{"role": "assistant", "content": result}]}

        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    agent = graph.compile(checkpointer=MemorySaver())

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}], "user_id": user_id},
        config={"configurable": {"thread_id": f"{user_id}:{session_id}"}},
    )

    return result["messages"][-1]["content"]