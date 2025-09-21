import telebot
import uuid
import json
import urllib3
import time
import re
import requests
from telebot.types import (
    BotCommand, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from datetime import datetime
from info_yt import ADMIN_ID
from database_manger import (
    get_user_balance, deduct_balance, set_user_state,
    get_user_state, get_user_temp_order_data, update_user_balance,get_debt_user
)
from database_manger_auto import add_pending_order,get_user_info, update_user, update_order_status,get_user_total, __init__,update_api,get_api
from tokenbot import TOKEN_AUTO
from info_yt_auto import alnukhba_get,LEVELS,REWARDS,get_user_level,progress_bar,alnukhuba_add, headers,smmcpan_api,smmcpan_url,lirat_url,headers_lirat,card_id,order_id
from quantity_auto import (
    auto_products_display_ff,
    auto_products_display_jawaker,
    auto_products_display_pubg,
    auto_products_display_payeer,
    auto_products_display_usdt,
    auto_products_handle_display_support_pages_instagram,
    auto_products_handle_display_mtn,
    auto_products_handle_display_syriatel,
    handle_auto_products_message_logic,
    get_quantity_btns_for_service,
    auto_products,
    auto_products_prices,
    auto_products_quantity,
    ids
)

# ================== INIT ================== #
__init__()
bot = telebot.TeleBot(TOKEN_AUTO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
bot.set_my_commands([BotCommand("start", "إعادة تشغيل البوت"),BotCommand("id","لإظهار معرف التلغرام الخاص بك")])

# ================== START ================== #
_original_request = requests.request
def dynamic_request(method, url, **kwargs):
    if "headers" not in kwargs:
        kwargs["headers"] = {}
    kwargs["headers"]["Authorization"] = get_api()
    kwargs["headers"]["Content-Type"] = "application/json"
    return _original_request(method, url, **kwargs)
requests.request = dynamic_request
requests.get = lambda url, **kwargs: dynamic_request("GET", url, **kwargs)
requests.post = lambda url, **kwargs: dynamic_request("POST", url, **kwargs)
requests.put = lambda url, **kwargs: dynamic_request("PUT", url, **kwargs)
requests.delete = lambda url, **kwargs: dynamic_request("DELETE", url, **kwargs)
@bot.message_handler(commands=["get_api"])
def get_api_for_admin(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(user_id,"⚠ عذرا صديقي ليس لديك الصلاحية لاستخدام هذا الامر")
        return
    bot.send_message(ADMIN_ID,f"""{get_api()}""")
@bot.message_handler(commands=["edit_api"])
def edit_api(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(user_id,"⚠ عذرا صديقي ليس لديك الصلاحية لاستخدام هذا الامر")
        return
    set_user_state(user_id,'state_awaiting_new_api')
    bot.send_message(user_id,"اهلا بك سيدي! 😊 يرحى كتابة API الجديد 📝")
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'state_awaiting_new_api')
def handle_users_message(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        set_user_state(user_id, None)
        return
    new_api = message.text
    temp_data = {'new_api': new_api, 'parse_mode': None}
    set_user_state(user_id, 'state_awaiting_new_api_confirmation', json.dumps(temp_data))
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد التعديل ✅",callback_data="confirm_new_api")
    btn_cancel = InlineKeyboardButton("إلغاء التعديل ✖",callback_data="cancel_new_api")
    markup.row(btn_confirm,btn_cancel)    
    try:
        bot.send_message(user_id, 
                         f"✉️ هل هذا هو ال API الجديد؟\n\n{new_api}",
                         reply_markup=markup,
                         parse_mode="Markdown")
    except Exception as e:
        print(f"Error previewing broadcast message with parse_mode: {e}")
        bot.send_message(user_id, 
                         f"✉️ ستُرسل الرسالة التالية إلى جميع المستخدمين (مشكلة في عرض التنسيق، ستُرسل كنص عادي):\n\n{new_api}",
                         reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.from_user.id == ADMIN_ID and call.data in ["confirm_new_api","cancel_new_api"])
def handle_users_message_confirmation(call):
    user_id = call.from_user.id
    temp_data = get_user_temp_order_data(user_id)
    if not temp_data or get_user_state(user_id) != 'state_awaiting_new_api_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية إرسال جماعي قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="لا توجد عملية إرسال جماعي قيد الانتظار أو انتهت صلاحيتها."
            )
        except Exception:
            pass
        set_user_state(user_id, None)
        return
    if call.data == "cancel_new_api":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية تجديد ال API  ❌."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الإرسال.", show_alert=False)
        return
    elif call.data == "confirm_new_api":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        new_api = temp_data.get('new_api')
        if not new_api:
            bot.answer_callback_query(call.id, "خطأ: لم يتم العثور على ال API الجديد!", show_alert=True)
            set_user_state(user_id, None)
            return
        try:
            if new_api.startswith("Bearer"):
                update_api(id=1,api=new_api)
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(ADMIN_ID,f"""سيدي تم تعديل ال API بنجاح
                                 {get_api()}""")
                return
            else:
                bot.send_message(ADMIN_ID,"سيدي ال API غير صالح.")
        except Exception as e:
            bot.send_message(ADMIN_ID,f"حدث خطأ أثناء تغيير ال API [{e}]")
@bot.message_handler(commands=["start"])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("حسابي 👤")
    item2 = KeyboardButton("الخدمات 🕹️")
    markup.row(item1, item2)
    bot.send_message(message.chat.id, "أهلا بك في بوت الشحن التلقائي لشركة يلا تكرم")
    bot.send_message(message.chat.id, "القائمة الرئيسية 🏠", reply_markup=markup)
    set_user_state(message.chat.id, None)
@bot.message_handler(commands=["id"])
def get_id(message):
    chat_id = message.from_user.id
    bot.send_message(message.chat.id,f"رقم المعرف الخاص بك هو 🆔 : `{chat_id}`", parse_mode="MarkdownV2")

# ================== HANDLE WALLET INPUT FOR USDT (BEP20) ================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_usdt_bep20')
def handle_wallet_input_for_usdt(message):
    wallet_address = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)

    if not temp_order_data or temp_order_data.get('state') != 'awaiting_usdt_bep20':
        bot.send_message(message.chat.id, "❌ لا يوجد طلب قيد الانتظار. ابدأ من جديد.")
        set_user_state(message.from_user.id, None)
        return
    if not re.fullmatch(r"^0x[a-fA-F0-9]{40}$", wallet_address):
        bot.send_message(message.chat.id, "⚠ العنوان غير صحيح! يجب أن يبدأ بـ 0x وطوله 42 خانة.")
        return

    # حفظ العنوان
    temp_order_data['wallet'] = wallet_address
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    service = temp_order_data['service']
    quantity = temp_order_data['quantity']
    price = temp_order_data['price']

    confirmation_message = (
        "يرجى تأكيد معلومات طلبك:\n"
        f"الخدمة: *{service}* 💲\n"
        f"الكمية: *{quantity}*\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"عنوان المحفظة: ```{wallet_address}```\n\n"
        "هل تريد المتابعة؟"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("تأكيد ✅", callback_data="confirm_usdt_bep20_purchase"),
        InlineKeyboardButton("إلغاء ❌", callback_data="cancel_usdt_bep20_purchase")
    )
    bot.send_message(message.chat.id, confirmation_message, reply_markup=markup, parse_mode="Markdown")

# =============== HANDLE NUMBER INPUT FOR MTN ===============#
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_mtnb')
def handle_number_input_for_mtnb(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_mtnb':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["رصيد MTN"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return
    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_mtnb_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_mtnb_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# =============== HANDLE NUMBER INPUT FOR MTN Cash ===============#
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_mtnc')
def handle_number_input_for_mtnb(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_mtnc':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["MTN Cash"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return
    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_mtnc_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_mtnc_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# =============== HANDLE INPUT ID FOR FREE FIRE AD =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_ffad')
def handle_id_input_for_ffa(message):
    user_id = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_ffad':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["Free Fire"])
    if not re.fullmatch(pattern, user_id):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_id
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_id}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_ffad_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_ffad_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')

# =============== HANDLE INPUT ID FOR FREE FIRE =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_ff')
def handle_id_input_for_ffa(message):
    user_id = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_ff':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["Free Fire"])
    if not re.fullmatch(pattern, user_id):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_id
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_id}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_ffa_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_ffa_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# =============== HANDLE INPUT ID FOR JAWAKER Tokens =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_jawaker_t')
def handle_id_input_for_ffa(message):
    user_id = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_jawaker_t':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["JAWAKER Tokens"])
    if not re.fullmatch(pattern, user_id):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_id
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_id}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_jawaker_t_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_jawaker_t_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')


