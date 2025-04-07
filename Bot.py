import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Data storage
users = {}  # user_id: {'balance': int, 'referrals': int, 'last_bonus': date}
referrals = {}  # user_id: referrer_id

# Bot token (replace with your own)
TOKEN = "7547464966:AAGFPwrRLf65JF3ceBidMy2eGvgKMFoyBVc"

# Constants
REFERRAL_REWARD = 5
WITHDRAWAL_LIMIT = 50


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Referral code (e.g., /start 12345678)
    ref_id = update.message.text.split(" ")[1] if len(update.message.text.split()) > 1 else None

    if user_id not in users:
        users[user_id] = {'balance': 0, 'referrals': 0, 'last_bonus': None}
        if ref_id and int(ref_id) != user_id and int(ref_id) in users:
            if user_id not in referrals:
                referrals[user_id] = int(ref_id)
                users[int(ref_id)]['balance'] += REFERRAL_REWARD
                users[int(ref_id)]['referrals'] += 1

    keyboard = [
        [InlineKeyboardButton("Check Balance", callback_data='balance')],
        [InlineKeyboardButton("Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("Daily Bonus", callback_data='bonus')],
        [InlineKeyboardButton("How to Earn", callback_data='earn')],
        [InlineKeyboardButton("My Referral Link", callback_data='ref_link')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome {user.first_name}! Earn ₹5 per referral!\nUse the menu below:",
        reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = {'balance': 0, 'referrals': 0, 'last_bonus': None}

    data = query.data

    if data == "balance":
        bal = users[user_id]['balance']
        await query.edit_message_text(f"Your balance is ₹{bal}")

    elif data == "withdraw":
        bal = users[user_id]['balance']
        if bal >= WITHDRAWAL_LIMIT:
            users[user_id]['balance'] = 0
            await query.edit_message_text("Withdrawal successful! You'll receive payment soon.")
        else:
            await query.edit_message_text("Minimum ₹50 required to withdraw.")

    elif data == "bonus":
        now = datetime.now().date()
        last_bonus = users[user_id]['last_bonus']
        if last_bonus != now:
            users[user_id]['balance'] += 1
            users[user_id]['last_bonus'] = now
            await query.edit_message_text("Daily bonus added: ₹1")
        else:
            await query.edit_message_text("You've already claimed your bonus today.")

    elif data == "earn":
        msg = "You can earn money in the following ways:\n" \
              "- Invite friends using your referral link.\n" \
              "- You earn ₹5 for each valid referral.\n" \
              "- Claim daily bonus (₹1/day).\n"
        await query.edit_message_text(msg)

    elif data == "ref_link":
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.edit_message_text(f"Your referral link:\n{ref_link}")


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(handle_error)

    print("Bot is running...")
    app.run_polling()
