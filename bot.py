import discord
from discord.ext import commands
import json
import os
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "server_progress.json"

# المستويات بالترتيب الإجباري
LEVELS = ["سهل", "متوسط", "صعب", "مستحيل"]

# بنك القضايا (مقسم حسب المستوى، 3 مشتبه بهم لكل قضية، وأدلة ذكية غير مكشوفة)
CASES = {
    "سهل": [
        {
            "id": "E1", "title": "قضية: اختفاء العقد الثمين",
            "desc": "سرق عقد ثمين من مكتب المدير خلال اجتماع قصير، الباب لم يكسر.",
            "scene": "https://images.unsplash.com/photo-1497366216548-37526070297c",
            "clues": [
                {"name": "الدليل 1: بصمات على المزهرية", "desc": "المزهرية قرب النافذة تحولت عن مكانها وعليها آثار بصمات.", "image": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9"},
                {"name": "الدليل 2: النافذة المفتوحة", "desc": "النافذة مفتوحة جزئياً، والغرفة في الطابق الأرضي.", "image": "https://images.unsplash.com/photo-1541888946425-d0fbb180ab5f"}
            ],
            "suspects": [
                {"name": "السكرتير (سامي)", "alibi": "1. يقول إنه نقل المزهرية لتنظيفها صباحاً.\n2. يدعي أنه كان يجهز القهوة وقت السرقة."},
                {"name": "المحاسب (عمر)", "alibi": "1. يقول إنه كان في مكتبه يراجع الحسابات.\n2. ينكر مروره بمكتب المدير نهائياً."},
                {"name": "الحارس (خالد)", "alibi": "1. يدعي إنه كان في جولة تفقدية بالخارج.\n2. يقول إنه لم يلاحظ فتح النافذة."}
            ],
            "correct": "السكرتير (سامي)"
        },
        {
            "id": "E2", "title": "قضية: سرقة الكمبيوتر المحمول",
            "desc": "تمت سرقة لابتوب الإدارة من غرفة الاجتماعات الموصدة بأمان.",
            "scene": "https://images.unsplash.com/photo-1517502884422-41eaead166d4",
            "clues": [
                {"name": "الدليل 1: فنجان قهوة دافئ", "desc": "فنجان قهوة ترك على الطاولة وما زال محتفظاً بحرارته.", "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd"},
                {"name": "الدليل 2: بطاقة تعريف مفقودة", "desc": "وجدت بطاقة تعريف تخص شخصاً ما قرب الباب الخلفي.", "image": "https://images.unsplash.com/photo-1582139329536-e7284fece509"}
            ],
            "suspects": [
                {"name": "المتدرب (راكان)", "alibi": "1. يدعي أنه نسي بطاقته في الداخل قبل خروجه مبكراً.\n2. يقول إنه شرب القهوة قبل الاجتماع بساعتين."},
                {"name": "المسؤول (بندر)", "alibi": "1. يقول إنه أغلق الغرفة بنفسه وترك المفتاح بالخارج.\n2. ينكر دخوله الغرفة بعد الاجتماع."},
                {"name": "عامل الصيانة (صالح)", "alibi": "1. يدعي أنه أصلح المصباح وغادر فوراً.\n2. يقول إنه لم يرى اللابتوب أصلاً."}
            ],
            "correct": "المتدرب (راكان)"
        }
    ],
    "متوسط": [
        {
            "id": "M1", "title": "قضية: الشاي المسموم في المستودع",
            "desc": "وجد حارس المستودع فاقداً للوعي بعد شرب كوب شاي مخصص له.",
            "scene": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c",
            "clues": [
                {"name": "الدليل 1: مسحوق أبيض بالمقبض", "desc": "آثار مسحوق غريب على مقبض إبريق الشاي بالمطبخ.", "image": "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa"},
                {"name": "الدليل 2: سجل الدخول المزور", "desc": "سجل الدخول للمستودع يشير لوقت غير حقيقي.", "image": "https://images.unsplash.com/photo-1453945619913-7fec0aeb5dd5"}
            ],
            "suspects": [
                {"name": "رئيس الإتحاد (عادل)", "alibi": "1. يدعي أنه كان في اجتماع رسمي طوال الوقت.\n2. يقول إن إبريق الشاي متاح للجميع."},
                {"name": "المسؤول المالي (فيصل)", "alibi": "1. يدعي أنه دخل للمطبخ لإحضار الماء فقط.\n2. ينكر تماماً لمس إبريق الشاي."},
                {"name": "الموظف الجديد (ناصر)", "alibi": "1. يدعي أنه غادر مبكراً لظرف قاهر.\n2. يقول إنه لا يعرف مكان المطبخ جيداً."}
            ],
            "correct": "المسؤول المالي (فيصل)"
        }
    ],
    "صعب": [
        {
            "id": "H1", "title": "قضية: اللوحة الفنية المزيفة",
            "desc": "استبدلت لوحة أثرية بأخرى مزيفة بدقة متناهية دون كسر إطار الحماية.",
            "scene": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675",
            "clues": [
                {"name": "الدليل 1: خيوط قماشية غريبة", "desc": "خيوط صوفية زرقاء ملتصقة بخلفية الإطار الحديدي.", "image": "https://images.unsplash.com/photo-1582139329536-e7284fece509"},
                {"name": "الدليل 2: مفتاح الإنذار المعطل", "desc": "نظام الإنذار عطل بطريقة هندسية من داخل غرفة التحكم.", "image": "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c"}
            ],
            "suspects": [
                {"name": "خبير الآثار (د. طارق)", "alibi": "1. يرتدي قميصاً أزرق صوفياً ويقول إنه فحص اللوحة بطلب من الإدارة.\n2. يدعي أنه لا يملك صلاحية غرفة التحكم."},
                {"name": "حارس الأمن (مهند)", "alibi": "1. يقول إنه كان راقداً بغرفة الحراسة طوال الليل.\n2. ينكر أي علم بطلس أو خيوط صوفية."},
                {"name": "المرمم الفني (سعيد)", "alibi": "1. يدعي أنه رمم الإطار الأسبوع الماضي فقط.\n2. يقول إن معطفه الأزرق تركه بالمنزل."}
            ],
            "correct": "خبير الآثار (د. طارق)"
        }
    ],
    "مستحيل": [
        {
            "id": "X1", "title": "قضية: السرقة دون أثر",
            "desc": "تمت سرقة خريطة سرية من خزانة رقمية مشفرة بكلمة مرور لا يعرفها سوى شخص واحد متوفى.",
            "scene": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5",
            "clues": [
                {"name": "الدليل 1: سجل النظام المحذوف", "desc": "تم التلاعب بملفات السيرفر عبر كود برمجي دقيق ومؤقت.", "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"},
                {"name": "الدليل 2: فلاش ميموري مخفية", "desc": "وجدت خلف شاشة الكمبيوتر تحتوي على أثر بصمة مشفرة جزئياً.", "image": "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa"}
            ],
            "suspects": [
                {"name": "مبتكر النظام (زياد)", "alibi": "1. يدعي أنه صمم الحماية ولا يمكن لأحد اختراقها سوى عبر الباب الخلفي الذي أغلقه.\n2. يقول إنه كان مسافراً وقت الاختراق."},
                {"name": "مدير التقنية (سلطان)", "alibi": "1. يدعي أنه يملك صلاحيات الطوارئ فقط.\n2. يقول إنه حاول إصلاح النظام بعد اكتشاف الثغرة."},
                {"name": "المتدرب الذكي (عصام)", "alibi": "1. يدعي أنه لا يملك صلاحيات السيرفر الرئيسي.\n2. يقول إنه كان يساعد مدير التقنية طوال الليل."}
            ],
            "correct": "مبتكر النظام (زياد)"
        }
    ]
}

# دوال حفظ واسترجاع التقدم ليعمل البوت 24/7
def load_progress(server_id):
    if not os.path.exists(DATA_FILE):
        return {"level_idx": 0, "solved_count": 0, "history": []}
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        return data.get(str(server_id), {"level_idx": 0, "solved_count": 0, "history": []})

def save_progress(server_id, progress):
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    data[str(server_id)] = progress
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

current_games = {}

class AccusationSelect(discord.ui.Select):
    def __init__(self, suspects):
        options = [discord.SelectOption(label=sus["name"], emoji="🔍") for sus in suspects]
        super().__init__(placeholder="اختر القاتل بحذر...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        game_id = f"{interaction.guild_id}"
        if game_id not in current_games:
            await interaction.response.send_message("انتهت هذه الجلسة، ابدأ قضية جديدة!", ephemeral=True)
            return
        
        chosen = self.values[0]
        game = current_games[game_id]
        
        if game["solved"]:
            await interaction.response.send_message("تم حل هذه القضية مسبقاً!", ephemeral=True)
            return

        correct_suspect = game["case"]["correct"]
        
        embed = discord.Embed(title="📊 نتيجة التحقيق الرسمية", color=discord.Color.green())
        embed.add_field(name="المحقق:", value=interaction.user.mention, inline=False)
        embed.add_field(name="الاتهام الموجه:", value=chosen, inline=False)
        
        if chosen == correct_suspect:
            embed.description = "🎉 **تهانينا! استنتاجك في محلّه!** لقد كشفت الجاني الحقيقي."
            game["solved"] = True
            
            pg = load_progress(interaction.guild_id)
            pg["solved_count"] += 1
            pg["history"].append(game["case"]["id"])
            
            # الانتقال للمستوى التالي بعد انهاء قضايا المستوى الحالي
            if pg["solved_count"] >= 5:
                pg["level_idx"] += 1
                pg["solved_count"] = 0
                if pg["level_idx"] < len(LEVELS):
                    embed.add_field(name="🆙 ترقية مستوى السيرفر!", value=f"اجتزتم المستوى بنجاح! تم فتح مستوى: **{LEVELS[pg['level_idx嘛']] if pg['level_idx'] < len(LEVELS) else ''}**", inline=False)
                else:
                    embed.add_field(name="🏆 إنجاز أسطوري!", value="لقد أتممتم جميع المستويات والقضايا بنجاح تام!", inline=False)
            
            save_progress(interaction.guild_id, pg)
        else:
            embed.description = "❌ **استنتاج خاطئ!** الجاني الحقيقي ما زال طليقاً، دققوا في الأدلة والحجج مجدداً."
            embed.color = discord.Color.red()
            
        await interaction.response.send_message(embed=embed)

class AccusationView(discord.ui.View):
    def __init__(self, suspects):
        super().__init__()
        self.add_item(AccusationSelect(suspects))

class DetectiveView(discord.ui.View):
    def __init__(self, case_data, ctx):
        super().__init__()
        self.case_data = case_data
        self.ctx = ctx

    @discord.ui.button(label="📸 عرض الأدلة المصورة", style=discord.ButtonStyle.primary)
    async def show_clues(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔍 **جاري إرسال الأدلة المصورة في الشات للجميع...**", ephemeral=True)
        for clue in self.case_data["clues"]:
            embed = discord.Embed(title=clue["name"], description=clue["desc"], color=discord.Color.blue())
            embed.set_image(url=clue["image"])
            await self.ctx.send(embed=embed)

    @discord.ui.button(label="👥 أقوال المشتبه بهم", style=discord.ButtonStyle.secondary)
    async def show_suspects(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="👥 المشتبه بهم وحججهم الدفاعية", color=discord.Color.gold())
        for sus in self.case_data["suspects"]:
            embed.add_field(name=sus["name"], value=sus["alibi"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="⚖️ توجيه الاتهام", style=discord.ButtonStyle.danger)
    async def accuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AccusationView(self.case_data["suspects"])
        await interaction.response.send_message("🚨 **من هو القاتل في نظريتك؟ اختر بحذر:**", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f'البوت جاهز ويعمل بكفاءة تامة: {bot.user}')

@bot.command(name="قضية")
async def start_case(ctx):
    server_id = ctx.guild.id
    pg = load_progress(server_id)
    
    if pg["level_idx"] >= len(LEVELS):
        await ctx.send("🏆 **تهانينا الكبرى!** لقد أتممتم جميع المستويات والقضايا المتاحة في السيرفر!")
        return
        
    current_level_name = LEVELS[pg["level_idx"]]
    available_cases = [c for c in CASES.get(current_level_name, []) if c["id"] not in pg["history"]]
    
    if not available_cases:
        await ctx.send(f"⚠️ لقد أنهيتم القضايا المتاحة في مستوى **{current_level_name}** بنجاح! سيتم الانتقال للمستوى التالي قريباً.")
        return
        
    case = random.choice(available_cases)
    current_games[str(server_id)] = {"case": case, "solved": False}
    
    embed = discord.Embed(
        title=f"🚨 قضية جديدة [المستوى: {current_level_name}]",
        description=f"{case['desc']}\n\nتأملوا مسرح الجريمة بالأسفل، واضغطوا على الأزرار لفحص الأدلة المصورة واستجواب المشتبه بهم الثلاثة في الروم العام!",
        color=discord.Color.red()
    )
    embed.set_image(url=case["scene"])
    
    view = DetectiveView(case, ctx)
    await ctx.send(embed=embed, view=view)

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))  # تأكد من وضع التوكن الخاص بك في متغير البيئة DISCORD_BOT_TOKEN
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# تشغيل الخادم الوهمي في خلفية البوت
t = threading.Thread(target=run_server)
t.start()