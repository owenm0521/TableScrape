from bs4 import BeautifulSoup
from selenium import webdriver
import pandas


class TableScraper:
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.title = ''
        self.position = []
        self.name = []
        self.score = []
        self.thru = []
        self.today = []
        self.make_cut = []
        self.top20 = []
        self.top5 = []
        self.win = []
        self.__scrape_table()

    def __create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=self.path, options=options)
        return driver

    def __get_page(self):
        driver = self.__create_driver()
        driver.get(self.url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        return soup

    def __scrape_table(self):
        page_data = self.__get_page()
        self.title = page_data.find('div', class_='event-name').text
        for row in page_data.find_all('div', id=lambda value: value and value.startswith("row")):
            """for each row in table: get data from table, convert percentages to american odds, store in arrays"""

            # position + name
            self.position.append(row.find('div', id='col_text0').text)
            self.name.append(row.find('div', id='col_text1').text)

            # score
            if row.find('div', id='col_text2'):
                self.score.append(row.find('div', id='col_text2').text)
            else:
                self.score.append('-')

            # today
            if row.find('div', id='col_text3'):
                self.today.append(row.find('div', id='col_text3').text)
            else:
                self.today.append('-')

            # thru
            if row.find('div', id='col_text4'):
                self.thru.append(row.find('div', id='col_text4').text)
            else:
                self.thru.append('-')

            # make cut %
            if row.find('div', id='col_text5'):
                percent = row.find('div', id='col_text5').text
                self.make_cut.append(percent_to_american(percent))
            else:
                self.make_cut.append('-')

            # top 20 %
            if row.find('div', id='col_text6'):
                percent = row.find('div', id='col_text6').text
                self.top20.append(percent_to_american(percent))
            else:
                self.top20.append('-')

            # top 5 %
            if row.find('div', id='col_text7'):
                percent = row.find('div', id='col_text7').text
                self.top5.append(percent_to_american(percent))
            else:
                self.top5.append('-')

            # win percent
            if row.find('div', id='col_text8'):
                percent = row.find('div', id='col_text8').text
                self.win.append(percent_to_american(percent))
            else:
                self.win.append('-')

    def __create_dictionary(self):
        table = {
            'Position': self.position,
            'Name': self.name,
            'Score': self.score,
            'Thru': self.thru,
            'Today': self.today,
            'Make Cut': self.make_cut,
            'Top 20': self.top20,
            'Top 5': self.top5,
            'Win': self.win
        }
        return table

    def __create_dataframe(self):
        pandas.set_option("display.max_rows", None, "display.max_columns", None)
        dataframe = pandas.DataFrame(self.__create_dictionary())
        return dataframe

    def get_csv(self):
        dataframe = self.__create_dataframe()
        dataframe.to_csv(self.title + '.csv', index=False)

    def update_table(self):
        self.__scrape_table()

    def __get_name(self, player_lastname):
        for name in self.name:
            if name.startswith(player_lastname.upper()):
                return self.name.index(name)
        return None

    def get_position(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.position[self.__get_name(player_lastname)]

    def get_score(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.score[self.__get_name(player_lastname)]

    def get_thru(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.thru[self.__get_name(player_lastname)]

    def get_today(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.today[self.__get_name(player_lastname)]

    def get_make_cut_odds(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.make_cut[self.__get_name(player_lastname)]

    def get_top5_odds(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.top5[self.__get_name(player_lastname)]

    def get_top20_odds(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.top20[self.__get_name(player_lastname)]

    def get_win_odds(self, player_lastname):
        if self.__get_name(player_lastname) is None:
            raise ValueError
        return self.win[self.__get_name(player_lastname)]


def percent_to_american(string_percent):
    """convert percent odds (string) to percent odds (float) to american odds (float) """
    num_percent = float(string_percent.strip('%'))
    if int(num_percent) == 0 or 100:
        return 0
    elif num_percent <= 50:
        return int((100 / (num_percent / 100)) - 100)
    else:
        return int((num_percent / (1 - (num_percent / 100))) * -1)


def main():
    urls = ['https://datagolf.com/live-predictive-model', 'https://datagolf.com/live-predictive-model-euro']
    # specify path to chrome driver
    path = '/Users/owenmorris/Desktop/chromedriver'
    for url in urls:
        tb = TableScraper(url, path)
        tb.get_csv()


if __name__ == "__main__":
    main()
