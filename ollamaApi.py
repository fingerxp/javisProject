import requests
import json
url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3",
    "prompt": "나는 형석이야. 너는 이름이 모니?"
}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print('Success')
    json_objects = response.content.decode().strip().split("\n")
    data = [json.loads(obj) for obj in json_objects]
    res_text = ''
    # 변환된 데이터 출력
    for item in data:
        print(item)
        res_text += item['response']
    print(res_text)
else:
    print("Error:", response.status_code, response.text)
