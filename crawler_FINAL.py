import requests
from bs4 import BeautifulSoup
import json
import csv
import pymongo

##=========================== CONFIG =====================================
global dbName, MONGODB_URL
global headers, url
MONGODB_URL = "mongodb://localhost:27017"

##=========================== CONST =====================================
path_productID = "./data/product-id2.txt"
path_product = "./data/product.txt"
path_product_csv = "./data/product.csv"

headers = {"Accept":"text/html",'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
url = "https://tiki.vn/laptop-may-vi-tinh/c1846?page={}&src=c.1846.hamburger_menu_fly_out_banner"
productAPI = "https://tiki.vn/api/v2/products/{}"
reviewAPI = "https://tiki.vn/api/v2/reviews?product_id={}"

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
        response = requests.get(url.format(i), headers={"User-Agent": "Chrome/50.0.2661.102"})
        parser = BeautifulSoup(response.text, 'html.parser')        
        product_box = parser.findAll(class_="product-item")
        
        for product in product_box:
            href = product.get("href")
            product_id_temp = href[href.rindex("p") + 1:]
            product_id = product_id_temp[:product_id_temp.rindex(".html")]
            product_list.append(product_id)
            
    print('get product id successfully!!!.')
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
      mycol = myclient[dbName][colName]
      
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
      print('insert review list successfully!!!.')
            
def checkExist(listItem,value = ''):
      if not any(item['id'] == value for item in listItem):
            return 1
      return 0

##=========================== MAIN =====================================

product_list_id = get_product_id()
print(product_list_id)
##save_product_id(product_list_id)

##product_list_id = read_product_id();
##
product_list = crawl_product(product_list_id)
insertIntoDB(product_list, 'products')
##
review_list = crawl_review(product_list_id)
parseReview(review_list)

##=========================== END =====================================


