import asyncio
import aiohttp
import os
from timer import countdown_timer
from banner import display_colored_text, color_codes

countdown_timer(3)

def _clear():
    os.system("clear")

def _banner():
    display_colored_text()
    print(f"{color_codes['green']}Welcome to JAWA PRIDE AIRDROP SCRIPT")
    print(f"{color_codes['yellow']}Join channel ✅ https://t.me/AirdropJP_JawaPride")
    print(f"{color_codes['blue']}Follow Twitter @JAWAPRIDE_ID ✅ https://x.com/JAWAPRIDE_ID")
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
        self.cooldown = self.cfg.get('countdown_loop', 3600)
        self.api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
        self.headers = {'Accept': '*/*', 'Content-Type': 'application/json', 'User-Agent': "Mozilla/5.0"}

    def read_config(self):
        return {'account_delay': 5, 'countdown_loop': 900}

    async def countdown_timer(self, seconds):
        while seconds > 0:
            hours, minutes = divmod(seconds // 60, 60)
            seconds_remaining = seconds % 60
            print(f"{color_codes['yellow']}Cooldown Timer: {hours:02}:{minutes:02}:{seconds_remaining:02}", end="\r")
            await asyncio.sleep(1)
            seconds -= 1
        print("\n")

    async def req_with_retry(self, session, url, method, payload=None, retries=3):
        for attempt in range(retries):
            try:
                async with session.request(method, url, headers=self.headers, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP Error: {response.status}")
                    return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    print(f"{color_codes['yellow']}Retrying... (Attempt {attempt + 1})")
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"{color_codes['red']}Failed after {retries} attempts: {e}")
                    raise

    async def process_account(self, session, token):
        try:
            query = {"query": "query getCurrentUser { currentUser { id totalPoint depositCount }}"}
            info = await self.req_with_retry(session, self.api_url, 'POST', query)
            balance = info['data']['currentUser']['totalPoint']
            print(f"{color_codes['cyan']}Balance: {balance}")
        except Exception as e:
            print(f"{color_codes['red']}Error processing account: {e}")

    async def main(self):
        while True:
            async with aiohttp.ClientSession() as session:
                tasks = [self.process_account(session, token) for token in self.tokens]
                await asyncio.gather(*tasks)

            cooldown_hours, cooldown_minutes = divmod(self.cooldown // 60, 60)
            cooldown_str = f"{cooldown_hours}h {cooldown_minutes}m" if cooldown_hours > 0 else f"{cooldown_minutes} minutes"
            print(f"{color_codes['green']}Cooldown: {cooldown_str} ({self.cooldown} sec)")
            await self.countdown_timer(self.cooldown)

if __name__ == "__main__":
    _clear()
    _banner()
    token_file = 'token.txt'
    grows = Grows(token_file)
    asyncio.run(grows.main())
