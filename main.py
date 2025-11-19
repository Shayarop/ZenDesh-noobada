from telethon import TelegramClient, events
import asyncio
import time
import random
from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='zendesh')
api_id = 27512928
api_hash = '05c7f1e9be23c37e15cfe245ce4b8a84'
client = TelegramClient('zendesh', api_id, api_hash)

spam_pool = []
raid_targets = set()

async def fireup():
    msg = "<b>ZenDesh is Ready and Working 🔥 | Dev : @ZenDesh</b>"
    await client.send_message('me', msg, parse_mode='html')

@client.on(events.NewMessage(pattern=r'^/add(?: (.+))?', outgoing=True))
async def addspam(e):
    msg = e.pattern_match.group(1)

    if msg:
        spam_pool.append(msg.strip())
        await e.edit(f"✅ Added:\n\n<code>{msg.strip()}</code>", parse_mode='html')
    elif e.is_reply:
        reply = await e.get_reply_message()
        if reply.text:
            spam_pool.append(reply.text.strip())
            await e.edit(f"✅ Added from replied message:\n\n<code>{reply.text.strip()}</code>", parse_mode='html')
        else:
            await e.edit("<b><i>❌ Cannot add empty/non-text message.</i></b>",
    parse_mode="html")
    else:
        await e.edit("<b><i>❌ Use: /add text or reply to a message.</i></b>",
    parse_mode="html")

@client.on(events.NewMessage(pattern=r'^/raidlist$', outgoing=True))
async def show_raid_list(e):
    if not raid_targets:
        await e.edit("<b>ℹ️ No active raid targets.</b>", parse_mode="html")
        return

    content = ""
    for i, user in enumerate(raid_targets, start=1):
        content += f"<b>{i}.</b> {user}<br>"

    pager = telegraph.create_page(
        title="ZenDesh Raid Targets",
        html_content=content
    )
    await e.edit(
    f'<b>🎯 Raid List:\n\n<a href="https://telegra.ph/{pager["path"]}">Click Me</a></b>',
    parse_mode="html"
)

@client.on(events.NewMessage(pattern=r'^/listspam$', outgoing=True))
async def listspam(e):
    if not spam_pool:
        await e.edit("<b>ℹ️ No spam messages saved.</b>",
    parse_mode="html")
        return

    content = ""
    for i, msg in enumerate(spam_pool, start=1):
        content += f"<b>{i}.</b> {msg}<br><br>"

    page = telegraph.create_page(
        title="ZenDesh Spam Pool",
        html_content=content
    )

    await e.edit(
    f'<b>📄 Spam Messages List:\n\n<a href="https://telegra.ph/{page["path"]}">Click Me</a></b>',
    parse_mode="html"
)

@client.on(events.NewMessage(pattern=r'^/raid(?:\s+@?\w+)?$', outgoing=True))
async def raid_setter(e):
    if e.is_reply:
        reply = await e.get_reply_message()
       # print(reply.is_channel)
        if reply.sender and hasattr(reply.sender, 'id') and not getattr(reply.sender, 'bot', False):
            if reply.sender.username:
                raid_targets.add(f"@{reply.sender.username}")
                await e.edit(
                    '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Raid added:</i></b> '
                    f'<b><i>@{reply.sender.username}</i></b>',
    parse_mode="html"
                )
            else:
                raid_targets.add(reply.sender_id)
                await e.edit(
                    '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Raid added:</i></b> '
                    f'<b><i>ID {reply.sender_id}</i></b>',
    parse_mode="html"
                )
            return
    parts = e.text.split()
    if len(parts) == 2 and parts[1].startswith("@"):
        raid_targets.add(parts[1])
        await e.edit(
            '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Raid added:</i></b> '
            f'<b><i>{parts[1]}</i></b>',
    parse_mode="html"
        )
    else:
        await e.edit(
            '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Usage:</i></b> '
            '<i>/raid @username or reply to user</i>',
    parse_mode="html"
        )

@client.on(events.NewMessage(pattern=r'^/spam(?:\s+[\d@]\w*)?', outgoing=True))
async def smart_spam(e):
    args = e.text.split()
    count = None
    target = None

    if len(args) >= 3 and args[1].isdigit():
        count = int(args[1])
        target = args[2]
    elif len(args) == 2 and args[1].isdigit():
        count = int(args[1])
    elif len(args) == 2 and args[1].startswith("@"):
        target = args[1]
    elif len(args) == 1:
        pass
    else:
        await e.edit("<b><i>❌ Usage: /spam 5 or /spam @user or reply to someone.</i></b>",parse_mode="html")
        return

    if not spam_pool:
        await e.edit("<b><i>⚠️ No spam messages saved.</i></b>",parse_mode="html")
        return

    if not target:
        reply = await e.get_reply_message()
        if reply:
            if reply.sender and reply.sender.username:
                target = f"@{reply.sender.username}"
            elif reply.sender_id:
                name = reply.sender.first_name if reply.sender and reply.sender.first_name else "Naam Rakh Le"
                target = f'<a href="tg://user?id={reply.sender_id}">{name}</a>'
            else:
                target = reply.id
        else:
            await e.edit("<b>❌ Mention a user or reply.</b>", parse_mode="html")
            return

    if count:
        messages = random.sample(spam_pool, min(count, len(spam_pool)))
    else:
        messages = spam_pool

    await e.delete()

    for msg in messages:
        try:
            if isinstance(target, str) and target.startswith('<a href='):
                await client.send_message(e.chat_id, f"{target} {msg}", parse_mode="html")
            elif isinstance(target, str) and target.startswith('@'):
                await client.send_message(e.chat_id, f"{target} {msg}", parse_mode="html")
            else:
                await client.send_message(e.chat_id, msg, reply_to=target)
            await asyncio.sleep(0.4)
        except:
            break

