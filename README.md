# Website Brand Info Extractor

A Python automation project that extracts structured brand, contact, metadata, and social information from a list of websites.

## Overview

This project reads website URLs from an input CSV file, visits each website, extracts useful brand and business information, and saves the results into a structured CSV file.

The tool is designed for freelance-style data extraction tasks where a client provides a list of websites and needs clean business information in CSV or Excel format.

## Features

* Reads multiple website URLs from an input CSV file
* Extracts website title and domain
* Extracts meta description
* Extracts H1 and H2 headings
* Finds public email addresses
* Finds public phone numbers
* Detects social media links
* Detects About and Contact page links
* Handles failed or blocked websites
* Detects soft-blocked pages where HTTP status is 200 but the content is blocked
* Saves clean structured output to CSV
* Prints a summary of successful, blocked, and failed extractions

## Data Extracted

The output CSV includes:

* Website URL
* Domain
* Status Code
* Access Status
* Page Title
* Meta Description
* H1 Heading
* H2 Headings
* Emails Found
* Phone Numbers Found
* Social Links
* About Page
* Contact Page
* Error Message
* Scrape Timestamp

## Test Run Summary

The scraper was tested on 20 websites.

* Successful extractions: 16
* Soft blocked pages: 1
* Blocked or failed pages: 3
* Request errors: 0
* Unexpected errors: 0

## Access Status Types

```text
success
```

The website was successfully accessed and data was extracted.

```text
soft_blocked
```

The website returned HTTP 200, but the page content appeared to be blocked.

```text
blocked_or_failed
```

The website returned a failed or blocked HTTP status code such as 403 or 406.

```text
request_error
```

The request failed due to timeout, connection issue, or another request-level problem.

## Technologies Used

* Python
* Requests
* BeautifulSoup
* Regex
* CSV
* URL parsing
* Error handling

## Repository Structure

```text
website-brand-info-extractor/
│
├── brand_extractor.py
├── input_websites.csv
├── brand_info_results.csv
├── requirements.txt
├── README.md
└── screenshots/
    ├── terminal_run.png
    └── csv_preview.png
```

## How To Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add website URLs to `input_websites.csv`:

```csv
website_url
https://www.nike.com
https://www.apple.com
https://www.shopify.com
```

3. Run the scraper:

```bash
python brand_extractor.py
```

4. The extracted data will be saved to:

```text
brand_info_results.csv
```

## Sample Use Cases

* Business website research
* Lead generation support
* Brand data collection
* Contact information extraction
* Website metadata analysis
* Social profile discovery
* Company directory enrichment

## Author

Shameer Shahid

Computer Science student focused on Python automation, web scraping, data extraction, and freelance-ready business tools.
