import requests
from bs4 import BeautifulSoup
import json
import csv
import pymongo

##=========================== CONST =====================================

path_productID = "./data/product-id2.txt"
path_product = "./data/product.txt"
path_product_csv = "./data/product.csv"

global headers, url
global dbName, MONGODB_URL

headers = {"Accept":"text/html"}
url = "https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846?page={}"
productAPI = "https://tiki.vn/api/v2/products/{}"
reviewAPI = "https://tiki.vn/api/v2/reviews?product_id={}"

MONGODB_URL = "mongodb://localhost:27017"
dbName = 'tiki'

##=========================== DEFINE FUNCTION =====================================

def crawl_product(product_list=[]):
    product_detail_list = []
    for product_id in product_list:
        response = requests.get(productAPI.format(product_id), headers={'User-Agent': "Chrome/50.0.2661.102"})
        if (response.status_code == 200):
            product_detail_list.append(response.json())
            print("Crawl product: ", product_id, ": ", response.status_code)
    return product_detail_list

def crawl_review(product_list=[]):
    review_list = []
    for product_id in product_list:
        response = requests.get(reviewAPI.format(product_id), headers={'User-Agent': "Chrome/50.0.2661.102"})
        if (response.status_code == 200):
            obj = {}
            obj = response.json()
            obj['product_id'] = product_id
            review_list.append(obj)
            print("Crawl review product: ", product_id, ": ", response.status_code)
    return review_list

def get_product_id():
    product_list  = []
    totalPage = 20;
    for i in range(1,totalPage + 1):
        response = requests.get(url.format(i), headers=headers)
        parser = BeautifulSoup(response.text, 'html.parser')
        product_box = parser.findAll(class_="product-item")
    
        for product in product_box:
            href = product.get("href")
            product_id = href[href.rindex("p") + 1:].replace(".html","")
            product_list.append(product_id)
    return product_list;

def read_product_id():
    product_list = []
    file = open(path_productID, "r")
    for line in file.readlines():
        product_list.append(line.replace('\n',''))
    file.close()
    return product_list;

def insertIntoDB(product_list, colName):
      myclient = pymongo.MongoClient(MONGODB_URL)
      mycol = myclient['tiki'][colName]
      
      x = mycol.insert_many(product_list)
      print(x.inserted_ids)

def parseReview(review_list = []):
      productRating = []
      users = []
      commnet_list = []
      for review in review_list:
            obj = {}
            comments = review['data'];
            stars = review['stars'];
            rating_average = review['rating_average']
            reviews_count = review['reviews_count']
            review_photo = review['review_photo'];
            obj['stars'] = stars
            obj['rating_average'] = rating_average
            obj['reviews_count'] = reviews_count
            obj['review_photo'] = review_photo
            obj['product_id'] = review['product_id']
            for comment in comments:
                  commnet_list.append(comment)
                  createdBy = comment['created_by']
                  if(checkExist(users, createdBy['id'])):
                        users.append(createdBy)
            productRating.append(obj)
            
      insertIntoDB(productRating, 'productRating')
      insertIntoDB(users, 'users')
      insertIntoDB(commnet_list, 'comments')
            
def checkExist(listItem,value = ''):
      if not any(item['id'] == value for item in listItem):
            return 1
      return 0

##=========================== MAIN =====================================

##product_list_id = get_product_id()

##save_product_id(product_list_id)

product_list_id = read_product_id();

## product_list = crawl_product(product_list_id)
## insertIntoDB(product_list, 'products')

review_list = crawl_review(product_list_id)
##insertIntoDB(review_list, 'reviews')
parseReview(review_list)

##=========================== END =====================================


##
# product_json_list = [adjust_product(p) for p in product_list]
# print(product_json_list)

### save product to csv
##save_product_list(product_json_list)



global fields
fields = [
  "id",
  "sku",
  "name",
  "url_key",
  "url_path",
  "type",
  "book_cover",
  "short_description",
  "price",
  "list_price",
  "price_usd",
#   "badges",
  "discount",
  "discount_rate",
  "rating_average",
  "review_count",
  "order_count",
  "favourite_count",
  "thumbnail_url",
  "has_ebook",
#   "inventory_status",
  "is_visible",
  "productset_group_name",
  "is_fresh",
  "seller",
  "is_flower",
  "is_gift_card",
#   "inventory",
  "url_attendant_input_form",
  "master_id",
  "salable_type",
  "data_version",
  "day_ago_created",
##  "categories",
  "meta_title",
  "meta_description",
  "meta_keywords",
  "liked",
##  "rating_summary",
  "description",
  "return_policy",
  "warranty_policy",
##  "brand",
##  "seller_specifications",
##  "current_seller",
##  "other_sellers",
##  "specifications"
##  "product_links",
##  "services_and_promotions",
##  "promotions",
##  "stock_item",
##  "installment_info",
##  "video_url",
##  "youtube",
##  "is_seller_in_chat_whitelist"
]



# def save_product_id(product_list=[]):
#     file = open(path_productID, "w+")
#     str = "\n".join(product_list)
#     file.write(str)
#     file.close()
#     print("Save file: ", path_productID)

# def adjust_product(product):
#     e = json.loads(product)
#     if not e.get("id", False):
#         return None

#     for field in flatten_field:
#         if field in e:
#             e[field] = json.dumps(e[field], ensure_ascii=true)

#     return e


# def save_raw_product(product_detail_list=[]):
#     file = open(path_product, "wb")
#     for p in product_detail_list:
#           file.write(json.dumps(p, ensure_ascii=False).encode('utf8'))
#           file.write(",".encode('utf-8'))
    
#     file.close()
#     print("Save file: ", path_product)


# def save_product_list(product_json_list):
#     file = open(path_product_csv, "w")
#     csv_writer = csv.writer(file)

#     count = 0
#     for p in product_json_list:
#         if p is not None:
#             if count == 0:
#                 header = p.keys() 
#                 csv_writer.writerow(header) 
#                 count += 1
#             csv_writer.writerow(p.values())
#     file.close()
#     print("Save file: ", path_product_csv)


