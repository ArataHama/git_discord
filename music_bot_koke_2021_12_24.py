#import keep_alive
from ctypes.wintypes import tagSIZE
from niconico_dl import NicoNicoVideoAsync
import pafy
import asyncio
from asyncio.events import set_child_watcher
from datetime import date
from re import T
import re
import time
import sys
from typing import ContextManager
import discord
import youtube_dl
#from googleapiclient.discovery import build
import niconico_dl  
import random
import os 
import shutil





# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

try:
    os.mkdir("music")
except:
    print("既にファイルがあります")
    pass


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'music\%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',

}

music_url_directory = "music"

#=======================
#youtbe API setting
API_KEY = "AIzaSyBsVtYsGwQgKDtLcE1n8gb7Dp2wxtg-j9Q"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSON = "v3"

#youtube = build(
#    YOUTUBE_API_SERVICE_NAME,
#    YOUTUBE_API_VERSON,
#    developerKey=API_KEY
#)
#=======================

Chance = 0.01

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


url_list = list()

play_is = False
load = False
message_is = None
music_files = list()
music_files_num = 0
DISCORD_TOKEN = "ODQyNTAzNTgxNzQzMDU0OTIw.YJ2Qmg.JFjN-lmFfPG-urwRXIhC_AopNOQ"
endtask = False


shutil.rmtree(music_url_directory)
os.mkdir(music_url_directory)
client = discord.Client()
#==========
#クラスでデータを保持するものを創ったらいいのでは？
class Sourse():
    def __init__(self,player,thumbnail,filename):
        self.player = player
        self.thumbnail = thumbnail
        self.fillname = filename
    
    def get_player(self):
        return self.player
    
    def get_thumbnail(self):
        return self.thumbnail
    
    def get_filename(self):
        return self.fillname
#==========
#フラグ管理クラス
#==========
class Flag():
    def __init__(self, message_is, load=False):
        self.message_is = message_is
        self.load = load
        self.id = int
        self.music_files = list()
        self.url_list = list()
        self.play_is = False
        self.loop_flag = True
#--------------------------------
#更新系
    def add_url_list(self, url_list):
        self.url_list.append(url_list)
    
    def add_music_files(self, music_file):
        self.music_files.append(music_file)
    
    def re_load(self, load):
        self.load = load
    
    def re_play_is(self, play_is):
        self.play_is = play_is
    def re_loop_flag(self, loop_flag):
        self.loop_flag = loop_flag
#-------------------------------------
# 情報取得用    

    def get_message_is(self):
        return self.message_is

    def get_load(self):
        return self.load
    
    def get_play_is(self):
        return self.play_is
    
    def get_url_list(self):
        return url_list.pop(0)

    def get_music_file(self):
        return self.music_files.pop(0)
    
    

    
    def get_url_list_info(self):
        return self.url_list
    
    def get_music_files_info(self):
        return self.music_files
    
    def get_loop_flag(self):
        return self.loop_flag
#---------------------------------
#消去形
    
    def url_list_clear(self):
        self.url_list.clear()
    
    def music_files_clear(self):
        self.music_files.clear()
#==================================
flags = list()
#==================================


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print(data.get("thumbnail"))
        thumbnail = data.get("thumbnail")
        try:
            print("youtube")
            url_pafy = pafy.new(url, gdata=False)
            url_pafy = url_pafy.getbestaudio(preftype="webm").url
        except:
            url_pafy = pafy.new(url).getbestvideo(preftype="mp4").url
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(url_pafy, **ffmpeg_options), data=data),thumbnail,filename


    #play_listのurlだけ追加する。
    @classmethod
    async def play_list(cls, url, *, loop=None, stream=False):
        play_list_in_url = []
        loop = loop or asyncio.get_event_loop()
        print("tottemo")
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print("owatta")
        for items in data["entries"]:
            print("st")
            play_list_in_url.append("https://www.youtube.com/watch?v=" + items["id"])
        return play_list_in_url

class nico(discord.PCMVolumeTransformer):

    def __init__(self, source, *, volume=0.5):
        super().__init__(source, volume)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):

        return cls(discord.FFmpegPCMAudio(url, **ffmpeg_options))


       
        
        




