import pandas as pd
from selenium import webdriver as wb
import time
from selenium.common.exceptions import NoSuchElementException
import re
import json
import pymysql

csv1 = pd.read_csv('Amazon Scraping .csv')

df = csv1.copy()
a = list(df['Asin'])
c = list(df['country'])

urls = ['https://www.amazon.' + str(Country) + '/dp/' + str(Asin) for Country, Asin in zip(c, a)][:100]

data = {"url_S": [], "Product_title": [], "Product_Price": [], "Image_url": [], "Product_details": [], "error_link": []}

for i in urls:
    driver = wb.Chrome(executable_path=r'D:\chromedriver_win32(1)\chromedriver.exe')
    driver.get(i)
    time.sleep(2)
    try:
        Product_title = driver.find_elements_by_class_name('a-size-extra-large')
        Product_image_url = driver.find_element_by_class_name('maintain-height').find_element_by_tag_name(
            'img').get_attribute('src')
        Product_Price = driver.find_elements_by_class_name('a-color-base')
        Product_details = driver.find_element_by_id('detailBullets_feature_div').find_elements_by_tag_name('li')
        data["url_S"].append(i)
        for each_title in Product_title:
            data["Product_title"].append(each_title.text)
        for each_price in Product_Price:
            data['Product_Price'].append(each_price.text)
        data["Image_url"].append(Product_image_url)
        for each_detail in Product_details:
            data["Product_details"].append(each_detail.text)
    except NoSuchElementException:
        data["error_link"].append(i + " " + 'not available')

try:
    while True:
        data['Product_Price'].remove('')
except ValueError:
    pass

try:
    while True:
        data['Product_title'].remove('')
except ValueError:
    pass

try:
    while True:
        data['Product_details'].remove('')
except ValueError:
    pass
# create jason file
with open("jsondata.json", "w") as final:
    json.dump(data, final)

# mysql connection


my_data = open("jsondata.json").read()

json_obj = json.loads(my_data)

con = pymysql.connect(host="localhost", user="root", password="", db="amazon_data")

cursor = con.cursor()

for item in json_obj:
    try:
        url_S = item.get("url_S")
        Product_title = item.get("Product_title")
        Product_Price = item.get("Product_Price")
        Image_url = item.get("Image_url")
        Product_details = item.get("Product_details")
        error_link = item.get("error_link")
        cursor.execute("insert into json_data(url_S,Product_title,Image_url,Product_details,error_link) values(%s,%s,%s,%s,%s,%s)",(url_S, Product_title, Image_url, Product_details, error_link))
    except AttributeError:
        pass

con.commit()
con.close()