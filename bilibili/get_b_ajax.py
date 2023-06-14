import requests
url = 'https://api.geetest.com/gettype.php'
resp = requests.get(url)
print(resp.headers)
print(resp.text)