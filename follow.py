"""Follow Twitter accounts using the x-automation auth."""
import asyncio, json, os
from dotenv import load_dotenv
from curl_cffi.requests import AsyncSession

load_dotenv()

AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
CT0 = os.environ.get("X_CT0", "")
BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
CLIENT_UUID = "nasty-follow-01"

def h(method="POST", path=""):
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

USER_BY_SCREEN = "IGgvgiOx4QZndDHuD3x9TQ"
ACCOUNTS = [
    # From the list Ronny asked to follow
    "Brazzers", "Pornhub", "Mi