@client.on(events.NewMessage(pattern=r'^/stopraid(?:\s+@?\w+| all)?$', outgoing=True))
async def stop_raid(e):
    global raid_targets

    parts = e.text.split()

    if len(parts) == 2 and parts[1].lower() == "all":
        raid_targets.clear()
        await e.edit(
            '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] All raid targets removed.</i></b>', parse_mode="html"
        )
        return

    if e.is_reply:
        reply = await e.get_reply_message()
        if reply.sender:
            if reply.sender.username and f"@{reply.sender.username}" in raid_targets:
                raid_targets.discard(f"@{reply.sender.username}")
                await e.edit(
                    f'<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Removed:</i></b> '
                    f'<b><i>@{reply.sender.username}</i></b>', parse_mode="html"
                )
            else:
                raid_targets.discard(reply.sender_id)
                await e.edit(
                    f'<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Removed ID:</i></b> '
                    f'<b><i>{reply.sender_id}</i></b>', parse_mode="html"
                )
            return

    if len(parts) == 2:
        raid_targets.discard(parts[1])
        await e.edit(
            f'<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Removed:</i></b> '
            f'<b><i>{parts[1]}</i></b>', parse_mode="html"
        )
    else:
        await e.edit(
            '<b><i>[<a href="https://t.me/ZenDesh">ϟ</a>] Usage:</i></b> '
            '<i>/stopraid @username, reply to user, or /stopraid all</i>', parse_mode="html"
        )

@client.on(events.NewMessage(pattern=r'^/delspam all$', outgoing=True))
async def del_all(e):
    spam_pool.clear()
    await e.edit("⚠️ All spam messages cleared.")

@client.on(events.NewMessage(pattern=r'^/delspam (\d+)$', outgoing=True))
async def del_index(e):
    index = int(e.pattern_match.group(1)) - 1
    if 0 <= index < len(spam_pool):
        removed = spam_pool.pop(index)
        await e.edit(f"✅ Removed:\n<code>{removed}</code>", parse_mode='html')
    else:
        await e.edit("❌ Invalid index.")

@client.on(events.NewMessage(pattern='/ping'))
async def pingx(e):
    if e.out:
        start = time.perf_counter()
        await asyncio.sleep(0.2)
        end = time.perf_counter()
        ms = int((end - start) * 1000)
        html = f"""<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Zindaa Nepali </b>! <code>PONG 🔥</code>
- - - - - - - - - - - - - - - - - - - - -
<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Status:</b> <code>Alive ! ✅</code>

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Speed:</b> <code>{ms} Ms</code>
- - - - - - - - - - - - - - - - - - - - -
<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Dev: </b><code>Sandesh Vaiya</code>"""
        await e.edit(html, parse_mode='html')

@client.on(events.NewMessage(pattern='/promo', outgoing=True))
async def promo_handler(e):
    if not e.is_reply:
        await e.edit("<b>❌ Reply to a message to promote.</b>", parse_mode='html')
        return

    reply_msg = await e.get_reply_message()

    status_msg = await e.edit("""<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Promoting Ads 📣</b>
- - - - - - - - - - - - - - - - - - - - -

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Total Chats:</b> <code>0</code>

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Success:</b> <code>0</code>

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Failed:</b> <code>0</code>
- - - - - - - - - - - - - - - - - - - - -
<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Dev: </b><code>Sandesh Vaiya</code>""",
        parse_mode='html'
    )

    total = success = failed = 0

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            total += 1
            try:
                await reply_msg.forward_to(dialog.id)
                success += 1
            except:
                failed += 1

            await status_msg.edit(f"""<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Promoting Ads 📣</b>
- - - - - - - - - - - - - - - - - - - - -

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Total Chats:</b> <code>{total}</code>

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Success:</b> <code>{success} ✅</code>

<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Failed:</b> <code>{failed} ❌</code>
- - - - - - - - - - - - - - - - - - - - -
<b>[<a href="https://t.me/ZenDesh">ϟ</a>] Dev: </b><code>Sandesh Vaiya</code>""",
                parse_mode='html'
            )
            await asyncio.sleep(0.5)
            
@client.on(events.NewMessage(incoming=True))
async def auto_raid(e):
    if not raid_targets or not spam_pool:
        return
    if e.is_channel is None:
        return
    sender = await e.get_sender()
    if not sender or sender.bot:
        return
    if sender.username and f"@{sender.username}" in raid_targets:
        msg = random.choice(spam_pool)
        await e.reply(msg)
    elif sender.id in raid_targets:
        msg = random.choice(spam_pool)
        await e.reply(msg)
            
async def boot():
    await fireup()

with client:
    client.loop.run_until_complete(boot())
    client.run_until_disconnected()
