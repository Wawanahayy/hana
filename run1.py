import asyncio
import json
import os
from colorama import init, Fore, Style
import httpx
import random
import time

init(autoreset=True)

# Display the JawaPride logo
os.system("curl -s https://raw.githubusercontent.com/Wawanahayy/JawaPride-all.sh/refs/heads/main/display.sh | bash")

api_url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"

# Load access tokens
with open("token.txt", "r") as file:
    access_tokens = [line.strip() for line in file if line.strip()]

# Load loading messages from file
with open("loading_messages.txt", "r") as file:
    loading_messages = [line.strip() for line in file if line.strip()]

headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}

async def send_request(url, method, payload_data=None, retries=3):
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(retries):
            try:
                response = await client.request(method, url, headers=headers, json=payload_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"{Fore.RED}HTTP error! Status: {e.response.status_code}. Retrying...{Style.RESET_ALL}")
                await asyncio.sleep(2)
            except httpx.RequestError as e:
                print(f"{Fore.RED}Request error: {e}. Retrying...{Style.RESET_ALL}")
                await asyncio.sleep(2)
        return None

async def refresh_access_token(refresh_token):
    api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
    data = f'grant_type=refresh_token&refresh_token={refresh_token}'
    response = await send_request(
        f'https://securetoken.googleapis.com/v1/token?key={api_key}', 'POST', data
    )
    return response.get('access_token') if response else None

async def loading_with_time():
    duration = 0
    colors = [Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.GREEN, Fore.RED]
    current_message = random.choice(loading_messages)

    while True:
        time_formatted = time.strftime("%H:%M:%S", time.gmtime(duration))
        color = random.choice(colors)
        print(f"{color}{current_message} {time_formatted}{Style.RESET_ALL}", end='\r')
        await asyncio.sleep(1)
        duration += 1

async def handle_grow_and_garden(refresh_token):
    new_access_token = await refresh_access_token(refresh_token)
    if not new_access_token:
        print(f"{Fore.RED}Skipping token due to refresh failure.{Style.RESET_ALL}")
        return

    headers['authorization'] = f'Bearer {new_access_token}'
    info_query = {
        "query": "query CurrentUser { currentUser { id sub name iconPath depositCount totalPoint evmAddress { userId address } inviter { id name } } }",
        "operationName": "CurrentUser"
    }

    loading_task = asyncio.create_task(loading_with_time())
    try:
        info = await send_request(api_url, 'POST', info_query)
        if info and info.get('data', {}).get('currentUser'):
            balance = info['data']['currentUser']['totalPoint']
            deposit = info['data']['currentUser']['depositCount']
            print(f"{Fore.GREEN}POINTS: {balance} | Deposit Counts: {deposit}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Failed to retrieve user info.{Style.RESET_ALL}")
            return

        bet_query = {
            "query": "query GetGardenForCurrentUser { getGardenForCurrentUser { id inviteCode gardenDepositCount gardenStatus { id activeEpoch growActionCount gardenRewardActionCount } gardenMilestoneRewardInfo { id gardenDepositCountWhenLastCalculated lastAcquiredAt createdAt } gardenMembers { id sub name iconPath depositCount } } }",
            "operationName": "GetGardenForCurrentUser"
        }

        profile = await send_request(api_url, 'POST', bet_query)
        if profile and profile.get('data', {}).get('getGardenForCurrentUser'):
            grow = profile['data']['getGardenForCurrentUser']['gardenStatus']['growActionCount']
            garden = profile['data']['getGardenForCurrentUser']['gardenStatus']['gardenRewardActionCount']

            if grow == 0:
                wait_time = 3600 + random.randint(60, 1200)
                print(f"{Fore.YELLOW}No grow actions left. Waiting for {wait_time // 3600} hours, {(wait_time % 3600) // 60} minutes, and {wait_time % 60} seconds...{Style.RESET_ALL}")
                await asyncio.sleep(wait_time)
                return

            while grow > 0:
                action_query = {
                    "query": "mutation issueGrowAction { issueGrowAction }",
                    "operationName": "issueGrowAction"
                }
                mine = await send_request(api_url, 'POST', action_query)
                if mine and mine.get('data') and mine['data'].get('issueGrowAction'):
                    reward = mine['data']['issueGrowAction']
                    balance += reward
                    grow -= 1
                    print(f"{Fore.GREEN}Rewards: {reward} | Balance: {balance} | Grow left: {grow}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to issue grow action or missing data.{Style.RESET_ALL}")
                    break

                await send_request(api_url, 'POST', {"query": "mutation commitGrowAction { commitGrowAction }", "operationName": "commitGrowAction"})

            while garden >= 10:
                garden_action_query = {
                    "query": "mutation executeGardenRewardAction($limit: Int!) { executeGardenRewardAction(limit: $limit) { data { cardId group } isNew } }",
                    "variables": {"limit": 10},
                    "operationName": "executeGardenRewardAction"
                }
                mine_garden = await send_request(api_url, 'POST', garden_action_query)
                if mine_garden and mine_garden.get('data') and mine_garden['data'].get('executeGardenRewardAction'):
                    card_ids = [item['cardId'] for item in mine_garden['data']['executeGardenRewardAction']]
                    print(f"{Fore.GREEN}Opened Garden: {card_ids}{Style.RESET_ALL}")
                    garden -= 10
                else:
                    print(f"{Fore.RED}Failed to execute garden reward action or missing data.{Style.RESET_ALL}")
                    break
    finally:
        loading_task.cancel()

async def main():
    while True:
        for refresh_token in access_tokens:
            await handle_grow_and_garden(refresh_token)
        print(f"{Fore.RED}All accounts processed. Cooling down...{Style.RESET_ALL}")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
