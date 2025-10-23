# 🎬 Demo Mode - Image to Text Complaint

This guide helps you run the bot in **demo mode** without real UMANG API credentials.

## 🚀 Quick Demo Setup

### Step 1: Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name: `My Grievance Demo Bot` (or any name)
4. Choose a username: `my_grievance_demo_bot` (must be unique, end with _bot)
5. Copy the token you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Bot Token

```bash
# Edit the .env file
nano .env

# Replace this line:
# TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-DUMMY_TOKEN

# With your real token:
# TELEGRAM_BOT_TOKEN=YOUR_ACTUAL_TOKEN_HERE
```

Save and exit (Ctrl+X, then Y, then Enter in nano)

### Step 3: Start the Bot

```bash
cd /Users/harshmodi/Desktop/Grievance-Redressal-Bot
source venv/bin/activate
python main.py
```

You should see:
```
Configuration validated successfully
Startup cleanup completed
Starting Grievance Redressal Bot...
Bot is ready to receive messages!
```

### Step 4: Test Image-to-Text Complaint

1. **Open your bot in Telegram** (search for the username you created)
2. **Send** `/start` - You'll see the welcome menu
3. **Click** "📸 Submit New Complaint"
4. **Take or send a photo** of:
   - A damaged road with text/signboard
   - A complaint poster
   - Any issue with visible text
   - Example: Road sign saying "MG Road, Mumbai" with potholes

5. **Watch the magic happen** ✨:
   - Bot extracts text using OCR
   - Detects location from text/GPS
   - Classifies complaint type
   - Shows analysis results

6. **Review and submit** - Bot will use **Mock UMANG** to simulate submission

---

## 📸 Demo Workflow Example

### What You'll See:

**1. Send Image →**
```
⏳ Processing your image...
🔍 Extracting text
📍 Detecting location
🏷️ Classifying complaint type
```

**2. Get Analysis →**
```
🔍 Image Analysis Complete

📝 Extracted Text:
Road repair needed. Large potholes at MG Road...

🎯 OCR Confidence: 94.5%

🏷️ Complaint Category: Roads
📊 Classification Confidence: 100.0%
⚡ Priority Level: High

📍 Detected Location: MG Road, Mumbai
🎯 Location Method: ocr
📊 Location Confidence: medium

💡 Suggestions for improvement:
• Consider mentioning if this is an urgent matter
```

**3. Submit →**
```
✅ Complaint Submitted Successfully!

📋 Reference ID: MOCK-CPGRAMS-001000
🎯 Tracking Number: TRK001000
🏢 Department: Ministry of Road Transport & Highways
⏰ Expected Resolution: 30 days

💾 Save the Reference ID to track your complaint
```

---

## 🎨 Demo Features

### ✅ What Works in Demo Mode

- ✅ **Image Upload** - Any photo format
- ✅ **OCR Text Extraction** - 7 Indian languages
- ✅ **Location Detection** - GPS metadata + text parsing
- ✅ **Smart Classification** - 10+ complaint categories
- ✅ **Manual Location Input** - GPS share or text address
- ✅ **Complaint Editing** - Edit extracted text
- ✅ **Mock Submission** - Simulates government portal
- ✅ **Status Tracking** - Track mock reference IDs
- ✅ **Manual Complaints** - Type complaints without images

### 📊 Supported Complaint Types

1. 🛣️ **Roads** - Potholes, traffic, highways
2. 💧 **Water** - Supply issues, leaks, drainage
3. ⚡ **Electricity** - Power cuts, equipment issues
4. 🗑️ **Sanitation** - Garbage, waste, cleanliness
5. 🏥 **Healthcare** - Hospital, doctor, medical issues
6. 🎓 **Education** - School, college problems
7. 🚌 **Transport** - Bus, train, station issues
8. 🏢 **Public Services** - Government offices, documents
9. 🏠 **Housing** - Building, society issues
10. 🍽️ **Food Safety** - Restaurant hygiene, quality

---

## 🧪 Test Scenarios

### Scenario 1: Road Complaint with Image
**Test Image**: Photo of pothole with road sign
**Expected**: 
- Extract text from sign
- Classify as "roads"
- Detect location if text contains address
- Assign high priority

### Scenario 2: Manual Text Complaint
**Test Input**: "Water supply not working in Sector 21, Noida, UP 201301 since 3 days"
**Expected**:
- Classify as "water"
- Extract location: Sector 21, Noida, UP
- Extract pincode: 201301
- Assign high priority

### Scenario 3: Image with No Text
**Test Image**: Plain photo without text
**Expected**:
- OCR warning about no text
- Prompt for manual location
- Continue with classification
- Allow manual complaint entry

### Scenario 4: GPS Location Sharing
**Test**: Share Telegram location
**Expected**:
- Accept GPS coordinates
- Reverse geocode to address
- Use high confidence location
- Proceed with submission

---

## 🎯 Demo Commands

