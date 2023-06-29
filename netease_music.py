import os

from plugins.plugin_music.netease.request import *
import plugins
from plugins import *
from common.log import logger
from bridge.bridge import Bridge
from bridge.context import ContextType
import re
from bridge.reply import Reply, ReplyType
from config import conf as root_config

trigger_prefix="$" #全局变量

@plugins.register(
    name="Music",
    desire_priority=0,
    hidden=True,
    desc="基于网易云搜索音乐的插件",
    version="0.1",
    author="nautilis",
)
class Music(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        conf = {}
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            conf = json.load(f)
        username = conf.get("username", "")
        passwd_md5 = conf.get("passwd_md5", "")
        if username == "" or passwd_md5 == "":
            logger.error("username or passwd_md5 not config, Music quit")
            return
        self.api = NetEaseApi(username, passwd_md5)

        #修改全局变量，需要使用global关键字声明
        global trigger_prefix
        trigger_prefix = root_config().get("plugin_trigger_prefix", "$")
        logger.info("[Music] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return
        query = e_context["context"].content
        logger.info("content => " + query)
        reply = Reply()
        reply.type = ReplyType.TEXT
        if query.startswith(f'{trigger_prefix}music '):
            query_list = query.split(" ", 1)
            query = query_list[1]
            if query.startswith(f'点歌'):
                msg = query.replace("点歌", "")
                msg = msg.strip()
                url, name, ar = self.search_song(msg)
                if url != "":
                    reply.content = "{} - {} \n点击下面的🔗即可播放:\n{}".format(name, ar, url)
                else:
                    reply.content = "找不到歌曲😮‍💨"
                logger.info("点歌 reply --> {}, url:{}".format(reply, url))
            else:
                chat = Bridge().get_bot("chat")
                all_sessions = chat.sessions
                # msgs = all_sessions.session_query(query, e_context["context"]["session_id"]).messages

                reply = chat.reply(query +" 以歌名 - 歌手的格式回复", e_context["context"])
                logger.info("music receive => query:{}, reply:{}".format(query, reply))
                logger.info("")
                url, name, ar = self.search_song(reply.content)
                if url == "":
                    reply.content = reply.content + "\n----------\n找不到相关歌曲😮‍💨"
                else:
                    reply.content = reply.content + "\n----------\n" + "{} - {} \n点击下面的🔗即可播放:\n{}".format(name,
                                                                                                                   ar,
                                                                                                                   url)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

            return

            # dir = "/Users/nautilis/myspace/project/ai/chatgpt-on-wechat/plugins/music/test.xlsx"
            # reply = Reply(ReplyType.FILE, dir)
            # e_context["reply"] = reply
            # e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, verbose=False, **kwargs):
        help_text = "推荐音乐\n"
        help_text += f"{trigger_prefix}music 推荐一首粤语经典歌曲"
        help_text += "点歌\n"
        help_text += f"{trigger_prefix}music 点歌 可惜我是水瓶座-杨千嬅"
        return help_text

    def search_song(self, song_info):
        regex = r"\W?(?P<so>\w+)\W?\s?-\s?(?P<ar>\w+)"
        res = re.search(regex, song_info)
        if res:
            song = res.group("so")
            ar = res.group("ar")
            print(song)
            print(ar)
            resp = self.api.search(song)
            if resp["code"] == 200:
                result = resp["result"]
                if result:
                    songs = result["songs"]
                    songid, name, ar = pick_song(songs, song, ar)
                    if songid > 0:
                        url = self.query_song_url(songid)
                        return url, name, ar
                    else:
                        logger.error("song not found")
            else:
                logger.error("search buss code not 200, code:{}, resp:{}".format(resp["code"], resp))
        else:
            logger.info("regex not match song and ar")
        return "", "", ""

    def query_song_url(self, id):
        urlRes = self.api.song_url([str(id)])
        if urlRes["code"] == 200:
            data = urlRes["data"]
            if len(data) > 0:
                url = data[0]["url"]
                print("url => {}".format(url))
                return url
            else:
                logger.info("query url data length is zero")
        else:
            logger.info("query url buss code not 200, code:{}".format(urlRes["code"]))
        return ""


def pick_song(songs, req_name, req_ar):
    sid, name, ar = pick_song_with_accuracy(songs, req_name, req_ar, "all")
    if sid < 0:
        sid, name, ar = pick_song_with_accuracy(songs, req_name, req_ar, "only_name")
    return sid, name, ar


def pick_song_with_accuracy(songs, req_name, req_ar, accuracy):
    for song in songs:
        name = song["name"]
        ars = song["ar"]
        id = song["id"]
        ar = ""
        if len(ars) > 0:
            ar = ars[0]["name"]
        if accuracy == "all":
            if contain(req_name, name) and contain(req_ar, ar):
                return id, name, ar
        elif accuracy == "only_name":
            if contain(req_name, name):
                return id, name, ar
    return -1, "", ""


def contain(a, b):
    if len(a) > len(b):
        return a.find(b) >= 0
    else:
        return b.find(a) >= 0
