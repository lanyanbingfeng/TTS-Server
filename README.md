# 通用本地 TTS 服务（文本转语音）

独立、离线、跨项目可用的语音合成 HTTP 服务。基于 FastAPI + sherpa-onnx VITS MeloTTS
（中英双语，女声），纯 CPU 推理，无需 GPU、无需联网。

与同级 `../stt-server` 配套：STT 收音频出文字，TTS 收文字出音频。

## 快速启动

1. 双击 `download-model.bat`（首次，下载约 160MB 模型）
2. 双击 `start.bat`
3. 看到 `Application startup complete` 即就绪

- 本机：`http://127.0.0.1:9710`
- 局域网：`http://<本机IP>:9710`

## 接口

### GET /health
```json
{"status":"ok","service":"tts-melo","port":9710,"num_speakers":1}
```

### POST /tts
- Body（JSON）：
```json
{"text": "你好，欢迎来到虚拟仿真实验室。", "sid": 0, "speed": 1.0}
```
  - `text`：要合成的文本（必填）
  - `sid`：说话人（本模型只有 1 个音色，传 0 即可）
  - `speed`：语速 0.5~2.0，默认 1.0
- 返回：**audio/wav 二进制流**（44.1kHz 单声道 PCM16），直接保存或播放即可

### curl 示例
```bash
curl -X POST http://127.0.0.1:9710/tts ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"你好世界\"}" ^
  --output out.wav
```

### Python 示例
```python
import requests
r = requests.post("http://127.0.0.1:9710/tts",
                  json={"text": "你好", "speed": 1.0})
with open("out.wav", "wb") as f:
    f.write(r.content)
```

### Unity C# 示例
```csharp
IEnumerator Speak(string text)
{
    string json = JsonUtility.ToJson(new TtsReq { text = text, speed = 1.0f });
    using var req = new UnityEngine.Networking.UnityWebRequest("http://127.0.0.1:9710/tts", "POST");
    req.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));
    req.downloadHandler = new DownloadHandlerAudioClip(req.url, AudioType.WAV);
    req.SetRequestHeader("Content-Type", "application/json");
    yield return req.SendWebRequest();

    if (req.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
    {
        var clip = ((DownloadHandlerAudioClip)req.downloadHandler).audioClip;
        GetComponent<AudioSource>().clip = clip;
        GetComponent<AudioSource>().Play();
    }
}
[System.Serializable] class TtsReq { public string text; public float speed; }
```

## 环境变量（可选）

| 变量 | 默认 | 说明 |
|---|---|---|
| TTS_PORT | 9710 | HTTP 端口 |
| TTS_THREADS | 2 | 推理线程数 |

## 全新机器部署

```bat
git clone https://github.com/lanyanbingfeng/TTS-Server.git
cd TTS-Server
download-model.bat
start.bat
```

首次 Windows 防火墙弹窗需允许 python.exe 通过。

## 目录结构

```
tts-server/
├── app.py
├── start.bat
├── download-model.bat
├── requirements.txt
├── README.md
├── .gitignore
├── .venv/            # 不进 git
└── models/           # 不进 git
    └── vits-melo-tts-zh_en/
        ├── model.onnx
        ├── tokens.txt
        ├── lexicon.txt
        ├── dict/
        └── *.fst
```