```
/start  - Start the bot and show menu
/help   - Show help and instructions  
/menu   - Return to main menu
/cancel - Cancel current operation
```

---

## 💡 Tips for Best Demo Results

### For Image-Based Complaints:
- ✅ Use well-lit photos
- ✅ Include text/signboards in frame
- ✅ Enable location services on phone (for GPS data)
- ✅ Clear, focused images work best

### For Manual Complaints:
- ✅ Include location details (area, pincode)
- ✅ Mention the issue type clearly
- ✅ Add timeline (when problem started)
- ✅ Describe severity/impact

---

## 🔍 What Happens Behind the Scenes

### Image Processing Pipeline:
1. **Download** - Image saved temporarily
2. **OCR** - Tesseract extracts text (multi-language)
3. **GPS Extract** - Check EXIF metadata for coordinates
4. **Text Parse** - Search for addresses, pincodes, locations
5. **Classify** - AI-based categorization (roads, water, etc.)
6. **Geocode** - Convert addresses to coordinates
7. **Format** - Prepare for submission
8. **Submit** - Mock UMANG client simulates submission
9. **Cleanup** - Temp files deleted automatically

### Classification Logic:
- **Keyword Matching** - Primary, secondary, Hindi keywords
- **Phrase Analysis** - Context-aware patterns
- **Confidence Scoring** - Based on matches
- **Department Routing** - Appropriate ministry/department
- **Priority Assignment** - High/Medium/Low based on category

---

## 🎬 Sample Demo Script

**For Showing to Others:**

1. **Introduction** (30 seconds)
   - "This bot helps citizens submit grievances to government"
   - "It uses AI to classify complaints automatically"
   - "Works in 7 Indian languages"

2. **Demo Image Upload** (2 minutes)
   - Send `/start`
   - Click "Submit New Complaint"
   - Upload sample pothole image
   - Watch automatic processing
   - Explain OCR, location, classification

3. **Show Results** (1 minute)
   - Point out extracted text
   - Show detected location
   - Explain classification confidence
   - Highlight department routing

4. **Submit & Track** (1 minute)
   - Submit complaint
   - Note reference ID
   - Show tracking feature
   - Explain expected resolution time

5. **Other Features** (1 minute)
   - Show manual complaint entry
   - Demonstrate location sharing
   - Show edit capability
   - Explain help menu

**Total Demo Time**: ~5 minutes

---

## 📱 Sample Test Images

Create or use these types of images for testing:

### 1. Road Issue
```
Text: "Pothole at MG Road, Mumbai 400001"
Image: Damaged road with sign
Expected: Roads category, Mumbai location, High priority
```

### 2. Water Problem
```
Text: "No water supply, Sector 15, Gurgaon"
Image: Dry tap with location sign
Expected: Water category, Gurgaon location, High priority
```

### 3. Garbage Issue
```
Text: "Garbage not collected, Bangalore"
Image: Waste pile with landmark
Expected: Sanitation category, Bangalore location, Medium priority
```

---

## 🆘 Troubleshooting Demo Issues

### Bot not responding?
```bash
# Check bot is running
ps aux | grep main.py

# Check logs
tail -f bot.log

# Restart bot
python main.py
```

### OCR not extracting text?
- Use clearer images
- Ensure text is readable
- Try manual complaint entry instead

### Location not detected?
- Include location text in image
- Use manual location input
- Share GPS location via Telegram

---

## 🎉 Demo Success Criteria

Your demo is successful if:

- ✅ Bot responds to messages
- ✅ Accepts and processes images
- ✅ Extracts text from images
- ✅ Classifies complaints correctly
- ✅ Detects locations (when available)
- ✅ Generates mock reference IDs
- ✅ Tracks complaints
- ✅ Handles errors gracefully

---

## 📊 Demo Metrics to Track

During demo, note:
- Response time (should be 2-5 seconds)
- OCR accuracy (typically 80-95%)
- Classification accuracy (check if correct category)
- Location detection rate
- User experience (smooth flow?)

---

## 🔄 After Demo

### To Stop the Bot:
```bash
Press Ctrl+C in the terminal
```

### To Restart:
```bash
python main.py
```

### To Update:
```bash
git pull
pip install -r requirements.txt
python main.py
```

---

## 🚀 Moving to Production

When ready for real UMANG API:

1. Get API credentials from API Setu
2. Update `.env`:
   ```
   UMANG_CLIENT_ID=your_real_id
   UMANG_CLIENT_SECRET=your_real_secret
   ```
3. Restart bot - it will auto-switch to real API
4. Test with real submissions
5. Monitor bot.log for any issues

---

## 💬 Feedback Collection

During demo, ask users:
- ✅ Was the OCR accurate?
- ✅ Was the classification correct?
- ✅ Was the location detected properly?
- ✅ Was the flow intuitive?
- ✅ Any features missing?
- ✅ Any errors encountered?

---

**Demo mode is fully functional and ready!** 🎊

Just get your bot token from @BotFather and start the bot!


