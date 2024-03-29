from collections import Counter
from typing import List

from prettytable import PrettyTable
from telegram import Bot, Update, ParseMode, ForceReply, CallbackQuery, InputMediaPhoto, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from config import telegram_bot, width_in_characters
from gmaps import GMaps
from offer import Offer
from offer_storage import OfferStorage


class TelegramBot:

    def __init__(self, offer_storage: OfferStorage, token=telegram_bot['token']):
        self.offer_storage = offer_storage
        self.bot = Bot(token)
        self.updater = Updater(bot=self.bot)
        self.updater.dispatcher.add_handler(CommandHandler('start', start))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_callback))
        self.updater.start_polling()

    def handle_callback(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        data = query.data.split('-')
        query.answer()
        if not data:
            return
        offer_id = data[0]
        if self.offer_storage.has_offer(offer_id) and self.offer_storage.get_offer(offer_id).is_complete:
            offer = self.offer_storage.get_offer(offer_id)
            callback_type = data[1]
            handlers[callback_type](update, query, data[2:], offer)
        else:
            query.edit_message_caption(
                caption='<b>Offer not loaded!</b>',
                parse_mode=ParseMode.HTML
            )

    def send_offer(self, chat_id: str, offer: Offer) -> None:
        if offer.images:
            self.bot.send_photo(
                chat_id=chat_id,
                photo=offer.images[0],
                caption=offer.generate_offer_message(),
                parse_mode=ParseMode.HTML,
                reply_markup=get_reply_markup(offer)
            )
        else:
            self.bot.send_message(
                chat_id=chat_id,
                text=offer.generate_offer_message(),
                parse_mode=ParseMode.HTML,
                reply_markup=get_reply_markup(offer)
            )

    def send_stats(self, chat_id: str,  stats: Counter):
        self.bot.send_message(
            chat_id=chat_id,
            text=f"<b>Initial stats</b><pre>\n</pre><pre>{get_stats_table(stats).get_string()}</pre>",
            parse_mode=ParseMode.HTML
        )

    def send_shutdown_notice(self, chat_id: str):
        self.bot.send_message(
            chat_id=chat_id,
            text='Bot got shutdown.',
            parse_mode=ParseMode.HTML
        )

    def send_error_message(self, chat_id: str, error_message: str):
        self.bot.send_message(
            chat_id=chat_id,
            text=f"An error occurred: <code>{error_message}</code>",
            parse_mode=ParseMode.HTML
        )

    def stop(self):
        self.updater.stop()


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        text=f'Welcome {user.mention_html()}! Your id is: <b>{user.id}</b>',
        parse_mode=ParseMode.HTML,
        reply_markup=ForceReply(selective=True)
    )


def get_reply_markup(offer: Offer) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        *([[InlineKeyboardButton(text=f"Next image ({1}/{len(offer.images)})", callback_data='-'.join([offer.id, 'image', '0']))]] if offer.images else []),
        [
            InlineKeyboardButton(text='Open', url=offer.link),
            InlineKeyboardButton(text='Map', url=f"https://maps.google.com/?q={offer.address}"),
            *([InlineKeyboardButton(text='Send', url=f"https://mail.google.com/mail/?view=cm&fs=1&to={offer.email}&su=Anfrage {offer.address}&body={offer.generate_email_body()}")] if offer.email else []),
            InlineKeyboardButton(text='Text', callback_data='-'.join([offer.id, 'body']))
        ],
        [InlineKeyboardButton(text='Travel times', callback_data='-'.join([offer.id, 'travelTimes']))],
        [InlineKeyboardButton(text='Delete', callback_data='-'.join([offer.id, 'delete']))],
    ])


def image_handler(update: Update, query: CallbackQuery, data: List[str], offer: Offer) -> None:
    original_message = update.callback_query.message
    current_image = int(data[0])
    next_image = (current_image + 1) % len(offer.images)
    query.edit_message_media(
        media=InputMediaPhoto(offer.images[next_image], caption=original_message.caption_html, parse_mode=ParseMode.HTML),
    )
    reply_markup = update.callback_query.message.reply_markup
    reply_markup.inline_keyboard.remove(reply_markup.inline_keyboard[0])
    reply_markup.inline_keyboard.insert(0, [InlineKeyboardButton(
        text=f"Next image ({next_image + 1}/{len(offer.images)})",
        callback_data='-'.join([offer.id, 'image', str(next_image)])
    )])
    query.edit_message_reply_markup(reply_markup=reply_markup)


def body_handler(update: Update, query: CallbackQuery, data: List[str], offer: Offer):
    body = f'''<code>{offer.email or 'No email found'}</code>
<pre>\n</pre>
<code>Anfrage {offer.address}</code>
<pre>\n</pre>
<code>{offer.generate_email_body()}</code>
'''
    if offer.images:
        query.edit_message_caption(
            caption=body,
            parse_mode=ParseMode.HTML,
            reply_markup=update.callback_query.message.reply_markup
        )
    else:
        query.edit_message_text(
            text=body,
            parse_mode=ParseMode.HTML,
            reply_markup=update.callback_query.message.reply_markup
        )


def delete_handler(update: Update, query: CallbackQuery, data: List[str], offer: Offer) -> None:
    update.callback_query.delete_message()


def travel_time_handler(update: Update, query: CallbackQuery, data: List[str], offer: Offer) -> None:
    if offer.travel_times:
        return  # should never be true, but it costs money, so better double-check
    original_message = update.callback_query.message
    gmaps = GMaps()
    offer.travel_times = gmaps.fetch_travel_times(offer.address)
    reply_markup = original_message.reply_markup
    reply_markup.inline_keyboard.remove(reply_markup.inline_keyboard[-2])
    if offer.images:
        query.edit_message_caption(
            caption=f"{original_message.caption_html}<pre>\n</pre><pre>{offer.get_travel_table().get_string()}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=f"{original_message.text_html}<pre>\n</pre><pre>{offer.get_travel_table().get_string()}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )


handlers = {
    'image': image_handler,
    'body': body_handler,
    'delete': delete_handler,
    'travelTimes': travel_time_handler
}


def get_stats_table(stats: Counter) -> PrettyTable:
    stats_table = PrettyTable(
        field_names=['Crawler', 'Count'],
        header=False,
        min_table_width=width_in_characters,
        border=False,
        padding_width=0
    )
    stats_table.align['Crawler'] = 'l'
    stats_table.align['Count'] = 'r'
    stats_table.add_rows(stats.items())
    return stats_table
