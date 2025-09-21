from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup , InlineQueryResultArticle, InputTextMessageContent

DESCRIPTION = 'انقر هنا لاختيار الكمية'

auto_products = {
    'Free Fire': "477016283341",
    'رصيد Syriatel': "220502002977",
    'رصيد MTN': "221244704710",
    'Syriatel Cash': "229419194970",
    'USDT (BEP20)': "728728418415",
    'Payeer': "723190407806",
    'لايكات Instagram': "777223974121",
    'فواتير MTN': "226065300858",
    'مشاهدات Instagram': "775026387880",
    'لايكات لمنشورات Facebook': "322513015004",
    'pubgS1': "729082935620",
    'pubgS2': "728879389218",
    'MTN Cash': '629136073479',
    'Jawaker Tokens': '551839839619',
    'عضويات Free Fire': '475572806030'
}

auto_products_quantity = {
    "Free Fire": ["110", "230", "583", "1188"],
    "رصيد Syriatel": ["1000","1950","2013","2301","3068","4026","5273","8149","10067","14381","19175","23969","31639","43144","47938","57526"],
    "رصيد MTN": ["1000","2000","5000","10000","20000","40000","50000","60000","70000","75000"],
    "Syriatel Cash": ["10000","20000","30000","50000","100000","150000","200000","250000","300000"],
    "USDT (BEP20)": ["1","2","5","10","15","20","25","50","100","200"],
    "Payeer": ["1","2","5","10","15","20","25","50","100","200"],
    "لايكات Instagram": ["100","500","1000","2000","5000"],
    "فواتير MTN": ["10000","15000","20000","25000","50000","75000","100000","150000","200000","300000","500000"],
    "مشاهدات Instagram": ["10000","20000","30000","50000","100000","150000","200000","500000","1000000"],
    "لايكات لمنشورات Facebook": ["50","100","200","500","1000","2000","5000","10000","20000","50000","100000","200000","500000"],
    "pubgS1": ["60","325","660"],
    "pubgS2": ["60","325","660"],
    "MTN Cash": ["10000","20000","50000","100000","200000","500000"],
    "Jawaker Tokens": ["10000","20000","50000","100000","200000","500000","1000000","2000000","5000000","10000000"],
    "عضويات Free Fire": ["عضوية شهرية"]
}

ids = {
    "Free Fire": r"[0-9]{9,}$",
    "رصيد Syriatel": r"[0-9]{10}$",
    "رصيد MTN": r"[0-9]{10}$",
    "Syriatel Cash": r"[0-9]{10}$",
    "USDT (BEP20)": r"0x[a-fA-F0-9]{40}$",
    "Payeer": r"P[0-9]{10}$",
    "لايكات Instagram": r'^(https?://)?(www\.)?instagram\.com/.*',
    "فواتير MTN": r"[0-9]{10}$",
    "لايكات لمنشورات Facebook": r'^(https?://)?(www\.)?facebook\.com/.*',
    "PUBG": r"[0-9]{9,}$",
    "MTN Cash": r'[0-9]{10}$',
    "Jawaker Tokens": r'[0-9]{6,}$'
}

