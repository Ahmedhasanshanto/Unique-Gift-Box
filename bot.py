import random
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging সেটআপ (রেলওয়ে ড্যাশবোর্ডে এরর দেখার জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# আপনার তথ্য (সরাসরি এখানে বসিয়ে দিন অথবা Railway Variables এ সেট করুন)
BOT_TOKEN = "8209132112:AAFg8u5ffRl6JJwbmrMyMyeYwiFAfSv0YJs"
ADMIN_ID = 1781001349 

# ===============================
# DATA STRUCTURES
# ===============================
packages = [
    ("🎁 Gift Box Lite - 599৳", "• Printed Couple T-Shirt\n• Card\n• 4 Pcs Chocolates\n• 5 Pictures\n• Box", 599),
    ("🎁 Gift Box Ultra Lite - 999৳", "• 2 Pcs Mug\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Box", 999),
    ("🎁 Gift Box Elite - 1499৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Earrings (18K)\n• Box", 1499),
    ("🎁 Gift Box Ultra Elite - 1999৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Diary\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• Ornament (Any One)\n• Box", 1999),
    ("🎁 Gift Box Premium - 2499৳", "• 2 Pcs Mug\n• 2 Custom T-Shirts\n• Diary\n• Card\n• 5 Pcs Chocolates\n• 10 Pictures\n• 2 Roses\n• Ornament (Any One)\n• Box", 2499),
]

addons = {
    "👕 Apparel": [("Printed T-Shirt", 350), ("Couple T-Shirt", 650), ("Custom Hoodie", 850)],
    "☕ Drinkware": [("White Magic Mug", 350), ("Couple Mug Set", 600), ("Travel Flask", 700)],
    "🍫 Chocolates": [("Dairy Milk Silk", 250), ("Ferrero Rocher", 350), ("Premium Box", 700)],
    "💍 Ornaments": [("GP Earrings", 350), ("Adjustable Ring", 250), ("Name Necklace", 800)],
    "🖼 Photos": [("Polaroid (10pc)", 200), ("Wooden Frame", 450), ("Photo Keychain", 150)],
    "🌹 Flowers": [("Red Rose", 100), ("Rose Bouquet", 800), ("Sunflower", 250)],
    "📒 Stationery": [("Premium Diary", 350), ("Executive Pen", 200), ("Greeting Card", 100)],
    "🎧 Gadgets": [("LED Night Lamp", 650), ("Bluetooth Speaker", 1200), ("Earbuds", 1500)]
}

user_cart = {}

# ===============================
# HELPER FUNCTIONS
# ===============================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data="home"), InlineKeyboardButton("🎁 Pre-Made", callback_data="pre")],
        [InlineKeyboardButton("🛠 Custom Box", callback_data="custom"), InlineKeyboardButton("🛒 Cart", callback_data="view_cart")],
        [InlineKeyboardButton("📞 Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def safe_edit(query, text, markup=None):
    try:
        await query.edit_message_text(text=text, reply_markup=markup)
    except:
        await query.message.reply_text(text=text, reply_markup=markup)

async def show_category(query, context):
    cat_list = list(addons.keys())
    idx = context.user_data.get("cat_index", 0)

    if idx >= len(cat_list):
        cart = user_cart.get(query.from_user.id, [])
        total = sum(i[1] for i in cart)
        context.user_data.update({"total": total, "type": "Custom Box", "state": "WAITING_DETAILS"})
        
        summary = "🛒 Items Selected:\n" + "\n".join([f"• {i[0]}" for i in cart])
        await safe_edit(query, f"{summary}\n\n💰 Total: {total}৳\n\nএখন আপনার নাম, ফোন নম্বর ও ঠিকানা লিখে পাঠান।")
        return

    category = cat_list[idx]
    items = addons[category]
    keyboard = [[InlineKeyboardButton(f"{it[0]} - {it[1]}৳", callback_data=f"add_{i}")] for i, it in enumerate(items)]
    
    nav = []
    if idx > 0: nav.append(InlineKeyboardButton("⬅ Back", callback_data="prev_cat"))
    nav.append(InlineKeyboardButton("Next ➡", callback_data="next_cat"))
    
    keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="home")])
    await safe_edit(query, f"📦 Category ({idx+1}/{len(cat_list)}): {category}", InlineKeyboardMarkup(keyboard))

