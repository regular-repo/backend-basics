# City Summary

CLI-утилита «Сводка по городу»: получает погоду и курс валюты из внешних API,
применяет простые правила и печатает сводку в консоль.

## Требования

- Python 3.12
- Аккаунт на [OpenWeatherMap](https://openweathermap.org/) и API-ключ

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Настройка

Задайте API-ключ OpenWeatherMap в переменной окружения `WEATHER_API_KEY`:

**Windows (PowerShell):**
```powershell
$env:WEATHER_API_KEY = "ключ"
```

**Linux/macOS:**
```bash
export WEATHER_API_KEY="ключ"
```

Ключ можно получить бесплатно на https://home.openweathermap.org/api_keys

## Запуск

```bash
python main.py --city Moscow
```

Другая валюта:
```bash
python main.py --city Moscow --currency EUR
```

## Пример вывода

```
Город: Москва
Погода: 14.29°C, пасмурно
Тёплая одежда: нет
USD – RUB: 84.84
Дорогой курс: нет
```

## Коды выхода

| Код | Значение |
|-----|----------|
| 0   | Успех |
| 2   | Ошибка аргументов |
| 3   | Город или код валюты не найдены |
| 4   | Внешний сервис недоступен после retry |

## Структура

```
city_summary/
├── main.py                   # CLI: argparse, вывод в консоль
├── requirements.txt
├── README.md
├── clients/                  # только HTTP
│   ├── http.py               # общий GET с timeout и retry
│   ├── weather.py            # get_weather(city) → dict
│   ├── rates.py              # get_rate(currency) → float
│   └── exceptions.py         # свои исключения
└── processing/               # правила и сборка сводки
    ├── preprocessing.py      # warm_clothes, expensive
    └── service.py            # build_city_summary
```

## Внешние API

- **Погода:** [OpenWeatherMap](https://openweathermap.org/)
- **Курсы валют:** [Frankfurter](https://frankfurter.dev/)