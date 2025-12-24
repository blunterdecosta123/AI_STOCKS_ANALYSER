from dotenv import load_dotenv
from pydantic import BaseModel # pydantic models for request validation

import uvicorn # server runner for FastAPI
from fastapi import FastAPI # FastAPI web framework for building APIs
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# langchain helps build LLM-powered applications with agents and tools it is a framework
from langchain.agents import create_agent 
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

import yfinance as yf

# Load environment variables from a .env file (if present).
load_dotenv()

# Create FastAPI app instance
app = FastAPI()

# Configure Thesys model wrapper. This uses a custom base_url and model id.
model = ChatOpenAI(
    model='c1/openai/gpt-5/v-20250930',
    base_url='https://api.thesys.dev/v1/embed/'
)

# A simple in-memory checkpointer for agent conversation state/history.
# Useful for resuming conversations or debugging; replace with persistent storage in production.
checkpointer = InMemorySaver()


# -------------------------
# Tools exposed to the agent
# -------------------------
# Each @tool-decorated function becomes a callable tool the agent can invoke.
# These tools use yfinance to fetch market data. They print to stdout when used (handy for logs).

@tool('get_stock_price', description='A function that returns the current stock price based on a ticker symbol.')
def get_stock_price(ticker: str):
    """
    Returns the latest close price for the given ticker.
    Note: yfinance returns price history; we take the last 'Close' value.
    """
    print('get_stock_price tool is being used')
    stock = yf.Ticker(ticker)
    # history()['Close'].iloc[-1] returns the most recent close price
    return stock.history()['Close'].iloc[-1]


@tool('get_historical_stock_price', description='A function that returns the current stock price over time based on a ticker symbol and a start and end date.')
def get_historical_stock_price(ticker: str, start_date: str, end_date: str):
    """
    Returns historical price data between start_date and end_date (inclusive/exclusive per yfinance behavior).
    The returned value is converted to a dictionary for easier serialization.
    """
    print('get_historical_stock_price tool is being used')
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date).to_dict()


@tool('get_balance_sheet', description='A function that returns the balance sheet based on a ticker symbol.')
def get_balance_sheet(ticker: str):
    """
    Returns the balance sheet DataFrame for the given ticker (pandas.DataFrame).
    The agent/tool caller should be prepared to handle a DataFrame or convert/serialize it.
    """
    print('get_balance_sheet tool is being used')
    stock = yf.Ticker(ticker)
    return stock.balance_sheet


@tool('get_stock_news', description='A function that returns news based on a ticker symbol.')
def get_stock_news(ticker: str):
    """
    Returns recent news items for the ticker. yfinance returns a list/dict of news items.
    """
    print('get_stock_news tool is being used')
    stock = yf.Ticker(ticker)
    return stock.news

@tool('get_company_info', description='Return company profile / info for a ticker (summary, sector, industry, website, etc.).')
def get_company_info(ticker: str):
    print('get_company_info tool is being used')
    stock = yf.Ticker(ticker)
    return stock.info  

@tool('get_dividends', description='Return dividend history for a ticker.')
def get_dividends(ticker: str):
    print('get_dividends tool is being used')
    stock = yf.Ticker(ticker)
    return stock.dividends.to_dict()

@tool('get_financials', description='Return financial statements (income statement / financials) for a ticker.')
def get_financials(ticker: str):
    print('get_financials tool is being used')
    stock = yf.Ticker(ticker)
    return stock.financials.to_dict()
# -------------------------
# Create the agent
# -------------------------
# The agent gets the model, the available tools, and a checkpointer to manage state.
agent = create_agent(
    model=model,
    checkpointer=checkpointer,
    tools=[get_stock_price, get_historical_stock_price, get_balance_sheet, get_stock_news, get_company_info, get_dividends, get_financials]
)


# -------------------------
# Request / Prompt models
# -------------------------
# Use pydantic models for request validation and type hints

class PromptObject(BaseModel):
    content: str  # The user's message content (text prompt)
    id: str       # Arbitrary id for the prompt (could be message id)
    role: str     # Role of the sender (e.g., "user", "assistant")


class RequestObject(BaseModel):
    prompt: PromptObject
    threadId: str
    responseId: str


# -------------------------
# API endpoint: /api/chat
# -------------------------
# This endpoint accepts a JSON body matching RequestObject and returns a streaming response.
# The agent is run in "stream" mode and the generator yields tokens as they arrive.
@app.post('/api/chat')
async def chat(request: RequestObject):
    # Config passed to the agent; here we set a configurable thread id for the agent's stream.
    config = {'configurable': {'thread_id': request.threadId}}

    # Generator function that will be used by StreamingResponse
    # It yields token.content strings produced by agent.stream(...)
    def generate():
        # Build messages passed to the agent:
        # - SystemMessage sets assistant behavior and available capabilities.
        # - HumanMessage is the prompt content supplied with the request.
        for token, _ in agent.stream(
            {'messages': [
                SystemMessage('You are a stock analysis assistant. You have the ability to get real-time stock prices, historical stock prices (given a date range), news,balance sheet data ,company information,dividend history, and financial statements for publicly traded companies using the provided tools. Use these tools to provide accurate and up-to-date information about stocks when responding to user queries.'),
                HumanMessage(request.prompt.content)
            ]},
            stream_mode='messages',
            config=config
        ):
            # Yield the raw token content. The client should be prepared to assemble tokens
            # into a complete message; tokens may be partial fragments of the final text.
            yield token.content

    # Return a StreamingResponse with media_type 'text/event-stream'
    return StreamingResponse(generate(), media_type='text/event-stream',
                             headers={
                                 'Cache-Control': 'no-cache, no-transform', # Prevent caching of streaming responses on some proxies
                                 'Connection': 'keep-alive', # Keep connection alive for streaming
                             })


# -------------------------
# Run the app
# -------------------------
# When executed directly, run uvicorn on 0.0.0.0:8888
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)


