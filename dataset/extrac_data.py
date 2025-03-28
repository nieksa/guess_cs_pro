import json
import requests

def request(payload, target_api, headers):
    try:
        response = requests.post(target_api, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

pro_info_json_file = r'C:\Users\lixuy\Desktop\csguess\pro_info.json'
target_api = 'https://api.blast.tv/v1/counterstrikle/guesses'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.7',
    'content-length': '51',
    'content-type': 'application/json',
    'origin': 'https://blast.tv',
    'priority': 'u=1, i',
    'referer': 'https://blast.tv/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}

# Load the existing data
with open(r'C:\Users\lixuy\Desktop\csguess\pro_namelist.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

ids = [entry['id'] for entry in data]

# Read existing pro_info.json to append data
try:
    with open(pro_info_json_file, 'r', encoding='utf-8') as file:
        pro_info = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    # If the file doesn't exist or is empty, initialize it as an empty list
    pro_info = []

# Iterate through the ids and fetch data from the API
for id in ids:
    payload = {'playerId': id}
    info = request(payload, target_api, headers)
    if info:
        print(info)
        # Append the fetched info to the list
        pro_info.append(info)

# Write the updated pro_info back to the JSON file
with open(pro_info_json_file, 'w', encoding='utf-8') as file:
    json.dump(pro_info, file, ensure_ascii=False, indent=4)

print(f"数据已成功更新到 {pro_info_json_file}")
