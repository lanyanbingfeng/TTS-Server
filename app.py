# 通用本地 TTS 服务（文本 -> 语音），后端 sherpa-onnx VITS MeloTTS 中英
#   GET  /health      健康检查
#   POST /tts         JSON {"text":"...","sid":0,"speed":1.0} -> 返回 WAV
import io
import os

import numpy as np
import soundfile as sf
import sherpa_onnx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "vits-melo-tts-zh_en")

print(f"[TTS] loading MeloTTS from {MODEL_DIR} ...")
tts = sherpa_onnx.OfflineTts(
    sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=os.path.join(MODEL_DIR, "model.onnx"),
                tokens=os.path.join(MODEL_DIR, "tokens.txt"),
                lexicon=os.path.join(MODEL_DIR, "lexicon.txt"),
                dict_dir=os.path.join(MODEL_DIR, "dict"),
            ),
            num_threads=2,
            debug=False,
        ),
        rule_fsts="",
    )
)
print(f"[TTS] model loaded, num_speakers={tts.num_speakers}")

TTS_PORT = int(os.environ.get("TTS_PORT", "9710"))

app = FastAPI(title="TTS Server (MeloTTS)", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class TtsRequest(BaseModel):
    text: str
    sid: int = 0
    speed: float = 1.0


@app.get("/health")
def health():
    return {"status": "ok", "service": "tts-melo", "port": TTS_PORT, "num_speakers": tts.num_speakers}


@app.post("/tts")
def synthesize(req: TtsRequest):
    text = (req.text or "").strip()
    if not text:
        return JSONResponse({"error": "empty text"}, status_code=400)

    audio = tts.generate(text, sid=req.sid, speed=req.speed)
    buf = io.BytesIO()
    sf.write(buf, np.array(audio.samples, dtype=np.float32),
             audio.sample_rate, format="WAV", subtype="PCM_16")
    return Response(content=buf.getvalue(), media_type="audio/wav",
                    headers={"Content-Disposition": 'inline; filename="tts.wav"'})


if __name__ == "__main__":
    import uvicorn
    print(f"[TTS] http on http://0.0.0.0:{TTS_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=TTS_PORT, log_level="info")