# =============== HANDLE NUMBER INPUT FOR SYRIATEL CASH =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_syrca')
def handle_number_input_for_syrca(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_syrca':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["Syriatel Cash"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_syrca_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_syrca_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')

# =============== HANDLE NUMBER INPUT FOR PAYEER =================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == "awaiting_payeer")
def handle_number_input_for_payeer(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_payeer':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["Payeer"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_payeer_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_payeer_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')

# ================== HANDLE NUMBER INPUT FOR SYRIATEL ================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_syrba')
def handle_number_input_for_syrba(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_syrba':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["رصيد Syriatel"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_syrba_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_syrba_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')

# ================== HANDLE NUMBER INPUT FOR MTN FATORA ================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_mtnf')
def handle_number_input_for_mtnf(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_mtnf':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["فواتير MTN"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_mtnf_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_mtnf_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# ================== HANDLE NUMBER INPUT FOR PUBG SERVER 1 ================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_pubgS1')
def handle_number_input_for_pubgs1(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_pubgS1':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["PUBG"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_pubgS1_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_pubgS1_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# ================== HANDLE NUMBER INPUT FOR PUBG SERVER 2 ================== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_pubgS2')
def handle_number_input_for_pubgs2(message):
    user_number = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_pubgS2':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["PUBG"])
    if not re.fullmatch(pattern, user_number):
        bot.send_message(message.from_user.id, "⚠ الرقم الذي أدخلته غير صالح. يجب أن يتكون من 10 أرقام فقط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = user_number
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{user_number}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_pubgS2_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_pubgS2_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')

# ================== HANDLE LINK INPUT FOR LIKES INSTAGRAM =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_likes_instagram')
def handle_link_input_for_likes_instagram(message):
    link = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_likes_instagram':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["لايكات Instagram"])
    if not re.fullmatch(pattern, link):
        bot.send_message(message.from_user.id, "⚠ الرابط الذي ادخلته غير صالح, يرجى التأكد من الرابط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = link
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{link}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_likes_instagram_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_likes_instagram_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# ================== HANDLE LINK INPUT FOR WATCH INSTAGRAM =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_watching_instagram')
def handle_link_input_for_watching_instagram(message):
    link = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_watching_instagram':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["لايكات Instagram"])
    if not re.fullmatch(pattern, link):
        bot.send_message(message.from_user.id, "⚠ الرابط الذي ادخلته غير صالح, يرجى التأكد من الرابط.")
        return

    service = temp_order_data.get('service')
    temp_order_data['num_id'] = link
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))

    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')

    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{link}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_watch_instagram_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_watch_instagram_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# ================== HANDLE LINK INPUT FOR LIKES FACEBOOK =============== #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == 'awaiting_likes_facebook')
def handle_link_input_for_watching_instagram(message):
    link = message.text.strip()
    temp_order_data = get_user_temp_order_data(message.from_user.id)
    if not temp_order_data or temp_order_data.get('state') != 'awaiting_likes_facebook':
        bot.send_message(message.from_user.id, "عذراً، لم يتم العثور على طلب قيد الانتظار. يرجى البدء من جديد.")
        set_user_state(message.from_user.id, None)
        return
    pattern = str(ids["لايكات لمنشورات Facebook"])
    if not re.fullmatch(pattern, link):
        bot.send_message(message.from_user.id, "⚠ الرابط الذي ادخلته غير صالح, يرجى التأكد من الرابط.")
        return
    service = temp_order_data.get('service')
    temp_order_data['num_id'] = link
    temp_order_data['status'] = 'awaiting_confirmation'
    set_user_state(message.from_user.id, 'awaiting_confirmation', json.dumps(temp_order_data))
    quantity = temp_order_data.get('quantity')
    price = temp_order_data.get('price')
    confirmation_message = (
        "الرجاء تأكيد المعلومات قبل إتمام الشراء:\n"
        f"الخدمة: *{service}* 🕹️\n"
        f"الكمية: *{quantity}* 🔆\n"
        f"السعر: *{price:.2f}* 💰\n"
        f"الرقم الخاص بك: ```{link}```\n\n"
        "هل أنت متأكد من هذه المعلومات؟"
    )
    markup = InlineKeyboardMarkup()
    btn_confirm = InlineKeyboardButton("تأكيد الشراء ✅", callback_data="confirm_likes_facebook_purchase")
    btn_cancel = InlineKeyboardButton("إلغاء الشراء ❌", callback_data="cancel_likes_facebook_purchase")
    markup.add(btn_confirm, btn_cancel)
    bot.send_message(message.from_user.id, confirmation_message, reply_markup=markup, parse_mode='Markdown')
