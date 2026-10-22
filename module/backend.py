from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import add_messages, StateGraph, START, END 
from langchain_core.messages import BaseMessage, HumanMessage
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from tools import search_tool, calculator, tavily_search
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

model = ChatOpenAI(model_name="gpt-5.5")


conn = sqlite3.connect(database='chat_history.db', check_same_thread = False)
checkpointer = SqliteSaver(conn = conn)


# tools
tools = [calculator, tavily_search]
model_with_tools = model.bind_tools(tools)
tool_node = ToolNode(tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat(state: ChatState):
    messages = state['messages']
    response = model_with_tools.invoke(messages)
    return {'messages': [response]}



graph = StateGraph(ChatState)

graph.add_node('chat', chat)
graph.add_node('tools', tool_node)

graph.add_edge(START, 'chat')
graph.add_conditional_edges('chat', tools_condition)
graph.add_edge('tools', 'chat')


workflow = graph.compile(checkpointer = checkpointer)

def invoke(messages: str, config):
    response = workflow.invoke(messages, config)
    return response

def stream(messages: str, config):
    stream_generator = workflow.stream(
        messages,
        config,
        stream_mode="messages"
    )
    return stream_generator
    
# test
# response = invoke({'messages': [HumanMessage(content='Hi! My name is atul kumar')]}, {'configurable': {"thread_id" : 'thread-2'}})
# print (response)


def retrive_all_threads():
    threads = set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(threads)

def retrive_thread_message(config):
    return workflow.get_state(config)


def retrive_all_conversations():
    threads = retrive_all_threads()
    conversation = {}
    for thread_id in threads:
        snapshot = workflow.get_state({'configurable': {'thread_id': thread_id}})
        conversation[thread_id] = []
        for message in snapshot.values['messages']:
            if message.type == 'human':
                conversation[thread_id].append({'role' : 'user', 'content': message.content}) 
            else:
                conversation[thread_id].append({'role' : 'assistant', 'content': message.content})
    
    return conversation


# print(retrive_all_conversations())