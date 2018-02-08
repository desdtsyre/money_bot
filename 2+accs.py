from threading import Thread
from time import sleep, time
import re

from pyrogram import Client

from pyrogram.api.types import UpdateNewChannelMessage
from pyrogram.api.functions.messages import GetBotCallbackAnswer
from pyrogram.api.types.update import Update
from pyrogram.api.types.update_new_message import UpdateNewMessage

class SlishRabotat(Thread):
    def __init__(self, session_name):
        Thread.__init__(self)
        self.session_name = session_name

    def run(self):
        last_time = 0

        doned = []

        bonuses_id = 1317469445
        bot_id = 398938067

        class NewBonus:
            def __init__(self, peer, msg_id: int, data: bytes):
                self.peer = peer
                self.msg_id = msg_id
                self.data = data

        class NewCaptcha:
            def __init__(self, peer, msg_id: int, data: bytes):
                self.peer = peer
                self.msg_id = msg_id
                self.data = data

        class Work(Thread):
            def __init__(self):
                Thread.__init__(self)
                self.active = True

            def run(self):
                print('new work')
                while self.active:
                    sleep(10)
                    client.send_message(bot_id, '👁 Смотреть пост')

            def stop(self):
                self.active = False
                self.join()

        def captcha(update):
            if isinstance(update, Update):
                for m in update.updates:
                    if isinstance(m, UpdateNewMessage):
                        msg = m.message
                        if msg.from_id == bot_id:
                            str_cap = re.match(r'^Чтобы продолжить, найдите кнопку . и нажмите на нее!$', msg.message)
                            if str_cap is not None:
                                row = msg.reply_markup.rows
                                for i in row:
                                    for b in i.buttons:
                                        if b.data.decode() == 'anti-nakrut':
                                            ret = NewCaptcha(
                                                peer=client.resolve_peer('@PayViewBot'),
                                                msg_id=msg.id,
                                                data=b.data
                                            )
                                            return ret
                            elif 'Уведомления о появлении новых постов' in msg.message:
                                return 'posts_end'
                    elif isinstance(m, UpdateNewChannelMessage):
                        msg = m.message
                        if msg.to_id.channel_id == bonuses_id:
                            try:
                                if msg.reply_markup:
                                    ret = NewBonus(
                                                peer=client.resolve_peer(msg.to_id.channel_id),
                                                msg_id=msg.id,
                                                data=msg.reply_markup.rows[0].buttons[1].data,
                                            )
                                    return ret
                            except AttributeError:
                                pass

        client = Client(session_name=self.session_name)

        work = Work()

        def replier(update):
            nonlocal work
            nonlocal last_time
            captcha_ret = captcha(update)
            if isinstance(captcha_ret, NewCaptcha):
                if captcha_ret.msg_id not in doned:
                    sleep(3)
                    client.send(GetBotCallbackAnswer(
                        peer=captcha_ret.peer,
                        msg_id=captcha_ret.msg_id,
                        data=captcha_ret.data
                    ))
                    doned.append(captcha_ret.msg_id)
                    return None
            elif captcha_ret == 'posts_end':
                if time()-last_time > 30:
                    last_time = time()
                    work.stop()
                    sleep(300)
                    work = Work()
                    work.start()
            elif isinstance(captcha_ret, NewBonus):
                sleep(3)
                client.send(GetBotCallbackAnswer(
                    msg_id=captcha_ret.msg_id,
                    peer=captcha_ret.peer,
                    data=captcha_ret.data,
                ))

        work.start()
        client.set_update_handler(replier)
        client.start()
        client.idle()

session_names = ['kolay', 'kolyan'] # Сюда писать все назвения сесий который будут работать в боте

for session in session_names:
    SlishRabotat(session).start()
