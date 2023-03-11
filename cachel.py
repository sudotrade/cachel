import argparse
import requests
from bs4 import BeautifulSoup
import subprocess
import httpx


class WaybackMachineDownloader:
    def get_timestamps(self, url):
        response = requests.get(f"https://web.archive.org/cdx/search/cdx?url={url}&output=json&fl=timestamp")
        timestamps = response.json()[1:]
        urls = [f"https://web.archive.org/web/{timestamp}/{url}" for timestamp in timestamps]
        return urls

# Step 1: Parse command line arguments
parser = argparse.ArgumentParser(description='Check subdomains for cached .js files')
parser.add_argument('-t', '--target', type=str, required=True, help='Target domain')
parser.add_argument('-o', '--output', type=str, required=True, help='Output file name')
args = parser.parse_args()

# Define domain as target
domain = args.target

# Step 2: Use assetfinder to find subdomains
subdomains = subprocess.check_output(['assetfinder', domain]).decode('utf-8').splitlines()

# Step 3: Use httpx to filter out non-live subdomains
live_subdomains = []
with httpx.Client() as client:
    for subdomain in subdomains:
        try:
            response = client.get(f"http://{subdomain}", timeout=2)
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
        downloader = WaybackMachineDownloader()
        urls = downloader.get_timestamps(subdomain)
        js_urls += [link for link in urls if link.endswith('.js')]

# Step 5: Write links to download .js files to output file
with open(args.output, 'w') as f:
    for link in js_urls:
        f.write(link + '\n')


# Step 6: Print the compiled result
print('Compiled Result:')
for link in js_urls:
    print(link)
