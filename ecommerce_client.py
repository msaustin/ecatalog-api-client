import requests
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError
import json


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None


class EcommerceAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.info(f"{method} {url} - Status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error: {e} - {response.text}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON Decode Error: {e}")
            raise

    # Product operations
    def get_products(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Product]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset

        response = self._make_request('GET', '/products', params=params)
        data = self._handle_response(response)

        products = []
        product_list = data if isinstance(data, list) else data.get('products', [])

        for product_data in product_list:
            try:
                products.append(Product(**product_data))
            except ValidationError as e:
                self.logger.warning(f"Invalid product data: {e}")

        return products

    def get_product(self, product_id: int) -> Optional[Product]:
        response = self._make_request('GET', f'/products/{product_id}')
        data = self._handle_response(response)

        try:
            return Product(**data)
        except ValidationError as e:
            self.logger.error(f"Invalid product data: {e}")
            return None

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        response = self._make_request('GET', f'/products/sku/{sku}')
        data = self._handle_response(response)

        try:
            return Product(**data)
        except ValidationError as e:
            self.logger.error(f"Invalid product data: {e}")
            return None

    def create_product(self, product: Product) -> Optional[Product]:
        product_data = product.model_dump(exclude_none=True)
        response = self._make_request('POST', '/products', json=product_data)
        data = self._handle_response(response)

        try:
            return Product(**data)
        except ValidationError as e:
            self.logger.error(f"Invalid product data: {e}")
            return None

    def update_product(self, product_id: int, product: Product) -> Optional[Product]:
        product_data = product.model_dump(exclude_none=True)
        response = self._make_request('PUT', f'/products/{product_id}', json=product_data)
        data = self._handle_response(response)

        try:
            return Product(**data)
        except ValidationError as e:
            self.logger.error(f"Invalid product data: {e}")
            return None

    def delete_product(self, product_id: int) -> bool:
        response = self._make_request('DELETE', f'/products/{product_id}')
        try:
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError:
            return False

    def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        params = {'q': query}
        if category:
            params['category'] = category

        response = self._make_request('GET', '/products/search', params=params)
        data = self._handle_response(response)

        products = []
        product_list = data if isinstance(data, list) else data.get('products', [])

        for product_data in product_list:
            try:
                products.append(Product(**product_data))
            except ValidationError as e:
                self.logger.warning(f"Invalid product data: {e}")

        return products

    # Category operations
    def get_categories(self) -> List[str]:
        response = self._make_request('GET', '/categories')
        data = self._handle_response(response)
        return data if isinstance(data, list) else data.get('categories', [])

    def get_products_by_category(self, category: str) -> List[Product]:
        response = self._make_request('GET', f'/categories/{category}/products')
        data = self._handle_response(response)

        products = []
        product_list = data if isinstance(data, list) else data.get('products', [])

        for product_data in product_list:
            try:
                products.append(Product(**product_data))
            except ValidationError as e:
                self.logger.warning(f"Invalid product data: {e}")

        return products