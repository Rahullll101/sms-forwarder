# SMS Forwarder - SIM7600G-H Troubleshooting Guide

> **Project**
>
> Raspberry Pi 4 + SIM7600G-H + Gammu SMSD + PostgreSQL + Python SMS Forwarder

---

# Table of Contents

1. Check USB Detection
2. Check ttyUSB Ports
3. Check Kernel Logs
4. Check USB Driver
5. Check if Device is Busy
6. Test AT Port using Minicom
7. Cannot Type AT Command
8. AT Command Gives No Response
9. Exit Minicom
10. Update Gammu Configuration
11. Restart Gammu
12. Verify SMS Flow
13. Emergency Recovery Checklist

---

# STEP 1 - Check whether Linux detects the modem

## Why?

If Linux cannot detect the modem, nothing else will work.

## Command

```bash
lsusb
```

## Expected Output

Something similar to

```
Bus 001 Device 004: ID 1e0e:9001 SIMCom Wireless SIM7600
```

(or another SIMCOM/Qualcomm USB ID depending on the current USB mode).:contentReference[oaicite:0]{index=0}

---

## If you DON'T see it

Possible reasons

- USB cable disconnected
- Cable supports charging only
- USB port issue
- Raspberry Pi USB issue
- Modem not powered

### Try

Reconnect modem

OR

Use another USB cable

OR

Use another USB Port

OR

Reboot Pi

```bash
sudo reboot
```

---

# STEP 2 - Check Serial Ports

## Why?

Gammu communicates only through serial ports.

## Command

```bash
ls /dev/ttyUSB*
```

## Expected Output

```
/dev/ttyUSB0
/dev/ttyUSB1
/dev/ttyUSB2
/dev/ttyUSB3
```

SIM7600 usually exposes multiple serial interfaces over USB.:contentReference[oaicite:1]{index=1}

---

## If you get

```
No such file or directory
```

Go to Step 3.

---

# STEP 3 - Check Kernel Logs

## Why?

Kernel logs show whether Linux detected the modem and created serial ports.

## Command

```bash
dmesg | grep ttyUSB
```

OR

```bash
dmesg | tail -50
```

## Expected Output

```
option ... GSM modem attached to ttyUSB0

option ... GSM modem attached to ttyUSB1

option ... GSM modem attached to ttyUSB2

option ... GSM modem attached to ttyUSB3
```

---

## If nothing appears

Driver probably didn't load.

Proceed to Step 4.

---

# STEP 4 - Check USB Serial Driver

## Why?

SIM7600 uses Linux "option" USB serial driver.

## Command

```bash
lsmod | grep option
```

## Expected Output

```
option

usb_wwan
```

---

## If nothing is returned

Load driver manually

```bash
sudo modprobe option
```

Reconnect modem afterwards.

Some systems also require adding the modem VID/PID to the driver if it's running in a different USB mode.:contentReference[oaicite:2]{index=2}

---

# STEP 5 - Check if another program is using ttyUSB2

Sometimes another application opens the port.

## Command

```bash
sudo lsof /dev/ttyUSB*
```

## Expected Output

No output

OR

Only gammu-smsd

---

## If ModemManager appears

Stop it

```bash
sudo systemctl stop ModemManager
```

or

```bash
sudo killall ModemManager
```

ModemManager can interfere with manual AT debugging.:contentReference[oaicite:3]{index=3}

---

# STEP 6 - Open Minicom

Install

```bash
sudo apt update
sudo apt install minicom
```

Open

```bash
sudo minicom -D /dev/ttyUSB2
```

If ttyUSB2 doesn't work, try

```bash
sudo minicom -D /dev/ttyUSB0
```

or

```bash
sudo minicom -D /dev/ttyUSB1
```

or

```bash
sudo minicom -D /dev/ttyUSB3
```

The correct AT interface can vary depending on firmware and USB mode.:contentReference[oaicite:4]{index=4}

---

# STEP 7 - I cannot type AT command

Sometimes it looks like the keyboard isn't working.

Actually it is.

The characters are simply NOT being echoed.

This is called

```
Local Echo Disabled
```

The modem still receives your typing.

---

## Solution 1 (Recommended)

Blind type

```
ATE1
```

Press

```
ENTER
```

If successful

Expected Output

```
OK
```

After that

Type

```
AT
```

Expected

```
AT
OK
```

`ATE1` enables command echo on the modem.:contentReference[oaicite:5]{index=5}

---

## Solution 2

Enable Minicom Local Echo

Press

```
Ctrl + A
```

Release

Press

```
E
```

Now type

```
AT
```

Expected

```
AT

OK
```

This toggles Minicom's local echo.:contentReference[oaicite:6]{index=6}

