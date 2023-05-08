
# currency-converter


Currency Converter using Mid-Market rates

## Live Demo / Docs

You can test this API here,
http://3.88.62.105:8000/docs


## Installation

Install project with pip

```bash
  pip install -r requirements.txt
```
    

## API Reference

#### **For authentication:** use below request Header 

| Header name | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required** |


#### To covert currency

```http
  POST /convert
```
```json
JSON body
{
    "amount":"float",
    "from_currency":"CURRENCY_CODE",
    "to_currency":"CURRENCY_CODE",
}
```


#### Get All Currencies list
currency_name<>currency_code mapping

```http
  GET /currencies
```

#### Get All conversions logs / list
History of all conversions by /convert endpoint

```http
  GET /history
```


## Deployment

To deploy this project run:

Local machine:
```bash
  python3 -m uvicorn currency_converter:app --reload
```
Production server
```bash
python3 -m gunicorn -k uvicorn.workers.UvicornWorker currency_converter:app --bind=172.31.82.199:8000 --daemon
```

replace 172.31.82.199 with your server local ip.