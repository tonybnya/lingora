"""
Script Name : gemini_live.py
Description : Gemini Live API session management for real-time audio translation.
Author      : @tonybnya
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiLive:
    """Manages a Gemini Live session for real-time audio-to-text translation.

    Uses ``system_instruction`` to tell the model to translate speech into the
    target language, ``input_audio_transcription`` for the source text, and
    ``output_audio_transcription`` for the translated text — no separate
    ``generateContent`` call needed.
    """

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gemini-3.1-flash-live-preview",
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._session: Any = None
        self._session_task: asyncio.Task[None] | None = None

    async def start(
        self,
        input_queue: asyncio.Queue[bytes | None],
        output_queue: asyncio.Queue[dict[str, Any]],
        *,
        target_language: str = "English",
    ) -> None:
        """Open a live session and start send/receive loops.

        The model is instructed via ``system_instruction`` to translate the
        user's speech to *target_language*.  Events are pushed to
        *output_queue*:

            ``{"type": "translation", "source": "...", "translation": "..."}``
            ``{"type": "error", "text": "..."}``

        Args:
            input_queue: Raw PCM 16 kHz 16-bit mono audio chunks.
                         Push ``None`` to signal end-of-stream.
            output_queue: Translation and error events.
            target_language: The language to translate speech into.
        """
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            system_instruction=types.Content(
                parts=[
                    types.Part(
                        text=(
                            f"Translate everything the user says to {target_language}. "
                            "Respond ONLY with the translated version in audio. "
                            "Do not add any commentary or extra text."
                        ),
                    ),
                ],
            ),
        )

        async def _run() -> None:
            try:
                logger.info("Connecting to Gemini Live (model=%s)…", self._model)
                async with self._client.aio.live.connect(
                    model=self._model,
                    config=config,
                ) as session:
                    logger.info("Gemini Live session opened")
                    self._session = session

                    async def _send_audio() -> None:
                        try:
                            while True:
                                chunk = await input_queue.get()
                                if chunk is None:
                                    break
                                await session.send_realtime_input(
                                    audio=types.Blob(
                                        data=chunk,
                                        mime_type="audio/pcm;rate=16000",
                                    ),
                                )
                        except asyncio.CancelledError:
                            pass
                        except Exception:
                            logger.exception("GeminiLive send loop error")

                    async def _receive_events() -> None:
                        last_input = ""
                        try:
                            while True:
                                async for response in session.receive():
                                    content = response.server_content
                                    if content is None:
                                        continue

                                    if (
                                        content.input_transcription
                                        and content.input_transcription.text
                                    ):
                                        last_input = content.input_transcription.text

                                    if (
                                        content.output_transcription
                                        and content.output_transcription.text
                                    ):
                                        await output_queue.put(
                                            {
                                                "type": "translation",
                                                "source": last_input,
                                                "translation": content.output_transcription.text,
                                            },
                                        )
                                        last_input = ""

                                    if content.turn_complete:
                                        last_input = ""
                        except asyncio.CancelledError:
                            pass
                        except Exception:
                            logger.exception("GeminiLive receive loop error")

                    send_task = asyncio.create_task(_send_audio())
                    recv_task = asyncio.create_task(_receive_events())

                    try:
                        await asyncio.gather(send_task, recv_task)
                    except Exception:
                        logger.exception("GeminiLive session error")
            except Exception as exc:
                logger.error("Gemini Live connect failed: %s", exc)
                await output_queue.put({"type": "error", "text": str(exc)})

        self._session_task = asyncio.create_task(_run())

    def stop(self) -> None:
        """Close the session and cancel background tasks."""
        if self._session_task and not self._session_task.done():
            self._session_task.cancel()