---

# STEP 8 - I can type AT but no OK comes back

Possible causes

- Wrong ttyUSB port
- Port busy
- Wrong USB mode
- Modem rebooting

Try another port

```
ttyUSB0

ttyUSB1

ttyUSB2

ttyUSB3
```

The first port giving

```
AT

OK
```

is normally the AT Command Port.

---

# STEP 9 - Device Busy Error

Example

```
Cannot open /dev/ttyUSB2

Device or resource busy
```

Check

```bash
sudo lsof /dev/ttyUSB2
```

Kill process if necessary

```bash
sudo kill -9 <PID>
```

Or stop ModemManager

```bash
sudo systemctl stop ModemManager
```

Or stop Gammu temporarily

```bash
sudo systemctl stop gammu-smsd
```

After testing

Restart it

```bash
sudo systemctl start gammu-smsd
```

---

# STEP 10 - Exit Minicom

Many people close the terminal.

Don't.

Proper way

Press

```
Ctrl + A
```

Release

Press

```
X
```

Expected

```
Leave without reset ?

Yes
```

Choose

```
Yes
```

Or

Press

```
Ctrl + A
```

Then

```
Z
```

to open the Minicom help menu.:contentReference[oaicite:7]{index=7}

---

# STEP 11 - Update Gammu Configuration

Open

```bash
sudo nano /etc/gammu-smsdrc
```

OR

```bash
nano ~/.gammurc
```

Locate

```
Device =
```

Example

```
Device = /dev/ttyUSB2
```

If AT testing showed another port responds correctly, update the configuration to that port.

Save

```
Ctrl + O
```

Press

```
Enter
```

Exit

```
Ctrl + X
```

---

# STEP 12 - Restart Gammu

```bash
sudo systemctl restart gammu-smsd
```

Verify

```bash
sudo systemctl status gammu-smsd
```

Expected

```
Active: active (running)
```

---

# STEP 13 - Watch Live Logs

```bash
sudo journalctl -u gammu-smsd -f
```

Expected

```
Incoming SMS

Inserted message

Starting RunOnReceive

Process Finished Successfully
```

Press

```
Ctrl + C
```

to stop following the logs.

---

# STEP 14 - Test SMS

Send an SMS.

Verify

```
SMS received

↓

Inserted into inbox

↓

RunOnReceive

↓

Python Script

↓

HTTP 200

↓

forwarded_messages updated
```

---

# STEP 15 - Check Database

```sql
SELECT * FROM forwarded_messages
ORDER BY id DESC
LIMIT 5;
```

Expected

```
http_status = 200

retry_count = 0
```

---

# Emergency Recovery Checklist

## USB detected?

```bash
lsusb
```

✔ SIM7600 listed

---

## Serial ports available?

```bash
ls /dev/ttyUSB*
```

✔ ttyUSB0
✔ ttyUSB1
✔ ttyUSB2
✔ ttyUSB3

---

## Driver loaded?

```bash
lsmod | grep option
```

If not

```bash
sudo modprobe option
```

---

## Kernel created ports?

```bash
dmesg | grep ttyUSB
```

---

## Port busy?

```bash
sudo lsof /dev/ttyUSB*
```

---

## Stop ModemManager

```bash
sudo systemctl stop ModemManager
```

---

## Stop Gammu (for manual testing)

```bash
sudo systemctl stop gammu-smsd
```

---

## Open Minicom

```bash
sudo minicom -D /dev/ttyUSB2
```

---

## AT Test

```
AT
```

Expected

```
OK
```

---

## Cannot see typing?

Blind type

```
ATE1
```

Press Enter

OR

```
Ctrl+A

E
```

Enable Local Echo

---

## Exit Minicom

```
Ctrl+A

X
```

---

## Start Gammu Again

```bash
sudo systemctl start gammu-smsd
```

---

## Watch Logs

```bash
sudo journalctl -u gammu-smsd -f
```

---

## Final Test

Send SMS

Expected Flow

```
SMS

↓

SIM7600

↓

ttyUSB2

↓

Gammu

↓

PostgreSQL

↓

RunOnReceive

↓

Python

↓

HTTPS

↓

HTTP 200

↓

forwarded_messages
```

---

# Notes

- `Ctrl + O` → Save in Nano
- `Ctrl + X` → Exit Nano
- `Ctrl + A`, then `E` → Toggle Local Echo in Minicom
- `Ctrl + A`, then `Z` → Minicom Help
- `Ctrl + A`, then `X` → Exit Minicom
- `Ctrl + C` → Stop `journalctl -f`
- `Ctrl + L` → Clear the terminal screen
- `history` → Show previously executed commands
- `clear` → Clear the terminal

