from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests

Config.set('graphics', 'resizable', True)


class Lesson3App(App):

    url = ""
    MAX_PAGES = 5

    lbl1 = Label(text='Спарсить цитаты с сайта Quotes to Scrape.\nНеобходимо извлечь саму цитату, автора и список тегов.', font_size='20sp')
    btn1 = Button(text="СПАРСИТЬ",
                  font_size="20sp",
                  background_color=(.67, 1, .33, 1),
                  color=(1, 1, 1, 1))
    lbl2 = Label(text='Строка состояния', font_size='20sp')
    txt1 = TextInput(font_size=18,
                     size_hint_y=None,
                     height=400)

    def build(self):

        self.url = "https://quotes.toscrape.com/"

        b = BoxLayout(orientation='vertical')

        self.btn1.bind(on_press=self.start_parsing)

        b.add_widget(self.lbl1)
        b.add_widget(self.btn1)
        b.add_widget(self.lbl2)
        b.add_widget(self.txt1)

        return b

    def get_page(self, pagenum = 0):

        if pagenum == 0:
            curr_url = self.url
        else:
            curr_url = f'{self.url}page/{pagenum}/'
        response = requests.get(curr_url)

        print(f'Парсинг URL: {curr_url}')
        soup = bs(response.content, 'html.parser')

        ret = []

        # Выделение цитат
        quotes = soup.find_all('div', attrs={'class': 'quote'})
        for quote in quotes:
            text = quote.select_one('span[class=text]').text.strip()
            author = quote.select_one('small[class=author]').text.strip()
            a_tags = quote.select_one('div[class=tags]').find_all('a', attrs={'class': 'tag'})
            tags = ""
            for tag in a_tags:
                tags += tag.contents[0].strip() + ', '
            if len(a_tags) > 0:
                tags = tags[:-2]
            tmp = {'text': text, 'author': author, 'tags': tags}
            ret.append(tmp)
        return ret

    def start_parsing(self, btn):
        self.lbl2.text = "Парсинг начался в " + datetime.now().strftime("%H:%M:%S")

        self.txt1.text = ""
        i = 0
        quotes_cnt = 1

        while i <= self.MAX_PAGES:
            if i == 1:
                i += 1
                continue
            ret = self.get_page(i)
            cnt = len(ret)
            if cnt == 0:
                break
            else:
                for j in range(cnt):
                    self.txt1.text = self.txt1.text + f'{quotes_cnt}) {ret[j]["author"]} [{ret[j]["tags"]}] {ret[j]["text"]} \n'
                    quotes_cnt += 1
            i += 1

        self.lbl2.text += "\nПарсинг окончился в " + datetime.now().strftime("%H:%M:%S")

        print(self.txt1.text)
        # Запись результатов также в файл
        with open('results', 'w') as f:
            f.write(self.txt1.text)

if __name__ == "__main__":
    app = Lesson3App()
    app.run()