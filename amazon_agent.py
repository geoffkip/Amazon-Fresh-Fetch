import os
import asyncio
from dotenv import load_dotenv

# Load environment variables (API Key)
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
from playwright.async_api import async_playwright

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    meal_plan_text: str        # Stores the written plan
    shopping_list: List[str]   # Stores the extracted ingredients
    cart_items: List[str]      # Items successfully added
    missing_items: List[str]   # Items out of stock
    user_approved: bool
    delivery_window: str

# --- 2. The Browser Tool (Auto-Login & Robust Selectors) ---
class AmazonFreshBrowser:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.session_file = "amazon_session.json" # Stores cookies here

    async def start(self):
        print("🚀 Launching Browser...")
        self.playwright = await async_playwright().start()
        # Slow mo helps Amazon register clicks
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=1500)
        
        # 1. Try to load saved session
        if os.path.exists(self.session_file):
            print(f"🍪 Found saved session. Attempting auto-login...")
            self.context = await self.browser.new_context(
                storage_state=self.session_file,
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        else:
            print("🆕 No session found. Starting fresh.")
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

        self.page = await self.context.new_page()
        await self.page.goto("https://www.amazon.com/alm/storefront?almBrandId=QW1hem9uIEZyZXNo")
        
        # 2. Check if login is actually needed
        try:
            # Look for the "Sign in" text in the top nav bar
            needs_login = await self.page.locator("#nav-link-accountList-nav-line-1").filter(has_text="Sign in").count() > 0
        except:
            needs_login = True

        if needs_login:
            print("\n⚠️  ACTION REQUIRED: You are NOT logged in.")
            print("⚠️  Please Log In manually within 60 seconds.")
            print("⚠️  Ensure you select your FRESH ZIP CODE (top left).")
            await asyncio.sleep(60)
            
            # Save the session after the user logs in
            print("💾 Saving session for next time...")
            await self.context.storage_state(path=self.session_file)
        else:
            print("✅ Auto-login successful! Skipping manual wait.")

    async def search_and_add(self, item_name: str) -> str:
        """Robust search that tries 4 different ways to find the 'Add' button."""
        try:
            print(f"🛒 Searching for: {item_name}")
            search_box = self.page.locator('input[id="twotabsearchtextbox"]')
            await search_box.clear()
            await search_box.fill(item_name)
            await search_box.press('Enter')
            
            # Wait for results
            try:
                await self.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=5000)
            except:
                print("  - Standard search results not found...")

            # Get first result
            first_result = self.page.locator('div[data-component-type="s-search-result"]').first
            if await first_result.count() == 0:
                return "NOT_FOUND (No results)"

            # Multi-Strategy Button Finder
            # 1. By Accessibility Role (Best)
            btn = first_result.get_by_role("button", name="Add to cart")
            # 2. By generic "Add" text
            if await btn.count() == 0: btn = first_result.get_by_role("button", name="Add", exact=True)
            # 3. By CSS Name
            if await btn.count() == 0: btn = first_result.locator("button[name='submit.addToCart']")
            # 4. By Input Type
            if await btn.count() == 0: btn = first_result.locator("input[name='submit.addToCart']")

            if await btn.count() > 0 and await btn.first.is_visible():
                await btn.first.click()
                await asyncio.sleep(2) # Wait for cart animation
                return f"Successfully added {item_name} to cart."
            return "NOT_FOUND (Button missing/hidden)"

        except Exception as e:
            return f"Error searching for {item_name}: {e}"

    async def close(self):
        if self.context:
            await self.context.storage_state(path=self.session_file)
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()

browser_tool = AmazonFreshBrowser()

# --- 3. Nodes (The AI Logic) ---

async def planner_node(state: AgentState):
    """Generates the Meal Plan text first."""
    print("\n🧠 Thinking... Generating your Weekly Meal Plan...")
    
    # Using Flash for speed
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.4, google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    user_prompt = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a world-class nutritionist. Create a detailed weekly meal plan based exactly on the user's constraints."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": user_prompt})
    
    print("\n📝 PLAN GENERATED:")
    print("-" * 20)
    print(response.content)
    print("-" * 20)

    return {
        "meal_plan_text": response.content,
        "messages": [HumanMessage(content="Plan generated.")]
    }

async def extractor_node(state: AgentState):
    """Extracts ingredients from the PLAN."""
    print("\n📑 Extracting grocery list from plan...")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"))
    plan_text = state["meal_plan_text"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a shopping assistant. Read the meal plan. "
                   "Extract a consolidated comma-separated list of grocery ingredients. "
                   "Exclude pantry staples (salt, oil, water). "
                   "Example: 'chicken breast, spinach, greek yogurt'"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"input": plan_text})
    items = [item.strip() for item in response.content.split(',')]
    print(f"🛒 Extracted {len(items)} items to buy.")
    
    return {"shopping_list": items}

