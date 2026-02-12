import asyncio
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    llm,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
import livekit.plugins.google

# ────────────────────────────────────────────────
# Logging & Config
# ────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rehmat-agent")

# Load environment variables (local dev only)
if Path(".env.local").exists():
    load_dotenv(".env.local")
elif Path(".env").exists():
    load_dotenv(".env")

KNOWLEDGE_FILE = Path("src/rehmateshereen_kb_structured.json")

server = AgentServer()


# ────────────────────────────────────────────────
# Knowledge Base
# ────────────────────────────────────────────────

class KnowledgeBase:
    def __init__(self, path: Path):
        self.data = self._load(path)

    def _load(self, path: Path) -> dict:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Knowledge base loaded successfully")
            return data
        except Exception as e:
            logger.error("Failed to load knowledge base", exc_info=True)
            return {}

    def format_for_prompt(self) -> str:
        lines = []
        info = self.data.get("business_info", {})

        lines.append(f"NAME: {info.get('business_name', '')}")
        lines.append(f"ABOUT: {info.get('business_description', '')}")
        lines.append(f"HOURS: {info.get('operating_hours', {}).get('daily', '')}")

        addresses = info.get("official_addresses", [])
        if addresses:
            lines.append("LOCATIONS:")
            for a in addresses:
                lines.append(f"- {a.get('address_type', 'Main')}: {a.get('location', '')}")

        products = self.data.get("products", [])
        if products:
            lines.append("\nMENU & PRICES:")
            current_cat = ""
            for p in products:
                cat = p.get("category", "Other")
                if cat != current_cat:
                    lines.append(f"\n{cat.upper()}")
                    current_cat = cat
                desc = f" ({p.get('description', '')})" if p.get("description") else ""
                
                sizes_data = p.get("sizes", [])
                if sizes_data:
                    # If sizes are dicts, extract name or size field
                    if isinstance(sizes_data[0], dict):
                        size_list = [s.get("size", "") for s in sizes_data]
                    else:
                        size_list = sizes_data
                    sizes = f" Sizes: {', '.join(size_list)}"
                else:
                    sizes = ""

                lines.append(f"• {p.get('name')} — {p.get('price')}{desc}{sizes}")

        return "\n".join(lines)

    # Renamed for clarity as it's used by the LLM
    def format_for_llm(self) -> str:
        return self.format_for_prompt()


kb = KnowledgeBase(KNOWLEDGE_FILE)


# --------------------------------------------------
# Tool Functions
# --------------------------------------------------
import re

