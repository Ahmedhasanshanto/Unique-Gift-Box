import random
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# আপনার টোকেন
BOT_TOKEN = "8209132112:AAFg8u5ffRl6JJwbmrMyMyeYwiFAfSv0YJs"

# ===============================
# PRE-MADE GIFT BOXES
# ===============================
packages = [
    ("🎁 Gift Box Lite - 599৳", "• Printed Couple T-Shirt\n• Card\n• 4 Pcs Chocolates\n• 5 Pictures\n• Box", 599, "sample_lite.jpg"),
    ("🎁 Gift Box Ultra Lite - 999৳", "• 2 Pcs Mug\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Box", 999, "sample_ultralite.jpg"),
    ("🎁 Gift Box Elite - 1499৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Earrings (18K)\n• Box", 1499, "sample_elite.jpg"),
    ("🎁 Gift Box Ultra Elite - 1999৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Diary\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Ornament (Any One)\n• Box", 1999, "sample_ultraelite.jpg"),
    ("🎁 Gift Box Premium - 2499৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Diary\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• 2 Roses\n• Ornament (Any One)\n• Box", 2499, "sample_premium.jpg"),
]

# ===============================
# EXPANDED ADDONS (Categorized)
# ===============================
addons = {
    "👕 Apparel": [
        ("Printed T-Shirt", 350), ("Couple T-Shirt (2pc)", 650), ("Custom Hoodie", 850),
        ("Premium Panjabi", 1200), ("Couple Pajama", 1100), ("Custom Cap", 250),
        ("Printed Apron", 400), ("Personalized Socks", 150)
    ],
    "☕ Drinkware": [
        ("White Magic Mug", 350), ("Black Magic Mug", 400), ("Couple Mug Set", 600),
        ("Travel Flask", 700), ("Steel Water Bottle", 450), ("Custom Tea Cup", 250)
    ],
    "🍫 Chocolates & Sweets": [
        ("Dairy Milk Silk", 250), ("Ferrero Rocher (4pc)", 350), ("KitKat Share Bag", 450),
        ("Premium Chocolate Box", 700), ("Imported Candy Jar", 400), ("Red Velvet Mini Cake", 500)
    ],
    "💍 Ornaments (18K GP)": [
        ("Gold Plated Earrings", 350), ("Adjustable Ring", 250), ("Custom Name Necklace", 800),
        ("Stone Bracelet", 500), ("Anklet (Nupur)", 450), ("Couple Rings", 700)
    ],
    "🖼 Photos & Frames": [
        ("Polaroid Photos (10pc)", 200), ("Wooden Photo Frame", 450), ("Photo Keychain", 150),
        ("3D Crystal Frame", 1500), ("Photo Wall Hanging", 600), ("Mini Photo Album", 800)
    ],
    "🌹 Flowers": [
        ("Red Rose (Single)", 100), ("Rose Bouquet (12pc)", 800), ("Mixed Flower Basket", 1200),
        ("Artificial Flower Box", 500), ("Sunflower Stick", 250)
    ],
    "📒 Stationery": [
        ("Premium Diary", 350), ("Executive Pen", 200), ("Customized Notebook", 300),
        ("Desk Organizer", 600), ("Planner 2024", 500), ("Greeting Card", 100)
    ],
    "🎧 Gadgets": [
        ("LED Night Lamp", 650), ("Bluetooth Speaker", 1200), ("Wireless Earbuds", 1500),
        ("Digital Watch", 900), ("Power Bank (Mini)", 1100)
    ],
    "🏠 Home Decor": [
        ("Scented Candle", 300), ("Mini Indoor Plant", 450), ("Decorative Fairy Light", 200),
        ("Customized Cushion", 500), ("Wall Clock", 800)
    ]
}

user_cart = {}

