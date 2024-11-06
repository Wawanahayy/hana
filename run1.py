import asyncio
import json
import os
from colorama import init, Fore, Style
import httpx
import random
import time

# Fungsi untuk mengirim permintaan HTTP
async def send_request(url, method, data=None):
    try:
        if method == 'POST':
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                return response.json()
        # Anda bisa menambahkan metode lain jika diperlukan
    except Exception as e:
        print(f"{Fore.RED}Request error: {e}{Style.RESET_ALL}")
        return None

# Fungsi untuk me-refresh token
async def refresh_access_token(refresh_token):
    # Implementasi untuk me-refresh token
    return "new_access_token"  # Gantilah dengan logika yang sesuai

# Fungsi untuk menunggu dengan loading (contoh placeholder)
async def loading_with_time():
    while True:
        print(f"{Fore.YELLOW}Loading...{Style.RESET_ALL}")
        await asyncio.sleep(10)

# Fungsi utama untuk menangani grow dan garden
async def handle_grow_and_garden(refresh_token):
    new_access_token = await refresh_access_token(refresh_token)
    if not new_access_token:
        print(f"{Fore.RED}Skipping token due to refresh failure.{Style.RESET_ALL}")
        return

    headers = {'authorization': f'Bearer {new_access_token}'}
    api_url = "https://api.example.com"  # Ganti dengan URL API yang sesuai
    
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
                
                # Skip jika data kosong atau None
                if not mine or not mine.get('data') or mine['data'].get('issueGrowAction') is None:
                    print(f"{Fore.RED}Skipping grow action due to missing data.{Style.RESET_ALL}")
                    await asyncio.sleep(random.randint(1, 3))  # Tunggu 1-3 detik sebelum melanjutkan
                    continue
                
                reward = mine['data']['issueGrowAction']
                balance += reward
                grow -= 1
                print(f"{Fore.GREEN}Rewards: {reward} | Balance: {balance} | Grow left: {grow}{Style.RESET_ALL}")
                await send_request(api_url, 'POST', {"query": "mutation commitGrowAction { commitGrowAction }", "operationName": "commitGrowAction"})

            while garden >= 10:
                garden_action_query = {
                    "query": "mutation executeGardenRewardAction($limit: Int!) { executeGardenRewardAction(limit: $limit) { data { cardId group } isNew } }",
                    "variables": {"limit": 10},
                    "operationName": "executeGardenRewardAction"
                }
                mine_garden = await send_request(api_url, 'POST', garden_action_query)
                
                # Skip jika data kosong atau None
                if not mine_garden or not mine_garden.get('data') or mine_garden['data'].get('executeGardenRewardAction') is None:
                    print(f"{Fore.RED}Skipping garden reward action due to missing data.{Style.RESET_ALL}")
                    await asyncio.sleep(random.randint(1, 3))  # Tunggu 1-3 detik sebelum melanjutkan
                    continue
                
                card_ids = [item['cardId'] for item in mine_garden['data']['executeGardenRewardAction']]
                print(f"{Fore.GREEN}Opened Garden: {card_ids}{Style.RESET_ALL}")
                garden -= 10
    finally:
        loading_task.cancel()

# Menjalankan proses utama
async def main():
    refresh_token = "your_refresh_token_here"  # Ganti dengan token refresh yang valid
    await handle_grow_and_garden(refresh_token)

# Menjalankan event loop
if __name__ == "__main__":
    asyncio.run(main())
