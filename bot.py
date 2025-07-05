import os
import random
import time
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from colorama import init, Fore, Style
import inquirer
from pathlib import Path

# Initialize colorama for colored output
init()

# Colors and Logger
class Colors:
    RESET = Style.RESET_ALL
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    WHITE = Fore.WHITE
    BOLD = Style.BRIGHT
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA

class Logger:
    @staticmethod
    def info(msg):
        print(f"{Colors.GREEN}[✓] {msg}{Colors.RESET}")

    @staticmethod
    def warn(msg):
        print(f"{Colors.YELLOW}[⚠] {msg}{Colors.RESET}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[✗] {msg}{Colors.RESET}")

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[✅] {msg}{Colors.RESET}")

    @staticmethod
    def loading(msg):
        print(f"{Colors.CYAN}[⟳] {msg}{Colors.RESET}")

    @staticmethod
    def step(msg):
        print(f"{Colors.WHITE}[➤] {msg}{Colors.RESET}")

    @staticmethod
    def banner():
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("-----------------------------------------------")
        print("  Snoonaut Auto Bot - ADB PYTHON  ")
        print("-----------------------------------------------")
        print(f"{Colors.RESET}\n")

# Random User-Agent
def random_ua():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]
    return random.choice(uas)

# Proxy Agent
def get_proxy():
    if Path("proxies.txt").exists():
        with open("proxies.txt", "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if proxies:
            proxy = random.choice(proxies)
            if not proxy.startswith(("http", "socks")):
                proxy = f"http://{proxy}"
            return {"http": proxy, "https": proxy}
    return None

# Load Cookies
def load_cookies():
    load_dotenv()
    cookies = []
    for key in os.environ:
        if key.startswith("COOKIE_") and "_vcrcs" not in key and "_csrf" not in key and "_session" not in key:
            cookie_parts = []
            for sub_key in os.environ:
                if sub_key.startswith(f"{key}_") or sub_key == key:
                    cookie_parts.append(os.environ[sub_key])
            cookies.append("; ".join(cookie_parts))
    print("Loaded cookies:", cookies)  # Debugging
    return cookies

# Create Requests Session
def create_session(cookie):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": cookie,
        "Referer": "https://earn.snoonaut.xyz/home",
        "User-Agent": random_ua(),
    })
    return session

# Daily Check-in Function
def perform_daily_check_in(session, cookie):
    Logger.loading("Performing daily check-in...")
    time.sleep(1)  # Delay to avoid bot detection
    try:
        proxies = get_proxy()
        response = session.post(
            "https://earn.snoonaut.xyz/api/checkin",
            json={},
            headers={"User-Agent": random_ua(), "content-type": "application/json"},
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            Logger.success(f"Daily check-in completed. Reward: {data.get('reward', 'N/A')}")
        else:
            Logger.warn("Daily check-in already completed or not available")
    except requests.exceptions.RequestException as e:
        Logger.error(f"Failed to perform daily check-in: {e}")
        if hasattr(e.response, "status_code") and e.response.status_code == 401:
            Logger.error("Cookie may have expired. Please update the cookie in .env")
        elif hasattr(e.response, "status_code") and e.response.status_code == 403:
            Logger.error("Request blocked by Vercel WAF. Check headers or cookies.")

# Fetch User Info
def fetch_user_info(session):
    Logger.loading("Fetching user info...")
    time.sleep(1)
    try:
        proxies = get_proxy()
        response = session.get(
            "https://earn.snoonaut.xyz/api/user/stats",
            headers={"User-Agent": random_ua()},
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        Logger.success("User info fetched successfully")
        Logger.info(f"Username: {data['user']['username']}, Snoot Balance: {data['user']['snootBalance']}")
        return data
    except requests.exceptions.RequestException as e:
        Logger.error(f"Failed to fetch user info: {e}")
        return None

# Fetch Tasks
def fetch_tasks(session, task_type):
    Logger.loading(f"Fetching {task_type} tasks...")
    time.sleep(1)
    try:
        proxies = get_proxy()
        response = session.get(
            f"https://earn.snoonaut.xyz/api/tasks?type={task_type}",
            headers={"User-Agent": random_ua()},
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        Logger.success(f"{task_type} tasks fetched successfully")
        return data.get("tasks", [])
    except requests.exceptions.RequestException as e:
        Logger.error(f"Failed to fetch {task_type} tasks: {e}")
        return []

# Generate Proof URL
def generate_proof_url():
    usernames = ["altcoinbear1", "cryptofan", "snootlover", "airdropking", "blockchainbro"]
    random_status_id = random.randint(1000000000000000000, 1900000000000000000)
    random_username = random.choice(usernames)
    return f"https://x.com/{random_username}/status/{random_status_id}"

# Complete Task
def complete_task(session, task):
    Logger.loading(f"Completing task {task['title']} ({task['id']})...")
    time.sleep(1)
    try:
        payload = {"taskId": task["id"], "action": "complete"}
        if task["title"] in ["Spread the Snoot!", "Like, Retweet and Comment"]:
            payload["proofUrl"] = generate_proof_url()
        
        proxies = get_proxy()
        response = session.post(
            "https://earn.snoonaut.xyz/api/tasks/complete",
            json=payload,
            headers={"User-Agent": random_ua(), "content-type": "application/json"},
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            Logger.success(f"Task {task['title']} completed, Reward: {data.get('reward')}")
    except requests.exceptions.RequestException as e:
        Logger.error(f"Failed to complete task {task['title']} ({task['id']}): {e}")

# Process Account
def process_account(cookie, mode):
    Logger.step(f"Processing account with cookie: {cookie[:50]}...")
    session = create_session(cookie)
    
    # Fetch user info
    user_info = fetch_user_info(session)
    if not user_info:
        return
    
    if mode == "daily":
        perform_daily_check_in(session, cookie)
    elif mode == "tasks":
        engagement_tasks = fetch_tasks(session, "engagement")
        referral_tasks = fetch_tasks(session, "referral")
        all_tasks = engagement_tasks + referral_tasks
        pending_tasks = [task for task in all_tasks if task.get("status") == "pending"]
        
        for task in pending_tasks:
            complete_task(session, task)
    
    Logger.success("Account processing completed")

# Prompt User for Mode
def prompt_user():
    questions = [
        {
            "type": "list",
            "name": "mode",
            "message": "What would you like to do?",
            "choices": [
                {"name": "Perform Daily Check-in", "value": "daily"},
                {"name": "Complete Tasks", "value": "tasks"},
            ]
        },
        {
            "type": "confirm",
            "name": "run_daily_with_timer",
            "message": "Would you like to schedule Daily Check-in to run every 24 hours?",
            "when": lambda answers: answers["mode"] == "daily",
            "default": False
        }
    ]
    return inquirer.prompt(questions)

# Main Function
def main():
    Logger.banner()
    
    cookies = load_cookies()
    if not cookies:
        Logger.error("No cookies found in .env")
        return
    
    answers = prompt_user()
    mode = answers["mode"]
    run_daily_with_timer = answers.get("run_daily_with_timer", False)
    
    # Run immediately
    for cookie in cookies:
        process_account(cookie, mode)
    
    # Set up timer for daily check-in if selected
    if mode == "daily" and run_daily_with_timer:
        DAILY_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
        Logger.info("Daily check-in scheduled to run every 24 hours.")
        while True:
            Logger.banner()
            Logger.info("Running scheduled daily check-in...")
            for cookie in cookies:
                process_account(cookie, "daily")
            time.sleep(DAILY_INTERVAL)
    
 /

   Logger.success("All accounts processed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        Logger.error(f"Main process failed: {e}")
