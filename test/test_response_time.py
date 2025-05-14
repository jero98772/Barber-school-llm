import asyncio
import time
from playwright.async_api import async_playwright

async def test_response_time():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000")

        await page.fill("#user-input", "¿Que horarios tiene el curso?")
        start_time = time.time()
        await page.press("#user-input", "Enter")

        await page.wait_for_selector(".bot-message", timeout=10000)
        end_time = time.time()

        # Calculate response time
        response_time = end_time - start_time
        assert response_time < 3.0, f"Response took too long: {response_time:.2f}s"

        print(f"Test Passed: Response in {response_time:.2f}s")

        await browser.close()

# Run the test
asyncio.run(test_response_time())