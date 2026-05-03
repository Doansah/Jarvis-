logging example (after first test)

01:36:33  INFO      __main__ — Jarvis started — USE_SMART_INTENT_FALLBACK=True

[Jarvis] Press Enter to start recording...
01:36:36  INFO      porcupine — Recording 7 seconds...
[Jarvis] Recording for 7s — speak now
[Jarvis] Done recording
01:36:43  INFO      transcription — Transcribing with model=gpt-4o-mini-transcribe (224044 bytes)
01:36:45  INFO      httpx — HTTP Request: POST https://api.openai.com/v1/audio/transcriptions "HTTP/1.1 200 OK"
01:36:45  INFO      transcription — Transcript: 'Turn off the rice paper lamp.'
01:36:45  INFO      __main__ — Deterministic parse: known=True action=LIGHT_OFF target=RICE_PAPER
01:36:50  INFO      lighting — Govee command success. capability=powerSwitch value=0

═════════════════════════════════════════════════════════
  Jarvis cycle complete  |  total: 14,262 ms
─────────────────────────────────────────────────────────
  Transcript : "Turn off the rice paper lamp."
  Intent     : LIGHT_OFF → RICE_PAPER  [deterministic]
─────────────────────────────────────────────────────────
  record       [ 7,254.0 ms]  ████████████████████████████████████████
  transcribe   [ 1,927.1 ms]  ███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  parse        [     0.1 ms]  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  dispatch     [ 5,081.0 ms]  ████████████████████████████░░░░░░░░░░░░
═════════════════════════════════════════════════════════

01:36:50  INFO      telemetry — Cycle summary — total=14262 ms steps={'record': '7254ms', 'transcribe': '1927ms', 'parse': '0ms', 'dispatch': '5081ms'}

[Jarvis] Press Enter to start recording...
01:36:55  INFO      porcupine — Recording 7 seconds...
[Jarvis] Recording for 7s — speak now
[Jarvis] Done recording
01:37:02  INFO      transcription — Transcribing with model=gpt-4o-mini-transcribe (224044 bytes)
01:37:03  INFO      httpx — HTTP Request: POST https://api.openai.com/v1/audio/transcriptions "HTTP/1.1 200 OK"
01:37:03  INFO      transcription — Transcript: 'Turn on the rice paper lamp.'
01:37:03  INFO      __main__ — Deterministic parse: known=True action=LIGHT_ON target=RICE_PAPER
01:37:06  INFO      lighting — Govee command success. capability=powerSwitch value=1

═════════════════════════════════════════════════════════
  Jarvis cycle complete  |  total: 11,443 ms
─────────────────────────────────────────────────────────
  Transcript : "Turn on the rice paper lamp."
  Intent     : LIGHT_ON → RICE_PAPER  [deterministic]
─────────────────────────────────────────────────────────
  record       [ 7,251.4 ms]  ████████████████████████████████████████
  transcribe   [   891.2 ms]  █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  parse        [     0.1 ms]  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  dispatch     [ 3,300.5 ms]  ██████████████████░░░░░░░░░░░░░░░░░░░░░░
═════════════════════════════════════════════════════════

01:37:06  INFO      telemetry — Cycle summary — total=11443 ms steps={'record': '7251ms', 'transcribe': '891ms', 'parse': '0ms', 'dispatch': '3301ms'}

[Jarvis] Press Enter to start recording...
01:37:13  INFO      porcupine — Recording 7 seconds...
[Jarvis] Recording for 7s — speak now
[Jarvis] Done recording
01:37:20  INFO      transcription — Transcribing with model=gpt-4o-mini-transcribe (224044 bytes)
01:37:22  INFO      httpx — HTTP Request: POST https://api.openai.com/v1/audio/transcriptions "HTTP/1.1 200 OK"
01:37:22  INFO      transcription — Transcript: 'turn on the toner.'
01:37:22  INFO      __main__ — Deterministic parse: known=False action=UNKNOWN target=ALL
01:37:22  INFO      __main__ — Deterministic miss — falling back to smart parser
01:37:22  INFO      actions — Smart fallback parsing: 'turn on the toner.'
01:37:23  INFO      httpx — HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
01:37:23  INFO      __main__ — Smart fallback result: known=False action=UNKNOWN target=ALL value=None
01:37:23  INFO      actions — Unknown intent logged only: turn on the toner.

═════════════════════════════════════════════════════════
  Jarvis cycle complete  |  total: 10,192 ms
─────────────────────────────────────────────────────────
  Transcript : "turn on the toner."
  Intent     : UNKNOWN  [smart_fallback]
─────────────────────────────────────────────────────────
  record       [ 7,243.4 ms]  ████████████████████████████████████████
  transcribe   [ 1,789.4 ms]  ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  parse        [ 1,159.0 ms]  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  dispatch     [     0.0 ms]  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
═════════════════════════════════════════════════════════

01:37:23  INFO      telemetry — Cycle summary — total=10192 ms steps={'record': '7243ms', 'transcribe': '1789ms', 'parse': '1159ms', 'dispatch': '0ms'}

[Jarvis] Press Enter to start recording...
01:37:34  INFO      porcupine — Recording 7 seconds...
[Jarvis] Recording for 7s — speak now
[Jarvis] Done recording
01:37:41  INFO      transcription — Transcribing with model=gpt-4o-mini-transcribe (224044 bytes)
01:37:42  INFO      httpx — HTTP Request: POST https://api.openai.com/v1/audio/transcriptions "HTTP/1.1 200 OK"
01:37:42  INFO      transcription — Transcript: 'Turn on the tall lamp.'
01:37:42  INFO      __main__ — Deterministic parse: known=True action=LIGHT_ON target=TALL_LAMP
01:37:42  INFO      lighting — Govee command success. capability=powerSwitch value=1

═════════════════════════════════════════════════════════
  Jarvis cycle complete  |  total: 8,078 ms
─────────────────────────────────────────────────────────
  Transcript : "Turn on the tall lamp."
  Intent     : LIGHT_ON → TALL_LAMP  [deterministic]
─────────────────────────────────────────────────────────
  record       [ 7,245.0 ms]  ████████████████████████████████████████
  transcribe   [   737.2 ms]  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  parse        [     0.1 ms]  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  dispatch     [    96.2 ms]  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
═════════════════════════════════════════════════════════

01:37:42  INFO      telemetry — Cycle summary — total=8078 ms steps={'record': '7245ms', 'transcribe': '737ms', 'parse': '0ms', 'dispatch': '96ms'}