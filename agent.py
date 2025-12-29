"""
LiveKit Voice Agent Test - Arabic STT with Groq LLM and ElevenLabs TTS

This script tests voice AI latency with:
- Google Cloud STT (Chirp 3) for Arabic speech recognition
- Groq LLM (Llama 3.1 8B) for fast inference
- ElevenLabs TTS (v2.5 Turbo) for speech synthesis
"""

import time
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, AgentServer, room_io
from livekit.plugins import google, groq, elevenlabs, silero, noise_cancellation

load_dotenv(".env.local")


class ArabicAssistant(Agent):
    """AI biographer for capturing elderly life stories in Arabic."""

    def __init__(self) -> None:
        super().__init__(
            instructions="""أنت كاتب سيرة ذاتية متخصص ولطيف. مهمتك هي التحدث مع كبار السن لمساعدتهم على مشاركة قصص حياتهم.

شخصيتك:
- صبور جداً ومتفهم
- إيجابي ومشجع دائماً
- فضولي ومهتم بصدق بكل تفاصيل حياتهم
- دافئ وحنون في أسلوبك

أسلوب المحادثة:
- اسأل أسئلة مفتوحة تشجع على الحكي والتذكر
- أظهر اهتماماً حقيقياً بكل قصة يشاركونها
- شجعهم بعبارات مثل "ما شاء الله" و"يا سلام" و"حدثني أكثر"
- إذا توقفوا، ساعدهم بلطف بأسئلة توجيهية
- احتفِ بذكرياتهم وإنجازاتهم
- لا تستعجلهم أبداً - خذ وقتك معهم

مواضيع للاستكشاف:
- الطفولة والعائلة
- الدراسة والعمل
- الزواج والأبناء
- اللحظات الفارقة في حياتهم
- الدروس والحكم التي تعلموها
- الأحلام والأمنيات

تذكر: كل قصة ثمينة، وكل ذكرى تستحق التوثيق. أنت هنا لتحفظ تراثهم وحكاياتهم للأجيال القادمة.""",
        )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent."""

    session_start = time.perf_counter()

    session = AgentSession(
        stt=google.STT(
            model="chirp_3",
            languages=["ar-XA"],
            location="us",
            enable_word_time_offsets=False,
        ),
        llm=groq.LLM(
            model="llama-3.3-70b-versatile",
        ),
        tts=elevenlabs.TTS(
            model="eleven_turbo_v2_5",
            voice_id="mRdG9GYEjJmIzqbYTidv",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=ArabicAssistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    setup_time = time.perf_counter() - session_start
    print(f"[LATENCY] Session setup: {setup_time * 1000:.0f}ms")

    await session.generate_reply(
        instructions="رحّب بالمستخدم بدفء وحنان. عرّف نفسك ككاتب سيرة ذاتية وأخبره أنك متشوق لسماع قصة حياته. اسأله عن اسمه وكيف يفضل أن تناديه."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
