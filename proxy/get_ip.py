import requests
import time
import json

def get_ip():
    targetUrl = "http://api.shenlongip.com/ip?key=hab42km1&pattern=json&count=10&need=1100&protocol=2"
    response = requests.get(targetUrl)
    response_text = response.text
    response_json = json.loads(response_text)
    print(response) 
    print(response_json)

    ip_list = []
    for info in response_json['data']:
        ip = info['ip']
        port = info['port']
        ip_port = 'https://' + ip + ":" + str(port)
        print(ip_port)
        ip_list.append(ip_port)

    ip_file_path = 'ip_list.txt'
    with open(ip_file_path, 'w') as f:
        for ip in ip_list:
            f.write(ip + '\n')

if __name__ == '__main__':
    while True:
        get_ip()
        time.sleep(50*3)
