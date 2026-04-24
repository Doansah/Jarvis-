# Jarvis-
Voice Assistant for controlling devices in my dorm room

Layer 1: Activate voice Recording

- wake word PORCUPINE
- push to talk button - hardware

records only 7 second segments

Layer 2: OpenAI Whisper 

- Whisper API parses the text
- [voice recording] -> 'let their be light' 

Layer 3: Intent Parser 

- 'let there be light' => callGoveeAPI()

Potential implementations: 
1) Call another smaller cheap ai model, to turn command into JSON 
    a) json is parsed by esp32 then callGoveeAPI() is executed 

2) Deterministic Solution (Parser)
    a) if 'light' && 'on' then callGoveeAPI()

perhaps default to deterministic solution, and fall back to AI


### Additional Considerations 

**Hardware Implementations:**
- Audio Detection 
    - distance (are multiple nodes necessary?)
- Battery Powered / Stationed 
- Communication Protocol: HTTP vs UDP vs WebSocket ...

