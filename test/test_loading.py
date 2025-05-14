import asyncio
from playwright.async_api import async_playwright

async def test_response_loading():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000")

        await page.fill("#user-input", "¿Que horarios tiene el curso?")
        await page.press("#user-input", "Enter")

        await page.wait_for_selector(".loading", timeout=1000)

        print("Test Passed: Loading indicator shown after sending message.")

        await browser.close()

asyncio.run(test_response_loading())