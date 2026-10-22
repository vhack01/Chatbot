from langchain_community.tools import tool, DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

search_tool = DuckDuckGoSearchRun(region='us-en')


tavily_search = TavilySearch(
    max_result=5,
    search_depth='basic'
)

@tool
def calculator(first_num: float, second_num: float, operation: str):
    """This tool is used to do any mathematical calculation like 
    add, sub, mul, div etc. 
    This tools take 2 argument and based on the operation it returns the answer"""

    try:
        if operation == 'add':
            result = first_num + second_num
        elif operation == 'sub':
            result = first_num - second_num
        elif operation == 'mul':
            result = first_num * second_num
        elif operation == 'div':
            if second_num == 0:
                return {'error': 'Division by zero is not allowed'}
            result = first_num / second_num
        else:
            return {'error': f'Unsupported operation "{operation}"'}

        return {'first_num': first_num, 'second_num': second_num, 'operation': operation, 'result': result}
    except Exception as e:
        return {'error': str(e)}
