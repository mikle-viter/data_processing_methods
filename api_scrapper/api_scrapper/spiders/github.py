import scrapy
from scrapy.http import FormRequest
import requests
from pymongo import MongoClient


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/login']
    base_url = 'https://github.com/'
    login = 'mikle.viter@gmail.com'
    password = '548^d$220*'
    # Задаем пользователей, по которым надо собрать данные
    source_users = ['anabranch',
                    'daviddingly',
                    'sauron4code']
    # source_users = ['anabranch']
    avatars_path = 'avatars'
    db_name = 'final_db'
    client_mongo = None
    db = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('Создание БД')
        # Соединение с MongoDB
        self.client_mongo = MongoClient()
        self.db = self.client_mongo[self.db_name]
        # Если коллекция существует, очищаем ее
        list_of_collections = self.db.list_collection_names()
        if 'source_users' in list_of_collections:
            self.db['source_users'].drop()
        if 'followers' in list_of_collections:
            self.db['followers'].drop()
        if 'following' in list_of_collections:
            self.db['following'].drop()

    def closed(self, reason):
        self.db['SpiderInfo'].drop()
        with open(f'{self.db_name}.txt', 'w') as f:
            f.write('Вывод подписчиков и подписок пользователей:')
            users = self.db['source_users'].distinct('user_nickname')
            for user in users:
                f.write(f"\n{user}:")
                f.write(f"\n\tПодписчики:")
                followers = self.db['followers'].find({'source_user': user})
                i = 0
                for follower in followers:
                    i += 1
                    f.write(f"\n\t\t{i}) {follower}")
                f.write(f"\n\tПодписки:")
                followings = self.db['following'].find({'source_user': user})
                i = 0
                for following in followings:
                    i += 1
                    f.write(f"\n\t\t{i}) {following}")
        self.client_mongo.close()

    def parse(self, response):
        print("Запуск")
        yield FormRequest.from_response(
            response,
            url=self.base_url+'session',
            method="POST",
            formdata={
                'login': self.login,
                'password': self.password
            },
            callback=self.after_login)

    def after_login(self, response):
        print("Авторизация прошла успешно")
        # self.write_to_file(response.text, 'file1.html')
        for source_user in self.source_users:
            # Переходим к пользователю
            yield response.follow(self.base_url+source_user, callback=self.start_crawling,
                                  meta={'source_user': source_user})

    def start_crawling(self, response):
        source_user = response.meta.get('source_user')
        print(f'Загружена страница искомого пользователя "{source_user}"')
        # self.write_to_file(response.text, 'file2.html')

        # Добавляем исходного пользователя в БД
        appcoll = self.db['source_users']
        appcoll.insert_one({'user_nickname': source_user})

        # Проверка наличия подписчиков и подписок
        followers_href = response.xpath(
            "//a[contains(@class,'Link--secondary') and contains(., 'followers')]/@href").get()
        following_href = response.xpath(
            "//a[contains(@class,'Link--secondary') and contains(., 'following')]/@href").get()
        if followers_href:
            # followers_cnt = response.xpath(
            #     "//a[contains(@class,'Link--secondary') and contains(., 'followers')]/span/text()").get()
            # print(f"Подписчики найдены. Их количество = {followers_cnt}")
            yield response.follow(followers_href, callback=self.parse_users,
                                  meta={'users_type': 'followers',
                                        'source_user': source_user})
        if following_href:
            # following_cnt = response.xpath(
            #     "//a[contains(@class,'Link--secondary') and contains(., 'following')]/span/text()").get()
            # print(f"Подписки найдены. Их количество = {following_cnt}")
            yield response.follow(following_href, callback=self.parse_users,
                                  meta={'users_type': 'following',
                                        'source_user': source_user})

    def parse_users(self, response):
        # self.write_to_file(response.text, 'file3.html')
        users_type = response.meta.get('users_type')
        source_user = response.meta.get('source_user')

        turbo_frame = response.xpath("//*[@id='user-profile-frame']")

        if turbo_frame:
            # user_list = turbo_frame.xpath("//a[contains(@class,'Link--secondary')]/@href").getall()
            # Получаем список пользователей
            user_list = turbo_frame.xpath("//a[contains(@class,'d-inline-block')]/@href").getall()
            # Удаляем дубликаты ссылок
            user_list = list(dict.fromkeys(user_list))[1:]
            # Обработка пользователей
            i = 0
            for user_href in user_list:
                yield response.follow(user_href, callback=self.parse_user,
                                      meta={'user_type': users_type,
                                            'user_link': user_href,
                                            'source_user': source_user})
                # i += 1
                # if i > 2:
                #     break
            next_page = response.xpath("//a[@rel='nofollow' and contains(text(), 'Next')]/@href").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse_users,
                                      meta={'users_type': users_type,
                                            'source_user': source_user})
                # next_page_link = response.urljoin(next_page)
                # yield scrapy.Request(url=next_page_link, callback=self.parse)

    def parse_user(self, response):
        # Сбор данных о пользователе
        user_type = response.meta.get('user_type')
        user_link = response.meta.get('user_link')
        source_user = response.meta.get('source_user')
        user_avatar_href = response.xpath("//img[contains(@class,'avatar-user')]/@src").get()
        user_name = ''.join(response.xpath("//span[contains(@class,'p-name')]/text()").getall()).strip()
        user_nickname = ''.join(response.xpath("//span[contains(@class,'p-nickname')]/text()").getall()).strip()
        user_followers_cnt = response.xpath(
            "//a[contains(@class,'Link--secondary') and contains(., 'followers')]/span/text()").get()
        user_following_cnt = response.xpath(
            "//a[contains(@class,'Link--secondary') and contains(., 'following')]/span/text()").get()
        user_repositories_cnt = response.xpath(
            "//a[@data-tab-item='repositories']/span[@class='Counter']/text()").get()
        user_projects_cnt = response.xpath(
            "//a[@data-tab-item='projects']/span[@class='Counter']/text()").get()
        user_packages_cnt = response.xpath(
            "//a[@data-tab-item='packages']/span[@class='Counter']/text()").get()
        user_stars_cnt = response.xpath(
            "//a[@data-tab-item='stars']/span[@class='Counter']/text()").get()
        user_activity_years = response.xpath("//a[contains(@id,'year-link-')]/text()").getall()
        img_name = user_link.replace('/', '')
        img_data = requests.get(user_avatar_href).content
        with open(f'{self.avatars_path}/{img_name}.jpeg', 'wb') as image:
            image.write(img_data)
        # Заполнение словаря пользователя
        user = {'source_user': source_user,
                # 'user_type': user_type,
                'user_link': user_link,
                'user_avatar_href': user_avatar_href,
                'user_name': user_name,
                'user_nickname': user_nickname,
                'user_followers_cnt': user_followers_cnt,
                'user_following_cnt': user_following_cnt,
                'user_repositories_cnt': user_repositories_cnt,
                'user_projects_cnt': user_projects_cnt,
                'user_packages_cnt': user_packages_cnt,
                'user_stars_cnt': user_stars_cnt,
                'user_activity_years_cnt': len(user_activity_years),
                'user_activity_years': user_activity_years,
            }

        # Запись в БД
        appcoll = self.db[user_type]
        appcoll.insert_one(user)

    @staticmethod
    def write_to_file(text, filename):
        # Запись текста в filename. Используется для отладки
        with open(f'{filename}', 'w') as f:
            f.write(text)
