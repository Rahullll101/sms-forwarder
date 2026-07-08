# SMS Forwarder

A production-ready SMS forwarding gateway built using **Python**, **PostgreSQL**, and **Gammu SMSD**.

The application receives inbound SMS messages from a physical SIM card connected through a **SIM7600G-H LTE modem**, stores them in PostgreSQL using Gammu SMSD, and reliably forwards them to an HTTPS endpoint with automatic retries, logging, and message archiving.

---

# Features

- Receive inbound SMS using a physical SIM card
- PostgreSQL as the message store
- Automatic SMS forwarding to HTTPS endpoint
- Configurable retry mechanism
- Permanent archive of successfully forwarded messages
- Retry queue with exponential delay
- Health check utility
- Structured logging
- Production-ready project structure
- Raspberry Pi compatible
- SIM7600G-H LTE modem compatible

---

# System Architecture

```
                   SMS Sender
                  (OTP Service)
                         │
                         ▼
                  Mobile Network
                         │
                         ▼
                   Physical SIM
                         │
                         ▼
                  SIM7600G-H Modem
                         │
                  USB Serial Interface
                         │
                         ▼
                   Raspberry Pi 4
                         │
                         ▼
                    Gammu SMSD
                         │
                         ▼
                PostgreSQL Inbox Table
                         │
                RunOnReceive Trigger
                         │
                         ▼
                 run_on_receive.py
                         │
                         ▼
                   SMS Processor
                         │
                HTTP POST Request
                 ┌────────┴────────┐
                 │                 │
            Success             Failure
                 │                 │
                 ▼                 ▼
     forwarded_messages      retry_queue
                 │                 │
                 ▼                 ▼
         Delete Inbox Row    Retry Worker
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                    Success              Max Retry
                         │                   │
                         ▼                   ▼
              forwarded_messages        Status = FAILED
```

---

# Folder Structure

```
sms-forwarder/
│
├── app/
│   ├── config.py
│   ├── database.py
│   ├── endpoint.py
│   ├── logger.py
│   ├── models.py
│   ├── processor.py
│   ├── repository.py
│   └── retry.py
│
├── scripts/
│   ├── run_on_receive.py
│   ├── retry_worker.py
│   └── health_check.py
│
├── sql/
│   └── schema.sql
│
├── docs/
│
├── systemd/
│
├── logs/
│
├── README.md
├── requirements.txt
└── .env
```

---

# Database Design

## inbox

Managed entirely by **Gammu SMSD**.

Stores every incoming SMS received by the modem.

Important columns:

- ID
- SenderNumber
- TextDecoded
- ReceivingDateTime
- Processed

---

## retry_queue

Managed by the application.

Stores only failed messages waiting for retry.

Columns:

- id
- inbox_id
- retry_count
- status
- next_retry_time
- last_error
- created_at

Status values:

- RETRY
- FAILED

---

## forwarded_messages

Permanent archive of successfully forwarded SMS.

Columns:

- id
- inbox_id
- sender
- message
- received_at
- forwarded_at
- http_status
- retry_count
- created_at

---

# SMS Processing Workflow

1. SMS arrives on the physical SIM.
2. SIM7600G-H receives the SMS.
3. Gammu SMSD inserts the message into the PostgreSQL `inbox` table.
4. Gammu executes the `RunOnReceive` script with the Inbox ID.
5. `run_on_receive.py` invokes the SMS processor.
6. The processor reads the SMS from the database.
7. The SMS is forwarded to the configured HTTPS endpoint.
8. If forwarding succeeds:
   - Archive the SMS in `forwarded_messages`
   - Remove the SMS from `inbox`
9. If forwarding fails:
   - Schedule a retry in `retry_queue`
10. `retry_worker.py` continuously processes pending retries.
11. If the maximum retry count is exceeded:
    - Update retry status to `FAILED`
    - Keep the SMS available for manual inspection.

---

# Retry Strategy

| Attempt | Delay |
|---------|-------|
| Retry 1 | 15 seconds |
| Retry 2 | 30 seconds |
| Retry 3 | 60 seconds |
| Retry 4 | Failed     |

The retry worker continuously polls the retry queue and retries messages whose scheduled retry time has been reached.

---

# Logging

Three independent log files are maintained.

## application.log

Contains normal application activity.

Examples:

- SMS received
- SMS processing started
- SMS forwarded successfully
- Retry worker started

---

## error.log

Contains unexpected failures.

Examples:

- HTTP errors
- Database errors
- Exceptions
- Stack traces

---

## retry.log

Contains retry scheduling information.

Examples:

- Retry scheduled
- Retry worker started
- Retry attempt
- Retry success

---

# Health Check

The application includes a health check utility.

Currently validates:

- PostgreSQL connectivity
- HTTPS endpoint availability
- Logs directory
- Available disk space

Future hardware checks include:

- Gammu SMSD status
- SIM7600 modem detection
- SIM registration
- Signal strength

---

# Configuration

Environment variables are stored in `.env`.

Typical configuration includes:

```
DATABASE_HOST=
DATABASE_PORT=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=

ENDPOINT_URL=

API_KEY=

MAX_RETRY=

LOG_LEVEL=
```

---

# Installation

Clone the repository.

```bash
git clone <repository-url>

cd sms-forwarder
```

Create virtual environment.

```bash
python -m venv venv
```

Activate environment.

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Initialize PostgreSQL schema.

```bash
psql -U postgres -d gammu -f sql/schema.sql
```

---

# Running

## Process one SMS

```bash
python -m scripts.run_on_receive <INBOX_ID>
```

Example

```bash
python -m scripts.run_on_receive 25
```

---

## Start Retry Worker

```bash
python -m scripts.retry_worker
```

---

## Run Health Check

```bash
python -m scripts.health_check
```

---

# Hardware Deployment

Target hardware:

- Raspberry Pi 4 model B
- SIM7600G-H LTE Modem
- Physical Nano SIM

Software:

- Ubuntu Linux
- PostgreSQL
- Python
- Gammu SMSD

Once deployed, Gammu SMSD automatically inserts new SMS messages into PostgreSQL and invokes `RunOnReceive` for processing.

---

# Failure Handling

If the endpoint is unavailable:

1. The SMS remains in the inbox.
2. Retry information is stored in `retry_queue`.
3. The retry worker retries the message according to the configured retry schedule.
4. After the maximum retry limit is reached, the retry status is updated to `FAILED`.

This ensures that no SMS is lost due to temporary endpoint failures.

---


# Tech Stack

- Python 3
- PostgreSQL
- Gammu SMSD
- Requests
- Psycopg
- Raspberry Pi
- SIM7600G-H LTE Modem
- Ubuntu Linux

---

# License

This project is intended for reliable inbound SMS forwarding using a physical SIM card and is designed for production deployment on Raspberry Pi-based IoT hardware.