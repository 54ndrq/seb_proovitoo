import csv
import os

import httpx
import logging
import zipfile
import io

from httpx import Response
from tabulate import tabulate

type CurrencyData = dict[str, list[float]]
type CurrencyMean = dict[str, float]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SELECTED_CURRENCIES: list[str] = ['USD', 'SEK', 'GBP', 'JPY']


def main() -> None:
    ecb_rates: Response
    historical_ecb_rates: Response
    ecb_rates, historical_ecb_rates = fetch_rates()

    historical_data: CurrencyData = extract_zip(historical_ecb_rates)
    historical_mean: CurrencyMean = calculate_mean(historical_data)

    currency_codes = list(historical_mean.keys())
    extracted_rates: CurrencyData = extract_zip(ecb_rates)

    create_html(currency_codes, extracted_rates, historical_mean)


def fetch_rates() -> tuple[Response, Response]:
    logger.info("Fetching rates...")

    try:
        ecb_rates = httpx.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip", timeout=30)
        ecb_rates.raise_for_status()

        historical_ecb_rates: Response = httpx.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip",
                                                   timeout=30)
        historical_ecb_rates.raise_for_status()

        logger.info("Fetching complete.")

    except Exception as e:
        logger.error(f"Failed to fetch rates: {e}")
        raise

    return ecb_rates, historical_ecb_rates


def extract_zip(response: Response) -> CurrencyData:
    logger.info("Extracting info from zip...")

    currencies: CurrencyData = {c: [] for c in SELECTED_CURRENCIES}

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        filename: str = zip_file.namelist()[0]

        with zip_file.open(filename) as csv_file:
            content: io.TextIOWrapper = io.TextIOWrapper(csv_file, encoding='utf-8')
            reader: csv.DictReader[str] = csv.DictReader(content)

            for row in reader:
                cleaned_row: dict[str, str] = {key.strip(): value.strip() for key, value in row.items()}
                for currency in SELECTED_CURRENCIES:
                    value: str = cleaned_row.get(currency)
                    currencies[currency].append(float(value))

    return currencies


def calculate_mean(data: CurrencyData) -> CurrencyMean:
    logger.info("Calculating historical means...")

    rates: CurrencyMean = {}
    for key in data.keys():
        total: float = sum(data[key])
        rates[key] = round(total / len(data[key]), 4)
    return rates


def create_html(currency_codes: list[str], rates: CurrencyData, mean: CurrencyMean) -> None:
    headers: list[str] = ['Currency Code', 'Rate', 'Mean Historical Rate']
    table_data: list[list[str | float]] = []

    for currency in currency_codes:
        current_rate: float = rates[currency][0]
        historical_mean: float = mean[currency]

        row: list[str | float] = [currency.upper(), current_rate, historical_mean]
        table_data.append(row)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    output_path = os.path.join(project_root, 'exchange_rates.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tabulate(table_data, headers=headers, tablefmt='html'))
        logger.info(f"HTML table saved to {output_path}")


if __name__ == "__main__":
    main()