class observer():#botが音楽を再生しているかどうか調べる
    def __init__(self,message):#初期化
        global message_is,play_is, flags
        self.id = message.guild.id
        print("init")
        print(self.id)
        
        
    @classmethod#クロック回路再生して居なければmainを呼ぶ
    async def monitor(self,id):
        global message_is, flags

        while True:
            for flag in flags:
                message_is = flag.get_message_is()
                if message_is.guild.id == id:
                    loop_flag = flag.get_loop_flag()
                    if loop_flag:
                        try:
                            data = True
                            await self.main(id ,data)#mainを呼ぶ
                        except AttributeError:
                            await client.close()
                    else:
                        break
                else:
                    print("これじゃない")
                    continue
                    
            
            await asyncio.sleep(5)#待つ　この間は他の応答を受け付けている
    @classmethod
    async def main(self,id, data):
        global flags
        if data == None:#最初に読んだときにスルーさせる
            print(id)
            loop = asyncio.get_event_loop()
            await loop.create_task(self.monitor(id))
            
            print("start")
            pass
        else:
            for flag in flags:
                print(id)
                message_is = flag.get_message_is()
                if message_is.guild.id == id:
                    try:
                        members = [i.name for i in message_is.author.voice.channel.members]
                        print(len(members))
                    except:

                        #flags.remove(flag)
                        #print("削除しました")
                        #message_is.guild.voice_client.stop()
                        #await message_is.guild.voice_client.disconnect()
                        #flag.re_loop_flag(False)
                        
                        #embed3 = discord.Embed(title="誰も聞いてくれないので切断しました。",description="", color=0x3cb371)
                        #await message_is.channel.send(embed=embed3, delete_after=15)
                        print("wawa ")

                    print(id)
                    print("同じ")
                    loop = asyncio.get_event_loop()
                    print(flag)
                    await loop.create_task(self.replay(self,flag,id))
                    print("chack")
                    return
                    
                        
                else:
                    print("これじゃない")
                    continue
            
        print("chack_now")
        return
        

    
    async def replay(self,flag,id):#次再生するところ
        self.flag = flag
        print("wa-")
        
        try:
            message_is = self.flag.get_message_is()
            print(message_is)
            print("messageis")
            if message_is.guild.id == id:
                print("gomessage")
                music_files = self.flag.get_music_files_info()
                url_list = self.flag.get_url_list_info()
                play_is = self.flag.get_play_is()
                load = self.flag.get_load()
            else:
                return
            

            if url_list:
                if  not message_is.guild.voice_client.is_playing(): #他に再生していないとき
                    
                    print(len(music_files)) #下のものは直接ファイルの中身を見てるんだけどこれはいまのPC以外に移せないから修正必須
                
                        #　ここにダウンロードした物の数のカウンターの加算分を追加（）
                        #　try exceptでエラー発生時にカウンダを減らすようにする
                    if message_is.guild.id == id:
                        Y_url = url_list.pop(0)
                        print(Y_url)
                        print(type(Y_url))
                        #if "https://nico.ms/" in Y_url:
                        #    print(Y_url)
                        #    Y_url = re.findall("[0-9]+",Y_url)
                        #    for i in Y_url:
                        #        Y_url = "https://www.nicovideo.jp/watch/" + str(i)
                        #    Nico = await  nico.niconico(Y_url)
                        #    url = Nico
                        #    source = url
                        if ("nicovideo.jp" in Y_url or "nico.ms" in Y_url):
                            niconico = NicoNicoVideoAsync(Y_url, log = True)
                            url = await niconico.get_download_link()
                            print("ニコニコ動画が読み込まれました。")
                            print(url)
                            ffop = {'options': '-vn -af "volume=0.3"'}
                            player = await nico.from_url(url)
                            source = player
                            message_is.guild.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

                        else:

                            try:
                                player,thumbnail,filename = await YTDLSource.from_url(Y_url, loop=client.loop)
                                source = discord.PCMVolumeTransformer(player, volume=0.1)

                                
                            except Exception:
                                embed3 = discord.Embed(title="動画を再生できませんでした。",description="", color=0x3cb371)
                                embed3.add_field(name="原因として",value="年齢制限がかかっている。",inline=False)
                                embed3.add_field(name="",value="niconico動画を再生しようとした。",inline=False)
                                embed3.add_field(name="などが考えられます。",value="",inline=False)
                                await message_is.channel.send(embed=embed3, delete_after=15)
                                return
                    else:
                        return
                        
                    print("準備中")
                #ここにMucic_file の起動するものが入るはず
                #ここに、music_fileが処理を完遂してキューが達成時に下の機能を起動したい。
                    flag.re_play_is(True)

                    message_is.guild.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                    print("player")
                    print(filename)
                    urlp4 = thumbnail
                    #動画をさいせいするぞ！
                    embed3 = discord.Embed(title="動画を再生します▶︎",description="", color=0x3cb371)
                    try:
                        embed3.description = (player.title)
                        embed3.set_thumbnail(url=urlp4)
                    except:
                        pass
                    await message_is.channel.send(embed=embed3, delete_after=15)
                
                
                    flag.re_play_is(False)

                    
        
        #except IndexError:
        #    print("index")
        #    pass
        except youtube_dl.utils.DownloadError:
            self.flag.re_play_is(False)
            load = False 
            loop = asyncio.get_event_loop()      #restart Load()
            task = loop.create_task(self.Load(self, flag))
            await task
            print("Downloaderr")
    pass
    

