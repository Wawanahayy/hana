import asyncio
import json
import os
from colorama import init, Fore, Style
import httpx
import random
import time

init(autoreset=True)

os.system("curl -s https://raw.githubusercontent.com/Wawanahayy/JawaPride-all.sh/refs/heads/main/display.sh | bash")

api_url = "https://hanafuda-backend-app-520478841386.us-central1.run.app/graphql"

with open("token.txt", "r") as file:
    access_tokens = [line.strip() for line in file if line.strip()]

with open("loading_messages.txt", "r") as file:
    loading_messages = [line.strip() for line in file if line.strip()]

headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}

async def colay(url, method, payload_data=None):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.request(method, url, headers=headers, json=payload_data)
            if response.status_code != 200:
                raise Exception(f'HTTP error! Status: {response.status_code}')
            return response.json()
        except httpx.ReadTimeout:
            print(f"{Fore.RED}Request timed out. Retrying...{Style.RESET_ALL}")
            return await colay(url, method, payload_data)

async def refresh_access_token(refresh_token):
    api_key = "AIzaSyDipzN0VRfTPnMGhQ5PSzO27Cxm3DohJGY"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'https://securetoken.googleapis.com/v1/token?key={api_key}',
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f'grant_type=refresh_token&refresh_token={refresh_token}'
        )
        if response.status_code != 200:
            raise Exception("Failed to refresh access token")
        return response.json().get('access_token')

async def loading_with_time():
    duration = 0
    colors = [Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.GREEN, Fore.RED]
    current_message = random.choice(loading_messages)

    while True:
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        time_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
        color = random.choice(colors)
        print(f"{color}{current_message} {time_formatted}{Style.RESET_ALL}", end='\r')
        await asyncio.sleep(0.02)
        duration += 1

    return current_message

async def handle_grow_and_garden(refresh_token):
    new_access_token = await refresh_access_token(refresh_token)
    headers['authorization'] = f'Bearer {new_access_token}'

    info_query = {
        "query": "query CurrentUser { currentUser { id sub name iconPath depositCount totalPoint evmAddress { userId address } inviter { id name } } }",
        "operationName": "CurrentUser"
    }
    
    loading_task = asyncio.create_task(loading_with_time())
    try:
        info = await colay(api_url, 'POST', info_query)

        if 'data' in info and 'currentUser' in info['data']:
            balance = info['data']['currentUser']['totalPoint']
            deposit = info['data']['currentUser']['depositCount']
            print(f"{Fore.GREEN}POINTS: {balance} | Deposit Counts: {deposit}{Style.RESET_ALL}")

        bet_query = {
            "query": "query GetGardenForCurrentUser { getGardenForCurrentUser { id inviteCode gardenDepositCount gardenStatus { id activeEpoch growActionCount gardenRewardActionCount } gardenMilestoneRewardInfo { id gardenDepositCountWhenLastCalculated lastAcquiredAt createdAt } gardenMembers { id sub name iconPath depositCount } } }",
            "operationName": "GetGardenForCurrentUser"
        }
        
        profile = await colay(api_url, 'POST', bet_query)

        if 'data' in profile and 'getGardenForCurrentUser' in profile['data']:
            grow = profile['data']['getGardenForCurrentUser']['gardenStatus']['growActionCount']
            garden = profile['data']['getGardenForCurrentUser']['gardenStatus']['gardenRewardActionCount']

            if grow == 0:
                wait_time = 3600 + random.randint(60, 1200)
                end_time = time.time() + wait_time
                print(f"{Fore.YELLOW}No grow actions left. Waiting for {wait_time // 3600} hours, {(wait_time % 3600) // 60} minutes, and {wait_time % 60} seconds...{Style.RESET_ALL}")

                while time.time() < end_time:
                    remaining_time = end_time - time.time()
                    hours = remaining_time // 3600
                    minutes = (remaining_time % 3600) // 60
                    seconds = remaining_time % 60
                    print(f"\r{Fore.YELLOW}Remaining time: {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds...", end='') 
                    await asyncio.sleep(1)

                print(f"{Fore.YELLOW}\nWait time is over. Proceeding to the next token.{Style.RESET_ALL}")
                return

            while grow > 0:
                action_query = {
                    "query": "mutation issueGrowAction { issueGrowAction }",
                    "operationName": "issueGrowAction"
                }
                mine = await colay(api_url, 'POST', action_query)
                
                if mine and 'data' in mine and 'issueGrowAction' in mine['data']:
                    reward = mine['data']['issueGrowAction']
                    balance += reward
                    grow -= 1
                    print(f"{Fore.GREEN}Rewards: {reward} | Balance: {balance} | Grow left: {grow}{Style.RESET_ALL}")

                commit_query = {
                    "query": "mutation commitGrowAction { commitGrowAction }",
                    "operationName": "commitGrowAction"
                }
                await colay(api_url, 'POST', commit_query)

            while garden >= 10:
                garden_action_query = {
                    "query": "mutation executeGardenRewardAction($limit: Int!) { executeGardenRewardAction(limit: $limit) { data { cardId group } isNew } }",
                    "variables": {"limit": 10},
                    "operationName": "executeGardenRewardAction"
                }
                mine_garden = await colay(api_url, 'POST', garden_action_query)
                
                if mine_garden and 'data' in mine_garden and 'executeGardenRewardAction' in mine_garden['data']:
                    card_ids = [item['cardId'] for item in mine_garden['data']['executeGardenRewardAction']['data']]
                    print(f"{Fore.GREEN}Opened Garden: {card_ids}{Style.RESET_ALL}")
                garden -= 10

    finally:
        loading_task.cancel()

async def main():
    while True:
        for refresh_token in access_tokens:
            await handle_grow_and_garden(refresh_token)
        print(f"{Fore.RED}All accounts have been processed. Cooling down...{Style.RESET_ALL}")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