# ================== MAIN SERVICES ================== #
@bot.message_handler(func=lambda message: message.text == "الخدمات 🕹️")
def display_services(message):
    markup = InlineKeyboardMarkup()
    games_btn = InlineKeyboardButton("قائمة الألعاب 🕹", callback_data="auto_games")
    bc_btn = InlineKeyboardButton("الرصيد والعملات 🎟️", callback_data="auto_balance")
    crypto_btn = InlineKeyboardButton("العملات المشفرة 💲",callback_data="auto_crypto")
    support_pages_btn = InlineKeyboardButton("دعم الصفحات 📱",callback_data="support_pages")
    markup.add(games_btn)
    markup.add(bc_btn)
    markup.add(crypto_btn)
    markup.add(support_pages_btn)
    bot.send_message(message.chat.id, "اختر من قائمة خدمات الشحن التلقائية ما تريد:", reply_markup=markup)
@bot.message_handler(func=lambda message: message.text == "حسابي 👤")
def show_balance(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    total = get_user_total(user_id)
    debt = get_debt_user(user_id)
    old_level, balance = get_user_info(user_id)
    new_level, next_level = get_user_level(total)
    if new_level > old_level:
        reward = 0
        for lvl in range(old_level+1, new_level+1):
            if lvl in REWARDS:
                reward += REWARDS[lvl]
        update_user(user_id, new_level=new_level, add_balance=reward)
        balance += reward
        bot.send_message(user_id, f"🎉 مبروك! صرت Prime {new_level} وأضيف لرصيدك {reward}$")

    bar, percent = progress_bar(total, new_level, next_level)

    if next_level:
        remain = next_level[1] - total
        text = f"""
🔑 حسابك:
- رصيدك: ${balance:.2f}
- رصيدك المدين: ${debt:.2f}
- المستوى الحالي: Prime {new_level}
- مجموع مشترياتك: ${total:.2f}
- باقي لك ${remain:.2f} لتوصل Prime {next_level[0]}
- التقدم: {bar} [{percent}%]
"""
    else:
        text = f"""
🔑 حسابك:
- رصيدك: ${balance:.2f}
- رصيدك المدين: ${debt:.2f}
- المستوى الحالي: Prime {new_level}
- مجموع مشترياتك: ${total:.2f}
- انت بأعلى مستوى 🎉
- التقدم: {bar}
"""
    bot.send_message(user_id, text)
# ================== INLINE QUERIES ================== #
@bot.inline_handler(func=lambda query: query.query.strip().startswith("FreeFire"))
def query_ff(query):
    results = auto_products_display_ff(query)
    bot.answer_inline_query(query.id,results,cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith("Payeer"))
def query_payeer(query):
    results = auto_products_display_payeer(query)
    bot.answer_inline_query(query.id,results,cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith("USDT"))
def query_usdt(query):
    results = auto_products_display_usdt(query)
    bot.answer_inline_query(query.id,results,cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith("JAWAKER"))
def query_jawaker(query):
    results = auto_products_display_jawaker(query)
    bot.answer_inline_query(query.id,results,cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith("PUBG"))
def query_pubg(query):
    results = auto_products_display_pubg(query)
    bot.answer_inline_query(query.id,results,cache_time=1) 
@bot.inline_handler(func=lambda query: query.query.strip().startswith('Syriatel_List'))
def query_syriatel(query):
    results = auto_products_handle_display_syriatel(query)
    bot.answer_inline_query(query.id, results, cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith('support_pages_facebook'))
def query_facebook(query):
    results = auto_products_handle_display_support_pages_facebook(query)
    bot.answer_inline_query(query.id, results, cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith('MTN_List'))
def query_mtn(query):
    results = auto_products_handle_display_mtn(query)
    bot.answer_inline_query(query.id, results, cache_time=1)
@bot.inline_handler(func=lambda query: query.query.strip().startswith('support_pages_instagram'))
def query_instagram(query):
    results = auto_products_handle_display_support_pages_instagram(query)
    bot.answer_inline_query(query.id, results, cache_time=1)
@bot.callback_query_handler(func=lambda call: call.data in ["auto_balance"])
def choose_auto_balance(call):
    if call.data == "auto_balance":    
        markup = InlineKeyboardMarkup()
        syriatel_btn = InlineKeyboardButton("Syriatel",switch_inline_query_current_chat='Syriatel_List')
        mtn_btn = InlineKeyboardButton("MTN",switch_inline_query_current_chat='MTN_List')
        back_btn = InlineKeyboardButton("الرجوع إلى الخلف 🔙",callback_data="back_to_services")
        markup.add(syriatel_btn)
        markup.add(mtn_btn)
        markup.add(back_btn)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="اختر الشبكة التي تريد التحويل إليها:",reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data in ["support_pages","back_to_services","auto_games","auto_crypto"])
def chose_social_pages_service(call):
    if call.data == "support_pages":    
        markup_s = InlineKeyboardMarkup()
        instagram_btn = InlineKeyboardButton("Instagram",switch_inline_query_current_chat='support_pages_instagram')
        #facebook_btn = InlineKeyboardButton("Facebook",switch_inline_query_current_chat='support_pages_facebook')
        back_btn = InlineKeyboardButton("الرجوع إلى الخلف 🔙",callback_data="back_to_services")
        markup_s.add(instagram_btn)
        #markup.add(facebook_btn)
        markup_s.add(back_btn)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="اختر نوع المنصة التي تريد ان تدعمها:",reply_markup=markup_s)
    elif call.data == "back_to_services":
        mark = InlineKeyboardMarkup()
        games_btn = InlineKeyboardButton("قائمة الألعاب 🕹", callback_data="auto_games")
        bc_btn = InlineKeyboardButton("الرصيد والعملات 🎟️", callback_data="auto_balance")
        crypto_btn = InlineKeyboardButton("العملات المشفرة 💲",callback_data="auto_crypto")
        support_pages_btn = InlineKeyboardButton("دعم الصفحات 📱",callback_data="support_pages")
        mark.add(games_btn)
        mark.add(bc_btn)
        mark.add(crypto_btn)
        mark.add(support_pages_btn)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="اختر من قائمة خدمات الشحن التلقائية ما تريد:", reply_markup=mark)
    elif call.data == "auto_games":
        markup_ag = InlineKeyboardMarkup()
        ff_btn = InlineKeyboardButton("Free Fire",switch_inline_query_current_chat="FreeFire")
        pubg_btn = InlineKeyboardButton("PUBG",switch_inline_query_current_chat="PUBG")
        jawaker_btn = InlineKeyboardButton("JAWAKER",switch_inline_query_current_chat="JAWAKER")
        back_btn_ag = InlineKeyboardButton("الرجوع إلى الخلف 🔙",callback_data="back_to_services")
        markup_ag.add(ff_btn)
        markup_ag.add(pubg_btn)
        markup_ag.add(jawaker_btn)
        markup_ag.add(back_btn_ag)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="اختر من قائمة خدمات الشحن التلقائية ما تريد:", reply_markup=markup_ag)
    elif call.data == "auto_crypto":
        markup_ac = InlineKeyboardMarkup()
        payeer_btn = InlineKeyboardButton("Payeer",switch_inline_query_current_chat="Payeer")
        usdt = InlineKeyboardButton("USDT",switch_inline_query_current_chat="USDT")
        back_btn_ac = InlineKeyboardButton("الرجوع إلى الخلف 🔙",callback_data="back_to_services")
        markup_ac.add(payeer_btn)
        markup_ac.add(usdt)
        markup_ac.add(back_btn_ac)
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="اختر من قائمة خدمات الشحن التلقائية ما تريد:", reply_markup=markup_ac)

