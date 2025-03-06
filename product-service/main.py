from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Sample in-memory product database
products = [
    {"id": 1, "name": "Laptop", "description": "A powerful gaming laptop", "price": 1200.99, "stock": 10},
    {"id": 2, "name": "Phone", "description": "A flagship smartphone", "price": 799.99, "stock": 15}
]

# Pydantic model for product data validation
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

# Get all products
@app.get("/products/")
def get_products():
    return products

# Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}

# Add new product
@app.post("/products/")
def create_product(product: Product):
    # Check if product with the same id already exists
    for p in products:
        if p["id"] == product.id:
            return {"error": "Product with this ID already exists"}
    # Add the new product to the list
    products.append(product.dict())
    return {"message": "Product created successfully", "product": product}

# Reduce stock (for order processing)
@app.put("/products/{product_id}/reduce-stock/")
def reduce_stock(product_id: int, quantity: int):
    for product in products:
        if product["id"] == product_id:
            if product["stock"] >= quantity:
                product["stock"] -= quantity
                return {"message": "Stock updated", "remaining_stock": product["stock"]}
            else:
                return {"error": "Not enough stock"}
    return {"error": "Product not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

