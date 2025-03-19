import re
import asyncio
import os
import pandas as pd
from playwright.async_api import async_playwright

INPUT_FILE = "car_input.txt"
OUTPUT_FILE = "car_output.txt"

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Error: {INPUT_FILE} not found!")

if not os.path.exists(OUTPUT_FILE):
    raise FileNotFoundError(f"Error: {OUTPUT_FILE} not found!")

# Function to read vehicle registrations from input.txt
def read_registrations(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

def read_expected_output(file_path):
    return pd.read_csv(file_path)

async def fetch_vehicle_details(reg):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://motorway.co.uk/sell-my-car")

        try:
            await page.click("button:has-text('Accept')", timeout=5000)
        except:
            pass

        # Fill in the registration number
        await page.fill("#vrm-input", reg)
        await page.press("#vrm-input", "Enter")

        # Wait for the "Did we get the reg right?" popup
        try:
            await page.wait_for_selector(
                ".Toast-shared-module__toasterContainer-muon",
                timeout=5000
            )
            print(f"Invalid registration {reg}: Skipping...")
            await browser.close()
            return {"VARIANT_REG": reg, "MAKE_MODEL": "Invalid Registration", "YEAR": "Invalid Registration"}
        except:
            pass

        try:
            print(f"Current URL: {page.url}")
            await page.wait_for_url("https://motorway.co.uk/mileage*", timeout=10000)
            await page.wait_for_selector("[data-cy='vehicleMakeAndModel']", timeout=10000)
        except:
            print(f"Error while navigating or loading vehicle details for {reg}. Skipping...")
            await browser.close()
            return {"VARIANT_REG": reg, "MAKE_MODEL": "Not Found", "YEAR": "Not Found"}

        # Extract car details
        try:
            make_model = await page.inner_text("[data-cy='vehicleMakeAndModel']")
            year = await page.inner_text(".vehicle-year")
        except:
            make_model, year = "Not Found", "Not Found"

        await browser.close()
        return {"VARIANT_REG": reg, "MAKE_MODEL": make_model, "YEAR": year}

async def main():
    registrations = read_registrations(INPUT_FILE)
    expected_data = read_expected_output(OUTPUT_FILE)

    # Fetch details for each registration
    results = []
    for reg in registrations:
        print(f"Checking: {reg} ...")
        details = await fetch_vehicle_details(reg)
        results.append(details)

    scraped_data = pd.DataFrame(results)

    comparison = expected_data.merge(scraped_data, on="VARIANT_REG", suffixes=("_expected", "_actual"))

    # Highlight mismatches
    def highlight_mismatch(val):
        return "background-color: red" if val[0] != val[1] else "background-color: lightgreen"

    comparison_styled = comparison.style.applymap(
        lambda val: highlight_mismatch((val, val)),
        subset=["MAKE_MODEL_expected", "MAKE_MODEL_actual", "YEAR_expected", "YEAR_actual"]
    )
    comparison.to_csv("comparison_results.csv", index=False)
    comparison_styled.to_excel("comparison_results.xlsx", index=False)

    print("✅ Comparison complete! Check 'comparison_results.csv' and 'comparison_results.xlsx'")

asyncio.run(main())
