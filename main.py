from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import os
import sqlite3


# Старт виртуального дисплея
screenW = 1200
screenH = 800
display = Display(visible=True, size=(screenW, screenH))
display.start()

# Установка параметров браузера
chrome_options = Options()
chrome_options.add_argument('window-size='+screenW.__str__()+'x'+screenH.__str__())
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome('drivers/chromedriver.exe', chrome_options=chrome_options)
driver.set_window_size(screenW - 20, screenH - 20)

# Загружаем страницу
s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)
driver.get('https://www.mvideo.ru/')

try:
    # Прокручиваем пока не найдем элемент
    body_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script(f"window.scrollTo(0, {body_height});")
        new_height = driver.execute_script("return document.body.scrollHeight")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h2[contains(text(),"Хиты продаж")]')))
            break
        except exceptions.TimeoutException:
            body_height = new_height

    div = driver.find_element(By.XPATH,
                              '//h2[contains(text(),"Хиты продаж")]/ancestor::mvid-simple-product-collection[@class="page-carousel-padding"]')

    div_new = div.find_element(By.TAG_NAME, 'mvid-product-cards-group')

    goods_names = div_new.find_elements(By.CLASS_NAME, "product-mini-card__name")
    goods_hrefs = div_new.find_elements(By.XPATH, '//a[@class="img-with-badge"]')
    goods_images = div_new.find_elements(By.CLASS_NAME, 'product-mini-card__image')
    goods_ratings = div_new.find_elements(By.CLASS_NAME, 'stars-container')
    goods_price_m = div_new.find_elements(By.CLASS_NAME, 'price__main-value')
    goods_price_s = div_new.find_elements(By.CLASS_NAME, 'price__sale-value')
    goods_bonuses = div_new.find_elements(By.CLASS_NAME, 'mbonus-block__value')

    my_goods = []
    for i in range(len(goods_names)):
        name = goods_names[i].text.strip()
        href = goods_hrefs[i].get_attribute('href')
        image = goods_hrefs[i].find_element(By.TAG_NAME, "img").get_attribute('srcset').split()[-2].replace("//", "")
        rating = goods_ratings[i].text.replace(",", ".").strip()
        price_m = goods_price_m[i].text.replace(",", ".").replace(" ₽", "").replace(" ", "")
        try:
            price_s = goods_price_s[i].text.replace(",", ".").replace(" ₽", "").replace(" ", "")
        except Exception:
            price_s = 0
        try:
            bonus = goods_bonuses[i].text.replace(",", ".").replace(" ", "").replace("+", "")
        except Exception:
            bonus = 0

        # Добавление данных в структуру
        my_goods.append({'name': name,
                         'href': href,
                         'image': image,
                         'rating': rating,
                         'price_m': price_m,
                         'price_s': price_s,
                         'bonus': bonus})

    # Создаем базу
    con = sqlite3.connect('my_goods.db')

    cursor = con.cursor()

    sql_str = '''
            create table if not exists my_goods(
                id integer primary key autoincrement,
                name text,
                href text,
                image text,
                rating float,
                price_m float,
                price_s float,
                bonus float
            )
        '''
    cursor.execute(sql_str)
    con.commit()

    # Очистка данных
    sql_str = 'delete from my_goods'
    cursor.execute(sql_str)
    con.commit()

    # Запись данных в БД
    try:
        for good in my_goods:
            name = good['name']
            href = good['href']
            image = good['image']
            rating = good['rating']
            price_m = good['price_m']
            price_s = good['price_s']
            bonus = good['bonus']

            sql_str = f"insert into my_goods(name, href, image, rating, price_m, price_s, bonus) " \
                      f"values('{name}', '{href}', '{image}', {rating}, {price_m}, {price_s}, {bonus})"
            # print(sql_str)
            cursor.execute(sql_str)
        con.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
    con.close()
    print('ОБРАБОТКА ЗАВЕРШЕНА')
    
except exceptions.NoSuchElementException:
    print('Хиты продаж не найдены')
    driver.quit()
    display.stop()

driver.quit()
display.stop()
