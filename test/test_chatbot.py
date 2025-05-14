import asyncio
from playwright.async_api import async_playwright

async def test_text_area_functionality():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000")

        await page.wait_for_selector("#user-input", timeout=3000)

        initial_responses = await page.locator(".bot-message").count()
        # print(initial_responses)

        # Submit empty
        await page.fill("#user-input", "")
        await page.click("#send-btn")
        await page.wait_for_timeout(10000)  

        after_empty_responses = await page.locator(".bot-message").count()
        # print(after_empty_responses)
        assert initial_responses == after_empty_responses, "Bot should not respond to empty input"

        # Type a valid message and press Enter
        await page.fill("#user-input", "¿Cuál es tu nombre?")
        await page.press("#user-input", "Enter")
        await page.wait_for_selector(".bot-message", timeout=10000)
        await page.wait_for_timeout(2000)  

        # Type another message and use Send button
        await page.fill("#user-input", "a")
        await page.click("#send-btn")
        await page.wait_for_selector(".bot-message", timeout=10000)
        await page.wait_for_timeout(2000)  

        print("Test Passed: Text area is functional with both Enter and Send button, and does not accept empty input.")

        await browser.close()

asyncio.run(test_text_area_functionality())