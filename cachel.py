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
        cache_info_dict[subdomain] = js_urls

# Step 4: Print the compiled result
for subdomain, js_urls in cache_info_dict.items():
    print(f"Subdomain: {subdomain}")
    for js_url in js_urls:
        print(js_url)
