# Написать приложение и функцию, которые собирают основные новости с сайта на выбор lenta.ru, mail.ru .
# Для парсинга использовать XPath
# Структура данных должна содержать:
# * название источника
# * наименование новости
# * ссылку на новость
# * дата публикации


from lxml import html
import requests
import re


def get_news_lenta():
    r = requests.get('https://lenta.ru/')
    root = html.fromstring(r.content)
    # Выбираем все ссылки, в адресах которых есть /news/
    news = root.xpath("//a[contains(@href,'/news/')]")
    ret = []
    for item in news:
        source = "mail.ru"
        name = ' '.join(item.xpath(".//span/text()")).encode(encoding='ISO-8859-1').decode().strip()
        if name == "":
            continue
        link = item.xpath("@href")[0]
        if not link.startswith('http'):
            date = re.search(r'\d\d\d\d/\d\d/\d\d', link).group().split('/')
            date = date[2] + '.' + date[1] + '.' + date[0]
            link = "https://lenta.ru/" + link
        else:
            date = re.search(r'\d\d-\d\d-\d\d\d\d', link).group().split('-')
            date = date[0] + '.' + date[1] + '.' + date[2]

        tmp = {'source': source, 'name': name, 'link': link, 'date': date}
        ret.append(tmp)
    return ret

if __name__ == "__main__":
    i = 1
    for item in get_news_lenta():
        print(f'{i}) Название источника: {item["source"]}; наименование новости: {item["name"]}; ссылка на новость: {item["link"]}; дата публикации: {item["date"]}')
        i += 1
