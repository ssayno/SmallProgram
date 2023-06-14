import requests
import asyncio


url = 'https://www.douyin.com/user/MS4wLjABAAAAcr8P4n7JPrKRe73LW-7PbLq-rVWw-I0sCccdUcJI5Fo?vid=7211344214016134440'
resp = requests.get(url)
print(resp.status_code)

def a_():
    print("a")

async def b_():
    print("b")


print(asyncio.iscoroutinefunction(a_))
print(asyncio.iscoroutinefunction(b_))

