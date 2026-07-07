                    SMS Received
                         │
                         ▼
                 Gammu SMSD
                         │
                         ▼
                    inbox (Gammu)
                         │
                         ▼
              RunOnReceive(ID)
                         │
                         ▼
              run_on_receive.py
                         │
                         ▼
                  processor.py
                         │
                         ▼
                 HTTPS Endpoint
                ┌────────┴────────┐
                │                 │
             Success           Failure
                │                 │
                ▼                 ▼
     Insert into forwarded_messages
                                  │
         Delete from inbox        │
                                  ▼
                           Insert/Update
                             retry_queue
                                  │
                                  ▼
                           retry_worker.py
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
                  Success                  Max Retry
                     │                         │
                     ▼                         ▼
      Insert into forwarded_messages     Status = FAILED
                     │
                     ▼
             Delete from inbox
                     │
                     ▼
         Delete from retry_queue