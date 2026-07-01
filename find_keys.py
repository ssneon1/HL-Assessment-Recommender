import json
import sys

def main():
    with open('data/shl_product_catalog.json', 'r', encoding='utf-8') as f:
        data = json.load(f, strict=False)
    
    unique_keys = set()
    for item in data:
        for k in item.get('keys', []):
            unique_keys.add(k)
    print("Unique keys:", unique_keys)

if __name__ == '__main__':
    main()
