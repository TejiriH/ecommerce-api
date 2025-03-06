from fastapi import FastAPI, HTTPException
from typing import Dict

app = FastAPI()

# In-memory cart storage (no database)
cart_db: Dict[int, Dict[int, int]] = {}

@app.get("/cart/{user_id}")
def get_cart(user_id: int):
    return cart_db.get(user_id, {})

@app.post("/cart/{user_id}/add/{product_id}")
def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    if user_id not in cart_db:
        cart_db[user_id] = {}

    cart_db[user_id][product_id] = cart_db[user_id].get(product_id, 0) + quantity
    return {"message": "Item added to cart", "cart": cart_db[user_id]}

@app.delete("/cart/{user_id}/remove/{product_id}")
def remove_from_cart(user_id: int, product_id: int):
    if user_id in cart_db and product_id in cart_db[user_id]:
        del cart_db[user_id][product_id]
        return {"message": "Item removed from cart"}
    raise HTTPException(status_code=404, detail="Item not found in cart")

@app.delete("/cart/{user_id}/clear")
def clear_cart(user_id: int):
    cart_db.pop(user_id, None)
    return {"message": "Cart cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
