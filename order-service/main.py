import logging
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

PRODUCT_SERVICE_URL = "http://product-service:8000"
CART_SERVICE_URL = "http://cart-service:8001"

# Setup logging for better debugging
logging.basicConfig(level=logging.DEBUG)

@app.post("/orders/{user_id}")
def place_order(user_id: int):
    try:
        # Fetch cart items
        cart_response = requests.get(f"{CART_SERVICE_URL}/cart/{user_id}")
        if cart_response.status_code != 200:
            logging.error(f"Failed to fetch cart for user {user_id}: {cart_response.text}")
            raise HTTPException(status_code=500, detail="Failed to fetch cart")

        cart_items = cart_response.json()
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Validate product stock
        for product_id, quantity in cart_items.items():
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
            if product_response.status_code != 200:
                logging.error(f"Failed to fetch product {product_id}: {product_response.text}")
                raise HTTPException(status_code=400, detail=f"Product {product_id} not found")

            product = product_response.json()
            if quantity > product["stock"]:
                logging.error(f"Not enough stock for product {product['name']}. Requested: {quantity}, Available: {product['stock']}")
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {product['name']}")

        # Reduce stock for each product
        for product_id, quantity in cart_items.items():
            reduce_stock_response = requests.put(f"{PRODUCT_SERVICE_URL}/products/{product_id}/reduce-stock/?quantity={quantity}")
            if reduce_stock_response.status_code != 200:
                logging.error(f"Failed to update stock for product {product_id}: {reduce_stock_response.text}")
                raise HTTPException(status_code=500, detail=f"Failed to update stock for product {product_id}")

        # Clear the cart after placing an order
        clear_cart_response = requests.delete(f"{CART_SERVICE_URL}/cart/{user_id}/clear")
        if clear_cart_response.status_code != 200:
            logging.error(f"Failed to clear cart for user {user_id}: {clear_cart_response.text}")
            raise HTTPException(status_code=500, detail="Failed to clear cart")

        return {"message": "Order placed successfully", "order": cart_items}

    except Exception as e:
        logging.error(f"Error placing order for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
