import asyncio
from playwright.async_api import async_playwright

async def test_input_visibilitu():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.goto("http://localhost:8000")

        assert await page.is_visible("#user-input"), "El área de texto no es visible en escritorio."
        placeholder = await page.get_attribute("#user-input", "placeholder")
        assert placeholder and len(placeholder.strip()) > 0, "El área de texto no tiene un placeholder útil."

        print("Escritorio: Área de entrada visible con placeholder.")

        await page.set_viewport_size({"width": 375, "height": 667})
        await page.reload()

        assert await page.is_visible("#user-input"), "El área de texto no es visible en móvil."
        placeholder_mobile = await page.get_attribute("#user-input", "placeholder")
        assert placeholder_mobile and len(placeholder_mobile.strip()) > 0, "Placeholder no se muestra correctamente en móvil."

        print("Móvil: Área de entrada visible con placeholder.")

        await browser.close()

asyncio.run(test_input_visibilitu())