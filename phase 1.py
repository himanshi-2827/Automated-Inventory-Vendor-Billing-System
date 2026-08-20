# Phase 1 - Simple Inventory System

products = {"Pen": 10, "Book": 50, "Bag": 500}
stock = {"Pen": 20, "Book": 10, "Bag": 5}

print("Products:", products)

product = input("Enter product: ")
qty = int(input("Enter quantity: "))

if product in stock and qty <= stock[product]:
    stock[product] -= qty
    total = products[product] * qty

    print("Product:", product)
    print("Quantity:", qty)
    print("Total: ₹", total)
    print("Remaining Stock:", stock[product])
else:
    print("Product not available or insufficient stock!")