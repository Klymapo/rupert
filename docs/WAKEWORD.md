# Wake word: Rupert

Rupert uses **openWakeWord** as an optional, local wake-word detector. Runtime inference stays on the machine and requires no API key.

## Why a custom model?

openWakeWord ships several pretrained phrases (including `hey_jarvis`), but not `Rupert`. The production target is therefore a custom ONNX model stored locally at:

```text
.runtime/models/wakeword/rupert.onnx
```

This path is ignored by Git.

## Install the runtime

```powershell
.\scripts\setup-wakeword.ps1
```

For a quick microphone/inference smoke test before the Rupert model exists:

```powershell
.\scripts\setup-wakeword.ps1 -DownloadSmokeModel
```

That optional step downloads the upstream `hey_jarvis_v0.1` model into `.runtime/models/wakeword/`.

## Train the word "Rupert"

The openWakeWord project provides an automated custom-model notebook. It can be used in free Google Colab for one-time training:

https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing

Training may happen in Colab, but **Rupert does not depend on Colab at runtime**. After training:

1. export/download the ONNX wake-word model;
2. name it `rupert.onnx`;
3. place it at `.runtime/models/wakeword/rupert.onnx`;
4. run `rupert wake-doctor`;
5. run `rupert wake-monitor` and say "Rupert" repeatedly at different distances/volumes.

## Configuration

`.env` supports:

```dotenv
WAKEWORD_MODEL=.runtime/models/wakeword/rupert.onnx
WAKEWORD_THRESHOLD=0.5
WAKEWORD_FRAMEWORK=onnx
WAKEWORD_CHUNK_SIZE=1280
```

Start with `0.5`. Increase the threshold if Rupert wakes accidentally; reduce it if it misses clear activations. Do not tune this from a single sample — test normal speech, TV/music noise and different distances.

## Safety boundary

v0.5 detects one activation and stops. It deliberately does **not** execute an action immediately after the wake word. Continuous wake -> command capture -> execution will only be enabled once false-positive behavior is measured on the real microphone.

This keeps the always-listening component local and prevents an imperfect wake-word model from becoming an automatic command trigger.
