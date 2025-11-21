import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from typing import List, Optional, TypedDict, Annotated
from operator import add

# LangChain / LangGraph imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Browser Automation imports
from playwright.async_api import async_playwright, Page

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    shopping_list: List[str]
    cart_items: List[str]
    missing_items: List[str]
    user_approved: bool
    delivery_window: str

# --- 2. The Browser Tool (Robust Version) ---
class AmazonFreshBrowser:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None

    async def start(self):
        """Starts the browser (Headed so you can see/login)."""
        print("🚀 Launching Browser...")
        self.playwright = await async_playwright().start()
        
        # Launch with slow_mo to help Amazon process clicks and headless=False to see it
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=1500)
        
        # Create context with a real User Agent so Amazon doesn't think we are a robot immediately
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # Navigate to Amazon Fresh
        await self.page.goto("https://www.amazon.com/alm/storefront?almBrandId=QW1hem9uIEZyZXNo")
        
        print("\n⚠️  ACTION REQUIRED: Browser is open.")
        print("⚠️  You have 60 seconds to MANUALLY LOG IN and select your FRESH ZIP CODE.")
        print("⚠️  If you don't log in, items will show as 'Not Found'.\n")
        
        await asyncio.sleep(30) # Wait 60s for user login
        print("⏰ Time up! Agent is taking control now...")

    async def search_and_add(self, item_name: str) -> str:
        """Searches for an item and tries multiple methods to add it to cart."""
        try:
            print(f"🛒 Searching for: {item_name}")
            
            # 1. Clear search bar and type
            # We use a generic selector for the search bar which is usually stable
            search_box = self.page.locator('input[id="twotabsearchtextbox"]')
            await search_box.clear()
            await search_box.fill(item_name)
            await search_box.press('Enter')
            
            # 2. Wait for results to load
            # We wait for the generic result container 's-search-result'
            try:
                await self.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=5000)
            except:
                print("  - Standard search results not found, checking alternative layout...")

            # 3. Get the FIRST result card
            # We only look for buttons INSIDE the first result to avoid clicking ads
            first_result = self.page.locator('div[data-component-type="s-search-result"]').first
            
            if await first_result.count() == 0:
                return "NOT_FOUND (No results)"

            print(f"  - Found product card. Looking for 'Add' button...")

            # 4. Multi-Strategy Button Finder
            # Amazon changes button classes daily. We try 4 different ways to find the button.
            
            # Strategy A: By Role (Best for accessibility)
            btn = first_result.get_by_role("button", name="Add to cart")
            
            # Strategy B: By Role with exact name "Add" (Common in grid view)
            if await btn.count() == 0:
                btn = first_result.get_by_role("button", name="Add", exact=True)
                
            # Strategy C: By CSS Name attribute (Old reliable)
            if await btn.count() == 0:
                btn = first_result.locator("button[name='submit.addToCart']")

            # Strategy D: By Input Type (Very old HTML structure)
            if await btn.count() == 0:
                btn = first_result.locator("input[name='submit.addToCart']")

            # 5. Execute Click
            if await btn.count() > 0:
                # Ensure the button is actually visible before clicking
                if await btn.first.is_visible():
                    await btn.first.click()
                    print("  - Clicked Add!")
                    # Short wait to ensure the cart animation finishes
                    await asyncio.sleep(2)
                    return f"Successfully added {item_name} to cart."
                else:
                    return "NOT_FOUND (Button hidden)"
            else:
                return "NOT_FOUND (Button missing)"

        except Exception as e:
            print(f"  - Error: {e}")
            return f"Error searching for {item_name}"

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Global browser instance
browser_tool = AmazonFreshBrowser()

# --- 3. Nodes (The Logic) ---