# ===============================
# HANDLERS
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎀 Welcome to Unique Gift Box!", reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "home":
        context.user_data.clear()
        await safe_edit(query, "🎀 Main Menu", main_menu())
    
    elif data == "help":
        await safe_edit(query, "📞 WhatsApp: 01754007868\nসরাসরি নক দিন।", main_menu())

    elif data == "pre":
        kb = [[InlineKeyboardButton(p[0], callback_data=f"pack_{i}")] for i, p in enumerate(packages)]
        kb.append([InlineKeyboardButton("⬅ Back", callback_data="home")])
        await safe_edit(query, "🎁 Select a Gift Box:", InlineKeyboardMarkup(kb))

    elif data.startswith("pack_"):
        idx = int(data.split("_")[1])
        p = packages[idx]
        context.user_data.update({"type": p[0], "total": p[2], "state": "WAITING_DETAILS"})
        kb = [[InlineKeyboardButton("✅ Order Now", callback_data=f"confirm_pre")], [InlineKeyboardButton("⬅ Back", callback_data="pre")]]
        await safe_edit(query, f"{p[0]}\n\n{p[1]}\n\n💰 Price: {p[2]}৳", InlineKeyboardMarkup(kb))

    elif data == "confirm_pre":
        await query.message.reply_text("আপনার নাম, ফোন নম্বর এবং ঠিকানা লিখে পাঠান:")

    elif data == "custom":
        user_cart[uid] = []
        context.user_data["cat_index"] = 0
        await show_category(query, context)

    elif data == "next_cat":
        context.user_data["cat_index"] = context.user_data.get("cat_index", 0) + 1
        await show_category(query, context)

    elif data == "prev_cat":
        context.user_data["cat_index"] = max(0, context.user_data.get("cat_index", 0) - 1)
        await show_category(query, context)

    elif data.startswith("add_"):
        idx = int(data.split("_")[1])
        cat = list(addons.keys())[context.user_data["cat_index"]]
        item = addons[cat][idx]
        if uid not in user_cart: user_cart[uid] = []
        user_cart[uid].append(item)
        await query.answer(f"Added: {item[0]}")

    elif data == "view_cart":
        cart = user_cart.get(uid, [])
        if not cart: return await query.answer("Cart is empty!")
        total = sum(i[1] for i in cart)
        txt = "🛒 Cart:\n" + "\n".join([f"• {i[0]} - {i[1]}৳" for i in cart]) + f"\n\nTotal: {total}৳"
        await safe_edit(query, txt, main_menu())

# ===============================
# COMMUNICATION (ORDER & FORWARD)
# ===============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    uid = user.id

    # ১. যদি ইউজার অর্ডার প্রসেসে থাকে
    if context.user_data.get("state") == "WAITING_DETAILS":
        order_type = context.user_data.get("type", "Unknown")
        total = context.user_data.get("total", 0)
        
        # এডমিনকে জানানো
        admin_msg = (
            f"📦 **NEW ORDER!**\n\n"
            f"👤 User: {user.full_name} (@{user.username})\n"
            f"🆔 ID: {user.id}\n"
            f"🛍 Item: {order_type}\n"
            f"💰 Amount: {total}৳\n"
            f"📝 Details:\n{text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        
        # ইউজারকে কনফার্ম করা
        await update.message.reply_text(f"✅ ধন্যবাদ {user.full_name}! আপনার অর্ডারটি গৃহীত হয়েছে। আমরা শীঘ্রই যোগাযোগ করবো।")
        context.user_data.clear()
        user_cart.pop(uid, None)

    # ২. ইউজার যদি এমনি নক দেয় (Knock)
    else:
        # এডমিনকে ফরওয়ার্ড করা
        forward_msg = (
            f"📩 **NEW MESSAGE**\n\n"
            f"From: {user.full_name} (@{user.username})\n"
            f"ID: {user.id}\n"
            f"Message: {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=forward_msg)
        # ইউজারকে রিপ্লাই
        await update.message.reply_text("আপনার মেসেজটি আমাদের টিমের কাছে পাঠানো হয়েছে। ধন্যবাদ!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is alive...")
    app.run_polling()

if __name__ == "__main__":
    main()