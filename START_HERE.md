# 🎬 START HERE - Demo Mode Quick Start

## 🚀 Get Started in 3 Simple Steps

### Step 1: Get Your Bot Token (2 minutes)

1. **Open Telegram** on your phone or computer
2. **Search for** `@BotFather`
3. **Send** `/newbot`
4. **Choose a name**: `My Grievance Demo Bot` (or anything you like)
5. **Choose username**: `my_grievance_demo_bot` (must end with `_bot` and be unique)
6. **Copy the token** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Configure & Start (1 minute)

**Option A: Automated (Recommended)**
```bash
cd /Users/harshmodi/Desktop/Grievance-Redressal-Bot
./start_demo.sh
```
The script will ask for your token and start the bot automatically!

**Option B: Manual**
```bash
# Edit .env file
nano .env

# Replace dummy token with your real token
# Save (Ctrl+X, Y, Enter)

# Start bot
source venv/bin/activate
python main.py
```

### Step 3: Test the Demo! (2 minutes)

1. **Open your bot** in Telegram (search for the username you created)
2. **Send** `/start` 
3. **Click** "📸 Submit New Complaint"
4. **Send a photo** with text (road sign, poster, any image with visible text)
5. **Watch the magic!** ✨

---

## 📸 What You'll See - Step by Step

### 1️⃣ You Send a Photo

<img of road with sign saying "MG Road, Mumbai - Pothole">

### 2️⃣ Bot Processes (2-5 seconds)

```
⏳ Processing your image...
🔍 Extracting text
📍 Detecting location
🏷️ Classifying complaint type
```

### 3️⃣ Bot Shows Analysis

```
🔍 Image Analysis Complete

📝 Extracted Text:
Road repair needed at MG Road, Mumbai 400001. 
Large pothole causing traffic issues.

🎯 OCR Confidence: 94.5%

🏷️ Complaint Category: Roads
📊 Classification Confidence: 100.0%
⚡ Priority Level: High

📍 Detected Location: MG Road, Mumbai, Maharashtra
🎯 Location Method: OCR Text Analysis
📊 Location Confidence: high

💡 Suggestions:
• Mention when the problem started
• Add safety concerns if any
```

### 4️⃣ You Review & Submit

Click: "✅ Proceed with Complaint"

### 5️⃣ Bot Submits (Mock UMANG)

```
📋 Complaint Submission Preview

Subject: Road Infrastructure Issue - MG Road, Mumbai
Category: roads
Priority: high
Department: Ministry of Road Transport & Highways

Description:
Category: Roads
Priority Level: High
Location: MG Road, Mumbai, Maharashtra
GPS Coordinates: 19.0760, 72.8777

Complaint Details:
Road repair needed at MG Road, Mumbai 400001...
```

Click: "🚀 Submit Complaint"

### 6️⃣ Get Confirmation

```
✅ Complaint Submitted Successfully!

📋 Reference ID: MOCK-CPGRAMS-001000
🎯 Tracking Number: TRK001000
🏢 Department: Ministry of Road Transport & Highways
⏰ Expected Resolution: 30 days

💾 Save the Reference ID to track your complaint status.
```

---

## 🎯 Demo Features to Showcase

### ✅ Core Features
- **Image OCR** - Extract text from photos (7 languages)
- **Smart Classification** - AI categorizes into 10+ types
- **Location Detection** - GPS metadata + text parsing
- **Department Routing** - Assigns to correct ministry
- **Priority Assignment** - High/Medium/Low based on severity

### ✅ Additional Features
- **Manual Complaints** - Type text without images
- **Location Sharing** - Share GPS via Telegram
- **Edit Capability** - Fix OCR mistakes
- **Tracking** - Check complaint status
- **Multi-language** - English, Hindi, Bengali, Telugu, etc.

---

## 💡 Test Scenarios

### Scenario 1: Road Complaint with Clear Text
**Try**: Photo of pothole with road sign
**Expected**: 
- Extracts "MG Road" or location text
- Classifies as "Roads" 
- Detects city/state
- High priority assigned

### Scenario 2: Water Supply Issue
**Try**: Photo of dry tap with location board
**Expected**:
- Extracts location from board
- Classifies as "Water"
- High priority (essential service)