# ================== HANDLE SERVICES ================== #
@bot.message_handler(func=lambda message: message.text in auto_products.values())
def handle_service(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    service = handle_auto_products_message_logic(message)
    if service and service in auto_products_prices:
        options_markup = get_quantity_btns_for_service(service)
        bot.send_message(
            message.chat.id,
            f"لقد اخترت *{service} Auto* الرجاء اختيار الكمية التي تريد أن تصلك 💵",
            reply_markup=options_markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, f"غير متوفر حالياً {service} Auto.")

# =============== HANDLE QUANTITES =============== #
@bot.callback_query_handler(func=lambda call: '|' in call.data and call.data.split('|')[0] in auto_products)
def handle_quantity(call):
    user_id = call.from_user.id
    try:
        service_name, quantity_value = call.data.split('|')
    except ValueError:
        bot.answer_callback_query(call.id, "بيانات غير صالحة. يرجى المحاولة مرة أخرى.", show_alert=True)
        return
    if service_name not in auto_products or \
       quantity_value not in auto_products_prices.get(service_name, {}) or \
       float(auto_products_prices[service_name][quantity_value]) <= 0:
        bot.answer_callback_query(call.id, "حدث خطأ: اختيار غير صالح للعبة أو الكمية. يرجى المحاولة مرة أخرى.", show_alert=True)
        return
    price = float(auto_products_prices[service_name][quantity_value])
    current_balance = get_user_balance(user_id)
    if current_balance is None:
        bot.answer_callback_query(call.id, "عذراً، لم نتمكن من الوصول إلى رصيدك. يرجى المحاولة لاحقاً.", show_alert=True)
        return
    if current_balance >= price:
        if service_name == 'Free Fire':
            state = 'awaiting_ff'
        elif service_name == 'Syriatel Cash':
            state = 'awaiting_syrca'
        elif service_name == 'رصيد Syriatel':
            state = 'awaiting_syrba'
        elif service_name == 'رصيد MTN':
            state = 'awaiting_mtnb'
        elif service_name == 'Payeer':
            state = 'awaiting_payeer'
        elif service_name == 'USDT (BEP20)':
            state = 'awaiting_usdt_bep20'
        elif service_name == 'لايكات Instagram':
            state = 'awaiting_likes_instagram'
        elif service_name == 'مشاهدات Instagram':
            state = 'awaiting_watching_instagram'
        elif service_name == 'فواتير MTN':
            state = 'awaiting_mtnf'
        elif service_name == 'لايكات لمنشورات Facebook':
            state = 'awaiting_likes_facebook'
        elif service_name == 'pubgS1':
            state = 'awaiting_pubgS1'
        elif service_name == 'pubgS2':
            state = 'awaiting_pubgS2'
        elif service_name == 'MTN Cash':
            state = 'awaiting_mtnc'
        elif service_name == 'JAWAKER TOKENS':
            state = 'awaiting_jawaker_t'
        elif service_name == 'عضويات Free Fire':
            state = 'awaiting_ffad'
        temp_data = json.dumps({
            "service": service_name,
            "quantity": quantity_value,
            "price": price,
            "state": state
        })
        set_user_state(user_id, state, temp_data)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(f"""تمام! رصيدك كافٍ للشراء 😊
                        لقد اخترت *{service_name} Auto* 🕹️
                        بكمية *{quantity_value}* 🔆
                        سعرها *{price:.2f}* 💰"""), 
            parse_mode='Markdown'
        )
        if service_name == 'Free Fire':
            id = f"يرجى ارسال ال ID الخاص بـ *Free Fire Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'عضويات Free Fire':
            id = f"يرجى ارسال ال ID الخاص بـ *عضويات Free Fire Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'Syriatel Cash':
            id = f"يرجى ارسال الرقم الخاص بـ *Syriatel Cash Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'رصيد Syriatel':
            id = f"يرجى ارسال الرقم الخاص بـ *رصيد Syriatel Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'رصيد MTN':
            id = f"يرجى ارسال الرقم الخاص بـ *رصيد MTN Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'Payeer':
            id = f"يرجى ارسال رقم المحفظة الخاص بـ *Payeer Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'USDT (BEP20)':
            id = f"يرجى ارسال رابط المحفظة الخاص بـ *USDT (BEP20) Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'لايكات Instagram':
            id = f"يرجى ارسال رابط الريل الخاص بـ *لايكات Instagram Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'مشاهدات Instagram':
            id = f"يرجى ارسال رابط الريل الخاص بـ *مشاهدات Instagram Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'فواتير MTN':
            id = f"يرجى ارسال الرقم الخاص بـ *فواتير MTN Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'لايكات لمنشورات Facebook':
            id = f"يرجى ارسال الرابط الخاص بـ *لايكات لمنشور Facebook Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'pubgS1':
            id = f"يرجى ارسال ال ID الخاص بـ *PUBG سيرفر 1 Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'pubgS2':
            id = f"يرجى ارسال ال ID الخاص بـ *PUBG سيرفر 2 Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'MTN Cash':
            id = f"يرجى ارسال الرقم الخاص بـ *MTN Cash Auto* لكي تتمكن من الشحن 🧰"
        elif service_name == 'JAWAKER TOKENS':
            id = f"يرجى ارسال ال ID الخاص بـ *JAWAKER Tokens Auto* لكي تتمكن من الشحن 🧰"
        bot.send_message(call.message.chat.id,id,parse_mode="Markdown")
        bot.answer_callback_query(call.id, text=f"الرصيد كافٍ، يرجى إدخال الرقم.", show_alert=False)
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(f"""عذرا ليس لديك رصيد كافٍ لإتمام عملية الشراء 😢
سعر الخدمة التي تريدها *{price:.2f}* 💰
يرجى إعادة تعبئة رصيدك والمحاولة من جديد 😊"""),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, text=f"رصيدك غير كافٍ. تحتاج إلى {price:.2f}.", show_alert=True)
    return