#=============================================================        


#=========================================================
#クラス再起動
class BotTask:
    "ネットワークが切れた時の再接続対応クラス"

    def __init__(self):
        self.retry_count = 0

    def start_with_retry(self):
        "再接続対応でbotを開始する"
        while True:
            try:
                #botstart
                self._start()
                #正常終了の時はスクリプトを終了する
                break
            except Exception as e:
                self.retry_count += 1
                print(e)
                #エラー発生時
                print("retry %d" % self.retry_count)
                # 2のリトライ回数乗x5秒待つ
                interval = 5*2**self.retry_count
                print("interval %d" % interval)
                #待ち時間が4時間を超えると再起動を終了する
                if interval >= 4*60*60:
                    break
                time.sleep(interval)
    
    def _start(self):
        #クライアントを作成
        global client
        client = self._make_client()
        token = DISCORD_TOKEN
        client.run(token, reconnect=False)
    
    def _make_client(self):
        "Discodeのクライアントを作成する"
        # リアクションの削除のために必要
        intents = discord.Intents.all()
        # Clientクラス内部で作られるイベントループは1スレッド1つ。
        # そしてエラーになると、それが閉じられるので、毎回新しく作成する
        loop = asyncio.new_event_loop()
        #クライアントを作成時に渡す
        client = discord.Client(intents=intents, loop=loop)
        @client.event
        async def on_ready():
            global message_is
            #接続させたのでretry_countを戻す
            self.retry_count = 0
            print("==========")
            print('We have logged in as {0.user}'.format(client))
            print("ログインしました")
            print(client.user.name)
            print(client.user.id)
            print("==========")
        

        @client.event
        async def on_message(message:discord.Message):
            global url_list,play_is,message_is,flags, endtask
            print("a")
        #ボットのメッセージを除去
            if message.author.bot:
                return
    
    #音声チャンネルにジョインする
            elif message.content == "!join" :
                if message.author.bot:#botは除外する
                    return
        
                if message.author.voice is None:#音声チャンネルにいない人からの通知は拒否する。
                    await message.channel.send("あなたは音声チャンネルに接続していません。")
                    return
                
                for flag in flags:
                    mes = flag.get_message_is()
                    if message.guild.id == mes.guild.id:
                        embed3 = discord.Embed(title="もうすでにいるよ!",description="", color=0x3cb371)              
                        await message.channel.send(embed=embed3, delete_after=15)
                        return
                    else:
                        pass

                await message.author.voice.channel.connect()
                await message.channel.send("接続しました。")

                message_is = message
                flags.append(Flag(message_is))
                obs = observer(message)
                loop = asyncio.get_event_loop()
                loop.create_task(obs.main(message.guild.id ,None))#音声チャンネル監視開始

    #音声チャンネルから切断する
            elif message.content == "!bye":
                if message.guild.voice_client is None :#もう音声チャンネルに接続していないときに呼び出す
                    await message.channel.send("接続していません。")
                
                for flag in flags:
                    mes = flag.get_message_is()
                    if message.guild.id == mes.guild.id:
                        flags.remove(flag)
                        print("削除しました")
        
                await message.guild.voice_client.disconnect()

                await message.channel.send("切断しました。")
        
            elif message.content.startswith("!!p "):#音楽の再生（多分youtube限定ニコニコは駄目だった）
                for flag in flags:
                    message_is = flag.get_message_is()
                    if message_is.guild.id == message.guild.id:
                        print("同じ")
                        
                    else:
                        print("これじゃない")
                        continue
                    url = message.content[4:]
                #urlが最低httpsであること
                    if "https://" in url:
                        message_is = message
            #もしプレイリストであったら
                        if "https://youtube.com/playlist?list=" in url:
                            embed3 = discord.Embed(title="再生リストの再生準備を始めます",description="", color=0x3cb371)
                            embed3.add_field(name="これは再生リストだね",value="再生までちょっと待ってね！",inline=False)                
                            await message.channel.send(embed=embed3, delete_after=15)
                            print("go!")

                            play_url_list = await YTDLSource.play_list(url)
                            print("end!")

            #プレイリストを各動画再生urlに分解
                            for urls in play_url_list:
                                flag.add_url_list(urls)
                                print(flag.get_url_list_info())
                                print("stack")
                            return
                        if message.guild.voice_client.is_playing():
                    #再生中に再生しない
                            await message.channel.send("再生中です。")
                            embed3 = discord.Embed(title="再生中です▶︎",description="", color=0x3cb371)
                            await message.channel.send(embed=embed3, delete_after=15)

                            
                            
                            flag.add_url_list(url)
                            await message.channel.send("再生待ちリストに入りました。")
                            return
                        if play_is:
                    #再生準備中に再生しない
                            await message.channel.send("再生中です。")

                            flag.add_url_list(url)
                            await message.channel.send("再生待ちリストに入りました。")
                            return
                #再生準備中フラグ立てる

        
        