async def parser_node(state: AgentState):
    """Parses input into ingredients using Gemini Flash."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Using Flash for speed and free tier access
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    initial_input = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a shopping assistant. Extract a list of grocery ingredients from the user's input. "
                   "Return ONLY a comma-separated list of items. If a quantity is not specified, assume 1. "
                   "Example output: 'milk, eggs, bread'"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": initial_input})
    
    items = [item.strip() for item in response.content.split(',')]
    
    return {
        "shopping_list": items,
        "messages": [HumanMessage(content=f"Parsed list: {items}")]
    }

async def shopper_node(state: AgentState):
    """Executes shopping and handles substitutions."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    shopping_list = state["shopping_list"]

    cart = []
    missing = []

    # Start browser if not already running
    if not browser_tool.page:
        await browser_tool.start()

    for item in shopping_list:
        result = await browser_tool.search_and_add(item)
        
        if "NOT_FOUND" in result:
            # SUBSTITUTION LOGIC
            print(f"⚠️ {item} out of stock or not found. Asking Gemini for substitution...")
            sub_prompt = f"The item '{item}' is not available on Amazon Fresh. Name ONE generic substitute I can search for. Return ONLY the name."
            sub_response = await llm.ainvoke([HumanMessage(content=sub_prompt)])
            sub_item = sub_response.content.strip()
            
            print(f"🔄 Trying substitute: {sub_item}")
            retry_result = await browser_tool.search_and_add(sub_item)
            
            if "Successfully added" in retry_result:
                cart.append(f"{sub_item} (Substituted for {item})")
            else:
                missing.append(item)
        else:
            cart.append(item)
            
    return {
        "cart_items": cart,
        "missing_items": missing,
        "messages": [HumanMessage(content=f"Shopping complete. Cart: {cart}. Missing: {missing}")]
    }

async def human_review_node(state: AgentState):
    """Pauses the graph for human review."""
    print("\n--- 🛑 HUMAN REVIEW REQUIRED ---")
    print(f"Current Cart: {state['cart_items']}")
    print(f"Missing Items: {state['missing_items']}")
    print("System paused. Waiting for approval to checkout.")
    return state

async def checkout_node(state: AgentState):
    """Simulates checkout process."""
    if not state.get("user_approved"):
        return {"messages": [SystemMessage(content="User aborted checkout.")]}

    print("\n💸 Proceeding to Checkout Logic...")
    # NOTE: We do not actually click 'Place Order' to prevent accidental charges in this demo.
    # await browser_tool.page.click("input[name='proceedToCheckout']")
    
    window = state.get("delivery_window", "Not specified")
    return {
        "messages": [SystemMessage(content=f"Order placed! Delivery set for: {window}")]
    }

# --- 4. Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("parser", parser_node)
workflow.add_node("shopper", shopper_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("checkout", checkout_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "shopper")
workflow.add_edge("shopper", "human_review")
workflow.add_edge("human_review", "checkout")
workflow.add_edge("checkout", END)

# Checkpointer memory allows us to pause and resume
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["checkout"])

# --- 5. Execution Script ---

async def main():
    config = {"configurable": {"thread_id": "grocery_run_1"}}
    
    # 1. Get User Input
    user_request = input("What would you like to cook (or paste ingredients)?\n> ")
    
    print("\n--- 🤖 Agent Starting ---")
    
    # 2. Run until the 'checkout' interruption
    async for event in app.astream({"messages": [HumanMessage(content=user_request)]}, config):
        # We just iterate to let the graph run; printing happens inside nodes
        pass

    # 3. Inspect State (The graph is now PAUSED)
    current_state = app.get_state(config)
    
    # If we finished shopping, the next node should be 'checkout'
    if current_state.next and current_state.next[0] == 'checkout':
        print("\n--- ⏸️ PAUSED FOR REVIEW ---")
        print("The agent has finished shopping. Do you want to proceed to checkout?")
        
        user_decision = input("Type 'yes' to checkout, 'no' to cancel: ").lower()
        
        if user_decision == 'yes':
            delivery_time = input("Enter delivery window (e.g., 5pm - 7pm): ")
            
            # Update state with approval info
            app.update_state(config, {
                "user_approved": True, 
                "delivery_window": delivery_time
            })
            
            print("\n--- 🚀 Resuming Checkout ---")
            # Resume execution (pass None to continue from pause)
            async for event in app.astream(None, config):
                 if "checkout" in event:
                     print(event["checkout"]["messages"][-1].content)
        else:
            print("❌ Checkout cancelled.")
            
    await browser_tool.close()

if __name__ == "__main__":
    asyncio.run(main())