# =============== CONFIRM / CANCEL FOR SYRIATEL CASH ================#
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_syrca_purchase","cancel_syrca_purchase"])
def handle_final_syrca_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_syrca_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_syrca_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ادخل رقم جوالك": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 1442,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4())
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)  # refund
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution_time = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution_time}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)

# =============== CONFIRM / CANCEL FOR USDT (BEP20) =================#
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_usdt_bep20_purchase","cancel_usdt_bep20_purchase"])
def handle_final_usdt_bep20_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_usdt_bep20_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_usdt_bep20_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['wallet']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {
                        "ادخل رابط المحفظة": f"{user_number}",
                        "يرجى اختيار الشبكة": "BSC ( BEP20 ) Fee 0.1$"},
                    "currency": "USD",
                    "product_id": 631,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4()),
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        replays = order_data.get("data",{}).get("replay",[])
                        execution_time = order_data.get("data",{}).get("diff")
                        txid = None
                        if replays:
                            raw_txid = replays[0].get("replay", [])[0]
                            if raw_txid and "0x" in raw_txid:
                                txid = raw_txid.split()[-1].strip()
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            if txid: 
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
    رقم الطلب: {api_order_id}
    الخدمة: {service} Auto
    TXID: {txid}
    ⏰ مدة تنفيذ الطلب: {execution_time}""")
                                break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# =============== CONFIRM / CANCEL FOR FREE FIRE =============== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_ffa_purchase","cancel_ffa_purchase"])
def handle_final_ffa_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_ffa_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_ffa_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                if quantity == '110':    
                    payload = {
                        "require": {"أيدي الحساب": f"{user_number}"},
                        "currency": "USD",
                        "order_uuid": str(uuid.uuid4()),
                        "product_id": 1683,
                        "quantity": 1,
                    }
                    try:    
                        post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                        post_data = post_response.json()
                        api_order_id = post_data.get("data", {}).get("order_id")
                    except requests.JSONDecodeError as e:
                        print(f"Error on: [{e}]")
                        bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                        bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                        bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                        update_user_balance(user_id,price)
                        return
                    if not api_order_id:
                        bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                        update_user_balance(user_id, price)
                        return
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {api_order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                    while True:
                        try:
                            get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                            order_data = get_response.json()
                            status = order_data.get("data", {}).get("status")
                            execution = order_data.get("data",{}).get("diff")
                            if status == "accept":
                                update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
    رقم الطلب: {api_order_id}
    الخدمة: {service} Auto
    ⏰ مدة تنفيذ الطلب: {execution}""")
                                break
                            elif status == "reject":
                                update_order_status(order_id, status)
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
    الرقم: {api_order_id}
    الحالة: {status}""")
                                update_user_balance(user_id, price)
                                break
                        except requests.RequestException as e:
                            print("Error connecting to API", e)
                            time.sleep(2)
                
                elif quantity == '230':    
                        payload = {
                            "require": {"أيدي الحساب": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1684,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return
                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                elif quantity == '583':    
                        payload = {
                            "require": {"أيدي الحساب": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1687,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return
                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                elif quantity == '1188':    
                        payload = {
                            "require": {"أيدي الحساب": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1689,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return
                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                else:
                        bot.send_message(user_id, "❌ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", parse_mode='Markdown')
                        bot.answer_callback_query(call.id, "ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", show_alert=True)
                        update_user_balance(user_id, price)
        set_user_state(user_id, None)
# =============== CONFIRM / CANCEL FOR MTN BALANCE =============== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_mtnb_purchase", "cancel_mtnb_purchase"])
def handle_final_mtnb_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_mtnb_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_mtnb_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ادخل رقم هاتفك": f"{user_number}"},
                    "currency": "USD",
                    "order_uuid": f"{str(uuid.uuid4())}",
                    "product_id": 532,
                    "quantity": f"{float(quantity)}",
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# ================== CONFIRM / CANCEL FOR SYRIATEL BALANCE ================== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_syrba_purchase", "cancel_syrba_purchase"])
def handle_final_syrba_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_syrba_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_syrba_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ادخل رقم جوالك": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 1444,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4()),  # UUID جديد لكل طلب
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not post_response:
                        bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                        bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                        update_user_balance(user_id,price)
                        return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)  # refund
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# =================== CONFIRM / CANCEL FOR PAYEER ======================== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_payeer_purchase","cancel_payeer_purchase"])
def handle_final_payeer_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_payeer_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_payeer_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"رقم الحساب": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 1510,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4())
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        replays = order_data.get("data",{}).get("replay",[])
                        execution_time = order_data.get("data",{}).get("diff")
                        operation_id = None
                        if replays:
                            raw_replay = replays[0].get("replay",[])[0]
                            if raw_replay and "رقم العملية" in raw_replay:
                                operation_id = raw_replay.split(":")[-1].strip()
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
رقم العملية: {operation_id}
⏰ مدة تنفيذ الطلب: {execution_time}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# ================== CONFIRM / CANCEL FOR MTN FATORA ================== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_mtnf_purchase", "cancel_mtnf_purchase"])
def handle_final_mtnf_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_mtnf_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_mtnf_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ادخل رقم هاتفك": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 1500,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4()),  # UUID جديد لكل طلب
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)  # refund
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# ============== CONFIRM / CANCEL FOR LIKES INSTAGRAM ================= #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_likes_instagram_purchase","cancel_likes_instagram_purchase"])
def handle_final_likes_instagram_fonfirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_likes_instagram_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_likes_instagram_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        link = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=link
            )
            if order_id:
                balance_resp = requests.post(url=smmcpan_url,data={"key": smmcpan_api, "action": "balance"})
                balance_resp.raise_for_status()
                balance = float(balance_resp.json().get("balance"))
                if balance >= 1:
                    order_payload = {
                        "key": smmcpan_api,
                        "action": "add",
                        "service": "20980",
                        "link": link,
                        "quantity": quantity
                    }
                    order_resp = requests.post(url=smmcpan_url,data=order_payload)
                    order_resp.raise_for_status()
                    order_result = order_resp.json()
                    if "order" in order_result:
                        order_id = order_result["order"]
                        bot.delete_message(chat_id=sticker_msg.chat.id, message_id=sticker_msg.message_id)
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")
                        for i in range(1000000):
                            status_resp = requests.post(url=smmcpan_url, data={
                                "key": smmcpan_api,
                                "action": "status",
                                "order": order_id
                            })

                            try:
                                status_resp.raise_for_status()   # يتأكد أن الرد مو 4xx/5xx
                                status = status_resp.json()      # يحاول يحول JSON
                            except ValueError:
                                bot.send_message(call.message.chat.id, f"⚠️ الرد مش JSON:\n{status_resp.text}")
                                return

                            order_status = status.get("status")
                            if order_status == "Completed":
                                update_order_status(order_id=order_id, status="accept")
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
                        رقم الطلب: {order_id}
                        الخدمة: {service} Auto
                        الكمية: {quantity}
                        الرابط: {link}""")
                                return
                            elif order_status == "Cancelled":
                                update_order_status(order_id=order_id, status="reject")
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
                        الرقم: {order_id}
                        الحالة: {order_status}""")
                                update_user_balance(user_id=call.message.from_user.id, amount_to_add=price)
                                return
                            else:
                                # إذا الطلب لسا "In progress" أو حالة تانية
                                print(f"Order Status {order_status}")
                                time.sleep(4)

                    elif order_result.get("error") == 'neworder.error.not_enough_funds':
                        bot.send_message(call.message.chat.id,"ليس لدى الإدارة رصيد كافٍ لإتمام عملية شرائك, يرجى إعلام الإدارة بذلك.")
                else:
                    bot.send_message(call.message.chat.id,"رصيد الإدارة منخفض جدا, يرجى إعلامهم بذلك.")
                set_user_state(user_id, None)
# ============== CONFIRM / CANCEL FOR WATCH INSTAGRAM ================= #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_watch_instagram_purchase","cancel_watch_instagram_purchase"])
def handle_final_likes_instagram_fonfirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_watch_instagram_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_watch_instagram_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        link = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=link
            )
            if order_id:
                balance_resp = requests.post(url=smmcpan_url,data={"key": smmcpan_api, "action": "balance"})
                balance_resp.raise_for_status()
                balance = float(balance_resp.json().get("balance"))
                if balance >= 0.1:
                    order_payload = {
                        "key": smmcpan_api,
                        "action": "add",
                        "service": "18855",
                        "link": link,
                        "quantity": quantity
                    }
                    order_resp = requests.post(url=smmcpan_url,data=order_payload)
                    order_resp.raise_for_status()
                    order_result = order_resp.json()
                    if "order" in order_result:
                        order_id = order_result["order"]
                        bot.delete_message(chat_id=sticker_msg.chat.id, message_id=sticker_msg.message_id)
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")
                        for i in range(1000000):
                            status_resp = requests.post(url=smmcpan_url, data={
                                "key": smmcpan_api,
                                "action": "status",
                                "order": order_id
                            })

                            try:
                                status_resp.raise_for_status()   # يتأكد أن الرد مو 4xx/5xx
                                status = status_resp.json()      # يحاول يحول JSON
                            except ValueError:
                                bot.send_message(call.message.chat.id, f"⚠️ الرد مش JSON:\n{status_resp.text}")
                                return

                            order_status = status.get("status")
                            if order_status == "Completed":
                                update_order_status(order_id=order_id, status="accept")
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
                        رقم الطلب: {order_id}
                        الخدمة: {service} Auto
                        الكمية: {quantity}
                        الرابط: {link}""")
                                return
                            elif order_status == "Cancelled":
                                update_order_status(order_id=order_id, status="reject")
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
                        الرقم: {order_id}
                        الحالة: {order_status}""")
                                update_user_balance(user_id=call.message.from_user.id, amount_to_add=price)
                                return
                            else:
                             
                                print(f"Order Status {order_status}")
                                time.sleep(4)

                    elif order_result.get("error") == 'neworder.error.not_enough_funds':
                        bot.send_message(call.message.chat.id,"ليس لدى الإدارة رصيد كافٍ لإتمام عملية شرائك, يرجى إعلام الإدارة بذلك.")
                else:
                    bot.send_message(call.message.chat.id,"رصيد الإدارة منخفض جدا, يرجى إعلامهم بذلك.")
                set_user_state(user_id, None)
# ============== CONFIRM / CANCEL FOR LIKES FACEBOOK ================= #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_likes_facebook_purchase","cancel_likes_facebook_purchase"])
def handle_final_likes_instagram_fonfirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_likes_facebook_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_likes_facebook_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        link = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=link
            )
            if order_id:
                balance_resp = requests.post(url=smmcpan_url,data={"key": smmcpan_api, "action": "balance"})
                balance_resp.raise_for_status()
                balance = float(balance_resp.json().get("balance"))
                if balance >= 0.1:
                    order_payload = {
                        "key": smmcpan_api,
                        "action": "add",
                        "service": "21142",
                        "link": link,
                        "quantity": quantity
                    }
                    order_resp = requests.post(url=smmcpan_url,data=order_payload)
                    order_resp.raise_for_status()
                    order_result = order_resp.json()
                    if "order" in order_result:
                        order_id = order_result["order"]
                        bot.delete_message(chat_id=sticker_msg.chat.id, message_id=sticker_msg.message_id)
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")
                        for i in range(1000000):
                            status_resp = requests.post(url=smmcpan_url, data={
                                "key": smmcpan_api,
                                "action": "status",
                                "order": order_id
                            })

                            try:
                                status_resp.raise_for_status()   # يتأكد أن الرد مو 4xx/5xx
                                status = status_resp.json()      # يحاول يحول JSON
                            except ValueError:
                                bot.send_message(call.message.chat.id, f"⚠️ الرد مش JSON:\n{status_resp.text}")
                                return

                            order_status = status.get("status")
                            if order_status == "Completed":
                                update_order_status(order_id=order_id, status="accept")
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
                        رقم الطلب: {order_id}
                        الخدمة: {service} Auto
                        الكمية: {quantity}
                        الرابط: {link}""")
                                return
                            elif order_status == "Cancelled":
                                update_order_status(order_id=order_id, status="reject")
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
                        الرقم: {order_id}
                        الحالة: {order_status}""")
                                update_user_balance(user_id=call.message.from_user.id, amount_to_add=price)
                                return
                            else:
                                # إذا الطلب لسا "In progress" أو حالة تانية
                                print(f"Order Status {order_status}")
                                time.sleep(4)

                    elif order_result.get("error") == 'neworder.error.not_enough_funds':
                        bot.send_message(call.message.chat.id,"ليس لدى الإدارة رصيد كافٍ لإتمام عملية شرائك, يرجى إعلام الإدارة بذلك.")
                else:
                    bot.send_message(call.message.chat.id,"رصيد الإدارة منخفض جدا, يرجى إعلامهم بذلك.")
                set_user_state(user_id, None)
# =============== CONFIRM / CANCEL FOR PUBG SERVER 1 =============== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_pubgS1_purchase","cancel_pubgS1_purchase"])
def handle_final_pubgS1_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_pubgS1_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_pubgS1_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                if quantity == '60':    
                    payload = {
                        "require": {"أيدي حساب الببجي": f"{user_number}"},
                        "currency": "USD",
                        "order_uuid": str(uuid.uuid4()),
                        "product_id": 1630,
                        "quantity": 1,
                    }
                    try:    
                        post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                        post_data = post_response.json()
                        api_order_id = post_data.get("data", {}).get("order_id")
                    except requests.JSONDecodeError as e:
                        print(f"Error on: [{e}]")
                        bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                        bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                        bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                        update_user_balance(user_id,price)
                        return
                    if not api_order_id:
                        bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                        update_user_balance(user_id, price)
                        return
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {api_order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                    while True:
                        try:
                            get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                            order_data = get_response.json()
                            status = order_data.get("data", {}).get("status")
                            execution = order_data.get("data",{}).get("diff")
                            if status == "accept":
                                update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
    رقم الطلب: {api_order_id}
    الخدمة: {service} Auto
    ⏰ مدة تنفيذ الطلب: {execution}""")
                                break
                            elif status == "reject":
                                update_order_status(order_id, status)
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
    الرقم: {api_order_id}
    الحالة: {status}""")
                                update_user_balance(user_id, price)
                                break
                        except requests.RequestException as e:
                            print("Error connecting to API", e)
                            time.sleep(2)
                
                elif quantity == '325':    
                        payload = {
                            "require": {"أيدي حساب الببجي": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1631,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return
                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                elif quantity == '660':    
                        payload = {
                            "require": {"أيدي حساب الببجي": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1632,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return
                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                else:
                        bot.send_message(user_id, "❌ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", parse_mode='Markdown')
                        bot.answer_callback_query(call.id, "ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", show_alert=True)
                        update_user_balance(user_id, price)
        set_user_state(user_id, None)
# =============== CONFIRM / CANCEL FOR PUBG SERVER 2 =============== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_pubgS2_purchase","cancel_pubgS2_purchase"])
def handle_final_ffa_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_pubgS2_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_pubgS2_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                if quantity == '60':    
                    payload = {
                        "require": {"أيدي ببجي": f"{user_number}"},
                        "currency": "USD",
                        "order_uuid": str(uuid.uuid4()),
                        "product_id": 1676,
                        "quantity": 1,
                    }
                    try:    
                        post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                        post_data = post_response.json()
                        api_order_id = post_data.get("data", {}).get("order_id")
                    except requests.JSONDecodeError as e:
                        print(f"Error on: [{e}]")
                        bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                        bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                        bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                        update_user_balance(user_id,price)
                        return
                    if not api_order_id:
                        bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                        update_user_balance(user_id, price)
                        return
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {api_order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                    while True:
                        try:
                            get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                            order_data = get_response.json()
                            status = order_data.get("data", {}).get("status")
                            execution = order_data.get("data",{}).get("diff")
                            if status == "accept":
                                update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
    رقم الطلب: {api_order_id}
    الخدمة: {service} Auto
    ⏰ مدة تنفيذ الطلب: {execution}""")
                                break
                            elif status == "reject":
                                update_order_status(order_id, status)
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
    الرقم: {api_order_id}
    الحالة: {status}""")
                                update_user_balance(user_id, price)
                                break
                        except requests.RequestException as e:
                            print("Error connecting to API", e)
                            time.sleep(2)
                
                elif quantity == '325':    
                        payload = {
                            "require": {"أيدي ببجي": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1677,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return

                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                elif quantity == '660':    
                        payload = {
                            "require": {"أيدي ببجي": f"{user_number}"},
                            "currency": "USD",
                            "order_uuid": str(uuid.uuid4()),
                            "product_id": 1678,
                            "quantity": 1,
                        }
                        try:    
                            post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                            post_data = post_response.json()
                            api_order_id = post_data.get("data", {}).get("order_id")
                        except requests.JSONDecodeError as e:
                            print(f"Error on: [{e}]")
                            bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                            bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                            bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                            update_user_balance(user_id,price)
                            return

                        if not api_order_id:
                            bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                            update_user_balance(user_id, price)
                            return

                        bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
        رقم الطلب: {api_order_id}
        سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                        while True:
                            try:
                                get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                                order_data = get_response.json()
                                status = order_data.get("data", {}).get("status")
                                execution = order_data.get("data",{}).get("diff")
                                if status == "accept":
                                    update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                    bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
        رقم الطلب: {api_order_id}
        الخدمة: {service} Auto
        ⏰ مدة تنفيذ الطلب: {execution}""")
                                    break
                                elif status == "reject":
                                    update_order_status(order_id, status)
                                    bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
        الرقم: {api_order_id}
        الحالة: {status}""")
                                    update_user_balance(user_id, price)
                                    break
                            except requests.RequestException as e:
                                print("Error connecting to API", e)
                                time.sleep(2)
                else:
                        bot.send_message(user_id, "❌ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", parse_mode='Markdown')
                        bot.answer_callback_query(call.id, "ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", show_alert=True)
                        update_user_balance(user_id, price)
        set_user_state(user_id, None)
# ================== CONFIRM / CANCEL FOR MTN Cash ================== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_mtnc_purchase", "cancel_mtnc_purchase"])
def handle_final_mtnf_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_mtnc_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_mtnc_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ادخل رقم هاتفك": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 1500,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4()),  # UUID جديد لكل طلب
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)  # refund
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# ================== CONFIRM / CANCEL FOR JAWAKER Tokens ================== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_jawaker_t_purchase", "cancel_jawaker_t_purchase"])
def handle_final_mtnf_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)

    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_jawaker_t_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_jawaker_t_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                payload = {
                    "require": {"ايدي الحساب": f"{user_number}"},
                    "currency": "USD",
                    "product_id": 809,
                    "quantity": f"{float(quantity)}",
                    "order_uuid": str(uuid.uuid4()),  # UUID جديد لكل طلب
                }
                try:    
                    post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                    post_data = post_response.json()
                    api_order_id = post_data.get("data", {}).get("order_id")
                except requests.JSONDecodeError as e:
                    print(f"Error on: [{e}]")
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                    bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                    update_user_balance(user_id,price)
                    return
                if not api_order_id:
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id, "⚠ عذرا, حدث خطأ فني من قبلنا...")
                    update_user_balance(user_id, price)  # refund
                    return
                bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
رقم الطلب: {api_order_id}
سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                while True:
                    try:
                        get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                        order_data = get_response.json()
                        status = order_data.get("data", {}).get("status")
                        execution = order_data.get("data",{}).get("diff")
                        if status == "accept":
                            update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                            bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
رقم الطلب: {api_order_id}
الخدمة: {service} Auto
⏰ مدة تنفيذ الطلب: {execution}""")
                            break
                        elif status == "reject":
                            update_order_status(order_id, status)
                            bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
