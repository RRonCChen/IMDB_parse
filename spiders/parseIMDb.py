import scrapy
from bs4 import BeautifulSoup


class IMDbItem(scrapy.Item):
    movie_name = scrapy.Field()
    graded = scrapy.Field()
    total_time = scrapy.Field()
    category = scrapy.Field()
    director =scrapy.Field()
    meta_score = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    box_office = scrapy.Field()
    score = scrapy.Field()
    vote = scrapy.Field()
    actors = scrapy.Field()

class IMDbSpider(scrapy.Spider):
    name = "IMDb_Spider"
    start_urls = ['http://www.imdb.com/search/title?release_date=2016&sort=boxoffice_gross_us,desc']

    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml')
        lister_items = soup.find_all('div', {'class': 'lister-item-content'})

        for item in lister_items:
            link = 'http://www.imdb.com' + item.find('a')['href']

            movie_data = {}
            movie_data['movie_name'] = item.find('a').text

            movie_data['actors'] = []

            if item.find('span', {'class': 'runtime'}):
                movie_data['total_time'] = item.find('span', {'class': 'runtime'}).text
            else:
                movie_data['total_time'] = 'null'

            if item.find('span', {'class': 'genre'}):
                movie_data['category'] = (item.find('span', {'class': 'genre'}).text).strip().split(',')
            else:
                movie_data['category'] = 'null'

            if item.find_all('span', {'name': 'nv'}):
                if item.find(lambda tag: tag.name == 'span' and tag.get('class') == ['text-muted']).text == 'Votes:':
                    movie_data['vote'] = item.find_all('span', {'name': 'nv'})[0].text

                    if len(item.find_all(lambda tag: tag.name == 'span' and tag.get('class') == ['text-muted'])) == 2:
                        movie_data['box_office'] = item.find_all('span', {'name': 'nv'})[1].text
                    else:
                        movie_data['box_office'] = 'null'

                elif item.find(lambda tag: tag.name == 'span' and tag.get('class') == ['text-muted']).text == 'Gross:':
                    movie_data['vote'] = 'null'
                    movie_data['box_office'] = item.find_all('span', {'name': 'nv'})[0].text
            else:
                movie_data['vote'] = 'null'
                movie_data['box_office'] = 'null'


            if item.find('strong'):
                movie_data['score'] = item.find('strong').text
            else:
                movie_data['score'] = 'null'

            if item.find_all('p')[2].find_all('a'):
                movie_data['director'] = item.find_all('p')[2].find_all('a')[0].text
            else:
                movie_data['director'] = 'null'

            if item.find('span', {'class': 'certificate'}):
                movie_data['graded'] = item.find('span', {'class': 'certificate'}).text
            else:
                movie_data['graded'] = 'null'

            if item.find('span', {'class': 'metascore'}):
                movie_data['meta_score'] = (item.find('span', {'class': 'metascore'}).text).strip()
            else:
                movie_data['meta_score'] = 'null'

            if item.find_all('p')[2].find_all('a'):
                for person in item.find_all('p')[2].find_all('a'):
                    if person != item.find_all('p')[2].find_all('a')[0] :
                        movie_data['actors'].append(person.text)

            request = scrapy.Request(link, callback=self.parse_date)
            request.meta['data']= movie_data
            yield request

        next_page = soup.find('a',{'class':'lister-page-next next-page'})['href']
        if next_page is not None:
            yield response.follow('http://www.imdb.com/search/title'+next_page,callback=self.parse)

    def parse_date(self,response):
        soup = BeautifulSoup(response.body, 'lxml')

        date = soup.find('meta',{'itemprop':'datePublished'})['content']
        # print(response.meta['data'])
        data = response.meta['data']
        IMDb_data =IMDbItem(**data,date=date)
        yield IMDb_data