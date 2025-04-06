import math
import time
import httpx
import jsonlines
from env import env
from bs4 import BeautifulSoup
import os
from models.laptop import CreateLaptopModel  # Cần tạo model này
from repositories.laptop import upsert_laptop  # Cần tạo repository này
from service.embedding import get_embedding

"""
How to run:
python
from tasks.import_laptop_data import *
import_jsonl_to_database()
"""

# request URL (API)
post_url = "https://papi.fptshop.com.vn/gw/v1/public/fulltext-search-service/category"

header = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9,vi;q=0.8",
    "content-type": "application/json",
    "order-channel": "1",
    "origin": "https://fptshop.com.vn",
    "priority": "u=1, i",
    "referer": "https://fptshop.com.vn/",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
}

category_slug = "may-tinh-xach-tay"  

file_path = "tasks/laptop_data.jsonl"  

def import_jsonl_to_database(
    file_path: str = file_path,
    start_offset: int = 0,
    limit: int | float = math.inf,
    batch_size: int = 10,
):
    if not os.path.isfile(file_path):
        extract_fpt_laptop_data(file_path=file_path)

    with jsonlines.open(file_path) as reader:
        current_offset = -1
        batch = []
        for laptop in reader:
            current_offset += 1
            if start_offset <= current_offset < start_offset + limit:
                batch.append(laptop)
                if len(batch) >= batch_size :
                    import_batch_data_to_database(batch)
                    batch = []
        if len(batch) > 0:
            import_batch_data_to_database(batch)

def import_batch_data_to_database(batch: list[dict]):
    for laptop in batch:
        id = laptop.get("code")
        name = laptop.get("name", "not known")
        slug = laptop.get("slug", "laptop")
        brand_code = laptop.get("brand", {}).get("code")
        product_type = laptop.get("productType", {}).get("name")
        description = laptop.get("description", "not description")
        promotions = laptop.get("promotions", [])
        skus = laptop.get("skus", [])
        key_selling_points = laptop.get("keySellingPoints", [])
        price = laptop.get("price", -1)
        score = laptop.get("score", 0)
        name_embedding = get_embedding(name)
        
        if id is not None:
            print(f"Upserting laptop: {id}, {name}, {brand_code}")

            upsert_laptop(
                CreateLaptopModel(
                    id=id,
                    name=name,
                    slug=slug,
                    brand_code=brand_code,
                    product_type=product_type,
                    description=description,
                    promotions=promotions,
                    skus=skus,
                    key_selling_points=key_selling_points,
                    price=price,
                    score=score,
                    data=laptop,
                    name_embedding=name_embedding,
                )
            )

def extract_fpt_laptop_data(
    skip_count: int = 0,
    batch_size: int = 16,
    sleep_after_batch: int | None = None,
    limit: int | float = math.inf,
    file_path: str = file_path,
):
    start_time = time.time()
    print("Import is running...")

    with httpx.Client() as client:
        imported_count = 0

        body = {
            "sortMethod": "noi-bat",
            "slug": category_slug,
            "skipCount": skip_count,
            "maxResultCount": batch_size,
            "categoryType": "category",
        }

        response = client.post(
            post_url,
            json=body,
            headers=header,
            timeout=20.0,
        )
        response.raise_for_status()
        response_data = dict(response.json())
        total_count = response_data.get("totalCount")
        items = response_data.get("items")

        if total_count is None or total_count <= 0 or items is None:
            raise Exception(f"not found category ({category_slug})")

        # Lấy mô tả của sản phẩm
        for item in items:
            item["description"] = get_description(item.get("slug"))

        if len(items) > limit:
            write_to_jsonlines(items[0:limit], file_path)
            imported_count += len(items)
        else:
            while len(items) > 0 and imported_count + len(items) <= limit:
                write_to_jsonlines(items, file_path)
                imported_count += len(items)
                if len(items) < batch_size:
                    break
                if sleep_after_batch is not None:
                    time.sleep(sleep_after_batch)

                body["skipCount"] = imported_count

                response = client.post(
                    post_url,
                    json=body,
                    headers=header,
                    timeout=20.0,
                )

                response.raise_for_status()
                response_data = dict(response.json())
                items = response_data.get("items")
                if items is None:
                    raise Exception(f"not found category ({category_slug})")
                for item in items:
                    description = get_description(item.get("slug"))
                    if description:
                        item["description"] = description

        print(f"Import successful {imported_count} {category_slug} items")
        print("--- %s seconds ---" % (time.time() - start_time))

def write_to_jsonlines(data: dict | list[dict], file_path: str = file_path):
    with jsonlines.open(file_path, "a") as writer:
        if type(data) is dict:
            writer.write(data)
        else:
            writer.write_all(data)

def get_description(item_slug: str) -> str | None:
    url = f"{env.FPTSHOP_BASE_URL}/{item_slug}"

    response = httpx.get(url, headers=header)
    data = BeautifulSoup(response.content, "html.parser")
    description_object = data.find("div", {"id": "ThongTinSanPham"})
    if description_object is None:
        return None

    description_object = description_object.select_one(
        "div.relative.w-full .description-container"
    )

    if description_object is None:
        return None

    contents = description_object.select("p, h2")

    return "\n".join([i.get_text() for i in contents])