الرقم: {api_order_id}
الحالة: {status}""")
                            update_user_balance(user_id, price)
                            break
                    except requests.RequestException as e:
                        print("Error connecting to API", e)
                        time.sleep(2)
            else:
                bot.send_message(user_id, "❌ حدث خطأ أثناء تسجيل طلبك. يرجى المحاولة مرة أخرى.", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "خطأ في تسجيل الطلب.", show_alert=True)
                update_user_balance(user_id, price)
    set_user_state(user_id, None)
# =============== CONFIRM / CANCEL FOR FREE FIRE AD =============== #
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_ffad_purchase","cancel_ffad_purchase"])
def handle_final_ffa_confirmation(call):
    user_id = call.from_user.id
    temp_order_data = get_user_temp_order_data(user_id)
    if not temp_order_data or temp_order_data.get('status') != 'awaiting_confirmation':
        bot.answer_callback_query(call.id, "لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها.", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="لا توجد عملية شراء قيد الانتظار أو انتهت صلاحيتها. يرجى البدء من جديد."
        )
        set_user_state(user_id, None)
        return

    if call.data == "cancel_ffad_purchase":
        set_user_state(user_id, None)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="تم إلغاء عملية الشراء ❌. يمكنك البدء من جديد."
        )
        bot.answer_callback_query(call.id, "تم إلغاء الشراء.", show_alert=False)
        return
    elif call.data == "confirm_ffad_purchase":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        sticker_msg = bot.send_sticker(call.message.chat.id, "CAACAgQAAxkBAAIbZ2jBvoTYV8jGPQX1Mct7b65abBsaAALEGQACCp8QUk-XUM-1ZpU9NgQ")
        service = temp_order_data['service']
        quantity = temp_order_data['quantity']
        price = temp_order_data['price']
        user_number = temp_order_data['num_id']

        current_balance = get_user_balance(user_id)
        if current_balance is None or current_balance < price:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"""❌ عذراً، رصيدك غير كافٍ لإتمام هذه العملية 😢
