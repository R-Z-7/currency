from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

def get_exchange_rates(currency_code):
    if API_KEY is None:
        return None, "API key not provided"

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{currency_code}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"], None
        else:
            return None, data.get("error")
    except requests.exceptions.HTTPError as errh:
        return None, f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return None, f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return None, f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return None, f"Oops: Something went wrong {err}"

def convert_currency(amount, from_currency, to_currency, exchange_rates):
    if exchange_rates is None:
        return "Failed to fetch exchange rates. Please try again later.", False

    if from_currency == to_currency:
        return amount, True

    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        return "Invalid currency code", False

    exchange_rate = exchange_rates[to_currency] / exchange_rates[from_currency]
    converted_amount = amount * exchange_rate
    return converted_amount, True

@app.route('/')
def index():
    currencies = [
        "INR", "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG",
        "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB",
        "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP",
        "CNY", "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD",
        "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP",
        "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG",
        "HUF", "IDR", "ILS", "IMP", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
        "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT",
        "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD",
        "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", "MZN",
        "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK",
        "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
        "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD",
        "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY",
        "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES",
        "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR",
        "ZMW", "ZWL"
    ]

    exchange_rates = {}
    errors = []

    for currency in currencies:
        rates, error = get_exchange_rates(currency)
        if rates is not None:
            exchange_rates[currency] = rates
        else:
            errors.append(error)

    if not errors:
        return render_template('index.html', currencies=currencies, exchange_rates=exchange_rates)
    else:
        error_message = "Failed to fetch exchange rates for some currencies. Please try again later."
        return render_template('index.html', result=error_message)

@app.route('/convert', methods=['POST'])
def convert():
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']
    amount = float(request.form['amount'])

    exchange_rates, error_message = get_exchange_rates(from_currency)

    if exchange_rates is None:
        return render_template('index.html', result=error_message)

    converted_amount, success = convert_currency(amount, from_currency, to_currency, exchange_rates)

    if not success:
        return render_template('index.html', result=converted_amount)

    return render_template('index.html', result=f'{amount} {from_currency} = {float(converted_amount):.2f} {to_currency}')

if __name__ == '__main__':
    app.run(debug=True)
