from unittest import async_case
from niconico_dl import NicoNicoVideoAsync
import pafy
import asyncio
import discord
import youtube_dl
import random
from discord.ext import commands
import discord_apikey

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'music\%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
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

#=======================
#youtbe API setting

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

message_is = None
observe_flag = False

#==========
#フラグおよびデータ管理クラス
#==========
class Flag():
    def __init__(self, message_is, load=False):
        self.message_is = message_is

        self.id = int
        self.url_list = list()
        self.pause_flag = False
        self.loop_flag = True
        self.nico_flag = False
#--------------------------------
#更新系
    def add_url_list(self, url_list):
        self.url_list.append(url_list)
    
    def set_pause_flag(self,pause_flag):
        self.pause_flag = pause_flag

    def re_loop_flag(self, loop_flag):
        self.loop_flag = loop_flag
#-------------------------------------
# 情報取得用    

    def get_message_is(self):
        return self.message_is

    def get_url_list(self):
        return url_list.pop(0)
    
    def get_pause_flag(self):
        return self.pause_flag
    
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

#==================================
flags = list()
#==================================
#youtubeの動画および動画リストを読み込む所
#
#:エラーが起こる場合
#：R18制限などがかかっている動画は読み込めずエラーがおこる。
#：（精度が低すぎるが）古すぎる動画を読み込もうとするとエラーが起こる。
# 回避処理を入れたい...
#==================================

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        print("youtube_dl.from_url")
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        print(data.get("thumbnail"))
        thumbnail = data.get("thumbnail")
        try:
            url_pafy = pafy.new(url, gdata=False)
            url_pafy = url_pafy.getbestaudio(preftype="webm").url
        except:
            url_pafy = pafy.new(url).getbestvideo(preftype="mp4").url
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(url_pafy, **ffmpeg_options), data=data),thumbnail,filename


    #play_listのurlだけ追加する。
    @classmethod
    async def play_list(cls, url, *, loop=None, stream=False):
        print("youtube_dl.play_list")
        play_list_in_url = []
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        for items in data["entries"]:
            play_list_in_url.append("https://www.youtube.com/watch?v=" + items["id"])
        return play_list_in_url

#=====================================================================
# ニコニコ動画のurlを持ってくる処理
# ===================================================================       
class nico(discord.PCMVolumeTransformer):

    def __init__(self, source, *, volume=0.3):
        super().__init__(source, volume)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        print("niconico_dl.from_url")
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
                if message_is.guild.id == id :
                    loop_flag = flag.get_loop_flag()
                    if loop_flag:
                        try:
                            data = True
                            await self.main(id ,data)#mainを呼ぶ
                        except AttributeError:
                            await bot.close()
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
            
            print("start_main")
            pass
        else:
            for flag in flags:
                print(id)
                message_is = flag.get_message_is()
                if message_is.guild.id == id: #一致する音声チャンネルの時
                    try:
                        members = [i.name for i in message_is.author.voice.channel.members] #人がいなくなったら削除しようとしたやつ：読んだ本人が音声チャンネルから抜けたらデータ取れなくなる。　別の方法がいる。
                        print(len(members))
                    except:

                        #flags.remove(flag)
                        #print("削除しました")
                        #message_is.guild.voice_client.stop()
                        #await message_is.guild.voice_client.disconnect()
                        #flag.re_loop_flag(False)
                        
                        #embed3 = discord.Embed(title="誰も聞いてくれないので切断しました。",description="", color=0x3cb371)
                        #await message_is.channel.send(embed=embed3, delete_after=15)
                        print("wawa")
 
                    if not flag.get_pause_flag(): #＝＝＝一時停止中でないときに読みこむ＝＝＝
                        print(id)
                        print("同じ_音声チャンネル")
                        loop = asyncio.get_event_loop()
                        print(flag)
                        await loop.create_task(self.replay(self,flag,id))
                        return
                    else:
                        return
                    
                        
                else:
                    print("これじゃない音声チャンネル")
                    continue
            
        print("chack_now")
        return
        

    
    async def replay(self,flag,id):#次再生するところ
        self.flag = flag
        print("_replay_")
        
        try:
            message_is = self.flag.get_message_is()
            print(message_is)
            print("messageis")
            if message_is.guild.id == id:
                print("gomessage")
                url_list = self.flag.get_url_list_info()
            else:
                return
            

            if url_list:
                if  not message_is.guild.voice_client.is_playing(): #他に再生していないとき
                
                    if message_is.guild.id == id:
                        #　ここの文はyoutubeの動画リストを再生する際に動画リストに
                        if None == url_list[0]:
                            trace = url_list.pop(0)
                        Y_url = url_list.pop(0)
                        print(Y_url)
                        print(type(Y_url))


                        if ("nicovideo.jp" in Y_url or "nico.ms" in Y_url): #ニコニコ動画のurlの時の処理
                            niconico = NicoNicoVideoAsync(Y_url)
                            niconico.connect()
                            url = await niconico.get_download_link()
                            print("ニコニコ動画が読み込まれました。")
                            print(url)
                            player = await nico.from_url(url)
                            source = player
                            message_is.guild.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                            embed3 = discord.Embed(title="ニコニコ動画を再生します▶︎",description="", color=0x3cb371)
                            return


                        else:

                            try:
                                player,thumbnail,filename = await YTDLSource.from_url(Y_url, loop=bot.loop)
                                source = discord.PCMVolumeTransformer(player, volume=0.1)
                                print("nandato")

                                
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
                
                

                    
        
        #except IndexError:
        #    print("index")
        #    pass
        except youtube_dl.utils.DownloadError:

            load = False 
            loop = asyncio.get_event_loop()      
            task = loop.create_task(self.Load(self, flag))
            await task
            print("Downloaderr")
    pass

