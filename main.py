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
    currencies={}
    try:
        response = requests.get("https://api.exconvert.com/currencies", params={"access_key":api_key})
        if response.status_code == requests.status_codes.codes.ok:
            data = response.json()
            currencies = data.get("currencies", {})
            error = None
        else:
            error = response.text
    except Exception as e:
        error = e
    return templates.TemplateResponse("index.html", {"request": request, "items": currencies.keys() if currencies else [], "error": error })
    
@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, from_currency: str = Form(...), to_currency: str = Form(...), amount: str = Form(...)):
    currencies = {}
    try:    
        response = requests.get("https://api.exconvert.com/currencies", {"access_key":api_key})
        if response.status_code == requests.status_codes.codes.ok:
            data = response.json()
            currencies = data.get("currencies", {})
            error = None
        else:
            error = response.text
        conversion = requests.get("https://api.exconvert.com/convert", {"access_key":api_key, "from":from_currency, "to":to_currency, "amount":amount})
        if conversion.status_code == requests.status_codes.codes.ok:
            data = conversion.json()
            result = data.get("result", {}).get(to_currency, "/")
        else:
            result = ""
            error = conversion.text
    except Exception as e:
        result = ""
        error = e
    return templates.TemplateResponse("index.html", {"request": request, "items": currencies.keys() if currencies else [], "result": round(result,2) if result else "", "from_currency": from_currency, "to_currency": to_currency, "amount": amount, "error": error})

@app.get("/exchange_rates", response_class=HTMLResponse)
async def exchange_rates(request: Request):
    try:
        response = requests.get("https://api.exconvert.com/currencies", params={"access_key":api_key})
        if response.status_code == requests.status_codes.codes.ok:
            data = response.json()
            currencies = data.get("currencies", {})
            error = None
        else:
            currencies = {}
            error = response.text
    except Exception as e:
        currencies = {}
        error = e
    return templates.TemplateResponse("exchange_rates.html", {"request": request, "items": currencies.keys() if currencies else [], "type_of_currency": "physical", "error": error })   

@app.post("/exchange_rates", response_class=HTMLResponse)
async def post_exchange_rates(request: Request, trigger: str=Form(...), type_of_currency: str = Form(...), from_currency: str = Form(None)):
    if trigger == "radio":
        from_currency = None
    if type_of_currency == "physical":
        endpoint = "https://api.exconvert.com/currencies"
    else:
        endpoint = "https://api.exconvert.com/crypto/currencies"
    currencies = {}
    rates = {}
    try:
        response = requests.get(endpoint, params={"access_key":api_key})
        if response.status_code == requests.status_codes.codes.ok:
            data = response.json()
            currencies = data.get("currencies", {})
            error = None
        else:
            error = response.text

        if from_currency:
            if type_of_currency == "physical":
                endpoint = "https://api.exconvert.com/fetchAll"
            else:
                endpoint = "https://api.exconvert.com/crypto/fetchAll"
            result = requests.get(endpoint, params={"access_key":api_key, "from":from_currency})
            if result.status_code == requests.status_codes.codes.ok:
                data = result.json()
                rates = data.get("result", {})
            else:
                rates = {}
                error = result.text
    except Exception as e:
        error = e
    return templates.TemplateResponse("exchange_rates.html", {"request": request, "items": currencies.keys(), "type_of_currency": type_of_currency, "from_currency": from_currency, "rates": rates, "error": error})
