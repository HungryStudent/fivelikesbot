import time
from datetime import date

import asyncpg
from asyncpg import Connection
from config import user, password, database, host


async def start():
    conn = await asyncpg.connect(user=user, password=password,
                                 database=database, host=host)
    await conn.execute("CREATE")
    await conn.close()


async def get_stat():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    data = {}
    all_count = await conn.fetchrow("SELECT COUNT(*) as all_count FROM users")
    start = time.mktime(date.today().timetuple())
    today_count = await conn.fetchrow("SELECT COUNT(*) as today_count FROM users WHERE reg_date > $1", int(start))

    data["all_count"] = all_count["all_count"]
    data["today_count"] = today_count["today_count"]

    all_likes_count = await conn.fetchrow("SELECT COUNT(*) as all_count FROM likes")
    today_likes_count = await conn.fetchrow("SELECT COUNT(*) as today_count FROM likes WHERE unix_time > $1",
                                            int(start))
    data["all_likes_count"] = all_likes_count["all_count"]
    data["today_likes_count"] = today_likes_count["today_count"]

    all_premium = await conn.fetchrow("SELECT COUNT(*) as all_premium FROM premium")
    today_premium = await conn.fetchrow("SELECT COUNT(*) as today_premium FROM premium WHERE buy_date > $1", int(start))
    active_premium = await conn.fetchrow("SELECT COUNT(*) as active_premium FROM users WHERE premium_time > $1",
                                         int(start))

    data["all_premium"] = all_premium["all_premium"]
    data["today_premium"] = today_premium["today_premium"]
    data["active_premium"] = active_premium["active_premium"]

    await conn.close()
    return data


