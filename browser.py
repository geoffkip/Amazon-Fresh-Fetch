import streamlit as st
import os
import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict

class AmazonFreshBrowser:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.session_file = "amazon_session.json"

    async def start(self):
        if self.page: return 
        st.toast("🚀 Launching Browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=1000)
        
        if os.path.exists(self.session_file):
            self.context = await self.browser.new_context(storage_state=self.session_file, viewport={"width": 1280, "height": 720})
            st.toast("🍪 Session loaded")
        else:
            self.context = await self.browser.new_context(viewport={"width": 1280, "height": 720})

        self.page = await self.context.new_page()
        await self.page.goto("https://www.amazon.com/alm/storefront?almBrandId=QW1hem9uIEZyZXNo")
        
        try:
            if await self.page.locator("#nav-link-accountList-nav-line-1").filter(has_text="Sign in").count() > 0:
                st.warning("⚠️ Please Log In manually in the browser window!")
                await asyncio.sleep(60)
                await self.context.storage_state(path=self.session_file)
        except: pass
        st.success("✅ Browser Ready")

    # --- BRUTE FORCE ADD ---
    async def search_and_add(self, item_name: str) -> dict:
        try:
            search_box = self.page.locator('input[id="twotabsearchtextbox"]')
            await search_box.clear()
            await search_box.fill(item_name)
            await search_box.press('Enter')
            try: await self.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=3000)
            except: pass

            results = await self.page.locator('div[data-component-type="s-search-result"]').all()
            if not results: return {"status": "NOT_FOUND", "price": 0.0}
            target_card = results[0]

            price = 0.0
            try:
                price_el = target_card.locator(".a-price .a-offscreen").first
                if await price_el.count() > 0:
                    txt = await price_el.text_content()
                    price = float(txt.replace("$", "").replace(",", "").strip())
            except: pass

            btn = target_card.get_by_role("button", name="Add to cart")
            if await btn.count() == 0: btn = target_card.locator("button[name='submit.addToCart']")
            if await btn.count() == 0: btn = target_card.locator("input[name='submit.addToCart']")

            if await btn.count() > 0 and await btn.first.is_visible():
                await btn.first.click()
                await asyncio.sleep(2)
                return {"status": "ADDED", "price": price}
            
            return {"status": "NOT_FOUND", "price": 0.0}
        except Exception as e:
            return {"status": f"ERROR", "price": 0.0}

    # --- SMART SHOPPER LOGIC ---
    async def search_and_get_options(self, item_name: str) -> List[Dict]:
        try:
            search_box = self.page.locator('input[id="twotabsearchtextbox"]')
            await search_box.clear()
            await search_box.fill(item_name)
            await search_box.press('Enter')
            try: await self.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=3000)
            except: pass

            results = await self.page.locator('div[data-component-type="s-search-result"]').all()
            options = []
            for i, res in enumerate(results[:3]): 
                try:
                    title = await res.locator("h2").first.text_content()
                    price_text = "0.00"
                    if await res.locator(".a-price .a-offscreen").count() > 0:
                        price_text = await res.locator(".a-price .a-offscreen").first.text_content()
                    options.append({
                        "index": i,
                        "title": title.strip(),
                        "price_str": price_text.strip(),
                        "price": float(price_text.replace("$", "").replace(",", "").strip()) if "$" in price_text else 0.0
                    })
                except: continue
            return options
        except: return []

    async def add_specific_item(self, index: int) -> bool:
        try:
            results = await self.page.locator('div[data-component-type="s-search-result"]').all()
            if index >= len(results): return False
            target = results[index]
            
            btn = target.get_by_role("button", name="Add to cart")
            if await btn.count() == 0: btn = target.locator("button[name='submit.addToCart']")
            if await btn.count() == 0: btn = target.locator("input[name='submit.addToCart']")
            
            if await btn.count() > 0:
                await btn.first.scroll_into_view_if_needed()
                if await btn.first.is_visible():
                    await btn.first.click()
                    await asyncio.sleep(1)
                    return True
            return False
        except: return False

    async def trigger_checkout(self):
        st.toast("🛒 Going to Cart...")
        await self.page.goto("https://www.amazon.com/gp/cart/view.html")
        await asyncio.sleep(3)
        st.toast("➡️ Clicking 'Check out Fresh Cart'...")
        try:
            fresh_btn = self.page.get_by_role("button", name="Check out Fresh Cart")
            if await fresh_btn.count() > 0:
                await fresh_btn.click()
                return True
            proceed_btn = self.page.locator("input[name='proceedToALMCheckout-QW1hem9uIEZyZXNo']")
            if await proceed_btn.count() > 0:
                await proceed_btn.click()
                return True
            fallback = self.page.get_by_role("button", name="Proceed to checkout")
            if await fallback.count() > 0:
                await fallback.click()
                return True
        except: return False
        return False

    async def close(self):
        if self.context: await self.context.storage_state(path=self.session_file)
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
