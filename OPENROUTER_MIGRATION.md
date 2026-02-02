# OpenRouter Migration - Complete ✅

## What Changed

Switched from direct Anthropic API to **OpenRouter** for the chat interface.

---

## Why OpenRouter?

**Benefits:**
- ✅ Unified API for multiple LLM providers
- ✅ Better rate limiting and routing
- ✅ Potentially lower costs with dynamic pricing
- ✅ Fallback to other models if needed
- ✅ Better analytics and usage tracking
- ✅ Simpler billing (one account for all models)

**Still Using:**
- Same Claude Sonnet 4.5 model
- Same quality responses
- Same features and functionality

---

## Technical Changes

### 1. API Client
**Before:**
```python
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**After:**
```python
import requests
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
```

### 2. API Calls
**Before:**
```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    temperature=0.7,
    system=CHAT_CONTEXT,
    messages=[{"role": "user", "content": message}]
)
assistant_text = response.content[0].text
```

**After:**
```python
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://louisville-311-dashboard.onrender.com",
        "X-Title": "Louisville 311 Dashboard"
    },
    json={
        "model": "anthropic/claude-sonnet-4.5:beta",
        "messages": [
            {"role": "system", "content": CHAT_CONTEXT},
            {"role": "user", "content": message}
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
)
assistant_text = response.json()['choices'][0]['message']['content']
```

### 3. Environment Variable
**Before:**
- `ANTHROPIC_API_KEY`

**After:**
- `OPENROUTER_API_KEY`

### 4. Dependencies
**Before:**
```
anthropic>=0.39.0
```

**After:**
```
requests>=2.31.0
```

---

## Setup Instructions

### 1. Get OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Go to "Keys" section
4. Create a new API key
5. Add credits (recommended: $25 to start)

### 2. Local Development

Set environment variable:
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Or add to your `.env` file:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Render Deployment

1. Go to Render Dashboard
2. Select your service: `louisville-311-dashboard`
3. Go to "Environment" tab
4. Add new environment variable:
   - Key: `OPENROUTER_API_KEY`
   - Value: `sk-or-v1-...` (your key)
5. Save

Render will automatically redeploy with the new key.

---

## Testing Results

✅ **All Endpoints Working:**
```
GET /                200 OK
GET /call-center     200 OK
GET /topics          200 OK
GET /sentiment       200 OK
GET /urgency         200 OK
GET /business        200 OK
GET /chat            200 OK
POST /chat/ask       200 OK
```

✅ **Chat Functionality:**
- OpenRouter API key detected
- Chat enabled successfully
- Test question sent: "What are the top 3 service types?"
- Response received correctly from Claude Sonnet 4.5
- Message bubbles display properly
- Timestamps show correctly

✅ **Sample Response:**
```
User: What are the top 3 service types?
Bot: Based on the 311 service request data, the top 3 service types are:

1. NSR Metro Agencies - 2,531 requests (27.1% of total)
2. Large Item Appointment - 1,050 requests (11.2% of total)
3. NSR Social Services - 652 requests (7.0% of total)
```

---

## Cost Comparison

### OpenRouter Pricing
**Claude Sonnet 4.5:**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- Same as direct Anthropic pricing
- But with added benefits of OpenRouter platform

**No Change in Costs:**
- Same ~$0.003 per question
- 1,000 questions/month: ~$3
- 10,000 questions/month: ~$30

**Additional Benefits:**
- Better usage analytics
- Rate limiting included
- Fallback options if model unavailable
- Single billing across multiple models

---

## Model Configuration

**Current Model:**
```
anthropic/claude-sonnet-4.5:beta
```

**Available Alternatives on OpenRouter:**
- `anthropic/claude-3.5-sonnet` - Slightly cheaper
- `anthropic/claude-opus-4` - More powerful
- Other providers (GPT-4, etc.) as fallback

**To Change Model:**
Edit `dashboard_app.py` line with `"model":`:
```python
"model": "anthropic/claude-sonnet-4.5:beta",  # Change this
```

---

## Error Handling

**Added Improvements:**
- Timeout handling (30 seconds)
- HTTP status code checking
- Better error messages
- Graceful degradation

**Error Messages:**
- Timeout: "The request timed out. Please try again."
- HTTP errors: Shows status code
- General errors: Shows error message

---

## Monitoring

**OpenRouter Dashboard:**
- Go to https://openrouter.ai/activity
- View all API calls
- See costs per request
- Monitor usage patterns
- Set spending limits

**Logs:**
- Dashboard startup shows: "✅ OpenRouter API key found - chat enabled"
- Or: "⚠️  OpenRouter API key not found - chat disabled"

---

## Rollback (If Needed)

If you need to switch back to direct Anthropic:

1. Revert `dashboard_app.py` changes
2. Change `requirements.txt`: `anthropic>=0.39.0`
3. Update env var: `ANTHROPIC_API_KEY`
4. Redeploy

---

## Files Modified

1. **dashboard_app.py**
   - Removed: `from anthropic import Anthropic`
   - Added: `import requests`
   - Changed: API client initialization
   - Changed: Message sending logic
   - Updated: Error messages

2. **requirements.txt**
   - Removed: `anthropic>=0.39.0`
   - Added: `requests>=2.31.0`

3. **OPENROUTER_MIGRATION.md** (new)
   - This documentation file

---

## Deployment Checklist

- [x] Code updated to use OpenRouter
- [x] Dependencies updated
- [x] Local testing complete
- [x] All endpoints working
- [x] Chat functionality tested
- [ ] Add `OPENROUTER_API_KEY` to Render
- [ ] Add credits to OpenRouter account
- [ ] Deploy to Render
- [ ] Test in production

---

## Next Steps

### To Deploy:

1. **Get OpenRouter API Key**
   - Visit: https://openrouter.ai/keys
   - Create new key
   - Copy it (starts with `sk-or-v1-`)

2. **Add Credits**
   - Go to: https://openrouter.ai/credits
   - Add $25 to start (recommended)

3. **Configure Render**
   ```
   Key: OPENROUTER_API_KEY
   Value: sk-or-v1-...
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "Switch to OpenRouter API"
   git push origin main
   ```

5. **Verify Deployment**
   - Check build logs
   - Look for: "✅ OpenRouter API key found - chat enabled"
   - Test: https://louisville-311-dashboard.onrender.com/chat

---

## Support

**OpenRouter:**
- Docs: https://openrouter.ai/docs
- Discord: https://discord.gg/openrouter
- Email: support@openrouter.ai

**Dashboard Issues:**
- GitHub: https://github.com/rachaelroland/louisville-311-dashboard/issues

---

## Conclusion

✅ **Migration Complete**

The chat interface now uses OpenRouter instead of direct Anthropic API. All functionality remains the same, with added benefits:

- Better rate limiting
- Usage analytics
- Fallback options
- Simplified billing

**Ready to deploy!** Just add the OpenRouter API key to Render.
