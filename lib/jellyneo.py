from lib import NeoPage
import re

import time
from . import item_db

re_jn_item = re.compile(r'''<a href="/item/(\d+)/"><img .*?></a><br><a .*?>(.*?)</a>(?:\n<br><span class="text-small"><a href=".*?" class=".*?"(?:title="(.*?)")?>(.*?)</a></span>)?''')

def price_of_item(name):
    np = NeoPage(base_url='https://items.jellyneo.net')
    path = '/search/'
    np.get(path, f'name={name}', 'name_type=3')
    results = re_jn_item.findall(np.content)
    item_id, name, price_updated, price = results[0]
    print(f'Price of {name} is {price}')

# Warning: Keep the request rate super low or you'll get IP banned.
def gen_restock_list():
    np = NeoPage(base_url='https://items.jellyneo.net')
    path = '/search/'
    args = []
    # For Fresh Foods shop.
    args.append('cat[]=1')
    # Hubert's Hot Dogs
    #args.append('cat[]=42')
    args.append('min_rarity=1')
    args.append('max_rarity=100')
    args.append('status=1')
    args.append('sort=5')
    args.append('sort_dir=desc')
    # Cove
    #args.append('scat[]=16')

    start = 0
    while True:
        np.get(path, *args, f'start={start}')
        time.sleep(10)
        referer = np.referer
        results = re_jn_item.findall(np.content)
        for item_id, name, price_updated, price in results:
            if price == 'Inflation Notice':
                np.set_referer(referer)
                np.get(f'/item/{item_id}')
                time.sleep(10)
                price = re.search('<div class="price-row">(.*?) NP', np.content)[1]
            try:
                price = lib.amt(price)
            except (ValueError, TypeError, IndexError):
                # safe assumption that unpriceable items are at least 10M NP?
                price = 10000001
            print(f'\'{name}\': {price},')
        start += 50
        if not re.search(r'<li class="arrow"><a href=".*?">&raquo;</a>', np.content):
            break
