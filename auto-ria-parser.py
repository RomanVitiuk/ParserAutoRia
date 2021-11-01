from collections import deque
from json import dump, load
from os import getcwd, listdir, mkdir
from os.path import exists

from bs4 import BeautifulSoup
from requests import get


def create_auto_catalog(url, path=getcwd(), file_name='page_of_catalog.html'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:93.0) Gecko/20100101 Firefox/93.0'
    }
    with open(f'{path}\\{file_name}', 'w', encoding='utf-8') as file:
        file.write(get(url=url, headers=headers).text)


def finder_all_car_brands():
    with open('page_of_catalog.html', 'r', encoding='utf-8') as file:
        data_page = file.read()
    soup = BeautifulSoup(data_page, 'lxml')
    return soup.find_all('section', class_='box-panel line')


def form_unique_cars_brand_list(array):
    auto_names = deque()
    for section in array:
        names = section.find_all('a', class_='item-brands')
        for name in names:
            auto_names.append(name.text.strip())
    auto_names = set(auto_names)
    sorted_auto_names = sorted(auto_names)
    return sorted_auto_names


def dictionary_of_cars_brand(array):
    clearing_data = [x.split()[0] if len(x.split()) == 2
                     else f'{x.split()[0]}-{x.split()[1]}'
                     for x in array]
    return {int(i): v for i, v in enumerate(clearing_data[:-8], start=1)}


def brands_name():
    list_names = dictionary_of_cars_brand(
        form_unique_cars_brand_list(
            finder_all_car_brands()))
    for index, value in list_names.items():
        print(index, value)
    pick_a_brand = int(input("Pick a brand by a number: \n"))
    return list_names[pick_a_brand]


def pagination_info(url):
    page_scr = get(url).text
    soup = BeautifulSoup(page_scr, 'lxml')
    pagination_numbers = soup.find_all('span', class_='page-item mhide')
    if len(pagination_numbers) == 0:
        return 1
    last_page_num = [x.text for x in pagination_numbers][-1]
    return int(last_page_num)


def parse_by_brand(directory_name='brands folder'):
    current_path = getcwd()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:93.0) Gecko/20100101 Firefox/93.0'
    }
    if not exists(f'{current_path}\\{directory_name}'):
        mkdir(directory_name)
    car_name = brands_name()
    url_by_brand = 'https://auto.ria.com/uk/newauto/marka-{}/'.format(car_name.lower())
    pagination = pagination_info(url_by_brand)
    path_to_storage_auto_brands = f'{current_path}\\{directory_name}'
    if not exists(f'{path_to_storage_auto_brands}\\{car_name}'):
        mkdir(f'{path_to_storage_auto_brands}\\{car_name}')
    preffix = 'https://auto.ria.com'
    result = []
    for index in range(1, pagination + 1):
        url = f'{url_by_brand}?page={index}'
        response = get(url, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        all_cars = [x for x in soup.find_all('section', class_='proposition')
                    if car_name.lower() in x.a['href']]
        for car in all_cars:
            try:
                link = f'{preffix}{car.a["href"]}'
            except:
                link = 'No information about car'
            try:
                name = car.find('span', class_='link').text.strip()
            except:
                name = 'No information about car'
            try:
                price_usd = car.find('span',
                                     class_='green bold size22').text.strip()[:-2]
            except:
                price_usd = 'No information about price'
            try:
                location = car.find('span', class_='item region').text.strip()
            except:
                location = 'No information about location of car'
            try:
                engine = car.find('span',
                                  class_='item region').find_next_sibling().text.strip().split('•')
                engine_type = engine[0].strip()
                engine_capacity = float(engine[1].strip().split()[0])
            except:
                engine_type = 'No information about engine type'
                engine_capacity = 'No information about engine capacity'
            try:
                transmission = car.find('span',
                                        class_='item region').find_next_sibling().find_next_sibling().text.strip()
            except:
                transmission = 'No information about transmission'
            try:
                drive_type = car.find('span',
                                      class_='item region').find_next_sibling().find_next_sibling().find_next_sibling().text
            except:
                drive_type = 'No information about drive type'

            result.append(
                {"car link": link,
                 "car name": name,
                 "car price": int(price_usd.replace(' ', '')),
                 "car location": location,
                 "car engine type": engine_type,
                 "car engine capacity": engine_capacity,
                 "car transmission": transmission,
                 "car drive type": drive_type}
            )
    with open(f'{path_to_storage_auto_brands}\\{car_name}\\final-{car_name.lower()}-list.json',
              'w', encoding='utf-8') as file:
        dump(result, file, indent=2, ensure_ascii=False)


def main():
    if 'page_of_catalog.html' not in listdir(getcwd()):
        catalog_url = 'https://auto.ria.com/uk/newauto/catalog/'
        create_auto_catalog(catalog_url)
    parse_by_brand()


if __name__ == '__main__':
    main()