# ===============================
# NAVIGATION HELPER
# ===============================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data="home"), InlineKeyboardButton("🎁 Pre-Made Boxes", callback_data="pre")],
        [InlineKeyboardButton("🛠 Build Custom Box", callback_data="custom"), InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")],
        [InlineKeyboardButton("📞 Contact Support", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def safe_edit(query, text, markup):
    try:
        await query.edit_message_text(text=text, reply_markup=markup)
    except:
        await query.message.reply_text(text=text, reply_markup=markup)

# ===============================
# SHOW CATEGORY WITH BACK BUTTON
# ===============================
async def show_category(query, context):
    cat_list = list(addons.keys())
    idx = context.user_data.get("cat_index", 0)

    # ইফ ক্যাটাগরি শেষ হয়ে যায়
    if idx >= len(cat_list):
        cart = user_cart.get(query.from_user.id, [])
        total = sum(i[1] for i in cart)
        context.user_data["total"] = total
        context.user_data["type"] = "Custom Box"
        
        summary = "🛒 Your Custom Box Items:\n"
        for i in cart: summary += f"• {i[0]} - {i[1]}৳\n"
        
        await safe_edit(query, f"{summary}\n💰 Total: {total}৳\n\nঅর্ডার করতে আপনার নাম, ফোন ও ঠিকানা লিখে পাঠান।", None)
        return

    category = cat_list[idx]
    items = addons[category]
    
    keyboard = []
    # আইটেম বাটন
    for i, item in enumerate(items):
        keyboard.append([InlineKeyboardButton(f"{item[0]} - {item[1]}৳", callback_data=f"add_{i}")])
    
    # নেভিগেশন বাটন (Back, Next)
    nav_row = []
    if idx > 0:
        nav_row.append(InlineKeyboardButton("⬅ Back", callback_data="prev_cat"))
    
    nav_row.append(InlineKeyboardButton("Next ➡", callback_data="next_cat"))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("❌ Cancel & Home", callback_data="home")])

    await safe_edit(query, f"📦 Category ({idx+1}/{len(cat_list)}): {category}\n\nআইটেম পছন্দ করতে তাতে ক্লিক করুন (একাধিক নিতে পারেন)। তারপর Next চাপুন।", InlineKeyboardMarkup(keyboard))

# ===============================
# START & BUTTON HANDLER
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎀 Welcome to Unique Gift Box!", reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "home":
        await safe_edit(query, "🎀 Main Menu", main_menu())

    elif data == "help":
        await safe_edit(query, "📞 WhatsApp: 01754007868\nসরাসরি কথা বলতে কল করুন।", main_menu())

    await context.bot.send_message(
    chat_id=1781001349,
    text=f"""
📦 New Order Received!

👤 Name: {update.message.from_user.full_name}
🆔 User ID: {update.message.from_user.id}
📩 Username: @{update.message.from_user.username}

📝 Details:
{update.message.text}

💰 Total: {total}৳
"""
)


    # --- Pre-Made Boxes ---
    elif data == "pre":
        keyboard = [[InlineKeyboardButton(pkg[0], callback_data=f"pack_{i}")] for i, pkg in enumerate(packages)]
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="home")])
        await safe_edit(query, "🎁 আমাদের গিফট বক্সগুলো দেখুন:", InlineKeyboardMarkup(keyboard))

    elif data.startswith("pack_"):
        idx = int(data.split("_")[1])
        title, details, price, _ = packages[idx]
        keyboard = [
            [InlineKeyboardButton("📸 View Photo", callback_data=f"sample_{idx}")],
            [InlineKeyboardButton("✅ Buy Now", callback_data=f"order_{idx}")],
            [InlineKeyboardButton("⬅ Back", callback_data="pre")]
        ]
        await safe_edit(query, f"{title}\n\n{details}\n\n💰 Price: {price}৳", InlineKeyboardMarkup(keyboard))

    # --- Custom Box Logic ---
    elif data == "custom":
        user_cart[user_id] = []
        context.user_data["cat_index"] = 0
        await show_category(query, context)

    elif data == "next_cat":
        context.user_data["cat_index"] += 1
        await show_category(query, context)

    elif data == "prev_cat":
        context.user_data["cat_index"] -= 1
        await show_category(query, context)

    elif data.startswith("add_"):
        idx = int(data.split("_")[1])
        cat_list = list(addons.keys())
        cat_idx = context.user_data.get("cat_index", 0)
        item = addons[cat_list[cat_idx]][idx]
        
        if user_id not in user_cart: user_cart[user_id] = []
        user_cart[user_id].append(item)
        await query.answer(f"✅ {item[0]} added to box!")

    # --- Cart Logic ---
    elif data == "view_cart":
        cart = user_cart.get(user_id, [])
        if not cart:
            await query.answer("Your cart is empty!", show_alert=True)
            return
        
        text = "🛒 Your Selection:\n\n"
        total = sum(i[1] for i in cart)
        for i, item in enumerate(cart, 1):
            text += f"{i}. {item[0]} - {item[1]}৳\n"
        
        text += f"\n💰 Total: {total}৳"
        keyboard = [[InlineKeyboardButton("🗑 Clear Cart", callback_data="clear_cart")], [InlineKeyboardButton("⬅ Back", callback_data="home")]]
        await safe_edit(query, text, InlineKeyboardMarkup(keyboard))

    elif data == "clear_cart":
        user_cart[user_id] = []
        await query.answer("Cart cleared!")
        await safe_edit(query, "🛒 Cart is now empty.", main_menu())

    elif data.startswith("order_"):
        idx = int(data.split("_")[1])
        context.user_data.update({"type": packages[idx][0], "total": packages[idx][2]})
        await query.message.reply_text("অর্ডার করতে নাম, ফোন ও ঠিকানা লিখে পাঠান:")

# ===============================
# MESSAGE HANDLER (Order Receive)
# ===============================
async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "total" in context.user_data:
        order_id = random.randint(1000, 9999)
        text = (f"🎉 Order Confirmed!\n\nOrder ID: #{order_id}\nItem: {context.user_data['type']}\n"
                f"Total: {context.user_data['total']}৳\n\nআমরা আপনার সাথে শীঘ্রই যোগাযোগ করছি।")
        await update.message.reply_text(text)
        context.user_data.clear()
        user_cart.pop(update.message.from_user.id, None)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()