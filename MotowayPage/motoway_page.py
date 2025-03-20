import asyncio
from playwright.async_api import Page

class MotowayPage:
    BASE_URL = "https://motorway.co.uk/sell-my-car"

    def __init__(self, page: Page):
        self.page = page

    async def open(self):
        await self.page.goto(self.BASE_URL)

    async def accept_cookies(self):
        try:
            await self.page.click("button:has-text('Accept')", timeout=2000)
        except:
            pass  # No cookie prompt

    async def enter_registration(self, reg):
        await self.page.fill("#vrm-input", reg)
        await self.page.press("#vrm-input", "Enter")

    async def check_invalid_reg(self):
        try:
            await self.page.wait_for_selector(".Toast-shared-module__toasterContainer-muon", timeout=2000)
            return True
        except:
            return False

    async def get_vehicle_details(self):
        try:
            await self.page.wait_for_url("https://motorway.co.uk/mileage*", timeout=10000)
            make_model = await self.page.inner_text("[data-cy='vehicleMakeAndModel']")
            year = await self.page.inner_text(".vehicle-year")
            return make_model, year
        except:
            return "Not Found", "Not Found"
