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
    """Voice assistant configured for Arabic input."""

    def __init__(self) -> None:
        super().__init__(
            instructions="""أنت مساعد صوتي ذكي ومفيد. تتحدث العربية بطلاقة.
            أجب على أسئلة المستخدم بشكل موجز ومباشر.
            لا تستخدم الرموز التعبيرية أو التنسيق المعقد.

            You are a helpful voice AI assistant fluent in Arabic.
            Respond to user questions concisely and directly.
            Keep responses short for voice - under 2-3 sentences.
            Do not use emojis or complex formatting.""",
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
            model="llama-3.1-8b-instant",
        ),
        tts=elevenlabs.TTS(
            model="eleven_turbo_v2_5",
            voice_id="pNInz6obpgDQGcFmaJgB",
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
        instructions="Greet the user in Arabic and English briefly. Keep it under 2 sentences."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
