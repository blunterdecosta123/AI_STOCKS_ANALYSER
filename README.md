# Stock Assistant — FastAPI + LangChain + yfinance + React (Vite)

A demo project that runs a LangChain agent (backed by a `c1/openai/gpt-5` model via Thesys)
and exposes it over a streaming FastAPI endpoint. The agent can call a set of `yfinance`-based
tools to fetch live and historical market data. A React (Vite) frontend mounts the
`@thesysai/genui-sdk` `C1Chat` UI and talks to the FastAPI backend through a dev proxy.

---

## Project overview

- **Backend**: FastAPI app running an LLM agent created with LangChain. The agent has several `@tool` functions that fetch data from Yahoo Finance via `yfinance`. The backend streams model responses using `StreamingResponse` (`text/event-stream`).
- **Frontend**: React app (Vite) using `@thesysai/genui-sdk`'s `C1Chat` component. Dev server proxies `/api` to the backend to avoid CORS during development.

Tools exposed to the agent (yfinance helpers)

The backend includes a variety of yfinance-based tools :

- get_stock_price<br>
- get_historical_stock_price<br>
- get_balance_sheet<br>
- get_stock_news<br>
- get_company_info<br>
- get_dividends<br>
- get_financials<br>

---

## Setup 

From the `backend/` folder:

1. (Optional) Create & activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate 
```  

2. Install dependencies. You can use the uv helper (if installed) or pip directly:

```bash
pip3 install uv
uv init
uv add pydantic fastapi "langchain[openai]" yfinance python-dotenv uvicorn
```
or with pip

```bash
pip3 install pydantic fastapi "langchain[openai]" yfinance python-dotenv uvicorn
```

3. Create .env to store the Thesys Api key:

```bash
THESYS_API_KEY='YOUR_API_KEY'
```

4. Run the backend:

```bash
# using uv helper:
uv run main.py

# or with uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

From the `frontend/` folder:

1. Create the app :

```bash
npm create vite@latest . -- --template react-ts
```

2. Install dependencies:

```bash
npm install @thesysai/genui-sdk @crayonai/react-ui
```

3. Start the dev server:

```bash
npm run dev
```

Open http://localhost:3000 and interact with the chat UI.

---

## Screenshots

![alt text](<Screenshot 2025-12-24 at 2.23.27 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.23.44 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.23.51 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.23.58 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.24.04 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.24.12 PM.png>)
![alt text](<Screenshot 2025-12-24 at 2.24.28 PM.png>)


