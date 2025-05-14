import asyncio
from playwright.async_api import async_playwright

async def test_friendly_error():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        await page.goto("http://localhost:8000")

        await page.route("**/stream/**", lambda route: asyncio.create_task(route.abort()))

        await page.fill("#user-input", "Hello")
        await page.click("#send-btn")  

        await page.wait_for_selector("#error-message")  
        
        error_message = await page.inner_text("#error-message")
        assert "try again" in error_message, "The error message is not as expected"

        print("Test Passed: The error message is correct!")

        await browser.close()

asyncio.run(test_friendly_error())