auto_products_prices = {
    "Free Fire": {
        "110": 1.2,
        "230": 2.35,
        "583": 5.95,
        "1188": 11.90
    },
    "رصيد Syriatel": {
        "1000": 0.14,
        "1950": 0.24,
        "2013": 0.26,
        "2301": 0.27,
        "3068": 0.36,
        "4026": 0.47,
        "5273": 0.61,
        "8149": 0.94,
        "10067": 1.16,
        "14381": 1.66,
        "19175": 2.21,
        "23969": 2.76,
        "31639": 3.64,
        "43144": 4.97,
        "47938": 5.52,
        "57526": 6.62
    },
    "رصيد MTN": {
        "1000": 0.13,
        "2000": 0.23,
        "5000": 0.58,
        "10000": 1.16,
        "20000": 2.31,
        "40000": 4.61,
        "50000": 5.76,
        "60000": 6.91,
        "70000": 8.10,
        "75000": 8.63
    },

    "Syriatel Cash": {
        "10000": 1.15,
        "20000": 2.29,
        "30000": 3.43,
        "50000": 5.72,
        "100000": 11.44,
        "150000": 17.16,
        "200000": 22.87,
        "250000": 28.59,
        "300000": 34.31
    },
    "USDT (BEP20)": {
        "1": 1.35,
        "2": 2.69,
        "5": 6.72,
        "10": 13.43,
        "15": 20.15,
        "25": 33.58,
        "50": 67.15,
        "100": 134.29,
        "200": 268.57
    },
    "Payeer": {
        "1": 1.35,
        "2": 2.7,
        "5": 6.75,
        "10": 13.5,
        "15": 20.25,
        "20": 26.99,
        "25": 33.74,
        "50": 67.48,
        "100": 134.95,
        "200": 269.90
    },
    "لايكات Instagram": {
        "100": 0.31,
        "500": 1.51,
        "1000": 3.01,
        "2000": 6.02,
        "5000": 15.07
    },
    "فواتير MTN": {
        "10000": 1.2,
        "15000": 1.71,
        "20000": 2.39,
        "25000": 2.98,
        "50000": 5.96,
        "75000": 8.94,
        "100000": 11.91,
        "150000": 17.87,
        "200000": 23.82,
        "300000": 35.73,
        "500000": 59.54
    },
    "مشاهدات Instagram": {
        "10000": 0.12,
        "20000": 0.24,
        "30000": 0.35,
        "50000": 0.59,
        "100000": 1.17,
        "150000": 1.75,
        "200000": 2.33,
        "500000": 5.9,
        "1000000": 11.7
    },
    "لايكات لمنشورات Facebook": {
        "50": 0.02,
        "100": 0.04,
        "200": 0.09,
        "500": 0.25,
        "1000": 0.50,
        "2000": 1,
        "5000": 2.5,
        "10000": 4.99,
        "20000": 9.99,
        "50000": 24.95,
        "100000": 49.91,
        "200000": 99.8,
        "500000": 250
    },
    "pubgS1": {
        "60": 1.14,
        "325": 5.72,
        "660": 11.44
    },
    "pubgS2": {
        "60": 1.13,
        "325": 5.73,
        "660": 11.45
    },
    "MTN Cash": {
        "10000": 1.25,
        "20000": 2.49,
        "50000": 6.22,
        "100000": 12.44,
        "200000": 24.88,
        "500000": 62.21
    },
    "Jawaker Tokens": {
        "10000": 1.41,
        "20000": 2.81,
        "50000": 7.01,
        "100000": 14.02,
        "200000": 28.04,
        "500000": 70.12,
        "1000000": 140.24,
        "2000000": 280.48,
        "5000000": 701.22,
        "10000000": 1405
    },
    "عضويات Free Fire": {
        "عضوية شهرية": 14.2
    }
}

# ============== Inline Queries ============= #
def auto_products_handle_display_inline_query_for_games(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='1',
        title="Free Fire",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products['Free Fire']),
        thumbnail_url='https://i.postimg.cc/TYCGw3My/download-1.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_handle_display_inline_query_for_crypto(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='1',
        title="USDT (BEP20)",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products['USDT (BEP20)']),
        thumbnail_url='https://i.postimg.cc/4yg8NDSW/usdt.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='2',
        title="Payeer",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products['Payeer']),
        thumbnail_url='https://i.postimg.cc/YSV8q0Yw/payeer.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_handle_display_inline_query_for_balance(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='1',
        title="رصيد Syriatel",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products['رصيد Syriatel']),
        thumbnail_url='https://i.postimg.cc/6QdQKhM7/download.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='2',
        title="رصيد MTN",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["رصيد MTN"]),
        thumbnail_url="https://i.postimg.cc/hjctt7Y2/download-4.png",
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='3',
        title="Syriatel Cash",
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products['Syriatel Cash']),
        thumbnail_url='https://i.postimg.cc/6QdQKhM7/download.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_handle_display_support_pages_instagram(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='insta_likes',
        title='لايكات Instagram',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["لايكات Instagram"]),
        thumbnail_url='https://i.postimg.cc/hvyw2NKc/instagram-6338393-1280.webp',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    #results.append(InlineQueryResultArticle(
    #    id='insta_watches',
    #    title='مشاهدات Instagram',
    #    description=DESCRIPTION,
    #    input_message_content=InputTextMessageContent(auto_products["مشاهدات Instagram"]),
    #    thumbnail_url='https://i.postimg.cc/hvyw2NKc/instagram-6338393-1280.webp',
    #    thumbnail_height=48,
    #    thumbnail_width=48
    #))
    return results