bot = commands.Bot(command_prefix="!!")

@bot.event
async def on_ready():
    print("==========")
    print('We have logged in as {0.user}'.format(bot))
    print("ログインしました")
    print(bot.user.name)
    print(bot.user.id)
    print("==========")

@bot.event
async def on_message(message):
    #処理
    await bot.process_commands(message)

@bot.command()
async def join(ctx):
    global flags, observe_flag
    if ctx.author.voice is None:#音声チャンネルにいない人からの通知は拒否する。
        await ctx.channel.send("あなたは音声チャンネルに接続していません。")
        return
                
    for flag in flags:
        mes = flag.get_message_is()
        if ctx.guild.id == mes.guild.id:
            embed3 = discord.Embed(title="もうすでにいるよ!",description="", color=0x3cb371)              
            await ctx.channel.send(embed=embed3, delete_after=15)
            return
        else:
            pass

    await ctx.author.voice.channel.connect()
    await ctx.channel.send("接続しました。")

    message_is = ctx
    flags.append(Flag(message_is))
    if not observe_flag: #まだ一つも音声チャンネルの監視を行っていないとき
        obs = observer(ctx)
        loop = asyncio.get_event_loop()
        loop.create_task(obs.main(ctx.guild.id ,None))#音声チャンネル監視開始
        observe_flag = True
    else:
        pass #この処理で2つ目以降の音声チャンネルに入った時重複ループの作成を回避する。

@bot.command()
async def bye(ctx):
    global flags
    if ctx.guild.voice_client is None :#もう音声チャンネルに接続していないときに呼び出す
        await ctx.channel.send("接続していません。")
                
    for flag in flags:
        mes = flag.get_message_is()
        if ctx.guild.id == mes.guild.id:
            flags.remove(flag)
            print("削除しました")
    await ctx.guild.voice_client.disconnect()
    try:
        NicoNicoVideoAsync.close()
    except:
        pass

        await ctx.channel.send("切断しました。")

@bot.command()
async def p(ctx, arg):
    global flags
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.guild.id == ctx.guild.id:
            print("同じ")
                        
        else:
            print("これじゃない")
            continue
        #urlが最低httpsであること
        if "https://" in arg:
            message_is = ctx
        #もしプレイリストであったら
            if "playlist?list=" in arg:
                embed3 = discord.Embed(title="再生リストの再生準備を始めます",description="", color=0x3cb371)
                embed3.add_field(name="これは再生リストだね",value="再生までちょっと待ってね！",inline=False)                
                await ctx.channel.send(embed=embed3, delete_after=15)
                print("go!")
                try:
                    play_url_list = await YTDLSource.play_list(arg)
                    print("end!")
                except:
                    print("youtube_downroad_err")
                    return

            #プレイリストを各動画再生urlに分解
                for urls in play_url_list:
                    flag.add_url_list(urls)
                print(flag.get_url_list_info())
                print("stack")
                return

            if ctx.guild.voice_client.is_playing():
                    #再生中に再生しない
                embed3 = discord.Embed(title="再生中です▶︎",description="", color=0x3cb371)
                await ctx.channel.send(embed=embed3, delete_after=15)

                            
                            
                flag.add_url_list(arg)
                await ctx.channel.send("再生待ちリストに入りました。")
                return

