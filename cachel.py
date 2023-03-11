import requests
from bs4 import BeautifulSoup
from waybackpy import WaybackMachineDownloader
from assetfinder import AssetFinder
from httpx import Client

# Step 1: Use AssetFinder to find subdomains
domain = "example.com"  # Replace with your target domain
finder = AssetFinder()
subdomains = finder.find_subdomains(domain)

# Step 2: Use httpx to filter live subdomains
client = Client()
live_subdomains = []
for subdomain in subdomains:
    url = f"http://{subdomain}.{domain}"
    try:
        response = client.head(url)
        if response.status_code < 400:
            live_subdomains.append(subdomain)
    except:
        pass

# Step 3: Use cache-checker to check for cached versions for each live subdomain
cache_info_dict = {}
for subdomain in live_subdomains:
    url = f"http://{subdomain}.{domain}"
    response = requests.get("https://www.giftofspeed.com/cache-checker/", params={"url": url})
    soup = BeautifulSoup(response.content, "html.parser")
    cache_info = soup.find_all("p", {"class": "results__value"})
    if "Not cached" not in [info.text for info in cache_info]:
        downloader = WaybackMachineDownloader()
        urls = downloader.get_timestamps(url)
        js_urls = [url for url in urls if url.endswith(".js")]
        cache_info_dict[subdomain] = js_urlsimport argparse
import requests
from bs4 import BeautifulSoup
import subprocess

# Step 1: Parse command line arguments
parser = argparse.ArgumentParser(description='Check subdomains for cached .js files')
parser.add_argument('-t', '--target', type=str, required=True, help='Target domain')
parser.add_argument('-o', '--output', type=str, required=True, help='Output file name')
args = parser.parse_args()

# Step 2: Use assetfinder to find subdomains
subdomains = subprocess.check_output(['assetfinder', args.target]).decode('utf-8').splitlines()

# Step 3: Use httpx to filter out non-live subdomains
live_subdomains = []
for subdomain in subdomains:
    try:
        response = requests.get(f"http://{subdomain}", timeout=2)
        if response.status_code < 400:
            live_subdomains.append(f"http://{subdomain}")
    except:
        pass

# Step 4: Send GET request to cache-checker website for each live subdomain
js_urls = []
for subdomain in live_subdomains:
    response = requests.get('https://www.giftofspeed.com/cache-checker/', params={'url': subdomain})
    soup = BeautifulSoup(response.text, 'html.parser')
    cache_info = soup.find_all('td', class_='result')
    if 'No' not in cache_info[0].text:
        urls = subprocess.check_output(['waybackurls', subdomain]).decode('utf-8').splitlines()
        js_urls += [link for link in urls if link.endswith('.js')]

# Step 5: Write links to download .js files to output file
with open(args.output, 'w') as f:
    for link in js_urls:
        f.write(link + '\n')


# Step 4: Print the compiled result
for subdomain, js_urls in cache_info_dict.items():
    print(f"Subdomain: {subdomain}")
    for js_url in js_urls:
        print(js_url)
