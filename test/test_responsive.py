from playwright.sync_api import sync_playwright

viewports = [
    {"name": "mobile", "width": 375, "height": 667},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "desktop", "width": 1440, "height": 900}
]

CHATBOT_SELECTOR = "#user-input"

def test_responsive():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for vp in viewports:
            print(f"\n🔍 Testing on {vp['name']} ({vp['width']}x{vp['height']})...")
            context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = context.new_page()
            page.goto("http://localhost:8000/") 

            assert page.locator(CHATBOT_SELECTOR).is_visible(), f"{CHATBOT_SELECTOR} is not visible on {vp['name']}"
            page.screenshot(path=f"screenshots/{vp['name']}.png", full_page=True)

            scroll_width = page.evaluate("() => document.body.scrollWidth")
            viewport_width = page.evaluate("() => window.innerWidth")
            assert scroll_width <= viewport_width, f"Unwanted horizontal scroll on {vp['name']}! scrollWidth={scroll_width}, viewportWidth={viewport_width}"


            print("✅ Passed: Layout is responsive and no horizontal scroll.")
            context.close()

            for vp in viewports:
                print(f"\n🔍 Testing on {vp['name']} ({vp['width']}x{vp['height']})...")
                context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
                page = context.new_page()
                page.goto("http://localhost:8000/dashboard") 

                # assert page.locator(CHATBOT_SELECTOR).is_visible(), f"{CHATBOT_SELECTOR} is not visible on {vp['name']}"
                page.screenshot(path=f"screenshots/{vp['name']}-db.png", full_page=True)

                scroll_width = page.evaluate("() => document.body.scrollWidth")
                viewport_width = page.evaluate("() => window.innerWidth")
                assert scroll_width <= viewport_width, f"Unwanted horizontal scroll on {vp['name']}! scrollWidth={scroll_width}, viewportWidth={viewport_width}"


                print("✅ Passed: Layout is responsive and no horizontal scroll.")
                context.close()
        
        browser.close()