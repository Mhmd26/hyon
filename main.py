import os
import asyncio
import random
import base64
import time
from datetime import datetime
from platform import python_version
from telethon import TelegramClient, events, version
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from pytz import timezone  
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.sessions import StringSession
import sys
import subprocess
import shutil

api_id = 23651425
api_hash = '6fa5fe38ef04b3677707d7e2551ac528'
file_path = "installation_date.txt"
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    with open(file_path, "r") as file:
        installation_time = file.read().strip()
else:
    installation_time = datetime.now().strftime("%Y-%m-%d")
    with open(file_path, "w") as file:
        file.write(installation_time)
StartTime = time.time()
is_running = False
update_lock = asyncio.Lock()
def convert_to_fancy_time(time_str):
    return time_str.translate(str.maketrans("0123456789:", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗:"))
async def edit_or_reply(event, text):
    await event.edit(text)
session_file = "session_data.json"
async def main():
    if os.path.exists(session_file):
        with open(session_file, "r") as file:
            data = json.load(file)
        phone_number = data.get("phone_number")
        group_id = data.get("group_id")
        session_name = data.get("session_name", "session_name")
    else:
        phone_number = input("Enter your phone number ☎️ (with country code): ")
        group_id = input("Enter the group ID or username where photos will be saved: ")
        session_name = "session_name"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    
    # تسجيل الدخول إذا لم يكن المستخدم مسجلاً
    if not await client.is_user_authorized():
        print("User not authorized. Logging in...")
        await client.send_code_request(phone_number)
        code = input("Enter the code you received 📩 : ")
        await client.sign_in(phone_number, code)
    
    # حفظ بيانات الجلسة والمعلومات في الملف
    with open(session_file, "w") as file:
        json.dump({
            "phone_number": phone_number,
            "group_id": group_id,
            "session_name": session_name
        }, file)
    
    print("Successfully logged in and session saved!")

    @client.on(events.NewMessage(incoming=True))
    async def auto_save_media(event):
        if event.is_private and event.media:
            media = event.media
            if hasattr(media, 'photo') and media.photo:
                photo = await event.download_media()
                sender = await event.get_sender()
                caption = f"""**
✎┊‌ تم حفظ الصورة بنجاح ✓
✎┊‌ أسم المرسل: {sender.first_name if sender.first_name else 'غير معروف'}
✎┊‌ معرف المستخدم: @{sender.username if sender.username else 'غير معروف'}
✎┊‌ تاريخ الإرسال: {event.date.strftime('%Y-%m-%d')}
              **  """
                await client.send_file(group_id, photo, caption=caption, link_preview=False)
                os.remove(photo)
            elif hasattr(media, 'video') and media.video:
                video = await event.download_media()
                sender = await event.get_sender()
                caption = f"""**
✎┊‌ تم حفظ الفيديو بنجاح ✓
✎┊‌ أسم المرسل: {sender.first_name if sender.first_name else 'غير معروف'}
✎┊‌ معرف المستخدم: @{sender.username if sender.username else 'غير معروف'}
✎┊‌ تاريخ الإرسال: {event.date.strftime('%Y-%m-%d')}
              **  """
                await client.send_file(group_id, video, caption=caption, link_preview=False)
                os.remove(video)
    @client.on(events.NewMessage(pattern=r"^(.ذاتيه|.ذاتية)$"))
    async def manual_save_media(event):
        await event.delete()
        if event.is_private:
            if not event.is_reply:
                await event.reply("", link_preview=False)
                return
            reply_message = await event.get_reply_message()
            if reply_message.media:
                media = reply_message.media
                if hasattr(media, 'photo') and media.photo:
                    photo = await reply_message.download_media()
                    sender = await reply_message.get_sender()
                    caption = f"""**
✎┊‌ تم حفظ الصورة الذاتية يدويًا ✓
✎┊‌ أسم المرسل: {sender.first_name if sender.first_name else 'غير معروف'}
✎┊‌ معرف المستخدم: @{sender.username if sender.username else 'غير معروف'}
✎┊‌ تاريخ الإرسال: {reply_message.date.strftime('%Y-%m-%d')}
                   ** """
                    await client.send_file(group_id, photo, caption=caption, link_preview=False)
                    os.remove(photo)
                elif hasattr(media, 'video') and media.video:
                    video = await reply_message.download_media()
                    sender = await reply_message.get_sender()
                    caption = f"""**
✎┊‌ تم حفظ الفيديو يدويًا ✓
✎┊‌ أسم المرسل: {sender.first_name if sender.first_name else 'غير معروف'}
✎┊‌ معرف المستخدم: @{sender.username if sender.username else 'غير معروف'}
✎┊‌ تاريخ الإرسال: {reply_message.date.strftime('%Y-%m-%d')}
                    **"""
                    await client.send_file(group_id, video, caption=caption, link_preview=False)
                    os.remove(video)
    @client.on(events.NewMessage(pattern=r"^\.فحص$")) 
    async def amireallyalive(event):
        me = await client.get_me()
        if event.sender_id != me.id:
            return 
        await event.delete()
        uptime = time.time() - StartTime
        days = int(uptime // (24 * 3600))
        hours = int((uptime % (24 * 3600)) // 3600)
        minutes = int((uptime % 3600) // 60)
        uptime_formatted = f"{days}d {hours}h {minutes}m"
        start_ping = time.time()
        sent_message = await client.send_message(event.chat_id, " ** ✎┊‌ 𝗣𝗹𝗲𝗮𝗦𝗲 𝘄𝗮𝗶𝘁 𝗺𝗲 ⏳**")
        ping = time.time() - start_ping
        ms = ping * 100 
        ping_formatted = f"{int(ms):02}.{int((ms % 1) * 100):02d}"
        await sent_message.delete()
        EMOJI = "✎┊‌"
        ALIVE_TEXT = "**╔========================╗ **"
        mention = f"[{me.first_name}](tg://user?id={me.id})"
        temp = f"""{ALIVE_TEXT}
**   [𝗦𝗰𝗼𝗿 𝘄𝗼𝗿𝗸𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝗳𝘂𝗹𝗹𝘆](t.me/Scorpion_scorp) ✅

   {EMOJI}‌‎𝐍𝐢𝐦𝐞 | {mention} ٫
   {EMOJI}‌‎𝐏𝐲𝐭𝐡𝐨𝐧 | {sys.version.split()[0]} ٫
   {EMOJI}‌‎𝐒𝐜𝐨𝐫𝐩𝐢𝐨𝐧 | {version.__version__} ٫
   {EMOJI}‌‎𝐔𝐩𝐭𝐢𝐦𝐞 | {uptime_formatted} ٫
   ‌‎{EMOJI}‌‎‌‎𝐏𝐢𝐧𝐠 | {ping_formatted}ms ٫
   ‌‎{EMOJI}‌‎‌‎𝐒𝐞𝐭𝐮𝐩 𝐃𝐚𝐭𝐞 | {installation_time} ٫

     - 𝗚𝗼 𝗮𝗻𝗱 𝗲𝗻𝗷𝗼𝘆 😉**
** ╚========================╝ **"""
        await client.send_message(event.chat_id, temp, link_preview=False)
    

        if HuRe_IMG:
            try:
                await event.client.send_file(
                    event.chat_id, HuRe_IMG, caption=temp, link_preview=False 
                )
            except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
                await event.reply("✎┊‌ خطأ في تحميل الصورة.", link_preview=False) 
        else:
            await event.reply(temp, link_preview=False)
        await event.delete()
    @client.on(events.NewMessage(incoming=True))
    async def forward_message(event):
        if event.is_private:
            await client.forward_messages(group_id, event.message)
            print(f"✎┊‌ تم إعادة توجيه رسالة من {event.sender_id} إلى المجموعة.")
    its_Reham = False
    @client.on(events.NewMessage(pattern=r".استثمار وعد"))
    async def invest(event):
        global its_Reham
        await event.delete()
        its_Reham = True
        while its_Reham:
            if event.is_group:
                await event.client.send_message(event.chat_id, "فلوسي")
                await asyncio.sleep(3)
                aljoker = await event.client.get_messages(event.chat_id, limit=1)
                aljoker = aljoker[0].message.split()[2:]
                l313l = aljoker[0] if aljoker and aljoker[0].isdigit() else None

                if l313l and int(l313l) > 500000000:
                    await event.client.send_message(event.chat_id, f"استثمار {l313l}")
                    await asyncio.sleep(5)
                    joker = await event.client.get_messages(event.chat_id, limit=1)
                    await joker[0].click(text="اي ✅")
                else:
                    await event.client.send_message(event.chat_id, f"استثمار {l313l if l313l else 'مبلغ غير متوفر'}")
                await asyncio.sleep(1215)
            else:
                await event.reply("**✎┊‌ أمر الاستثمار يمكن استخدامه فقط في المجموعات.**")
    @client.on(events.NewMessage(pattern=r".ايقاف استثمار وعد"))
    async def stop_invest(event):
        global its_Reham
        its_Reham = False
        await event.reply("**✎┊‌ تم تعطيل عملية الاستثمار بنجاح ✓**")
    active_tasks = {}
    
    @client.on(events.NewMessage(pattern=r"^\.كرر (\d+) (\d+)$"))
    async def repeat_message(event):
        try:
            parts = event.message.text.split()
            count = int(parts[1])
            interval = int(parts[2])
        except ValueError:
            await event.reply("**✎┊‌ حدث خطأ في المعطيات. تأكد من إدخال العدد والثواني بشكل صحيح.**")
            return
        if not event.is_reply:
            await event.reply("**✎┊‌ يجب أن يكون الأمر ردًا على رسالة لتكرارها.**")
            return
        reply_message = await event.get_reply_message()
        chat_id = event.chat_id
        if chat_id in active_tasks:
            await event.reply("**✎┊‌ يوجد تكرار نشط بالفعل. استخدم الأمر .ايقاف التكرار لإيقافه.**")
            return
        await event.delete()
        await event.reply("**✎┊‌ تم تفعيل التكرار ✓**")
        async def repeat_task():
            for i in range(count):
                if chat_id not in active_tasks:
                    break
                if reply_message.media:
                    await event.client.send_message(chat_id, file=reply_message.media)
                else:
                    await event.client.send_message(chat_id, reply_message.text)
                await asyncio.sleep(interval)
            active_tasks.pop(chat_id, None)
        task = asyncio.create_task(repeat_task())
        active_tasks[chat_id] = task
    @client.on(events.NewMessage(pattern=r"^\.ايقاف التكرار$"))
    async def stop_repeat(event):
        chat_id = event.chat_id
        if chat_id in active_tasks:
            task = active_tasks.pop(chat_id)
            task.cancel()
            await event.reply("**✎┊‌ تم إيقاف التكرار ✗**")
        else:
            await event.reply("**✎┊‌ لا يوجد تكرار نشط لإيقافه.**")
    @client.on(events.NewMessage(pattern=".اسم وقتي"))
    async def update_time_name(event):
        await event.delete()
        global is_running
        if is_running:
            await event.reply("** ✎┊‌ الاسم الوقتي يعمل بالفعل ! **")
            return
        is_running = True
        await event.reply("** ✎┊‌ تم تشغيل الاسم الوقتي ✓**")
        country_timezone = "Asia/Riyadh"
        tz = timezone(country_timezone)
        while is_running:
            try:
                current_time = datetime.now(tz).strftime("%I:%M")
                fancy_time = convert_to_fancy_time(current_time)
                me = await client.get_me()
                original_name = me.first_name.split("|", 1)[-1].strip()
                new_name = f"{fancy_time} | {original_name}"
                await client(UpdateProfileRequest(first_name=new_name))
                print(f"✅ تم تحديث الاسم إلى: {new_name}")
            except Exception as e:
                print(f"Error updating name: {e}")
            await asyncio.sleep(60)
    @client.on(events.NewMessage(pattern=".ايقاف اسم وقتي"))
    async def stop_time_name(event):
        await event.delete()
        global is_running
        if not is_running:
            await event.reply("** ✎┊‌الاسم الوقتي غير مفعل**")
            return
        is_running = False
        try:
            me = await client.get_me()
            original_name = me.first_name.split("|", 1)[-1].strip()
            await client(UpdateProfileRequest(first_name=original_name))
            await event.reply("**✎┊‌ تم إيقاف الاسم الوقتي **")
            print(f"🛑 تم إيقاف التحديث والعودة إلى الاسم الأصلي: {original_name}")
        except Exception as e:
            print(f"Error stopping update: {e}")

    @client.on(events.NewMessage(pattern=".الاوامر"))
    async def command_list(event):
        await edit_or_reply(
            event, 
            "**✎┊‌ قآئمة الأوامر  \n\n"
            "-‌ اختر احداها : \n"
            "- { `.امر الذاتية` } \n"
            "- { `.امر التكرار` } \n"
            "- { `.امر الاسم الوقتي` } \n"
            "- { `.فحص` }\n\n"
            "- سورس العقرب ✏️**"
        )
        
    @client.on(events.NewMessage(pattern=".امر الذاتية"))
    async def command_list(event):
        await edit_or_reply(
            event, 
            "**✎┊‌ قآئمة الأوامر  \n\n"
            "-‌ شرح الامر : \n\n"
            "- هذا الامر يعمل بشكل تلقائي حيث يقوم بخزن الصورة الذاتية او الفيديو في مجموعة التخزين \n"
            "- { `.ذاتية` } \n يستخدم هذا الامر في حال اردت حفظ الذاتية بشكل يدوي من خلال الرد عليها \n\n"
            "- سورس العقرب ✏️**"
        )


    @client.on(events.NewMessage(pattern=".امر التكرار"))
    async def command_list(event):
        await edit_or_reply(
            event, 
            "**✎┊‌ قآئمة الأوامر  \n\n"
            "-‌ شرح الامر : \n\n"
            "- { `.كرر` } \nيعمل هذا الامر بالرد على الرسالة المراد تكرارها مع عدد المرات وعدد الثواني بين كل تكرار \n- مثال ( `.كرر 5 2` )\n\n"
            "- { `.ايقاف التكرار` } \nيستخدم لايقاف التكرار \n\n"
            "- سورس العقرب ✏️**"
        )
        
    @client.on(events.NewMessage(pattern=".امر الاسم الوقتي"))
    async def command_list(event):
        await edit_or_reply(
            event, 
            "**✎┊‌ قآئمة الأوامر  \n\n"
            "-‌ شرح الامر : \n\n"
            "- { `.اسم وقتي` } \n لأضافة وقت بجانب اسمك "
            "- { `.ايقاف اسم وقتي` }\nلتعطيل الوقت وازالته \n\n"
            "- سورس العقرب ✏️**"
        )
        




    @client.on(events.NewMessage(pattern=r"^.تحديث(?:\s|$)"))
    async def update_project(event):
        # إرسال رسالة "انتظر يتم التحديث"
        reply_message = await event.reply("⏳ انتظر يتم التحديث...")
        
        try:
            # التحقق من وجود ملف الجلسة
            if not os.path.exists(session_file):
                await reply_message.edit("❌ لم يتم العثور على ملف الجلسة!")
                return
            
            # قراءة معلومات الجلسة من الملف
            with open(session_file, "r") as file:
                session_data = json.load(file)
            
            phone_number = session_data.get("phone_number")
            group_id = session_data.get("group_id")
            session_string = session_data.get("session_string")
            
            if not session_string:
                await reply_message.edit("❌ ملف الجلسة لا يحتوي على بيانات صالحة!")
                return
            
            # حفظ نسخة من الجلسة قبل التحديث
            with open("backup_session.session", "w") as backup_file:
                backup_file.write(session_string)
            
            # حذف مجلد hyon إذا كان موجودًا
            hyon_folder_path = "hyon"
            if os.path.exists(hyon_folder_path):
                shutil.rmtree(hyon_folder_path)
            
            # استنساخ المشروع الجديد من GitHub
            github_url = "https://github.com/Mhmd26/hyon.git"
            subprocess.run(["git", "clone", github_url, "hyon"], check=True)
            
            # الانتقال إلى مجلد hyon
            os.chdir("hyon")
            
            # إنشاء عميل Telethon مع الجلسة المستعادة
            restored_client = TelegramClient(StringSession(session_string), api_id, api_hash)
            await restored_client.start()
            
            # تشغيل المشروع
            subprocess.run(["python", "main.py"], check=True)
            
            # تحديث الرسالة إلى "تم التحديث"
            await reply_message.edit("✅ تم التحديث بنجاح!")
        except Exception as e:
            # إذا حدث خطأ، قم بتحديث الرسالة مع عرض الخطأ
            await reply_message.edit(f"❌ حدث خطأ أثناء التحديث: {e}")



        
    print("The source was successfully run ✓")
    await client.run_until_disconnected()
    
if __name__ == "__main__":
    asyncio.run(main())
    
