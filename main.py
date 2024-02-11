import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv

def get_url():
    # Функция нужна для того чтобы найти ссылку на товар.
    
    # Найти нужный товар.
    product = input('Искать товар на Ozon: ')
    url = 'https://ozon.kz/search/?&text=' + product
    
    return url


def get_source_html(page_url='', idx=1):
    # У этой функции задача сохранить html код страницы,
    # для дальнейшего использования.
    
    
    if not page_url:
        url = get_url()
        
        with open('product.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                ('Название товара', 'Цена товара', 'Информация о товаре')
            )
    else:
        url = 'https://ozon.kz' + page_url

    # Строки с ошибками
    str_eror = """
          Простите, произошла ошибка. Попробуйте обновить страницу или вернуться на шаг назад.
        """
        
    str_eror2 = """
      Простите, по вашему запросу товаров сейчас нет.
    """
    
    # Инициализация WebDriver
    driver = webdriver.Chrome()
    
    # Открытие URL-адреса
    
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        # Проверка на наличие данного текста в коде,
        # с последующим соответствующим выводом.
        
        if soup.find('div', string=str_eror):
            return 'Страниц с этим товаром больше нет'
        elif soup.find('div', string=str_eror2):
            return 'Страниц с этим товаром не найдено'
        
        # Запись html кода
        with open('file.html', "w") as file:
            file.write(driver.page_source)  
            
    except Exception as ex:
        print(ex)

    finally:
        # Закрытие браузера
        driver.quit()
    
    return scrap_and_save(idx)


def scrap_and_save(n):
    
    # Функция обрабатывает HTML код,
    # сначала ищет ссылки на товар,
    # далее парсит данные и записывает их в csv файл.
      
    # Открывает файл с кодом HTML.
    with open('file.html') as file:
        soup = BeautifulSoup(file, 'lxml')
        
        data = soup.find_all('a', class_='tile-hover-target')
        links = []
        
        links = [i.get('href') for i in data]

        # Здесь происходит перебор ссылок
        # из переменной 'links', для парсинга данных 
        # и до записи их в файл csv.
        for i in links[::2]:
            link_product = requests.get(url='https://ozon.kz' + i)
            soup = BeautifulSoup(link_product.text, 'lxml')

            script = soup.find('script', {'type': 'application/ld+json'}).string

            product_data = eval(script)

            name = product_data['name']
            price = product_data['offers']['price']
            description = product_data["description"]
            
            products = [
                name, price, description
            ]

            # До запись полученных данных в csv.
            with open('product.csv', 'a') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(products)
    
    # В данном участке кода происходит
    # поиск следующей страницы пагинации.
    try:        
        with open('file.html') as file:
            soup = BeautifulSoup(file, 'lxml')           
            print(f'Загруженно {n} - шт страниц')
        
            n += 1
            # Следующая страница пагинации.
            next_link = soup.find('a', string=str(n))['href']
    
    # Если срабатывает данная ошибка
    # это значит что все данные страницы загружены.         
    except TypeError:
        return 'Все страницы с товаром загружены' 
                            
    return get_source_html(next_link, n)
 

if __name__ == "__main__":
    print(get_source_html())    
