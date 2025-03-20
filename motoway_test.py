import os
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from MotowayPage.motoway_page import MotowayPage

INPUT_FILE = "car_input.txt"
OUTPUT_FILE = "car_output.txt"

def read_registrations(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

def read_expected_output(file_path):
    return pd.read_csv(file_path)

async def fetch_vehicle_details(reg):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        motoway = MotowayPage(page)

        await motoway.open()
        await motoway.accept_cookies()
        await motoway.enter_registration(reg)

        if await motoway.check_invalid_reg():
            print(f"Invalid registration {reg}: Skipping...")
            await browser.close()
            return {"VARIANT_REG": reg, "MAKE_MODEL": "Invalid", "YEAR": "Invalid"}

        make_model, year = await motoway.get_vehicle_details()
        await browser.close()
        return {"VARIANT_REG": reg, "MAKE_MODEL": make_model, "YEAR": year}

async def main():
    registrations = read_registrations(INPUT_FILE)
    expected_data = read_expected_output(OUTPUT_FILE)

    results = []
    for reg in registrations:
        print(f"Checking: {reg} ...")
        details = await fetch_vehicle_details(reg)
        results.append(details)

    scraped_data = pd.DataFrame(results)

    comparison = expected_data.merge(scraped_data, on="VARIANT_REG", suffixes=("_expected", "_actual"))

    # Highlight mismatches
    def highlight_mismatch(val, row, col_expected, col_actual):
        expected = row[col_expected]
        actual = row[col_actual]
        return "background-color: red" if expected != actual else "background-color: lightgreen"

    comparison_styled = comparison.style.apply(
        lambda row: row.map(lambda val: highlight_mismatch(val, row, "MAKE_MODEL_expected", "MAKE_MODEL_actual")),
        axis=1
    )
    comparison_styled = comparison_styled.apply(
        lambda row: row.map(lambda val: highlight_mismatch(val, row, "YEAR_expected", "YEAR_actual")),
        axis=1
    )

    # Save results
    comparison.to_csv("comparison_results.csv", index=False)
    comparison_styled.to_excel("comparison_results.xlsx", index=False)

    print("✅ Comparison complete! Check 'comparison_results.csv' and 'comparison_results.xlsx'")

if __name__ == "__main__":
    asyncio.run(main())
