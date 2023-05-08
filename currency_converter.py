import json
import requests
from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from bs4 import BeautifulSoup
from datetime import datetime


# redoc_url=None, openapi_url=None
app = FastAPI(title="Currency Converter using Mid-Market rates")


api_authKeys = [
    "akljnv13bvi2vfo0b0bw",
    "Dkljnv13bvi2vfo0b0bw"
]


API_KEY_NAME = "api_key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def auth_via_api_key(api_key_header: str = Security(api_key_header)):

    if api_key_header not in api_authKeys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authenticated"
        )


class ConvertCurrency(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


@app.post("/convert", dependencies=[Depends(auth_via_api_key)])
async def convert(apibody: ConvertCurrency):
    time_of_conversion = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    input_from_currency = apibody.from_currency
    input_to_currency = apibody.to_currency
    input_amount = float(apibody.amount)

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4342.0 Safari/537.36",
    }

    url = 'https://wise.com/gb/currency-converter/' + input_from_currency.lower() + \
        '-to-' + input_to_currency.lower() + '-rate?amount=1000'
    req = requests.get(url, headers)
    dom_nodes = BeautifulSoup(req.content, 'html.parser')

    dom_nodes = dom_nodes.find(['body'])
    conversion_rate = 0
    conversion_rate_all = dom_nodes.select(
        '.cc__source-to-target .text-success:last-child')

    if (len(conversion_rate_all) > 0):
        conversion_rate = conversion_rate_all[0].getText().strip()

    conversion_rate = float(conversion_rate)

    if (conversion_rate != 0):
        converted_amount = input_amount * conversion_rate

        to_be_return = {}
        to_be_return["converted_amount"] = round(converted_amount, 3)
        to_be_return["rate"] = round(conversion_rate, 3)

        to_be_return["metadata"] = {}
        to_be_return["metadata"]["time_of_conversion"] = time_of_conversion
        to_be_return["metadata"]["from_currency"] = input_from_currency
        to_be_return["metadata"]["to_currency"] = input_to_currency

        history_json_object = json.dumps(to_be_return)

        history_logsf = open("history_logs", "a")
        history_logsf.write(history_json_object + "\n")
        history_logsf.close()

        return to_be_return
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong! Please make sure you've input correct currency codes. see /currencies endpoint for more details."
        )


@app.get("/currencies", dependencies=[Depends(auth_via_api_key)])
async def currencies():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4342.0 Safari/537.36",
    }

    url = 'https://wise.com/gb/currency-converter/currencies'
    req = requests.get(url, headers)
    dom_nodes = BeautifulSoup(req.content, 'html.parser')

    dom_nodes = dom_nodes.find(['body'])
    to_be_return_currencies = {}

    currencies_all = dom_nodes.select('#__NEXT_DATA__')
    if (len(currencies_all) > 0):
        currencies_all_JSONstr = currencies_all[0].getText().strip()
        try:
            NEXT_DATA = json.loads(currencies_all_JSONstr)
            all_currencies_json = NEXT_DATA['props']['pageProps']['model']['currencies']
            all_messages_json = NEXT_DATA['props']['pageProps']['messages']

            for currency_letter in all_currencies_json:
                for currency in all_currencies_json[currency_letter]:
                    read_msg_key = 'currency.' + currency['code']
                    name_of_currency = all_messages_json[read_msg_key]
                    to_be_return_currencies[name_of_currency] = currency['code']
        except Exception as ex:
            print("error", ex)

        if (to_be_return_currencies != {}):

            # currenciesjson_object = json.dumps(
            #     to_be_return_currencies, indent=4)
            # with open("currencies.json", "w") as outfile:
            #     outfile.write(currenciesjson_object)

            return to_be_return_currencies
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Something went wrong!"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong!"
        )


@ app.get("/history", dependencies=[Depends(auth_via_api_key)])
async def history():

    history_logs = ''
    try:
        fhistory_log = open("history_logs", "r")
        history_logs = fhistory_log.readlines()
    except FileNotFoundError as ex:
        print("FileNotFoundError", ex)
        fhistory_logs = open("history_logs", "w")
        fhistory_logs.write("")
        fhistory_logs.close()

    if (len(history_logs) > 0):
        to_be_return_str = ",".join(reversed(history_logs))
        to_be_return_str = "[" + to_be_return_str + "]"

        to_be_return_history = json.loads(to_be_return_str)

        if (to_be_return_history != []):
            return to_be_return_history
        else:
            return to_be_return_history
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found!"
        )
'''
python3 -m uvicorn --host "172.31.82.199" currency_converter:app
python3 -m uvicorn currency_converter:app --host 172.31.82.199 --port 8080
python3 -m gunicorn -k uvicorn.workers.UvicornWorker currency_converter:app --bind=172.31.82.199:8000 --daemon
'''