async def shopper_node(state: AgentState):
    """Executes shopping with substitutions."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=os.getenv("GOOGLE_API_KEY"))
    shopping_list = state["shopping_list"]
    cart, missing = [], []

    if not browser_tool.page: await browser_tool.start()

    for item in shopping_list:
        result = await browser_tool.search_and_add(item)
        
        if "NOT_FOUND" in result:
            print(f"⚠️ {item} missing. Asking Gemini for substitute...")
            sub_resp = await llm.ainvoke([HumanMessage(content=f"Item '{item}' unavailable. Name ONE generic substitute.")])
            sub_item = sub_resp.content.strip()
            
            print(f"🔄 Trying substitute: {sub_item}")
            retry = await browser_tool.search_and_add(sub_item)
            if "Successfully" in retry: cart.append(f"{sub_item} (Sub for {item})")
            else: missing.append(item)
        else:
            cart.append(item)
            
    return {"cart_items": cart, "missing_items": missing}

async def human_review_node(state: AgentState):
    print("\n--- 🛑 HUMAN REVIEW REQUIRED ---")
    print(f"Cart: {state['cart_items']}")
    print(f"Missing: {state['missing_items']}")
    return state

async def checkout_node(state: AgentState):
    if not state.get("user_approved"): return {"messages": [SystemMessage(content="Aborted.")]}
    window = state.get("delivery_window", "Not specified")
    return {"messages": [SystemMessage(content=f"Process Complete. Delivery: {window}")]}

# --- 4. Graph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("extractor", extractor_node)
workflow.add_node("shopper", shopper_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("checkout", checkout_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "extractor")
workflow.add_edge("extractor", "shopper")
workflow.add_edge("shopper", "human_review")
workflow.add_edge("human_review", "checkout")
workflow.add_edge("checkout", END)

app = workflow.compile(checkpointer=MemorySaver(), interrupt_before=["checkout"])

# --- 5. Execution ---
async def main():
    # The DEFAULT detailed prompt (Used if user presses Enter)
    default_prompt = """You are a meal planning expert. Help me build a weekly meal plan for dinner and lunch- I need healthy meals on the table in 30 minutes or less. I’d like it to be a full Monday-Friday meal plan with the links to the recipes and a grocery list included. I’m feeding 2 people, 2 adults. We don't eat pork. I’m accommodating no other allergens or restrictions and try to have a balanced diet focusing that incorporates a variety of whole grains. I'd like it to be heart healthy. I include protein and fresh produce at every meal. We enjoy global flavors like Mexican, Mediterranean, stir fries. I aim for 30 grams of protein at every meal. We usually cook 3 nights a week and use leftovers for lunch or other dinner. One or two lunches can be a sandwich/wrap or salad (something quick as for lunch I typically don't have time. For one meal a week it can be a bit of a longer cooking time. My preferred cooking styles are sheet pan or one saute pan, slow cooker and grilling. I own an Instant Pot and a rice cooker. We would prefer 1-2 vegetarian meals per week. We try to limit red meat to about 1-2 times a week. We eat all other animal products including beef, chicken, tilapia, salmon, cod, shrimp and lamb. Please have the plan include a variety of proteins - so one night chicken, one night beef. We want to include premium cuts while also incorporating budget-friendly staples and limiting specialty ingredients. My preferred grocery stores are amazon fresh, also, food lion, harris teeters and Wegmans. I'd also like you to include breakfast - we typically eat yogurt with whole grain toast or English muffins with peanut butter, jam, avocado and cheese. Some days we also make eggs and some days I sometimes make muffins. Feel free to suggest other healthy breakfast options. Avoiding sugar crashes is also important to me."""
    
    print("\n" + "="*60)
    print("🥕 AMAZON FRESH AI AGENT")
    print("="*60)
    print("Enter your meal request below.")
    print("OR press [ENTER] to use your default Weekly Plan settings.")
    print("-" * 60)
    
    user_input = input("> ")
    
    # Logic: If input is empty (Enter key), use default. Otherwise use input.
    if not user_input.strip():
        print("\nUsing DEFAULT Weekly Meal Plan settings...")
        final_prompt = default_prompt
    else:
        print("\nUsing CUSTOM user request...")
        final_prompt = user_input

    config = {"configurable": {"thread_id": "auto_login_run"}}
    
    # Start the Agent
    async for event in app.astream({"messages": [HumanMessage(content=final_prompt)]}, config): pass

    # Handle Pause
    state = app.get_state(config)
    if state.next and state.next[0] == 'checkout':
        decision = input("\nProceed to checkout? (yes/no): ").lower()
        if decision == 'yes':
            win = input("Delivery window: ")
            app.update_state(config, {"user_approved": True, "delivery_window": win})
            async for event in app.astream(None, config): pass

    await browser_tool.close()

if __name__ == "__main__":
    asyncio.run(main())