#def auto_products_handle_display_support_pages_facebook(inline_query):
    #results = []
    #results.append(InlineQueryResultArticle(
    #    id='facebook_likes_manshoor',
    #    title='لايكات لمنشورات Facebook',
    #    description=DESCRIPTION,
    #    input_message_content=InputTextMessageContent(auto_products["لايكات لمنشورات Facebook"]),
    #    thumbnail_url='https://i.postimg.cc/MGzG00fD/facebook.jpg',
    #    thumbnail_height=48,
    #    thumbnail_width=48
    #))
    #return results
def auto_products_handle_display_syriatel(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='syriatel_b',
        title='رصيد Syriatel',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["رصيد Syriatel"]),
        thumbnail_url='https://i.postimg.cc/6QdQKhM7/download.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='syriatel_c',
        title='Syriatel Cash',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["Syriatel Cash"]),
        thumbnail_url='https://i.postimg.cc/6QdQKhM7/download.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_handle_display_mtn(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='mtn_b',
        title='رصيد MTN',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["رصيد MTN"]),
        thumbnail_url='https://i.postimg.cc/hjctt7Y2/download-4.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='mtn_f',
        title='فواتير MTN',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["فواتير MTN"]),
        thumbnail_url='https://i.postimg.cc/hjctt7Y2/download-4.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='mtn_c',
        title='MTN Cash',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["MTN Cash"]),
        thumbnail_url='https://i.postimg.cc/hjctt7Y2/download-4.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_display_ff(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='ffd',
        title='جواهر Free Fire',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["Free Fire"]),
        thumbnail_url='https://i.postimg.cc/TYCGw3My/download-1.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='ffad',
        title='عضويات Free Fire',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["عضويات Free Fire"]),
        thumbnail_url='https://i.postimg.cc/TYCGw3My/download-1.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_display_jawaker(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='jawaker_t',
        title='توكينز Jawaker',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["Jawaker Tokens"]),
        thumbnail_url='https://i.postimg.cc/mgJ7cqQ1/download-3.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_display_pubg(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='pubgs1',
        title='PUBG سيرفر 1',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["pubgS1"]),
        thumbnail_url='https://i.postimg.cc/xT0nnb7D/download-2.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    results.append(InlineQueryResultArticle(
        id='pubgs2',
        title='PUBG سيرفر 2',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["pubgS2"]),
        thumbnail_url='https://i.postimg.cc/xT0nnb7D/download-2.jpg',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    
    return results
def auto_products_display_payeer(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='payeer',
        title='Payeer',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["Payeer"]),
        thumbnail_url='https://i.postimg.cc/YSV8q0Yw/payeer.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results
def auto_products_display_usdt(inline_query):
    results = []
    results.append(InlineQueryResultArticle(
        id='bep20',
        title='USDT (BEP20)',
        description=DESCRIPTION,
        input_message_content=InputTextMessageContent(auto_products["USDT (BEP20)"]),
        thumbnail_url='https://i.postimg.cc/4yg8NDSW/usdt.png',
        thumbnail_height=48,
        thumbnail_width=48
    ))
    return results

# ============== Helpers ============= #
def handle_auto_products_message_logic(message):
    selected_service_name = None
    for name, code in auto_products.items():
        if code == message.text:
            selected_service_name = name
            break
    return selected_service_name

def get_quantity_btns_for_service(service_name: str):
    markup = InlineKeyboardMarkup()
    auto_quantities = auto_products_quantity.get(service_name)
    if auto_quantities:
        def sort_key(item):
            try:
                return int(item)
            except ValueError:
                return float('inf')
        sorted(list(auto_quantities), key=sort_key)
        for qty in auto_quantities:
            price_display = auto_products_prices.get(service_name, {}).get(qty, 'N/A')
            btn_text = f"{qty} (السعر: {price_display} 💰)"
            
            query_to_write = f"{service_name}|{qty}"
            btn = InlineKeyboardButton(text=btn_text, callback_data=query_to_write)
            markup.add(btn)
    return markup
