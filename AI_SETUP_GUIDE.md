# AI-Powered Image Analysis Setup Guide

The Grievance Redressal Bot now uses AI vision models to intelligently analyze images instead of simple OCR. This provides much better understanding of grievance images.

## Features

### What AI Can Detect:
- **Visual Problems**: Potholes, garbage, broken infrastructure, water leaks, etc.
- **Severity Assessment**: Automatically rates issues as low, medium, high, or critical
- **Smart Categorization**: Accurately classifies into roads, water, electricity, sanitation, etc.
- **Context Understanding**: Understands the nature of the problem, not just text
- **Department Routing**: Suggests the appropriate government department

### Example Use Cases:
- 📸 Photo of a pothole → AI detects "damaged road surface with large pothole"
- 📸 Photo of garbage pile → AI detects "unsanitary waste accumulation"
- 📸 Photo of broken streetlight → AI detects "non-functional street lighting"
- 📸 Photo of water leak → AI detects "water pipeline leakage"

## Setup Options

### Option 1: OpenAI GPT-4 Vision (Recommended)

**Best for**: Highest accuracy and detailed analysis

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to your `.env` file:
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```

**Cost**: ~$0.01-0.03 per image (very affordable for personal use)

### Option 2: Google Gemini Vision (Free Tier Available)

**Best for**: Free usage with good accuracy

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to your `.env` file:
   ```bash
   GOOGLE_API_KEY=your-google-api-key-here
   ```

**Cost**: Free tier available with generous limits

### Option 3: Fallback Mode (No API Key)

If no API keys are configured, the bot will automatically fall back to basic OCR mode. This works but provides less intelligent analysis.

## Complete Setup Steps

1. **Install Dependencies** (already done):
   ```bash
   pip3 install -r requirements.txt
   pip3 install "python-telegram-bot[job-queue]"
   ```

2. **Create `.env` file**:
   ```bash
   cp env.example .env
   ```

3. **Configure your `.env` file**:
   ```bash
   # Required
   TELEGRAM_BOT_TOKEN=8396842677:AAE7OfuzPhZ0_UGRNKxjkNksQma_TajpTzw
   
   # Choose one (or both for redundancy)
   OPENAI_API_KEY=sk-your-key-here
   # OR
   GOOGLE_API_KEY=your-key-here
   
   # Optional
   DATABASE_URL=sqlite:///grievance_bot.db
   LOG_LEVEL=INFO
   ```

4. **Run the bot**:
   ```bash
   python3 main.py
   ```

## Testing the AI Analysis

1. Start the bot on Telegram
2. Send `/start` command
3. Click "📸 Submit New Complaint"
4. Send a photo of any infrastructure issue
5. Watch the AI analyze it!

## API Key Priority

The bot will try APIs in this order:
1. OpenAI GPT-4 Vision (if `OPENAI_API_KEY` is set)
2. Google Gemini Vision (if `GOOGLE_API_KEY` is set)
3. Fallback OCR mode (if no keys are set)

## Cost Estimation

### OpenAI GPT-4 Vision:
- ~$0.01-0.03 per image
- 100 images = ~$1-3
- Very affordable for personal/community use

### Google Gemini:
- Free tier: 60 requests per minute
- Paid tier: Very competitive pricing
- Great for high-volume usage

## Troubleshooting

### "No AI API keys configured" warning:
- Add either `OPENAI_API_KEY` or `GOOGLE_API_KEY` to your `.env` file
- The bot will still work with basic OCR

### API errors:
- Check your API key is valid
- Ensure you have credits/quota available
- Check your internet connection

### Bot not starting:
- Make sure you ran: `pip3 install "python-telegram-bot[job-queue]"`
- Check your `TELEGRAM_BOT_TOKEN` is correct
- Look at the error logs for details

## Benefits Over Simple OCR

| Feature | Simple OCR | AI Vision |
|---------|-----------|-----------|
| Text extraction | ✅ Good | ✅ Excellent |
| Visual understanding | ❌ None | ✅ Advanced |
| Context awareness | ❌ Limited | ✅ Full context |
| Problem detection | ❌ Keywords only | ✅ Visual analysis |
| Severity assessment | ❌ Manual | ✅ Automatic |
| Department routing | ⚠️ Basic | ✅ Intelligent |

## Example AI Response

**Input**: Photo of a road with large pothole

**AI Analysis**:
```
Description: "The image shows a damaged asphalt road surface with a 
large pothole approximately 2 feet in diameter. The pothole appears 
deep and poses a safety hazard to vehicles and pedestrians."

Category: roads
Severity: high
Key Issues:
- Large pothole in road surface
- Safety hazard for vehicles
- Requires immediate repair

Suggested Department: Public Works Department (PWD)
```

## Privacy & Security

- Images are sent to AI providers (OpenAI/Google) for analysis
- No images are permanently stored by the bot
- AI providers have their own privacy policies
- For sensitive deployments, consider self-hosted AI models

## Next Steps

1. Get an API key (OpenAI or Google)
2. Add it to your `.env` file
3. Run the bot: `python3 main.py`
4. Test with real grievance photos!

Enjoy intelligent grievance analysis! 🤖✨
