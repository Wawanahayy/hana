import asyncio
import aiohttp
import os
from timer import countdown_timer
from banner import display_colored_text, color_codes

countdown_timer(3)

def _clear():
    """Function to clear the terminal screen (for Linux/macOS)."""
    os.system("clear")

def _banner():
    """Display the application banner."""
    display_colored_text()  # Displaying the banner with colored and blinking text
    print(f"{color_codes['green']}Welcome to JAWA PRIDE AIRDROP SCRIPT")
    print(f"{color_codes['yellow']}Don't Forget To join channel ✅ https://t.me/AirdropJP_JawaPride")
    print(f"{color_codes['blue']}Follow twitter @JAWAPRIDE_ID ✅ https://x.com/JAWAPRIDE_ID")
    print(f"{color_codes['red']}More details https://linktr.ee/Jawa_Pride_ID")
    print(f"{color_codes['magenta']}⭐️ THANK YOU ⭐️")
    print("~" * 65)

class Grows:
    def __init__(self, token_file):
        self.cfg = self.read_config()
        with open(token_file, "r") as file:
            self.tokens = [line.strip() for line in file if line.strip()]
        self.api_url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"
        self.delay = self.cfg.get('account_delay', 5)
        self.countdown_before_start = self.cfg.get('countdown_before_start', 5)
        self.cooldown = self.cfg.get('countdown_loop', 3600)
        self.api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
        self.headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0"
        }

    def read_config(self):
        """Function to read the configuration."""
        return {
            'account_delay': 5,
            'countdown_before_start': 5,
            'countdown_loop': 900,
        }

    async def countdown_timer(self, seconds):
        """Countdown timer with dynamic output."""
        while seconds > 0:
            hours, minutes = divmod(seconds // 60, 60)
            seconds_remaining = seconds % 60
            print(f"{color_codes['yellow']}Cooldown Timer: {hours:02}:{minutes:02}:{seconds_remaining:02}", end="\r")
            await asyncio.sleep(1)
            seconds -= 1
        print("\n")  # Clear the line after countdown finishes

    async def req_with_retry(self, session, url, method, payload=None, retries=3):
        """Handle API requests with retry mechanism."""
        for attempt in range(retries):
            try:
                async with session.request(method, url, headers=self.headers, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP Error: {response.status}")
                    return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    print(f"{color_codes['yellow']}Retrying... (Attempt {attempt + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"{color_codes['red']}Failed after {retries} attempts: {e}")
                    raise

    async def refresh_token(self, session, token):
        """Refresh and set authorization token once per session."""
        url = f'https://securetoken.googleapis.com/v1/token?key={self.api_key}'
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = f'grant_type=refresh_token&refresh_token={token}'
        async with session.post(url, headers=headers, data=payload) as response:
            if response.status != 200:
                raise Exception(f"{color_codes['red']}Failed to refresh token")
            data = await response.json()
            return data.get('access_token')

    async def grow(self, session):
        """Perform the grow action and return reward."""
        query = {
            "query": """
                mutation executeGrowAction {
                    executeGrowAction(withAll: true) {
                        totalValue
                        multiplyRate
                    }
                    executeSnsShare(actionType: GROW, snsType: X) {
                        bonus
                    }
                }
            """,
            "operationName": "executeGrowAction"
        }
        res = await self.req_with_retry(session, self.api_url, 'POST', query)
        if res and 'data' in res and 'executeGrowAction' in res['data']:
            return res['data']['executeGrowAction']['totalValue']
        else:
            print(f"{color_codes['red']}Error: Unexpected response: {res}")
            return 0

    async def process_account(self, session, token):
        """Process grow action and handle rewards."""
        try:
            auth_token = await self.refresh_token(session, token)
            self.headers['authorization'] = f'Bearer {auth_token}'

            query = {
                "query": "query getCurrentUser { "
                         "currentUser { id totalPoint depositCount } "
                         "getGardenForCurrentUser { "
                         "gardenStatus { growActionCount gardenRewardActionCount } "
                         "} "
                         "} ",
                "operationName": "getCurrentUser"
            }
            info = await self.req_with_retry(session, self.api_url, 'POST', query)
            balance = info['data']['currentUser']['totalPoint']
            grow = info['data']['getGardenForCurrentUser']['gardenStatus']['growActionCount']
            garden = info['data']['getGardenForCurrentUser']['gardenStatus']['gardenRewardActionCount']

            print(f"{color_codes['cyan']}Grow: {grow} | Garden: {garden} | Balance: {balance}")

            if grow > 0:
                reward = await self.grow(session)
                if reward:
                    balance += reward
                    print(f"{color_codes['green']}Grow actions: {reward} | Balance: {balance}")
                else:
                    print(f"{color_codes['red']}Grow: zero/enough | Garden: {garden} | Balance: {balance}")
            else:
                print(f"{color_codes['red']}Grow: zero/enough | Garden: {garden} | Balance: {balance}")

        except Exception as e:
            print(f"{color_codes['red']}Error processing account: {e}")

async def main(self):
    print(f"{color_codes['blue']}Waiting for {self.countdown_before_start} seconds before start!")
    print("~" * 65)

    # Countdown timer before the main loop starts
    await asyncio.sleep(self.countdown_before_start)

    while True:  # Keeps running without recursive calls
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_account(session, token) for token in self.tokens]
            await asyncio.gather(*tasks)

        # Log cooldown time
        cooldown_hours, cooldown_minutes = divmod(self.cooldown // 60, 60)
        cooldown_str = f"{cooldown_hours} hours {cooldown_minutes} minutes" if cooldown_hours > 0 else f"{cooldown_minutes} minutes"
        print(f"{color_codes['green']}Cooldown time: {cooldown_str} / {self.cooldown} seconds!")

        # Countdown for cooldown period
        await self.countdown_timer(self.cooldown)

        # Restart the loop instead of recursive calls
        print(f"{color_codes['yellow']}Restarting tasks...")


if __name__ == "__main__":
    # Initial Banner Display
    _clear()
    _banner()

    token_file = 'token.txt'
    grows = Grows(token_file)
    asyncio.run(grows.main())
