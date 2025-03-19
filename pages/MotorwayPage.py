import motoway_test

def __init__(self, page):
        self.page = page

async def navigate(self):
        """Navigates to the Motorway page and accepts cookies if prompted."""
        await self.page.goto("https://motorway.co.uk/sell-my-car")

        # Handle cookie popup if it appears
        try:
            await self.page.click("button:has-text('Accept')", timeout=5000)
        except:
            pass  # If no cookie prompt, continue

async def enter_registration(self, reg):
        """Enters the vehicle registration number and submits the form."""
        await self.page.fill("#vrm-input", reg)
        await self.page.press("#vrm-input", "Enter")

async def check_invalid_registration(self, reg):
        """Checks if the registration number is invalid by detecting a toast message."""
        try:
            await self.page.wait_for_selector(".Toast-shared-module__toasterContainer-muon", timeout=5000)
            print(f"Invalid registration {reg}: Skipping...")
            return True
        except:
            return False  # No error toast means it's a valid registration

async def get_vehicle_details(self, reg):
        """Extracts vehicle details from the mileage page."""
        try:
            print(f"Current URL: {self.page.url}")  # Debugging URL
            await self.page.wait_for_url("https://motorway.co.uk/mileage*", timeout=10000)
            await self.page.wait_for_selector("[data-cy='vehicleMakeAndModel']", timeout=10000)
            make_model = await self.page.inner_text("[data-cy='vehicleMakeAndModel']")
            year = await self.page.inner_text(".vehicle-year")  # Assuming this selector exists
            return {"VARIANT_REG": reg, "MAKE_MODEL": make_model, "YEAR": year}
        except:
            print(f"Error while navigating or loading vehicle details for {reg}. Skipping...")
            return {"VARIANT_REG": reg, "MAKE_MODEL": "Not Found", "YEAR": "Not Found"}

async def fetch_vehicle_details(reg):
    """Fetches vehicle details using Playwright and the Page Object Model."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for silent execution
        page = await browser.new_page()
        motorway = MotorwayPage(page)

        await motorway.navigate()
        await motorway.enter_registration(reg)

        if await motorway.check_invalid_registration(reg):
            await browser.close()
            return {"VARIANT_REG": reg, "MAKE_MODEL": "Invalid Registration", "YEAR": "Invalid Registration"}

        details = await motorway.get_vehicle_details(reg)
        await browser.close()
        return details
def read_registrations(file_path):
    """Reads vehicle registrations from a text file."""
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

def read_expected_output(file_path):
    """Reads expected results from a CSV file."""
    return pd.read_csv(file_path)

async def main():
    registrations = read_registrations(INPUT_FILE)
    expected_data = read_expected_output(OUTPUT_FILE)

    # Fetch details for each registration asynchronously
    tasks = [fetch_vehicle_details(reg) for reg in registrations]
    results = await asyncio.gather(*tasks)

    # Convert results to DataFrame
    scraped_data = pd.DataFrame(results)

    # Merge and compare
    comparison = expected_data.merge(scraped_data, on="VARIANT_REG", suffixes=("_expected", "_actual"))

    # Highlight mismatches
    def highlight_mismatch(val):
        return "background-color: red" if val[0] != val[1] else "background-color: lightgreen"

    comparison_styled = comparison.style.map(
        lambda val: highlight_mismatch((val, val)),
        subset=["MAKE_MODEL_expected", "MAKE_MODEL_actual", "YEAR_expected", "YEAR_actual"]
    )

    # Save results
    comparison.to_csv("comparison_results.csv", index=False)
    comparison_styled.to_excel("comparison_results.xlsx", index=False)

    print("✅ Comparison complete! Check 'comparison_results.csv' and 'comparison_results.xlsx'")

# Run the script
asyncio.run(main())