def sanitize_urdu(text: str) -> str:
    """
    Sanitizes Urdu text to enforce gender neutrality using Regex.
    Removes forbidden endings from verbs.
    """
    # Replace any customer-directed GI/GA endings
    # pattern: (verb_stem)(forbidden_suffix) -> keep verb_stem
    # Using the user's specific logic:
    text = re.sub(r"(چاہیں|کریں|لیں|پسند کریں)(گی|گے)", r"\1", text)
    
    # Backup lookup for full phrases
    replacements = {
        "کریں گے": "کر دوں", "کریں گی": "کر دوں",
        "بتائیں گے": "بتا دوں", "بتائیں گی": "بتا دوں",
        "دیکھنا چاہوں گی": "دیکھنا", "دیکھنا چاہیں گے": "دیکھنا",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

class RehmatTools:
    """
    Tools for Rehmat-e-Shereen with minimal state tracking.
    """
    def __init__(self):
        self.confirmation_done = False
        self.final_order_details = ""

    @llm.function_tool(description="Call this ONLY after the customer explicitly confirms the full order summary (items, address, bill).")
    async def confirm_order(self, details: str):
        details = sanitize_urdu(details)
        self.confirmation_done = True
        self.final_order_details = details
        logger.info(f"✅ Order Confirmed: {details}")
        return "Order confirmed. Say goodbye and wait for customer to end call."

# --------------------------------------------------
# Assistant
# --------------------------------------------------
class RehmatAssistant(Agent):
    """
    Rehmat-e-Shereen dedicated female voice assistant.
    """
    
    def __init__(self, fnc_ctx: RehmatTools) -> None:
        knowledge_text = kb.format_for_llm()
        
        super().__init__(
            instructions=f"""
CLARIFICATION — NO AMBIGUITY (GENDER RULES)
• Customer-directed verbs must NEVER use "گے / گی"
• Self-referential verbs must ALWAYS be feminine ("کرتی ہوں", "بتاتی ہوں")
• Customer-facing language is GENDER-NEUTRAL.

PRICING RULES (STRICT)
• Prices must be spoken exactly as written (e.g. "200 Rupay" not "takreeban 200").
• Always say "روپے" (Rupees)
• Never say "تقریباً" (Approx), "آس پاس", "اندازاً"

🛑 BANNED PHRASES (Real Protection):
- "Chahin ge" / "Chahin gay" / "Chahiye ho ga" -> ❌ STRICTLY BANNED
- "Dekhna chahin ge" -> ❌ BANNED. Say **"Kya pesh kiya jaye?"**
- "Pasand karen ge  " -> ❌ BANNED. Say **"Kya add kar doon?"**
- "Karen ge" / "Karen ge" -> ❌ BANNED. Say **"Kar doon"**

✅ صرف نیوٹرل اردو استعمال کریں:

Allowed Neutral Forms:
"ap kia khana psnd kare"
"ap kia order karna psnd kare ge "
"کیا شامل کر دوں؟"
"کیا لکھوں؟"
"کیا آرڈر میں ڈالوں؟"
"کیا پیش کیا جائے؟"
"کیا آپ کو یہ پسند ہے؟"
"کیا مزید کچھ شامل کر دوں؟"

🚫 Strictly BANNED customer verbs:
کریں گے / کریں گی
چاہیں گے / چاہیں گی
پسند کریں گے / کریں گی
دیکھنا چاہیں گے
لینا چاہیں گے
ہوگا / ہوگی (when referring to customer action)

✅ GREETING LINE (Exact Phrase):
"السلام علیکم! رحمتِ شیریں میں خوش آمدید۔ آپ کا آرڈر کیا لکھوں؟"

4. **MANDATORY:** You must ONLY address the customer as **"Aap" (آپ)**.
5. **SELF-IDENTIFICATION:** You are female (use "Main karti hoon", "Main batati hoon").

---

آپ کا نام "رحمتِ شیریں اسسٹنٹ" ہے۔
آپ رحمتِ شیریں کی ایک انتہائی تجربہ کار، بااخلاق، خوش گفتار اور مکمل طور پر تربیت یافتہ خاتون (Female) کال سینٹر نمائندہ ہیں۔

آپ سینئر ہیومن ایجنٹ کی طرح کام کرتی ہیں:
- آپ کو کسی سے پوچھنے کی ضرورت نہیں، آپ خود ماہر ہیں۔
- آپ کا مقصد صرف آرڈر لینا اور کسٹمر کو مطمئن کرنا ہے۔

🚀 رفتار اور گفتگو (REAL HUMAN SPEED)
کسٹمر کی بات ختم ہوتے ہی فوراً جواب دیں — خاموشی ناقابل قبول ہے۔
ہر جواب مختصر، واضح اور قدرتی ہو۔
غیر ضروری وضاحت، فلسفہ یا لیکچر نہ دیں۔
لہجہ:
دوستانہ, پُرسکون, پروفیشنل, پراعتماد

⚠️ hesitation، filler words یا robotic انداز منع ہے۔

🎭 صنف اور خطاب (ABSOLUTE RULE — ZERO TOLERANCE)
آپ ہمیشہ مؤنث صیغے استعمال کریں:
"میں بتا دیتی ہوں"
"میں کنفرم کر رہی ہوں"
کسٹمر کی صنف کبھی فرض نہ کریں۔
درج ذیل الفاظ ہمیشہ کے لیے ممنوع ہیں:
بھائی، بہن، صاحب، سر، میڈم، باجی، جناب
صرف اور صرف "آپ" استعمال کریں — ہر جملے میں۔
⚠️ یہ اصول کسی صورت نہیں ٹوٹے گا۔
🗣️ تلفظ، لہجہ اور زبان (VOICE-SAFE)
Nimco → "Nim-co" (نِمکو)
Garlic Bread → "Garlic Bread" (انگریزی)
Patties → "Patties" (پیٹیز)
❌ غلط تلفظ ناقابلِ قبول ہے۔
زبان:
صاف، شائستہ دیسی اردو
نہ بہت بھاری
نہ غیر ضروری انگریزی
🛑 سخت دائرہ کار (HARD SCOPE LOCK)
آپ صرف رحمتِ شیریں پر بات کریں گی۔
درج ذیل موضوعات مکمل طور پر بلاک ہیں:
سیاست
مذہب
ذاتی مشورے
عام گپ شپ
کسی اور بیکری یا برانڈ کا ذکر
اگر کسٹمر آف-ٹاپک جائے:
"جی میں آپ کی رحمتِ شیریں کے آرڈر میں مدد کر سکتی ہوں، آپ کیا دیکھنا چاہیں گے؟"
📚 نالج بیس (MASTER-LEVEL CONTROL)
آپ کے پاس رحمتِ شیریں کی مکمل اور اپ-ٹو-ڈیٹ معلومات موجود ہیں۔
تمام معلومات یہاں سے استعمال کریں:

{knowledge_text}
❗ اہم اصول:
آپ کبھی یہ الفاظ استعمال نہیں کریں گی:
"معلوم نہیں"
"کنفرم کر کے بتاؤں گی"
"مینیجر سے پوچھوں گی"
اگر کوئی چیز واضح نہ ہو تو اعتماد کے ساتھ گفتگو کو قریبی متبادل یا آرڈر فلو کی طرف موڑ دیں:
مثال:
"جی اس سائز میں یہی آپشن دستیاب ہے، اگر آپ چاہیں تو میں اس کی جگہ یہ والا آپشن آرڈر میں شامل کر سکتی ہوں۔"
آپ ہر صورتحال کو خود handle کرتی ہیں۔
🛒 آرڈر پلیسنگ اور کنفرمیشن (NON-NEGOTIABLE)
کال ختم ہونے سے پہلے لازمی:
آرڈر کی تمام اشیاء
وزن / مقدا
ڈیلیوری ایڈریس
مکمل بل
مثال:

"تو آپ کا آرڈر یہ ہے:
ایک پاؤنڈ رس ملائی،
آدھا کلو نمکو،
ڈیلیوری [ایڈریس] پر،
اور ٹوٹل بل [رقم] بنتا ہے —
کیا میں آرڈر کنفرم کر دوں؟"
کنفرمیشن کے بغیر کال ختم نہ کریں۔

🎯 شخصیت اور رویہ (SENIOR AGENT BEHAVIOR)
صبر وال
پراعتماد
مسئلہ حل کرنے والی
کبھی defensive نہیں
ہر سوال کو اہم سمجھتی ہیں
کسٹمر کو سنا ہوا محسوس کراتی ہیں
آپ رحمتِ شیریں کی نمائندگی کرتی ہیں — لہٰذا ہر لفظ میں وقار ہو۔
👋 الوداع (FIXED — FINAL LINE)
ہمیشہ یہی آخری جملہ بولیں:
"رحمتِ شیریں پر تشریف لانے کا شکریہ، اللہ حافظ، خوش رہیں!"
اس کے بعد خاموشی سے کال ختم ہونے کا انتظار کریں۔

IMPORTANT: When reciting order summary, speak without interruptions. After summary, allow interruptions for confirmation.
""",
            tools=llm.find_function_tools(fnc_ctx),
            # Extreme speed optimization
            min_endpointing_delay=0.1, # Minimized delay for instant start
            max_endpointing_delay=0.5,
            allow_interruptions=True,
        )


# ────────────────────────────────────────────────
# Prewarm (VAD model)
# ────────────────────────────────────────────────

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


# ────────────────────────────────────────────────
# Session Handler
# ────────────────────────────────────────────────

@server.rtc_session()
async def rehmat_session(ctx: JobContext):
    logger.info(f" Starting Rehmat-e-Shereen session in room: {ctx.room.name}")

    # Initialize tools and assistant
    fnc_ctx = RehmatTools()
    assistant = RehmatAssistant(fnc_ctx=fnc_ctx)

    # Gemini Realtime Model
    realtime_model = livekit.plugins.google.realtime.RealtimeModel(
        voice="Aoede",
        temperature=0.45,
        instructions=assistant.instructions,
    )

    try:
        session = AgentSession(
            llm=realtime_model,
            # We rely purely on Gemini Realtime for audio to avoid credential issues with external TTS
        )

        await session.start(
            agent=assistant,
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=lambda p: (
                        noise_cancellation.BVCTelephony()
                        if p.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                        else noise_cancellation.BVC()
                    )
                )
            ),
        )
    except Exception as e:
        logger.error(f"❌ Failed to start session: {e}", exc_info=True)
        return

    await ctx.connect()
    logger.info("✅ Room connected")

    # Farewell detection
    farewell_phrases = ["اللہ حافظ", "خدا حافظ", "بس شکریہ", "ٹھیک ہے شکریہ", "allah hafiz", "khuda hafiz"]
    
    @session.on("user_speech_committed")
    def on_user_speech(msg):
        text = msg.alternatives[0].text.lower() if msg.alternatives else ""
        if any(phrase in text for phrase in farewell_phrases):
            logger.info("👋 Farewell detected, ending call after response")
            asyncio.create_task(end_call_gracefully())
    
    async def end_call_gracefully():
        await asyncio.sleep(2.0)  # Let assistant finish goodbye
        await ctx.disconnect()
        logger.info("🔚 Call ended")

    # Immediate warm welcome message
    async def send_greeting():
        await asyncio.sleep(1.0)
        logger.info("🤖 Triggering auto-greeting...")
        # Create a dummy user message to force the agent to speak the greeting
        msg = llm.ChatMessage(role="system", content="System: Time to start. Say the exact greeting: 'السلام علیکم! رحمتِ شیریں میں خوش آمدید۔ میں آپ کی کس طرح مدد کر سکتی ہوں؟'")
        await session.conversation.item.create(msg)
        # Force generation
        await session.response.create()

    asyncio.create_task(send_greeting())


# ────────────────────────────────────────────────
# Run the agent
# ────────────────────────────────────────────────

if __name__ == "__main__":
    cli.run_app(server)