#!/usr/bin/env python3
"""
Reset bot connection and clear any webhooks
"""
import asyncio
import logging
from telegram import Bot
from config import Config

async def reset_bot():
    """Reset bot connection and clear webhooks"""
    try:
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        print("🔄 Resetting bot connection...")
        
        # Delete webhook if any
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted and pending updates cleared")
        
        # Get bot info to verify connection
        me = await bot.get_me()
        print(f"✅ Bot connection verified: @{me.username}")
        
        print("🎉 Bot reset complete! You can now start the bot.")
        
    except Exception as e:
        print(f"❌ Error resetting bot: {e}")

if __name__ == "__main__":
    asyncio.run(reset_bot())