### Scenario 3: Manual Text Complaint
**Try**: Type "Garbage not collected for a week at Sector 21, Noida"
**Expected**:
- Classifies as "Sanitation"
- Extracts location: Sector 21, Noida
- Medium priority

### Scenario 4: No Text in Image
**Try**: Send plain photo without text
**Expected**:
- Bot prompts for manual location
- Offers to edit/add text
- Still allows submission

---

## 📊 Success Indicators

Your demo is working if you see:

- ✅ Bot responds immediately to /start
- ✅ Accepts photo uploads
- ✅ Shows "Processing..." message
- ✅ Extracts text from image (even partial)
- ✅ Classifies into a category
- ✅ Generates MOCK-CPGRAMS reference ID
- ✅ No error messages

---

## 🆘 Quick Troubleshooting

### Bot not responding?
```bash
# Check if bot is running
ps aux | grep main.py

# Check logs
tail -20 bot.log

# Restart
./start_demo.sh
```

### "Invalid bot token" error?
- Double-check token from @BotFather
- No spaces before/after token in .env
- Token should start with numbers, contain a colon

### OCR not extracting text?
- ✅ This is normal for images without text
- ✅ Bot will still work, just prompt for manual input
- ✅ Try images with clear, printed text

### Slow processing?
- ✅ First image takes 5-10 seconds (OCR loading)
- ✅ Subsequent images: 2-5 seconds
- ✅ Normal for high-quality OCR

---

## 🎬 Demo Script (For Presentations)

**30-Second Pitch:**
> "This bot helps citizens submit complaints to government automatically. Upload a photo, AI extracts text, detects location, classifies the issue, and submits to the right department. Works in 7 Indian languages!"

**2-Minute Demo:**
1. Open bot (10 sec)
2. Upload image (10 sec)
3. Show analysis (30 sec)
4. Submit & get reference (20 sec)
5. Show tracking (20 sec)
6. Explain other features (30 sec)

**Key Points to Emphasize:**
- ⚡ Fast processing (2-5 seconds)
- 🎯 High accuracy (90%+ OCR)
- 🤖 AI classification (no manual selection)
- 📍 Smart location detection
- 🏢 Correct department routing
- 🌐 Multi-language support

---

## 📈 What's Happening Behind the Scenes

```
Photo Upload
    ↓
Tesseract OCR (Text Extraction)
    ↓
Location Detector (GPS + Text Analysis)
    ↓
Complaint Classifier (AI Categorization)
    ↓
Department Router (Ministry Assignment)
    ↓
Mock UMANG Submission
    ↓
Reference ID Generated
    ↓
Database Storage
```

---

## 🔄 Next Steps After Demo

### Immediate:
- ✅ Test different complaint types
- ✅ Try manual complaints
- ✅ Test location sharing
- ✅ Try tracking feature

### Short-term:
- 📝 Collect feedback
- 🐛 Note any issues
- 💡 Suggest improvements
- 🎨 Customize messages

### Long-term:
- 🔐 Get real UMANG API credentials
- 🚀 Deploy to production server
- 📊 Add analytics
- 🌍 Promote to users

---

## 💬 Sample Messages for Testing

Copy-paste these into the bot to test:

**Road Issue:**
```
Large pothole at sector 15, Gurgaon, Haryana 122001 causing accidents
```

**Water Problem:**
```
No water supply since 3 days in Koramangala, Bangalore
```

**Power Cut:**
```
Frequent power cuts in Andheri West, Mumbai for past week
```

**Sanitation:**
```
Garbage not collected in Connaught Place, Delhi for 5 days
```

---

## 🎉 You're All Set!

**Bot Token?** ✅ Get from @BotFather
**Bot Running?** ✅ ./start_demo.sh
**Test Photo Ready?** ✅ Any image with text

**Now open Telegram, find your bot, and send `/start`!**

---

## 📞 Need Help?

- 📖 **Full Guide**: See DEMO_GUIDE.md
- 🔧 **Setup Issues**: See SETUP.md  
- 📝 **README**: See README.md
- 💬 **Logs**: Check bot.log

---

**Happy Testing! 🚀**

The bot is working in DEMO MODE with Mock UMANG - perfect for testing and demonstrations!


