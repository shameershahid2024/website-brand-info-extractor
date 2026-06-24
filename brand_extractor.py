import csv
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


INPUT_FILE = "input_websites.csv"
OUTPUT_FILE = "brand_info_results.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/145.0.0.0 Safari/537.36"
}

SOCIAL_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",
    "pinterest.com"
]


def read_websites(filename):
    websites = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            url = row.get("website_url", "").strip()

            if url:
                websites.append(url)

    return websites


def clean_text(text):
    if not text:
        return ""

    return " ".join(text.split())


def extract_emails(text, soup):
    emails = set()

    found_emails = re.findall(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        text
    )
    emails.update(found_emails)

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split("?")[0]
            emails.add(email)

    return " | ".join(sorted(emails))


def extract_phones(text):
    phones = set()

    phone_patterns = re.findall(
        r"(\+?\d[\d\s().-]{7,}\d)",
        text
    )

    for phone in phone_patterns:
        cleaned = clean_text(phone)

        if len(cleaned) >= 8:
            phones.add(cleaned)

    return " | ".join(sorted(phones))


def extract_social_links(soup, base_url):
    social_links = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(base_url, href)

        for domain in SOCIAL_DOMAINS:
            if domain in full_url.lower():
                social_links.add(full_url)

    return " | ".join(sorted(social_links))


def find_page_link(soup, base_url, keywords):
    for link in soup.find_all("a", href=True):
        href = link["href"].lower()
        text = clean_text(link.get_text()).lower()

        for keyword in keywords:
            if keyword in href or keyword in text:
                return urljoin(base_url, link["href"])

    return ""


def is_soft_blocked(title, page_text):
    """
    Detects pages that return HTTP 200 but still show a block/access-denied page.
    This avoids using very broad words like 'blocked' alone because they can
    create false positives on normal pages.
    """
    title_text = title.lower()
    page_text_lower = page_text.lower()

    strong_title_blocks = [
        "request has been blocked",
        "access denied",
        "403 forbidden",
        "forbidden",
        "captcha",
        "verify you are human",
        "unusual traffic",
        "temporarily blocked"
    ]

    for keyword in strong_title_blocks:
        if keyword in title_text:
            return True

    strong_page_blocks = [
        "your request has been blocked",
        "access to this page has been denied",
        "please verify you are human",
        "checking if the site connection is secure"
    ]

    for keyword in strong_page_blocks:
        if keyword in page_text_lower:
            return True

    return False


def extract_brand_info(url):
    result = {
        "website_url": url,
        "domain": "",
        "status_code": "",
        "access_status": "",
        "title": "",
        "meta_description": "",
        "h1": "",
        "h2_headings": "",
        "emails_found": "",
        "phones_found": "",
        "social_links": "",
        "about_page": "",
        "contact_page": "",
        "error": "",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        parsed_url = urlparse(url)
        result["domain"] = parsed_url.netloc

        response = requests.get(url, headers=HEADERS, timeout=20)
        result["status_code"] = response.status_code

        if response.status_code != 200:
            result["access_status"] = "blocked_or_failed"
            result["error"] = f"HTTP {response.status_code}"
            return result

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        # Title
        if soup.title:
            result["title"] = clean_text(soup.title.get_text())

        # Detect soft blocks
        if is_soft_blocked(result["title"], page_text):
            result["access_status"] = "soft_blocked"
            result["error"] = "Page returned 200 but content appears blocked"
        else:
            result["access_status"] = "success"

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            result["meta_description"] = clean_text(meta_desc["content"])

        # H1
        h1 = soup.find("h1")
        if h1:
            result["h1"] = clean_text(h1.get_text())

        # H2 headings
        h2_list = []
        for h2 in soup.find_all("h2"):
            text = clean_text(h2.get_text())

            if text:
                h2_list.append(text)

        result["h2_headings"] = " | ".join(h2_list[:10])

        # Emails, phones, social links
        result["emails_found"] = extract_emails(page_text, soup)
        result["phones_found"] = extract_phones(page_text)
        result["social_links"] = extract_social_links(soup, url)

        # About/contact pages
        result["about_page"] = find_page_link(
            soup,
            url,
            ["about", "about us", "company"]
        )

        result["contact_page"] = find_page_link(
            soup,
            url,
            ["contact", "contact us", "support", "help"]
        )

        return result

    except requests.exceptions.RequestException as e:
        result["access_status"] = "request_error"
        result["error"] = str(e)
        return result

    except Exception as e:
        result["access_status"] = "unexpected_error"
        result["error"] = f"Unexpected error: {e}"
        return result


def save_results(results, filename):
    if not results:
        print("No results to save.")
        return

    fieldnames = list(results[0].keys())

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} rows to {filename}")


def print_summary(results):
    success_count = sum(1 for row in results if row["access_status"] == "success")
    soft_blocked_count = sum(1 for row in results if row["access_status"] == "soft_blocked")
    failed_count = sum(1 for row in results if row["access_status"] == "blocked_or_failed")
    request_error_count = sum(1 for row in results if row["access_status"] == "request_error")
    unexpected_error_count = sum(1 for row in results if row["access_status"] == "unexpected_error")

    print("\nSummary")
    print("-" * 60)
    print(f"Successful extractions : {success_count}")
    print(f"Soft blocked pages     : {soft_blocked_count}")
    print(f"Blocked/failed pages   : {failed_count}")
    print(f"Request errors         : {request_error_count}")
    print(f"Unexpected errors      : {unexpected_error_count}")


def main():
    print("=" * 60)
    print("WEBSITE BRAND INFO EXTRACTOR")
    print("=" * 60)

    websites = read_websites(INPUT_FILE)

    print(f"Websites loaded: {len(websites)}")

    results = []

    for index, website in enumerate(websites, start=1):
        print(f"\n[{index}/{len(websites)}] Scraping: {website}")

        data = extract_brand_info(website)
        results.append(data)

        print(f"Status Code: {data['status_code']}")
        print(f"Access Status: {data['access_status']}")

        if data["error"]:
            print(f"Error: {data['error']}")
        else:
            print(f"Title: {data['title'][:80]}")

        time.sleep(1)

    save_results(results, OUTPUT_FILE)
    print_summary(results)

    print("\nDone.")
    print("=" * 60)


if __name__ == "__main__":
    main()