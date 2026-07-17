"""Quick follow script using the same auth as the x-automation server."""
import asyncio, os, json, sys
from dotenv import load_dotenv
from curl_cffi.requests import AsyncSession

load_dotenv()

AUTH_TOKEN = os.environ["X_AUTH_TOKEN"]
CT0 = os.environ["X_CT0"]
BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
CLIENT_UUID = "nasty-follow-script"

def build_headers(method="POST", path=""):
    return {
        "authorization": f"Bearer {BEARER}",
        "cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}",
        "x-csrf-token": CT0,
        "content-type": "application/json",
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
        "x-client-uuid": CLIENT_UUID,
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://x.com",
        "referer": "https://x.com/home",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

async def get_user_id(session, screen_name):
    """Look up a screen name to get the user_id (rest_id)."""
    # Use the old REST API for user lookup (doesn't require auth)
    url = f"https://x.com/i/api/graphql/nOZBu2hMV8seLY2iFQXPhQ/UserByScreenName"
    params = {"variables": json.dumps({"screen_name": screen_name, "withSafetyModeUserFields": True})}
    headers = build_headers("GET", f"/i/api/graphql/nOZBu2hMV8seLY2iFQXPhQ/UserByScreenName")
    
    resp = await session.get(url, headers=headers, params=params, timeout=15)
    data = resp.json()
    
    try:
        result = data["data"]["user"]["result"]
        if result.get("__typename") == "User":
            user_id = result["rest_id"]
            name = result["legacy"]["name"]
            followers = result["legacy"].get("followers_count", 0)
            return user_id, name, followers
        else:
            return None, f"suspended/deactivated: {screen_name}", 0
    except (KeyError, TypeError) as e:
        return None, f"not found: {str(e)[:80]}", 0

async def follow_user(session, user_id, screen_name):
    """Follow a user by their rest_id."""
    url = "https://x.com/i/api/1.1/friendships/create.json"
    headers = build_headers("POST", "/i/api/1.1/friendships/create.json")
    data = {
        "include_profile_interstitial_type": 1,
        "skip_status": True,
        "user_id": user_id,
    }
    
    resp = await session.post(url, headers=headers, data=data, timeout=15)
    result = resp.json()
    
    if resp.status_code == 200 or result.get("following") == True:
        return True, "followed"
    elif resp.status_code == 403:
        return False, f"blocked/forbidden: {result}"
    elif resp.status_code == 429:
        return False, "rate limited"
    else:
        return False, f"error {resp.status_code}: {str(result)[:100]}"

async def main(screen_names):
    async with AsyncSession(impersonate="chrome136") as session:
        for sn in screen_names:
            sn = sn.strip()
            if not sn:
                continue
            
            # Look up user ID
            user_id, name, followers = await get_user_id(session, sn)
            
            if user_id is None:
                print(f"❌ @{sn} — {name}")
                continue
            
            print(f"🔍 @{sn} → {name} ({followers:,} followers)...", end=" ")
            
            # Follow
            success, msg = await follow_user(session, user_id, sn)
            
            if success:
                print(f"✅ {msg}")
            else:
                print(f"❌ {msg}")
            
            # Small delay to avoid rate limits
            await asyncio.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python follow_accounts.py @account1 @account2 ...")
        sys.exit(1)
    asyncio.run(main(sys.argv[1:]))
