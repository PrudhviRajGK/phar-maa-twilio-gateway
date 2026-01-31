# PHAR-MAA Twilio Gateway

## Purpose

This is a **minimal webhook forwarder** deployed on Render. It contains:
- ✅ Twilio webhook endpoints
- ✅ HTTP forwarding to local backend
- ❌ NO AI logic
- ❌ NO database access
- ❌ NO embeddings
- ❌ NO sensitive keys

## Architecture

```
[ User (WhatsApp/SMS) ]
         ↓
    [ Twilio ]
         ↓
[ Render: Gateway Service ] ← You are here
         ↓ (HTTP forward)
[ Local: PHAR-MAA Backend ]
         ↓
[ Agents / AI / DB / Embeddings ]
```

## Why Split Deployment?

**Security & Control:**
- Minimizes public attack surface
- Keeps sensitive AI models and keys local
- Mirrors how regulated systems separate ingestion from processing
- No risk of exposing OpenAI keys or database credentials

**Flexibility:**
- Can update AI logic without redeploying gateway
- Can run backend on powerful local hardware
- Can switch between local/cloud backend easily

## Deployment

### 1. Deploy to Render

```bash
# From twilio-gateway directory
git init
git add .
git commit -m "Initial gateway"
```

Connect to Render and deploy using `render.yaml`.

### 2. Expose Local Backend

Use ngrok or Cloudflare Tunnel:

```bash
# Option 1: ngrok
ngrok http 8000

# Option 2: Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8000
```

### 3. Configure Environment Variable

In Render dashboard, set:
- `LOCAL_BACKEND_URL` = your ngrok/Cloudflare URL (e.g., `https://abc123.ngrok.io`)

### 4. Configure Twilio Webhooks

In Twilio console, set webhook URLs to:
- WhatsApp: `https://your-render-app.onrender.com/twilio/whatsapp`
- SMS: `https://your-render-app.onrender.com/twilio/sms`

## Testing

```bash
# Health check
curl https://your-render-app.onrender.com/health

# Test webhook (simulate Twilio)
curl -X POST https://your-render-app.onrender.com/twilio/whatsapp \
  -d "From=whatsapp:+1234567890" \
  -d "Body=Hello"
```

## What This Service Does NOT Do

- ❌ Process messages with AI
- ❌ Store data in database
- ❌ Run embeddings
- ❌ Make OpenAI API calls
- ❌ Execute business logic
- ❌ Store state

**It only forwards messages. That's it.**

## Security Notes

- No sensitive environment variables needed
- Only `LOCAL_BACKEND_URL` is required
- If compromised, attacker gains nothing (no keys, no data)
- All sensitive operations happen in local backend

## Monitoring

Check Render logs for:
- Incoming webhook requests
- Forwarding status
- Backend response codes

## Production Considerations

For production deployment:
1. Replace ngrok with proper VPN or private network
2. Add authentication between gateway and backend
3. Implement rate limiting
4. Add request validation
5. Use HTTPS for backend communication
6. Consider deploying backend to cloud with proper security
