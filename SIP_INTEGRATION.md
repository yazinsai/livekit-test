# LiveKit SIP Integration Guide

This document describes how to connect phone calls to your LiveKit voice agent.

## Architecture

```
Phone Call → Twilio → LiveKit Cloud SIP → LiveKit Room → agent.py
                      (5fkanfa0cli.sip.livekit.cloud)
```

## Current Configuration (Working)

### Phone Number
**Call: +1 234-332-2724** to reach the AI agent

### LiveKit Inbound SIP Trunk
- **Trunk ID:** `ST_okMDbxEYUMEN`
- **Name:** `autobiographer-inbound`
- **Phone Number:** `+12343322724`
- **Authentication:** None
- **Allowed IPs:** `0.0.0.0/0` (all IPs - Twilio uses internal proxies)

### LiveKit Dispatch Rule
- **Rule ID:** `SDR_PkB85iDMXcnX`
- **Name:** `autobiographer-dispatch`
- **Room Pattern:** `call-_<caller>_<random>` (each caller gets their own room)

### Twilio SIP Trunk
- **Trunk SID:** `TKf171584b190ac6e104631f731e261751`
- **Origination URI:** `sip:5fkanfa0cli.sip.livekit.cloud;transport=tcp`
- **Phone Number:** `+12343322724` (assigned to trunk)

### LiveKit SIP Endpoint
```
sip:5fkanfa0cli.sip.livekit.cloud
```

> **Important:** The SIP endpoint is different from the WebSocket URL. Find your SIP URI in the LiveKit Cloud dashboard under Telephony → SIP trunks.

---

## Setup Guide

### Step 1: Find Your LiveKit SIP Endpoint

1. Go to [LiveKit Cloud Dashboard](https://cloud.livekit.io)
2. Navigate to **Telephony** → **SIP trunks**
3. Copy the **SIP URI** shown at the top (e.g., `sip:5fkanfa0cli.sip.livekit.cloud`)

### Step 2: Create LiveKit Inbound Trunk

Via CLI:
```bash
lk sip inbound create /tmp/trunk.json
```

With `/tmp/trunk.json`:
```json
{
  "name": "my-inbound-trunk",
  "numbers": ["+1XXXXXXXXXX"],
  "allowedAddresses": ["0.0.0.0/0"]
}
```

> **Note:** Use `0.0.0.0/0` for Twilio since calls arrive via internal proxies with unpredictable IPs. Security is provided by the phone number restriction and project-specific SIP endpoint.

Or via Dashboard: **Telephony** → **Create new** → **Trunk** → **Inbound**

### Step 3: Create Dispatch Rule

Via CLI:
```bash
lk sip dispatch create /tmp/dispatch.json
```

With `/tmp/dispatch.json`:
```json
{
  "name": "my-dispatch-rule",
  "rule": {
    "dispatchRuleIndividual": {
      "roomPrefix": "call-"
    }
  }
}
```

### Step 4: Configure Twilio

1. **Create a SIP Trunk** in [Twilio Console](https://console.twilio.com/us1/develop/voice/manage/sip-trunking)

2. **Add Origination URI:**
   ```
   sip:5fkanfa0cli.sip.livekit.cloud;transport=tcp
   ```

3. **Assign Phone Number** to the trunk

> **Note:** Twilio Elastic SIP Trunking does NOT support digest authentication. Use IP allowlisting on the LiveKit trunk instead.

---

## Running the Agent

```bash
cd ~/projects/autobiographer.ai/livekit-poc
source .venv/bin/activate
python agent.py dev
```

---

## Testing

### Test with Real Phone
1. **Call +1 234-332-2724** from your phone
2. The call routes: Phone → Twilio → LiveKit SIP → Room → Agent
3. Room created: `call-_+1XXXXXXXXXX_<random>`
4. Agent (Sana) greets you in Arabic

### Verify with CLI
```bash
# List active rooms
lk room list

# List SIP trunks
lk sip inbound list

# List dispatch rules
lk sip dispatch list
```

---

## Troubleshooting

### 404 No trunk found
- **Cause:** Wrong SIP endpoint in Twilio origination URL
- **Fix:** Use the SIP URI from LiveKit dashboard (under Telephony), NOT the WebSocket URL

### 407 Unauthorized
- **Cause:** LiveKit trunk has auth credentials but Twilio can't send them
- **Fix:** Remove auth credentials and set `allowedAddresses` to `["0.0.0.0/0"]`

### Call rings but no agent
- **Cause:** Agent not running or not registered
- **Fix:** Start agent with `python agent.py dev` and check logs

### Audio quality issues
- Enable Krisp noise cancellation on the trunk
- Check RTP ports if using intermediate server

---

## Quick Reference

| Resource | Value |
|----------|-------|
| **Phone Number** | **+1 234-332-2724** |
| LiveKit SIP Endpoint | `sip:5fkanfa0cli.sip.livekit.cloud` |
| LiveKit Trunk ID | `ST_okMDbxEYUMEN` |
| Dispatch Rule ID | `SDR_PkB85iDMXcnX` |
| Twilio Trunk SID | `TKf171584b190ac6e104631f731e261751` |
| Room Pattern | `call-_<caller>_<random>` |

---

## CLI Commands

```bash
# List SIP trunks
lk sip inbound list

# Update trunk
lk sip inbound update --id ST_xxx --numbers "+1234567890"

# List dispatch rules
lk sip dispatch list

# List active rooms
lk room list

# Delete trunk
lk sip inbound delete ST_xxx

# Delete dispatch rule
lk sip dispatch delete SDR_xxx
```
