from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pathlib
from PIL import Image, ImageTk

# -----------------------------------------------------
def get_exchange_rate(): # Функция, с помощью которой делается запрос и получается обменный курс криптовалюты
    crypto_name = crypto_combo.get()
    cur_name = cur_combo.get()

    if crypto_name and cur_name:
        try:
            crypto_id, cur_id = crypto_list[crypto_name], cur_list[cur_name]

            # Отправляем GET-запрос
            responce = requests.get(f'https://api.coingecko.com/api/v3/simple/'
                                    f'price?ids={crypto_id}&vs_currencies={cur_id}')

            # Проверяем успешность запроса
            responce.raise_for_status()
            data = responce.json()

            # С помощью ключей с id-криптовалюты и id-валюты, присваиваем переменной обменный курс
            cur_rate = data[crypto_id][cur_id]
            text = f'За один {crypto_name}\n {cur_rate} {cur_id.upper()}'
            cur_rate_lbl.config(text=text)

        except Exception as e:
            mb.showerror('Ошибка', f'Произошла ошибка {e}')

    else:
        mb.showwarning('Внимание!',
                       'Выберите необходимые данные из выпадающих списков')


# -----------------------------------------------------
def exit_(): # Функция, удаляющая окно и все виджеты
    mb.askokcancel('Подтвердите действие', 'Вы действительно хотите выйти?')
    window.destroy()


# -----------------------------------------------------
def coin_market_data(): # Функция, которая собирает и выводит рыночные данные о криптовалюте
    crypto_name = crypto_combo.get()
    cur_name = cur_combo.get()

    if crypto_name and cur_name:
        try:
            crypto_id, cur_id = crypto_list[crypto_name], cur_list[cur_name]

            # Отправляем GET-запрос
            responce = requests.get(f'https://api.coingecko.com/api/v3/coins/'
                                    f'markets?vs_currency={cur_id}&ids={crypto_id}')

            # Проверяем успешность запроса
            responce.raise_for_status()
            data = responce.json()

            market_cap = f'{data[0]['market_cap']} {cur_id.upper()}' # Рыночная капитализация
            # Изменение капитализации за сутки в процентах
            f_market_cap_change_perc = f'{data[0]['market_cap_change_percentage_24h']:.3f}%'
            market_cap_rank = f'{data[0]['market_cap_rank']} место' #Ранг рыночной капитализации
            total_volume = f'{data[0]['total_volume']} {cur_id.upper()}' # Общий объём
            circulating_supply = f'{data[0]['circulating_supply']:.1f} {cur_id.upper()}'  # Циркулирующий запас

            # Создаем таблицу с данными
            table = pd.DataFrame({
                'Метрика': ['Рыночная капитализация', 'Динамика капитализации за сутки', 'Ранг рыночной капитализации',
                            'Общий объём', 'Циркулирующий запас'],
                'Значение': [market_cap, f_market_cap_change_perc, market_cap_rank, total_volume,
                             circulating_supply]
            })

            return table
        except Exception as e:
            mb.showerror('Ошибка', f'Произошла ошибка {e}')

            return None
    else:
        mb.showwarning('Внимание!', 'Выберите необходимые данные из выпадающих списков')
        return None


# -----------------------------------------------------
def market_data(): # Функция, которая запускает сбор рыночных данных крипты и собирает их в таблицу
    crypto_name = crypto_combo.get()
    cur_name = cur_combo.get()

    if crypto_name and cur_name:
        try:
            new_window = Toplevel(window)
            new_window.title('Продвинутые данные')
            new_window.geometry('400x270')
            new_window.resizable(False, False)

            table = coin_market_data() # Вызываем функцию для сбора метрик и получаем из неё таблицу в DataFrame
            tree = ttk.Treeview(new_window) # Создаём таблицу в tkinter
            tree["columns"] = ("Метрика", "Значение") # Определяем столбцы таблицы

            # Форматируем столбцы таблицы
            tree.column("#0", width=0, stretch=NO)
            tree.column("Метрика", anchor=W, width=200)
            tree.column("Значение", anchor=W, width=200)

            # Создаем заголовки таблицы
            tree.heading("#0", text="", anchor=W)
            tree.heading("Метрика", text="Метрика", anchor=W)
            tree.heading("Значение", text="Значение", anchor=W)

            # Выводим данные в таблицу
            for index, row in table.iterrows():
                tree.insert("", END, values=list(row))

            tree['height'] = 10

            tree.pack() # Размещаем таблицу в окне

            # Создаём кнопку для вывода графика matplotlib
            button = Button(new_window, text=f'Динамика курса {crypto_name} в течение года', command=chart_drawing)
            button.pack(pady=10)
        except Exception as e:
            mb.showerror('Ошибка', f'Произошла ошибка {e}')
    else:
        mb.showwarning('Внимание!',
                       'Выберите необходимые данные из выпадающих списков')


# -----------------------------------------------------
def date_transformer(timestamp): # Функция, которая преобразует дату из формата Unix
    if timestamp:
        try:
            date_unix = datetime.datetime.fromtimestamp(timestamp / 1000) # Переводим из миллисекунд в секунды
            date = date_unix.date() # Получаем дату в формате datetime ГГГГ-ММ-ДД

            return date
        except Exception as e:
            mb.showerror('Ошибка',
                         f'Произошла ошибка при форматировании даты: {e}')
            return None
    else:
        mb.showerror('Ошибка', 'Дата в формате Unix не получена')
        return None


