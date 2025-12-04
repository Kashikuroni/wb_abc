from enum import Enum

class ExternalApiUrls(str, Enum):
    BASE_URL = "https://statistics-api.wildberries.ru/api/"
    SUPPLIER_ORDERS = "v1/supplier/orders"