async def add_action(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.execute("UPDATE users SET last_online = $1 WHERE user_id = $2", int(time.time()), user_id)
    await conn.close()


async def add_user(user_id, name, photo_id, ref_id):
    conn = await asyncpg.connect(user=user, password=password,
                                 database=database, host=host)
    await conn.execute(
        "INSERT INTO users(user_id, name, photo_id, premium_time, gender, age, city, rating, is_ban, is_deactivate, today_rating, invited, reg_date, last_online) VALUES ($1, $2, $3, 0, "
        "'не указано', 0,'не указано', 0, false, false, 0, $4, $5, $6)",
        user_id, name, photo_id, ref_id, int(time.time()), int(time.time()))
    await conn.close()


async def get_users():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    data = await conn.fetch("SELECT user_id FROM users")
    users = []
    await conn.close()
    for row in data:
        users.append(row["user_id"])
    return users


async def check_user(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow("SELECT id, is_ban FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return row


async def get_my_user(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow(
        "With rnu as (SELECT row_number() over(order by rating desc) as rating_pos, rating, name, photo_id, premium_time, "
        "gender, age, city, user_id, is_deactivate FROM users) select rating_pos, rating, name, photo_id, premium_time, gender, age, "
        "city, is_deactivate from rnu WHERE user_id = $1",
        user_id)
    await conn.close()
    return row


async def get_user(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow("SELECT name, photo_id, gender, age, city FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return row


async def get_user_for_estimate(user_id, premium=1):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    if premium:
        query = "SELECT user_id, name, photo_id, gender, age, city  FROM users WHERE NOT EXISTS(SELECT id FROM likes " \
                "WHERE likes.user_id=$1 and likes.owner_id = users.user_id) and users.user_id <> $2 and is_ban = " \
                "false and is_deactivate = false and premium_time > $3 "
        row = await conn.fetchrow(query, user_id, user_id, int(time.time()))
        if row is not None:
            await conn.close()
            return row
    query = "SELECT user_id, name, photo_id, gender, age, city  FROM users WHERE NOT EXISTS(SELECT id FROM likes " \
            "WHERE likes.user_id=$1 and likes.owner_id = users.user_id) and users.user_id <> $2 and is_ban = false " \
            "and is_deactivate = false and premium_time < $3 "
    row = await conn.fetchrow(query, user_id, user_id, int(time.time()))
    if row is None:
        query = "SELECT user_id, name, photo_id, gender, age, city  FROM users WHERE NOT EXISTS(SELECT id FROM likes " \
                "WHERE likes.user_id=$1 and likes.owner_id = users.user_id) and users.user_id <> $2 and is_ban = " \
                "false and is_deactivate = false and premium_time > $3 "
        row = await conn.fetchrow(query, user_id, user_id, int(time.time()))
        return row
    await conn.close()
    return row


async def get_user_rating(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow(
        "SELECT COUNT(owner_id) as users_count, AVG(score) as rating FROM likes WHERE owner_id = $1 and is_skip = false",
        user_id)
    await conn.close()
    return row


async def reset_rating():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    await conn.fetch(f"UPDATE users SET today_rating = 0")
    await conn.close()


async def get_top():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetch(
        "SELECT DISTINCT user_id, name, rating FROM users WHERE is_ban = false ORDER BY rating DESC LIMIT 10")
    await conn.close()
    return row


async def get_today_top():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetch(
        "SELECT DISTINCT user_id, name, today_rating as rating FROM users WHERE is_ban = false ORDER BY today_rating DESC LIMIT 10")
    await conn.close()
    return row


async def change(user_id, column: str, value):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    await conn.fetch(f"UPDATE users SET {column} = $1 WHERE user_id = $2", value, user_id)
    await conn.close()


async def add_new_estimate(user_id, owner_id, score):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)

    if score == "skip":
        await conn.execute(
            "INSERT INTO likes(user_id, owner_id, score, is_viewed, is_skip, unix_time) VALUES ($1, $2, 0, true, true, $3)",
            user_id, owner_id, int(time.time()))
        return
    await conn.execute("DELETE FROM likes WHERE user_id = $1 and owner_id = $2", user_id, owner_id)
    await conn.execute(
        "INSERT INTO likes(user_id, owner_id, score, is_viewed, is_skip, unix_time) VALUES ($1, $2, $3, false, false, $4)",
        user_id, owner_id, int(score), int(time.time()))

    start = time.mktime(date.today().timetuple())
    await conn.execute(
        "UPDATE users SET rating = (SELECT AVG(score) FROM likes WHERE owner_id = $1), today_rating = (SELECT AVG(score) FROM likes WHERE owner_id = $2 and unix_time > $3) WHERE user_id = $4",
        owner_id, owner_id, int(start), owner_id)
    await conn.close()


async def get_estimate_user(user_id):
    conn: Connection = await asyncpg.connect(user=user, password=password,
                                             database=database, host=host)
    row = await conn.fetchrow(
        "SELECT user_id, name, photo_id, gender, age, city FROM users WHERE user_id = (SELECT user_id FROM likes "
        "WHERE owner_id = $1 and is_viewed = false and is_skip = false LIMIT 1)", user_id)
    if row is None:
        return None, 0, 0
    score = await conn.fetchrow("SELECT score FROM likes WHERE user_id = $1 and owner_id = $2", row["user_id"], user_id)
    await conn.execute("UPDATE likes SET is_viewed = true WHERE user_id = $1 and owner_id = $2", row["user_id"],
                       user_id)
    count = await conn.fetchrow(
        "SELECT COUNT(id) FROM likes WHERE owner_id = $1 and is_viewed = false and is_skip = false", user_id)
    return row, count["count"], score["score"]


async def deactivate_profile(flag, user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    await conn.fetch(f"UPDATE users SET is_deactivate = $1 WHERE user_id = $2", flag, user_id)
    await conn.close()


async def check_premium(user_id, get_date=False):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow(f"SELECT premium_time FROM users WHERE user_id = $1", user_id)
    await conn.close()
    if get_date:
        return row["premium_time"] > time.time(), row["premium_time"]
    else:
        return row["premium_time"] > time.time()


async def get_referals_count(user_id):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    row = await conn.fetchrow(f"SELECT COUNT(id) as count FROM users WHERE invited = $1", user_id)
    await conn.close()
    return row["count"]


async def add_premium(user_id, days):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    if await check_premium(user_id):
        row = await conn.fetchrow("SELECT premium_time FROM users WHERE user_id = $1", user_id)
        await conn.execute("UPDATE users SET premium_time = premium_time + $1 WHERE user_id = $2", days * 24 * 3600,
                           user_id)
    else:
        await conn.execute(f"UPDATE users SET premium_time = $1 WHERE user_id = $2",
                           int(time.time()) + days * 24 * 3600, user_id)
    await conn.close()


async def add_receipt(user_id, amount):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    await conn.execute("INSERT INTO premium(user_id, buy_date, amount) VALUES ($1, $2, $3)", user_id, int(time.time()),
                       amount)
    await conn.close()


async def change_ban(user_id, flag):
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    await conn.fetch(f"UPDATE users SET is_ban = $1 WHERE user_id = $2", flag, user_id)
    await conn.close()


async def get_not_view():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    rows = await conn.fetch(
        f"SELECT DISTINCT user_id FROM users WHERE $1 - last_online > 86400 and EXISTS(SELECT id FROM likes " \
        "WHERE likes.owner_id = users.user_id and likes.is_viewed = false)", int(time.time()))
    await conn.close()
    users = [x["user_id"] for x in rows]
    return users


async def get_new_reg():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    rows = await conn.fetch(f"SELECT DISTINCT user_id, name FROM users WHERE ($1 - reg_date BETWEEN 172800 and 259200)",
                            int(time.time()))
    await conn.close()
    return rows


async def get_ending_premium():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    rows = await conn.fetch(f"SELECT DISTINCT user_id FROM users WHERE (premium_time - $1 BETWEEN 0 and 3600)",
                            int(time.time()))
    await conn.close()
    return rows


async def get_start_users():
    conn = await asyncpg.connect(user=user, password=password, database=database, host=host)
    rows = await conn.fetch(f"SELECT user_id FROM users WHERE name = '/start';")
    await conn.close()
    return rows