#ここからurl_listをためてそこからplayするようにしたい

            flag.add_url_list(arg)
            print("hairimasita")
            await ctx.channel.send("再生待ちリストに入りました。")
            print(url_list)
        

        else:
            embed3 = discord.Embed(title="無効なURLです",description="", color=0x3cb371)
            await ctx.channel.send(embed=embed3, delete_after=15)

@bot.command()
async def pp(ctx):
    global flags
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
            pass
        else:
            return
        message_is.guild.voice_client.stop()

        embed3 = discord.Embed(title="次の動画を再生します▶︎",description="", color=0x3cb371)
        await message_is.channel.send(embed=embed3, delete_after=15)
@bot.command()
async def st(ctx):
    global flags
    if ctx.guild.voice_client is None:
        await ctx.channel.send("接続していません。")
        return
        #再生するときのみ停止
    if not ctx.guild.voice_client.is_playing():
        await ctx.channel.send("再生していません。")
        return
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
            flag.set_pause_flag(True)

        else:
            continue
    ctx.guild.voice_client.stop()
        
    await ctx.channel.send("ストップしました。")

@bot.command()
async def clear(ctx):
    global flags
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
            pass
        else:
            continue
        flag.url_list.clear()
#await message.channel.send("再生準備キューに入っていたものをすべて消去しました。")
    embed3 = discord.Embed(title="再生準備キューに入っていたものをすべて消去しました。",description="", color=0x3cb371)
    await ctx.channel.send(embed=embed3, delete_after=15)
@bot.command()
async def chack(ctx):
    global flags
    print(len(flags))
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
            pass
        else:
            continue                
    ch = len(flag.get_url_list_info())
#await message.channel.send(f"{ch}個の再生準備中の曲が存在します。")
    embed3 = discord.Embed(title=f"{ch}個の再生準備中の曲が存在します。",description="", color=0x3cb371)
    await ctx.channel.send(embed=embed3, delete_after=15)
@bot.command()
async def shuffle(ctx):
    global flags
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
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
    await ctx.channel.send(embed=embed3, delete_after=15)

@bot.command()
async def rest(ctx):
    global flags
    for flag in flags:
        message_is = flag.get_message_is()
        if message_is.channel == ctx.channel:
            flag.set_pause_flag(False)
            await ctx.channel.send("一時停止を解除しました。") 
        else:
            continue 

@bot.command()
async def helps(ctx):
    embed3 = discord.Embed(title="このBotのhelpです。",description="", color=0x3cb371)
    embed3.add_field(name="!!join",value="今いる音声チャンネルにボットが来るよ！",inline=False)
    embed3.add_field(name="!!bye",value="今いる音声チャンネルから去るよ！",inline=False)
    embed3.add_field(name="!!p ",value="!!pの後ろに一つスペースを開けてからurlを入れると再生してくれるよ! 再生リストでもok!",inline=False)
    embed3.add_field(name="!!pp",value="再生キューの次の動画を再生するよ！",inline=False)
    embed3.add_field(name="!!st",value="再生を一時停止するよ！",inline=False)
    embed3.add_field(name="!!rest",value="再生を再開するよ！",inline=False)
    embed3.add_field(name="!!clear",value="再生準備中の曲をすべて削除するよ！",inline=False)
    embed3.add_field(name="!!chack",value="いくつの曲が再生準備してるかわかるよ！",inline=False)
    embed3.add_field(name="!!shuffle",value="曲の再生順を適当に変えちゃうよ！",inline=False)
    

    await ctx.channel.send(embed=embed3, delete_after=15)

bot.run(DISCORD_TOKEN)