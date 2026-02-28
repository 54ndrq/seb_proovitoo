# SEB Proovitöö – ECB Exchange Rates

## Prerequisites

- Python 3.12+
- uv or pip

## Getting Started

### 1. Install dependencies

Using uv:

```bash
uv sync
```

**Using pip:**

```bash
pip install -r requirements.txt
```

### 2. Run the application

**Using uv:**

```bash
uv run python src/seb_proovitoo/main.py
```

**Using pip / plain Python:**

```bash
python src/seb_proovitoo/main.py
```

The generated `exchange_rates.html` file will appear in the project root.

## AI usage

Used prompts:
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221Ymgib5C-vnDks-f5t4LxOnc_Doydqkpz%22%5D,%22action%22:%22open%22,%22userId%22:%22107458982624595056829%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing
```
Python: I need to create a python project. I will need to HTTP GET a .zip url, get the contents of it (a csv file), transform the data and output the result into a html.
What are the best, latest, modern packages to do these things? OR, if there are solutions in the python standard library, which ones?
```

https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221Wz1WpRNmerjYNfyRkjN6-JZg2-g7wlF9%22%5D,%22action%22:%22open%22,%22userId%22:%22107458982624595056829%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing
```
I need to set up a python development environment on windows 11. What are the best modern tools to manage that, and python dependencies etc. Also, what is the modern idiomatic python project structure.
```

```
How do you do in modern python strongly typed coding style?
```

In copilot through IDE, Opus 4.6 (can't link chatlogs):

```
Code review this project, output only criticisms with how minor or major they are. Find any missed edge-cases handling etc.
```

Answer:
```
. MAJOR - In extract_zip, if a currency value is "N/A" (which the ECB data actually contains for some dates/currencies), calling float(value) will raise a ValueError. There is no handling for missing or non-numeric values
. MAJOR - In extract_zip, if cleaned_row.get(currency) returns None (currency not found in a row), float(None) will raise a TypeError. There is no None check before the conversion
. MAJOR - In calculate_mean, if a currency has an empty list, len(data[key]) will be zero and you get a ZeroDivisionError. This can happen if all values were skipped or the data is empty
. MODERATE - The type alias syntax "type CurrencyData = ..." requires Python 3.12+. This is not documented anywhere and will cause a SyntaxError on older Python versions
. MODERATE - fetch_rates catches the broad Exception class. This swallows everything including KeyboardInterrupt (in Python 3 KeyboardInterrupt does not inherit Exception, so this is less severe, but it still catches things like MemoryError indirectly through the httpx call). It would be better to catch httpx.HTTPStatusError and httpx.RequestError specifically
. MODERATE - The extract_zip function assumes the zip file always contains at least one file. If zip_file.namelist() returns an empty list, zip_file.namelist()[0] will raise an IndexError
. MODERATE - The extract_zip function assumes the first file in the zip is always the CSV. There is no validation of the filename or file extension
. MINOR - create_html writes raw HTML without any DOCTYPE, html, head, or body tags. The output is not a valid HTML document, which may cause rendering issues in some browsers
. MINOR - The ecb_rates type annotation on line 22 (ecb_rates: Response) before the tuple unpacking is unnecessary and misleading since it is immediately overwritten by the tuple assignment
. MINOR - SELECTED_CURRENCIES is hardcoded. If the ECB ever changes or removes one of these currency codes, the program will fail silently or crash without a clear message
. MINOR - There is no retry logic for the HTTP requests. Network flakiness will cause immediate failure
. MINOR - The f-string inside logger.error is evaluated before being passed to the logger. It should use lazy formatting like logger.error("Failed to fetch rates: %s", e) to avoid unnecessary string formatting if the log level is above ERROR
. MINOR - The output file path is constructed relative to the file location using parent directory traversal. This is fragile and will break if the project structure changes or the file is moved
. MINOR - There is no encoding or escaping of currency data before writing to HTML. If any data contained special HTML characters it would be injected directly
. MINOR - The function calculate_mean returns a CurrencyData (dict of string to list of float) but each list always contains exactly one element. This is a misuse of the type, a dict mapping to a single float would be clearer and avoid the awkward [0] indexing elsewhere
```

```
. MINOR - The function calculate_mean returns a CurrencyData (dict of string to list of float) but each list always contains exactly one element. This is a misuse of the type, a dict mapping to a single float would be clearer and avoid the awkward [0] indexing elsewhere

fix this
```