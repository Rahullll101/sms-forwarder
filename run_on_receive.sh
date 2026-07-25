#!/bin/bash

MESSAGE_ID="$1"

cd /home/kali/Projects/sms-forwarder

source .venv/bin/activate

python3 -m scripts.run_on_receive "$MESSAGE_ID"
