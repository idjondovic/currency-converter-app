from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests
import httpx

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("API_KEY")
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    response = requests.get("https://api.exconvert.com/currencies", params={"access_key":api_key})
    if response.status_code == requests.status_codes.codes.ok:
        data = response.json()
        currencies = data.get("currencies", {})
    else:
        currencies = {}
    return templates.TemplateResponse("index.html", {"request": request, "items": currencies.keys()})
    
@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, from_currency: str = Form(...), to_currency: str = Form(...), amount: str = Form(...)):
    response = requests.get("https://api.exconvert.com/currencies", {"access_key":api_key})
    if response.status_code == requests.status_codes.codes.ok:
        data = response.json()
        currencies = data.get("currencies", {})
    else:
        currencies = {}

    conversion = requests.get("https://api.exconvert.com/convert", {"access_key":api_key, "from":from_currency, "to":to_currency, "amount":amount})
    if conversion.status_code == requests.status_codes.codes.ok:
        data = conversion.json()
        result = data.get("result", {}).get(to_currency, "/")
    else:
        result = "/"
    return templates.TemplateResponse("index.html", {"request": request, "items": currencies.keys(), "result": result, "from_currency": from_currency, "to_currency": to_currency, "amount": amount})

@app.get("/exchange_rates", response_class=HTMLResponse)
async def exchange_rates(request: Request):
    response = requests.get("https://api.exconvert.com/currencies", params={"access_key":api_key})
    if response.status_code == requests.status_codes.codes.ok:
        data = response.json()
        currencies = data.get("currencies", {})
    else:
        currencies = {}
    return templates.TemplateResponse("exchange_rates.html", {"request": request, "items": currencies.keys()})

@app.post("/exchange_rates", response_class=HTMLResponse)
async def post_exchange_rates(request: Request, from_currency: str = Form(...)):
    response = requests.get("https://api.exconvert.com/currencies", params={"access_key":api_key})
    if response.status_code == requests.status_codes.codes.ok:
        data = response.json()
        currencies = data.get("currencies", {})
    else:
        currencies = {}

    result = requests.get("https://api.exconvert.com/fetchAll", params={"access_key":api_key, "from":from_currency})
    if result.status_code == requests.status_codes.codes.ok:
        data = result.json()
        rates = data.get("result", {})
    else:
        rates = {}
    return templates.TemplateResponse("exchange_rates.html", {"request": request, "items":currencies.keys(), "from_currency": from_currency, "rates": rates})