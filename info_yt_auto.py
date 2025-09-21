from database_manger_auto import get_api
alnukhuba_add = "https://api.alnukhba-store.com/api/order/add"
alnukhba_get = "https://api.alnukhba-store.com/api/order/get"
headers = {
    "Authorization": f"{get_api()}",
    "Content-Type": "application/json"
}
smmcpan_url = 'https://smmcpan.com/api/v2'
smmcpan_api = 'a65a213664e37dd710e30c849c5d03ec'
lirat_url = 'https://backend.lirat.store/api/user/vitual-cards/show-card'
card_id = "26ffd9b5-8c73-43f3-9a99-d3052d3d09e6"
order_id = "ID_7807363486570469"
headers_lirat = {
    "Authorization": "Bearer 322969|imeAeaqzHv35FfvOM5lGSjKxCzF2i2uSfHVRJVwgb912a789",
    "Content-Type": "application/json"
}
LEVELS = {
    0: 0,
    1: 20,
    2: 50,
    3: 120,
    4: 250,
    5: 500,
    6: 1000,
    7: 2000,
    8: 3500
}
REWARDS = {
    1: 3,   
    2: 8,  
    3: 12,
    4: 15,
    5: 18,
    6: 25,
    7: 35,
    8: 50
}
def get_user_level(total):
    level = 0
    next_level = None
    for lvl, amount in LEVELS.items():
        if total >= amount:
            level = lvl
        else:
            next_level = (lvl, amount)
            break
    return level, next_level

def progress_bar(total, current_level, next_level):
    if not next_level:
        return "🟩" * 10, 100
    needed = next_level[1] - LEVELS[current_level]
    progress = total - LEVELS[current_level]
    percent = int((progress / needed) * 100)
    filled = percent // 10
    bar = "🟩" * filled + "⬜" * (10 - filled)
    return bar, percent
