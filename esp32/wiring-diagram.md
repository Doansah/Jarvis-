1. Wire it up
ESP32 pin	Connect to
GPIO 21	OLED SDA
GPIO 22	OLED SCL
3.3V	OLED VCC
GND	OLED GND
GPIO 12	Button 1 (Cycle) → other leg to GND
GPIO 14	Button 2 (Power) → other leg to GND
2. Get the OLED driver
In the MicroPython REPL, run:


import mip
mip.install("ssd1306")
Or manually download ssd1306.py and upload it.

3. Fill in your credentials
Open esp32/config.py and replace the placeholder strings with:

Your WiFi SSID/password
Your Govee API key (same one in the root config.py)
The SKU and device ID for each of your three lights (copy from the root config.py)
4. Upload and run
Using Thonny (easiest): open each file and use File → Save to MicroPython device. Upload in order: ssd1306.py → config.py → boot.py → main.py. Then hit reset — the OLED should show the preset screen.