import requests
from PIL import Image
from io import BytesIO
import imagehash

headers = {
    "User-Agent": "Mozilla/5.0"
}

url = "https://www.reddit.com/r/meme.json"
response = requests.get(url, headers=headers)
data = response.json()

downloaded_hashes = set()
downloaded_count = 0
image_number = 1

for post in data["data"]["children"]:
    post_data = post["data"]

    # Skip if no preview images
    if "preview" not in post_data:
        continue

    images = post_data["preview"].get("images")
    if not images:
        continue

    # Get the source image URL (highest quality)
    img_url = images[0]["source"]["url"]

    # Reddit escapes some characters in URLs, fix that
    img_url = img_url.replace("&amp;", "&")

    try:
        img_data = requests.get(img_url, headers=headers).content
        img = Image.open(BytesIO(img_data)).convert("RGB")

        img_hash = imagehash.average_hash(img)
        if img_hash in downloaded_hashes:
            continue

        filename = f"meme{image_number}.png"
        img.save(filename)
        downloaded_hashes.add(img_hash)

        print(f"Downloaded {filename} from {img_url}")

        image_number += 1
        downloaded_count += 1

        if downloaded_count >= 5:
            break

    except Exception as e:
        print(f"Failed to process image {img_url}: {e}")

if downloaded_count < 5:
    print(f"Only {downloaded_count} unique memes found.")