متبقي **{price - (current_balance or 0):.2f}** 💰 ,يرجى شحن رصيدك والمحاولة من جديد.""",
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام الشراء.", show_alert=True)
            set_user_state(user_id, None)
            return
        if deduct_balance(user_id, price):
            order_id = add_pending_order(
                user_id=user_id,
                first_name=call.from_user.first_name,
                service=service,
                quantity=quantity,
                price=price,
                num_id=user_number
            )
            if order_id:
                if quantity == 'عضوية شهرية':    
                    payload = {
                        "require": {"أيدي اللاعب": f"{user_number}"},
                        "currency": "USD",
                        "order_uuid": str(uuid.uuid4()),
                        "product_id": 1462,
                        "quantity": 1,
                    }
                    try:    
                        post_response = requests.post(url=alnukhuba_add, headers=headers, json=payload, verify=False)
                        post_data = post_response.json()
                        api_order_id = post_data.get("data", {}).get("order_id")
                    except requests.JSONDecodeError as e:
                        print(f"Error on: [{e}]")
                        bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                        bot.send_message(call.message.chat.id,"⚠ عذرا لم يتم إنشاء الطلب, هناك عطل في الـ API يرجى إخبار الإدارة بذلك!")
                        bot.send_message(ADMIN_ID,f"سيدي هناك عطل طارئ في الـ API الخاص بسيرفر النخبة: [{e}]")
                        update_user_balance(user_id,price)
                        return
                    if not api_order_id:
                        bot.send_message(call.message.chat.id, "⚠ هذه الخدمة متوقفة مؤقتا من قبل السيرفر...")
                        update_user_balance(user_id, price)
                        return
                    bot.delete_message(chat_id=sticker_msg.chat.id,message_id=sticker_msg.message_id)
                    bot.send_message(call.message.chat.id, f"""تم إنشاء طلبك بنجاح ✅
    رقم الطلب: {api_order_id}
    سيتم تنفيذ الطلب, قد يحتاج بضعة ثواني ⏳""")

                    while True:
                        try:
                            get_response = requests.get(f"{alnukhba_get}/{api_order_id}", headers=headers, verify=False)
                            order_data = get_response.json()
                            status = order_data.get("data", {}).get("status")
                            execution = order_data.get("data",{}).get("diff")
                            if status == "accept":
                                update_order_status(order_id=order_id, status="accept")  # تحديث حالة الطلب
                                bot.send_message(call.message.chat.id, f"""✅ تهانيا! تم تنفيذ طلبك بنجاح!
    رقم الطلب: {api_order_id}
    الخدمة: {service} Auto
    ⏰ مدة تنفيذ الطلب: {execution}""")
                                break
                            elif status == "reject":
                                update_order_status(order_id, status)
                                bot.send_message(call.message.chat.id, f"""❌ عذراً، فشل تنفيذ الطلب.
    الرقم: {api_order_id}
    الحالة: {status}""")
                                update_user_balance(user_id, price)
                                break
                        except requests.RequestException as e:
                            print("Error connecting to API", e)
                            time.sleep(2)
                else:
                        bot.send_message(user_id, "❌ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", parse_mode='Markdown')
                        bot.answer_callback_query(call.id, "ليس لدى الإدارة رصيد كافٍ لتنفيذ طلبك يرجى إعلامهم بذلك.", show_alert=True)
                        update_user_balance(user_id, price)
        set_user_state(user_id, None)
#
@bot.message_handler(commands=["start_check_api"])
def start_check_api(message):
    response = requests.get(url=f"{lirat_url}/{card_id}",headers=headers_lirat)
    card_data = response.json()
    bot.send_message(ADMIN_ID,"تم بدء تشغيل التحقق من الـ API")
    while True:
        try:
            balance = card_data.get("data",{}).get("balance")
            print(f'[{datetime.now()}] {balance}')
            time.sleep(10)
        except Exception as e:
            bot.send_message(ADMIN_ID,text=f"حدث خطأ في API ليرات: {e}")
            break
@bot.message_handler(commands=["start_check_server"])
def start_check_api(message):
    response = requests.get(url=f"{alnukhba_get}/{order_id}",headers=headers)
    order_data = response.json()
    bot.send_message(ADMIN_ID,"تم بدء تشغيل وضع التحقق من API سيرفر النخبة")
    while True:
        try:
            status = order_data.get("data",{}).get("status")
            print(f'[{datetime.now()}] {status}')
            time.sleep(10)
        except Exception as e:
            bot.send_message(ADMIN_ID,text=f"حدث خطأ في API ALNUKHBA STORE: {e}")
            break

print("Bot is polling...")
bot.infinity_polling()