# -----------------------------------------------------
def coin_hist_chart(): # Функция собирает динамику курса искомой крипты в течение года
    crypto_name = crypto_combo.get()
    cur_name = cur_combo.get()

    if crypto_name and cur_name:
        try:
            crypto_id, cur_id = crypto_list[crypto_name], cur_list[cur_name]

            # Отправляем GET-запрос
            responce = requests.get(f'https://api.coingecko.com/api/v3/'
                                    f'coins/{crypto_id}/market_chart?vs_currency={cur_id}&days=365')

            # Проверяем успешность запроса
            responce.raise_for_status()
            data = responce.json()
            dates, prices = [], [] # Создаём пустые списки для дат и стоимости крипты
            for d in data['prices']:
                dates.append(date_transformer(d[0])) # Добавляем в список преобразованные даты
                prices.append(round(d[1], 2)) # Добавляем в список динамику курса крипты, округлённую до 2-х десятых

            return dates, prices
        except Exception as e:
            mb.showerror('Ошибка', f'Произошла ошибка {e}')

            return None
    else:
        mb.showwarning('Внимание!',
                       'Выберите необходимые данные из выпадающих списков')


# -----------------------------------------------------
def rate_chart(dates, prices): # Функция рисует график с помощью модуля matplotlib
    crypto_name = crypto_combo.get()
    cur_acr = cur_list[cur_combo.get()].upper()
    if all(dates) and all(prices):
        try:
            # Создаём график
            plt.plot(dates, prices)
            plt.xlabel('Месяцы')
            plt.ylabel(f'Стоимость в {cur_acr}')
            plt.title(f'Динамика курса {crypto_name} за год')

            # Добавляем подписи месяцев на ось X
            months = mdates.MonthLocator()  # Каждый месяц
            month_fmt = mdates.DateFormatter('%b')  # Формат как аббревиатура месяца (например, Jan, Feb, и т.д.)
            # Решил отказать от формата %b-%y из-за того, что подписи в этом случае выглядят наляписто

            ax = plt.gca() # Получаем экземпляр оси X
            ax.xaxis.set_major_locator(months) # Определяем способ определения позиций меток (помесячно)
            ax.xaxis.set_major_formatter(month_fmt) # Определяем способ отображения меток

            plt.show()

        except Exception as e:
            mb.showerror('Ошибка', f'Произошла ошибка {e}')
    else:
        mb.showerror('Ошибка',
                     f'Нет данных по динамике курса {crypto_name} или данные повреждены')


# -----------------------------------------------------
def chart_drawing(): # Функция запускает процесс отрисовки графика
    dates, prices = coin_hist_chart()[0], coin_hist_chart()[1]
    rate_chart(dates, prices)


# -----------------------------------------------------
# Создаём и настраиваем главный виджет
window = Tk()
window.title('Курсы обмена валют')
window.geometry('400x170')
window.resizable(False, False)

current_dir = pathlib.Path(__file__).parent # Получаем директорию текущего файла
ico_path = 'ico.png' # Определяем относительный путь к иконке приложения
ico_absolute_path = current_dir / ico_path # Конструируем абсолютный путь к файлам
image_ico = Image.open(ico_absolute_path) # Открываем изображение с помощью PIL
ico_image = ImageTk.PhotoImage(image_ico) # Преобразовываем изображение в формат .ico
window.iconphoto(True, ico_image) # Устанавливаем иконку с помощью метода iconphoto
# -----------------------------------------------------
# Словарь с основными криптовалютами
crypto_list = {
    'Bitcoin': 'bitcoin',
    'Ethereum': 'ethereum',
    'Ripple': 'ripple',
    'Litecoin': 'litecoin',
    'Cardano': 'cardano',
    'Binance Coin': 'binancecoin',
    'Tether': 'tether',
    'Stellar': 'stellar',
    'Monero': 'monero',
    'NEM': 'nem'
}
# -----------------------------------------------------
# Словарь с основными денежными валютами
cur_list = {
    'Российский рубль': 'rub',
    'Доллар США': 'usd',
    'Евро': 'eur',
    'Китайский юань': 'cny'
}
# -----------------------------------------------------
# Создаём интерфейс
# Настройки текстовых меток
Label(text='Криптовалюта').grid(row=0, column=0, pady=(10, 0), padx=(20, 0), sticky='W')
Label(text='Денежная валюта').grid(row=2, column=0, pady=(20, 0), padx=(20, 0), sticky='W')
Label(text=f'Текущий курс крипты',
      font=('SegoeUI', 12, 'bold')).grid(row=0, column=1, padx=(25, 0), pady=(10, 0))
# -----------------------------------------------------
# Настройки текстовой метки, которая выводит текущий курс криптовалюты
cur_rate_lbl = Label(text='', font=('SegoeUI', 12, 'bold'), fg='red')
cur_rate_lbl.grid(row=1, column=1, rowspan=2, sticky='S', padx=(25, 0), pady=(10, 10))
# -----------------------------------------------------
# Настройки выпадающего списка с криптой
crypto_combo = ttk.Combobox(values=list(crypto_list.keys()))
crypto_combo.grid(row=1, column=0, padx=(20, 0), pady=(0, 20))
crypto_combo.set(value='Bitcoin')
# -----------------------------------------------------
# Настройки выпадающего списка с валютой
cur_combo = ttk.Combobox(values=list(cur_list.keys()))
cur_combo.grid(row=4, column=0, padx=(20, 0))
cur_combo.set(value='Доллар США')
# -----------------------------------------------------
# Настройки кнопки
exchange_rate_btn = Button(text='Уточнить курс', command=get_exchange_rate, width=19)
exchange_rate_btn.grid(row=4, column=1, padx=(25, 0))
# -----------------------------------------------------
# Создаём меню
menu_bar = Menu(window)
window.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Файл', menu=file_menu)
file_menu.add_command(label='Рыночные данные', command=market_data)
file_menu.add_separator()
file_menu.add_command(label='Выход', command=exit_)
# -----------------------------------------------------
window.mainloop()