#ここからurl_listをためてそこからplayするようにしたい

                        flag.add_url_list(url)
                        print("hairimasita")
                        await message.channel.send("再生待ちリストに入りました。")
                        print(url_list)
        

                    else:
                        embed3 = discord.Embed(title="無効なURLです",description="", color=0x3cb371)
                        await message.channel.send(embed=embed3, delete_after=15)
            
        
        
        

            elif message.content.startswith("!!pp"): #今流れている音楽をすくに止めて次のキューに入っている音楽を再生する。

                for flag in flags:
                    message_is = flag.get_message_is()
                    if message_is.channel == message.channel:
                        pass
                    else:
                        return
                    
                message_is.guild.voice_client.stop()

                embed3 = discord.Embed(title="次の動画を再生します▶︎",description="", color=0x3cb371)
                await message_is.channel.send(embed=embed3, delete_after=15)
 
                #player,thumbnail = await YTDLSource.from_url(Y_url,loop=client.loop)    
#再生する
                #message.guild.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

                #urlp4 = thumbnail
                #embed3 = discord.Embed(title="動画を再生します▶︎",description="", color=0x3cb371)
                #embed3.description = (player.title)
                #embed3.set_thumbnail(url=urlp4)
                #await message.channel.send(embed=embed3, delete_after=15)
#再生停止する
            elif message.content == "!!st":
                if message.guild.voice_client is None:
                    await message.channel.send("接続していません。")
                    return
        #再生するときのみ停止
                if not message.guild.voice_client.is_playing():
                    await message.channel.send("再生していません。")
                    return
        
                message.guild.voice_client.stop()
        
                await message.channel.send("ストップしました。")



#再生準備キューの中に入っているものをすべて消すのもあったほうがいいね（あとで）
            elif message.content == "!!clear":
                for flag in flags:
                    message_is = flag.get_message_is()
                    if message_is.channel == message.channel:
                        pass
                    else:
                        continue
                    flag.url_list.clear()
                    flag.music_files.clear()
        #await message.channel.send("再生準備キューに入っていたものをすべて消去しました。")
                embed3 = discord.Embed(title="再生準備キューに入っていたものをすべて消去しました。",description="", color=0x3cb371)
                await message.channel.send(embed=embed3, delete_after=15)
