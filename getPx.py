import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
def fetch_proxy_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_proxies(html):
    soup = BeautifulSoup(html, 'html.parser')
    proxies = []

    # 找到所有的行
    rows = soup.select('#ipc tbody tr')
    for row in rows:
        # 提取 IP 地址和端口
        ip = row.find_all('td')[0].text.strip()
        port = row.find_all('td')[1].text.strip()
        proxies.append((ip, port))

    return proxies

def write_proxies_to_file(proxies, file_path='valid_proxies.txt'):
    with open(file_path, 'w') as file:
        for ip, port in proxies:
           if check_proxy(f'{ip}:{port}') is True:
             file.write(f'{ip}:{port}\n')


def check_proxy(proxy):
    url = 'https://httpbin.org/ip'  # 一个返回 IP 的测试接口
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=5)
      
        if response.status_code == 200:
            print(f'{proxy} ok')
            return True
        else:
            print(f'{proxy} faile')
            return False
    except Exception as e:
        print(f'{proxy} faile')
        return False


 

# 主程序
url='https://www.zdaye.com/dayProxy/ip/335693.html'
# url = 'https://www.zdaye.com/dayProxy/ip/335694.html'
html_content = fetch_proxy_page(url)

if html_content:
    proxy_list = extract_proxies(html_content)
    write_proxies_to_file(proxy_list)