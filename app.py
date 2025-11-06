# app.py
from flask import (
    Flask, render_template, session, redirect,
    url_for, request, flash, request as flask_request
)
from decimal import Decimal
import os
from telegram.telegrambot import sendMessage, token

app = Flask(__name__)
app.secret_key = os.urandom(24)          # random secret key

# ----------------------------------------------------------------------
# PRODUCTS (no duplicates)
# ----------------------------------------------------------------------
PRODUCTS = [
    {"id": 1, "name": "Blue T-Shirt",          "price": Decimal("19.99"), "desc": "Comfortable cotton tee.",               "image": "https://images.pexels.com/photos/428338/pexels-photo-428338.jpeg"},
    {"id": 2, "name": "Sneakers",              "price": Decimal("59.99"), "desc": "Lightweight running shoes.",            "image": "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg"},
    {"id": 3, "name": "Hat",                   "price": Decimal("14.50"), "desc": "Stylish cap.",                          "image": "https://images.pexels.com/photos/91224/pexels-photo-91224.jpeg"},
    {"id": 4, "name": "Backpack",              "price": Decimal("39.00"), "desc": "Durable travel backpack.",              "image": "https://images.pexels.com/photos/374574/pexels-photo-374574.jpeg"},
    {"id": 5, "name": "Wireless Earbuds",      "price": Decimal("79.99"), "desc": "Noise-cancelling Bluetooth earbuds.",   "image": "https://images.pexels.com/photos/373945/pexels-photo-373945.jpeg"},
    {"id": 6, "name": "Smartwatch",            "price": Decimal("129.99"),"desc": "Fitness tracking smartwatch.",          "image": "https://images.pexels.com/photos/267394/pexels-photo-267394.jpeg"},
    {"id": 7, "name": "Water Bottle",          "price": Decimal("12.00"), "desc": "Insulated stainless steel bottle.",     "image": "https://images.pexels.com/photos/414517/pexels-photo-414517.jpeg"},
    {"id": 8, "name": "Leather Wallet",        "price": Decimal("25.00"), "desc": "Genuine leather wallet with card slots.","image": "https://images.pexels.com/photos/4046304/pexels-photo-4046304.jpeg"},
    {"id": 9, "name": "Sunglasses",            "price": Decimal("22.50"), "desc": "UV-protected stylish sunglasses.",      "image": "https://images.pexels.com/photos/46710/pexels-photo-46710.jpeg"},
    {"id":10, "name": "Gaming Mouse",          "price": Decimal("34.99"), "desc": "RGB wired gaming mouse.",                "image": "https://images.pexels.com/photos/160107/pexels-photo-160107.jpeg"},
    {"id":11, "name": "Portable Charger",      "price": Decimal("29.99"), "desc": "10000mAh power bank.",                  "image": "https://images.pexels.com/photos/50711/pexels-photo-50711.jpeg"},
    {"id":12, "name": "Notebook",              "price": Decimal("6.99"),  "desc": "Hardcover dotted journal.",             "image": "https://images.pexels.com/photos/1230936/pexels-photo-1230936.jpeg"},
    {"id":13, "name": "Desk Lamp",             "price": Decimal("18.50"), "desc": "Adjustable LED desk lamp.",             "image": "https://images.pexels.com/photos/271639/pexels-photo-271639.jpeg"},
    {"id":14, "name": "Headphones",            "price": Decimal("49.99"), "desc": "Over-ear noise-cancelling headphones.", "image": "https://images.pexels.com/photos/159853/headphones-music-sound-159853.jpeg"},
    {"id":15, "name": "Coffee Mug",            "price": Decimal("9.99"),  "desc": "Ceramic coffee mug for hot drinks.",    "image": "https://images.pexels.com/photos/585750/pexels-photo-585750.jpeg"},
    {"id":16, "name": "Coffee Mug",            "price": Decimal("9.99"),  "desc": "Ceramic coffee mug for hot drinks.",    "image": "https://images.pexels.com/photos/585750/pexels-photo-585750.jpeg"},
]

def get_product(pid: int):
    return next((p for p in PRODUCTS if p["id"] == pid), None)

# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html", products=PRODUCTS)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    total = sum(
        Decimal(item["price"]) * item["quantity"]
        for item in cart.values()
    )
    return render_template("cart.html", cart=cart, total=total)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = get_product(product_id)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("home"))

    cart = session.get("cart", {})
    pid_str = str(product_id)

    if pid_str in cart:
        cart[pid_str]["quantity"] += 1
    else:
        cart[pid_str] = {
            "id": product["id"],
            "name": product["name"],
            "price": str(product["price"]),   # keep Decimal precision
            "quantity": 1,
            "image": product["image"]
        }

    session["cart"] = cart
    session.modified = True
    flash(f"{product['name']} added to cart!", "success")
    # go back to the page the user came from (or home)
    return redirect(flask_request.referrer or url_for("home"))

@app.route("/update_cart/<int:pid>", methods=["POST"])
def update_cart(pid):
    cart = session.get("cart", {})
    pid_str = str(pid)
    action = request.form.get("action")

    if pid_str not in cart:
        return redirect(url_for("view_cart"))

    if action == "increase":
        cart[pid_str]["quantity"] += 1
    elif action == "decrease" and cart[pid_str]["quantity"] > 1:
        cart[pid_str]["quantity"] -= 1
    elif action == "remove":
        cart.pop(pid_str, None)

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))

@app.route("/remove_from_cart/<int:pid>")
def remove_from_cart(pid):
    cart = session.get("cart", {})
    cart.pop(str(pid), None)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("view_cart"))

# ----------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------
 # import token too

@app.get('/contact')
def contact():
    return render_template('contact.html')

@app.post('/contact/submit')
def contact_submit():
    form = request.form
    name = form.get('name')
    email = form.get('email')
    subject = form.get('subject')
    phone = form.get('phone')
    message = form.get('message')

    if not name or not email or not message:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('contact'))

    telegram_message = f"""
    🔔 <b>New Contact Form Submission</b>

    👤 <b>Name:</b> {name}
    📧 <b>Email:</b> {email}
    📞 <b>Phone:</b> {phone or 'Not provided'}
    💡 <b>Subject:</b> {subject or 'Not provided'}
    💬 <b>Message:</b>
    {message}
    """

    result = sendMessage(token, telegram_message)

    if '"ok":true' in result:
        flash('Thank you! Your message has been sent successfully.', 'success')
    else:
        flash('Sorry, there was an error sending your message. Please try again.', 'error')

    return redirect(url_for('contact'))

if __name__ == "__main__":
    app.run(debug=True)