#再生準備中キューに何個入ってるかしらべてみよー！
            elif message.content == "!!chack":
                print(len(flags))
                for flag in flags:
                    message_is = flag.get_message_is()
                    if message_is.channel == message.channel:
                        pass
                    else:
                        continue                
                ch = len(flag.get_url_list_info())
        #await message.channel.send(f"{ch}個の再生準備中の曲が存在します。")
                embed3 = discord.Embed(title=f"{ch}個の再生準備中の曲が存在します。",description="", color=0x3cb371)
                await message.channel.send(embed=embed3, delete_after=15)
            elif message.content =="!!shuffle": 
                for flag in flags:
                    message_is = flag.get_message_is()
                    if message_is.channel == message.channel:
                        if len(flag.get_url_list_info()) > 0:
                            pass
                        else:
                            embed3 = discord.Embed(title="再生準備中の曲はないのにシャッフルすることはできないよ～",description="", color=0x3cb371)
                            embed3.add_field(name="もしかして",value="再生リストを読み込んでからすぐはシャッフルできないよ",inline=False)
                            message_is.channel.send(embed=embed3, delete_after=15)
                    else:
                        continue
                print(url_list)
                ch = len(flag.get_url_list_info())
                url_list_tmp = random.sample(flag.get_url_list_info(),ch)
                flag.url_list_clear()
                for inp_url in url_list_tmp:
                    flag.add_url_list(inp_url)
                print(flag.get_url_list_info())
        
        #await message.channel.send(f"{ch}個の再生準備中の曲が存在します。")
                embed3 = discord.Embed(title=f"{ch}個の曲の再生順をランダムに変えちゃったよ？",description="", color=0x3cb371)
                await message.channel.send(embed=embed3, delete_after=15)
            elif message.content =="!!end": #bot本体を停止させるコマンド管理者以外は打てない（今はサーバー管理者のみ（bot管理者のみにしないと1つのサーバでやられるとすべてのサーバに入っているbotが停止する。））
                if message.author.guild_permissions.administrator:

                    embed3 = discord.Embed(title=f"ボットをシャットダウンします",description="", color=0x3cb371)
                    await message.channel.send(embed=embed3, delete_after=15)
                    endtask = True
                    await message.guild.voice_client.disconnect()
                    await client.close()
            elif message.content=="!!restart":
                if message.author.guild_permissions.administrator:

                    embed3 = discord.Embed(title=f"ボットをリスタートします",description="", color=0x3cb371)
                    await message.channel.send(embed=embed3, delete_after=15)
                    await message.guild.voice_client.disconnect()
                    await client.close()
            

#heipを用意する
            elif message.content == "!!help":
                embed3 = discord.Embed(title="このBotのhelpです。",description="", color=0x3cb371)
                embed3.add_field(name="!join",value="今いる音声チャンネルにボットが来るよ！",inline=False)
                embed3.add_field(name="!bye",value="今いる音声チャンネルから去るよ！",inline=False)
                embed3.add_field(name="!!p ",value="!!pの後ろに一つスペースを開けてからurlを入れると再生してくれるよ! 再生リストでもok!",inline=False)
                embed3.add_field(name="!!pp",value="再生キューの次の動画を再生するよ！",inline=False)
                embed3.add_field(name="!!st",value="再生を停止するよ！",inline=False)
                embed3.add_field(name="!!clear",value="再生準備中の曲をすべて削除するよ！",inline=False)
                embed3.add_field(name="!!chack",value="いくつの曲が再生準備してるかわかるよ！",inline=False)
                embed3.add_field(name="!!shuffle",value="曲の再生順を適当に変えちゃうよ！",inline=False)
                embed3.add_field(name="!!end",value="サーバの管理者のみ使用できるbotの緊急停止コマンドです。これを使用した時は速やかに制作者に使用した理由ともに報告をお願いします。すべてのサーバのボットが停止します。",inline=False)


                await message.channel.send(embed=embed3, delete_after=15)





        return client
#=========================================================

    
    
    
    


task = BotTask()
task.start_with_retry()
for flag in flags:
    flags.remove(flag)
    print("削除しました")
if not endtask:
    task.start_with_retry()
#作った音声ファイルを消去

shutil.rmtree(music_url_directory)
os.mkdir(music_url_directory)


if endtask:
    sys.exit()
       #サムネイル取得用のURL校正
        #urlp1 = (song.removeprefix('https://www.youtube.com/watch?v='))
        #urlp2 = (urlp1.removeprefix('https://youtu.be/'))
        #urlp3 = (urlp2.partition('&')[0])
        #urlm1 = ('http://img.youtube.com/vi/')
        #urlm2 = ('/default.jpg')
        #urlp4 = (urlm1+urlp3+urlm2)
        #embed生成
        #embed3 = discord.Embed(title="動画を再生します▶︎",description="", color=0x3cb371)
        #embed3.description = (f"[{songn}]({song})")
        #embed3.set_thumbnail(url=urlp4)
        #await ctx.send(embed=embed3, delete_after=15)

        #botが落ちた際に再起動する準備を整える必要ありツーかやりたい
        