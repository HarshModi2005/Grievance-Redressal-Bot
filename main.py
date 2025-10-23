"""
Main Telegram Bot application for Grievance Redressal System
"""
import os
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
from io import BytesIO

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode

# Import our modules
from config import Config, validate_config
from database import db_manager
from ocr_processor import ocr_processor
from location_detector import location_detector
from complaint_classifier import complaint_classifier
from umang_client import umang_client

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Conversation states
(
    MAIN_MENU,
    WAITING_FOR_IMAGE,
    PROCESSING_IMAGE, 
    LOCATION_INPUT,
    LOCATION_CONFIRMATION,
    COMPLAINT_REVIEW,
    MANUAL_COMPLAINT_INPUT,
    COMPLAINT_SUBMISSION,
    TRACKING_INPUT
) = range(9)

class GrievanceBotHandler:
    """Main bot handler class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Create temp directory for images
        self.temp_dir = 'temp_images'
        os.makedirs(self.temp_dir, exist_ok=True)
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /start command"""
        try:
            user = update.effective_user
            
            # Create/update user record
            db_manager.create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            welcome_message = (
                "🙏 *Welcome to Grievance Redressal Bot*\n\n"
                "I help you submit public grievances to appropriate government departments through official channels.\n\n"
                "📝 *What I can do:*\n"
                "• Process images to extract complaint details\n"
                "• Detect location automatically\n"
                "• Classify and route complaints appropriately\n"
                "• Submit to CPGRAMS/UMANG system\n"
                "• Track complaint status\n\n"
                "⚖️ *Important Notice:*\n"
                "This is an unofficial citizen assistance tool. All complaints are submitted to official government portals. "
                "Your data is handled securely per IT Act 2000.\n\n"
                "Choose an option below to get started:"
            )
            
            keyboard = [
                [KeyboardButton("📸 Submit New Complaint")],
                [KeyboardButton("📊 Track Existing Complaint")],
                [KeyboardButton("📝 Manual Complaint Entry")],
                [KeyboardButton("❓ Help & Instructions")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
            
            await update.message.reply_text(
                welcome_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return MAIN_MENU
            
        except Exception as e:
            self.logger.error(f"Error in start command: {e}")
            await update.message.reply_text(
                "❌ Sorry, something went wrong. Please try again."
            )
            return MAIN_MENU
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /help command"""
        help_text = (
            "🔧 *How to Use Grievance Redressal Bot*\n\n"
            
            "📸 *Image-based Complaint:*\n"
            "1. Click 'Submit New Complaint'\n"
            "2. Send a photo of the issue\n"
            "3. I'll extract text and detect location\n"
            "4. Review and confirm details\n"
            "5. Submit to government portal\n\n"
            
            "📝 *Manual Complaint Entry:*\n"
            "• Use if you don't have a photo\n"
            "• Type your complaint details\n"
            "• Provide location manually\n\n"
            
            "📊 *Track Complaints:*\n"
            "• Use reference ID to check status\n"
            "• Get updates on progress\n\n"
            
            "🏷️ *Supported Complaint Types:*\n"
            "• Roads & Transport\n"
            "• Water & Drainage\n"
            "• Electricity & Power\n"
            "• Sanitation & Waste\n"
            "• Healthcare Services\n"
            "• Education & Schools\n"
            "• Public Services\n"
            "• Housing & Buildings\n"
            "• Food Safety\n\n"
            
            "📞 *Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/cancel - Cancel current operation\n"
            "/menu - Return to main menu\n\n"
            
            "🔒 *Privacy:*\n"
            "Your data is encrypted and handled securely. "
            "We comply with IT Act 2000 and government data protection guidelines."
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        return MAIN_MENU
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /cancel command"""
        user_id = update.effective_user.id
        
        # Clear any pending session data
        db_manager.clear_session(user_id)
        
        await update.message.reply_text(
            "❌ Operation cancelled. Returning to main menu.",
            reply_markup=self.get_main_menu_keyboard()
        )
        
        return MAIN_MENU
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /menu command"""
        await update.message.reply_text(
            "📋 Main Menu - Choose an option:",
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    def get_main_menu_keyboard(self):
        """Get main menu keyboard"""
        keyboard = [
            [KeyboardButton("📸 Submit New Complaint")],
            [KeyboardButton("📊 Track Existing Complaint")],
            [KeyboardButton("📝 Manual Complaint Entry")],
            [KeyboardButton("❓ Help & Instructions")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle main menu button selections"""
        try:
            text = update.message.text
            
            if text == "📸 Submit New Complaint":
                return await self.start_image_complaint(update, context)
            elif text == "📊 Track Existing Complaint":
                return await self.start_tracking(update, context)
            elif text == "📝 Manual Complaint Entry":
                return await self.start_manual_complaint(update, context)
            elif text == "❓ Help & Instructions":
                return await self.help_command(update, context)
            else:
                await update.message.reply_text(
                    "Please select one of the menu options.",
                    reply_markup=self.get_main_menu_keyboard()
                )
                return MAIN_MENU
                
        except Exception as e:
            self.logger.error(f"Error handling main menu: {e}")
            await update.message.reply_text("❌ Error processing request. Please try again.")
            return MAIN_MENU
    
    async def start_image_complaint(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start image-based complaint process"""
        try:
            user_id = update.effective_user.id
            
            # Clear any existing session
            db_manager.clear_session(user_id)
            
            instructions = (
                "📸 *Image-Based Complaint Submission*\n\n"
                "Please send a clear photo of the issue you want to report.\n\n"
                "📋 *Tips for better results:*\n"
                "• Take photo in good lighting\n"
                "• Include any text or signboards\n"
                "• Show the problem clearly\n"
                "• Enable location services for GPS data\n\n"
                "I'll analyze the image to extract text and detect location automatically."
            )
            
            keyboard = [[KeyboardButton("❌ Cancel")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                instructions,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return WAITING_FOR_IMAGE
            
        except Exception as e:
            self.logger.error(f"Error starting image complaint: {e}")
            await update.message.reply_text("❌ Error starting complaint process.")
            return MAIN_MENU
    
    async def handle_image_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle image upload and processing"""
        try:
            user_id = update.effective_user.id
            
            if not update.message.photo:
                await update.message.reply_text(
                    "📸 Please send a photo, not other file types."
                )
                return WAITING_FOR_IMAGE
            
            # Show processing message
            processing_msg = await update.message.reply_text(
                "⏳ Processing your image...\n"
                "🔍 Extracting text\n"
                "📍 Detecting location\n"
                "🏷️ Classifying complaint type"
            )
            
            # Get the largest photo
            photo = update.message.photo[-1]
            
            # Download image
            photo_file = await photo.get_file()
            image_path = os.path.join(self.temp_dir, f"{user_id}_{datetime.now().timestamp()}.jpg")
            await photo_file.download_to_drive(image_path)
            
            # Process image with OCR
            ocr_result = ocr_processor.extract_text_from_image(image_path)
            
            # Extract GPS coordinates
            gps_coords = ocr_processor.extract_gps_from_image(image_path)
            
            # Detect location from text
            text_location = location_detector.detect_location_from_text(ocr_result.get('cleaned_text', ''))
            
            # Classify complaint
            classification = complaint_classifier.classify_complaint(
                ocr_result.get('cleaned_text', ''),
                {'location': text_location, 'gps': gps_coords}
            )
            
            # Combine location methods
            location_info = location_detector.combine_location_methods(
                gps_coords, text_location
            )
            
            # Store session data
            session_data = {
                'image_path': image_path,
                'ocr_result': ocr_result,
                'gps_coords': gps_coords,
                'text_location': text_location,
                'classification': classification,
                'location_info': location_info,
                'step': 'image_processed'
            }
            
            db_manager.create_or_update_session(
                user_id, 
                json.dumps(session_data, default=str), 
                'image_processed'
            )
            
            # Delete processing message
            await processing_msg.delete()
            
            # Show results
            return await self.show_image_analysis_results(update, context, session_data)
            
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            await update.message.reply_text(
                "❌ Error processing image. Please try again with a different photo."
            )
            return WAITING_FOR_IMAGE
    
    async def show_image_analysis_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, session_data: Dict) -> int:
        """Show image analysis results to user"""
        try:
            ocr_result = session_data['ocr_result']
            classification = session_data['classification']
            location_info = session_data['location_info']
            
            # Build result message
            result_message = "🔍 *Image Analysis Complete*\n\n"
            
            # OCR Results
            if ocr_result.get('extraction_success'):
                result_message += f"📝 *Extracted Text:*\n{ocr_result['cleaned_text'][:200]}{'...' if len(ocr_result['cleaned_text']) > 200 else ''}\n\n"
                result_message += f"🎯 *OCR Confidence:* {ocr_result['confidence']:.1f}%\n\n"
            else:
                result_message += "📝 *Text Extraction:* No readable text found\n\n"
            
            # Classification Results
            category = classification['primary_category'].replace('_', ' ').title()
            result_message += f"🏷️ *Complaint Category:* {category}\n"
            result_message += f"📊 *Classification Confidence:* {classification['confidence_score']:.1f}%\n"
            result_message += f"⚡ *Priority Level:* {classification['priority_level'].title()}\n\n"
            
            # Location Results
            if location_info.get('final_address'):
                result_message += f"📍 *Detected Location:* {location_info['final_address']}\n"
                result_message += f"🎯 *Location Method:* {location_info['method_used']}\n"
                result_message += f"📊 *Location Confidence:* {location_info['confidence']}\n\n"
            else:
                result_message += "📍 *Location:* Could not detect automatically\n\n"
            
            # Suggested improvements
            suggestions = complaint_classifier.suggest_improvements(
                ocr_result.get('cleaned_text', ''),
                classification
            )
            
            if suggestions:
                result_message += "💡 *Suggestions for improvement:*\n"
                for suggestion in suggestions:
                    result_message += f"• {suggestion}\n"
                result_message += "\n"
            
            # Create action buttons
            buttons = []
            
            if location_info.get('final_address'):
                buttons.append([InlineKeyboardButton("✅ Proceed with Complaint", callback_data="proceed_complaint")])
            else:
                buttons.append([InlineKeyboardButton("📍 Add Location Manually", callback_data="add_location")])
            
            buttons.extend([
                [InlineKeyboardButton("✏️ Edit Complaint Details", callback_data="edit_complaint")],
                [InlineKeyboardButton("🔄 Try Another Image", callback_data="retry_image")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_complaint")]
            ])
            
            reply_markup = InlineKeyboardMarkup(buttons)
            
            await update.message.reply_text(
                result_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return COMPLAINT_REVIEW
            
        except Exception as e:
            self.logger.error(f"Error showing analysis results: {e}")
            await update.message.reply_text("❌ Error displaying results.")
            return MAIN_MENU
    
    async def handle_complaint_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle complaint action buttons"""
        try:
            query = update.callback_query
            await query.answer()
            
            action = query.data
            user_id = update.effective_user.id
            
            if action == "proceed_complaint":
                return await self.proceed_with_complaint(update, context)
            elif action == "add_location":
                return await self.request_location_input(update, context)
            elif action == "edit_complaint":
                return await self.edit_complaint_details(update, context)
            elif action == "retry_image":
                return await self.start_image_complaint(update, context)
            elif action == "cancel_complaint":
                return await self.cancel_command(update, context)
            else:
                await query.edit_message_text("❌ Unknown action. Please try again.")
                return MAIN_MENU
                
        except Exception as e:
            self.logger.error(f"Error handling complaint actions: {e}")
            return MAIN_MENU
    
    async def proceed_with_complaint(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Proceed with complaint submission"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Get session data
            session = db_manager.get_session_data(user_id)
            if not session:
                await query.edit_message_text("❌ Session expired. Please start again.")
                return MAIN_MENU
            
            session_data = json.loads(session.session_data)
            
            # Prepare complaint for submission
            formatted_complaint = complaint_classifier.format_for_submission(
                session_data['ocr_result'].get('cleaned_text', ''),
                session_data['classification'],
                session_data['location_info']
            )
            
            # Add user information
            user = update.effective_user
            formatted_complaint.update({
                'citizen_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'citizen_mobile': None,  # We don't have phone number
                'citizen_email': None,   # We don't have email
                'attachments': [session_data['image_path']]
            })
            
            # Add coordinates if available
            coords = session_data['location_info'].get('final_coordinates')
            if coords:
                formatted_complaint['latitude'] = coords[0]
                formatted_complaint['longitude'] = coords[1]
            
            # Show submission preview
            preview_message = (
                "📋 *Complaint Submission Preview*\n\n"
                f"*Subject:* {formatted_complaint['subject']}\n\n"
                f"*Category:* {formatted_complaint['category']}\n"
                f"*Priority:* {formatted_complaint['priority']}\n"
                f"*Department:* {formatted_complaint['department']}\n\n"
                f"*Description:*\n{formatted_complaint['description'][:300]}{'...' if len(formatted_complaint['description']) > 300 else ''}\n\n"
                "Click 'Submit' to send this complaint to the official government portal."
            )
            
            buttons = [
                [InlineKeyboardButton("🚀 Submit Complaint", callback_data="confirm_submission")],
                [InlineKeyboardButton("✏️ Edit Details", callback_data="edit_complaint")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_complaint")]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            
            await query.edit_message_text(
                preview_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Store formatted complaint in session
            session_data['formatted_complaint'] = formatted_complaint
            db_manager.create_or_update_session(
                user_id,
                json.dumps(session_data, default=str),
                'ready_for_submission'
            )
            
            return COMPLAINT_SUBMISSION
            
        except Exception as e:
            self.logger.error(f"Error in proceed_with_complaint: {e}")
            await query.edit_message_text("❌ Error preparing complaint.")
            return MAIN_MENU
    
    async def confirm_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Confirm and submit complaint"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            
            # Get session data
            session = db_manager.get_session_data(user_id)
            if not session:
                await query.edit_message_text("❌ Session expired. Please start again.")
                return MAIN_MENU
            
            session_data = json.loads(session.session_data)
            formatted_complaint = session_data.get('formatted_complaint')
            
            if not formatted_complaint:
                await query.edit_message_text("❌ No complaint data found.")
                return MAIN_MENU
            
            # Show submission progress
            await query.edit_message_text(
                "⏳ Submitting your complaint to the government portal...\n"
                "Please wait..."
            )
            
            # Submit to UMANG/CPGRAMS
            submission_result = umang_client.submit_grievance(formatted_complaint)
            
            if submission_result['success']:
                # Save complaint to database
                complaint_data = {
                    'complaint_text': session_data['ocr_result'].get('cleaned_text', ''),
                    'extracted_text': session_data['ocr_result'].get('cleaned_text', ''),
                    'category': formatted_complaint['category'],
                    'location_address': session_data['location_info'].get('final_address'),
                    'image_path': session_data.get('image_path'),
                    'umang_reference_id': submission_result['reference_id'],
                    'status': 'submitted'
                }
                
                # Add coordinates if available
                coords = session_data['location_info'].get('final_coordinates')
                if coords:
                    complaint_data['location_latitude'] = coords[0]
                    complaint_data['location_longitude'] = coords[1]
                
                complaint = db_manager.create_complaint(user_id, complaint_data)
                db_manager.update_complaint(complaint.id, {'submitted_at': datetime.now()})
                
                # Success message
                success_message = (
                    "✅ *Complaint Submitted Successfully!*\n\n"
                    f"📋 *Reference ID:* `{submission_result['reference_id']}`\n"
                    f"🎯 *Tracking Number:* `{submission_result['tracking_number']}`\n"
                    f"🏢 *Department:* {submission_result['assigned_department']}\n"
                    f"⏰ *Expected Resolution:* {submission_result['expected_resolution_days']} days\n\n"
                    "💾 Save the Reference ID to track your complaint status.\n\n"
                    "Use the 'Track Complaint' option in the main menu to check progress."
                )
                
                await query.edit_message_text(
                    success_message,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Show main menu after delay
                await asyncio.sleep(2)
                await context.bot.send_message(
                    chat_id=user_id,
                    text="📋 Main Menu:",
                    reply_markup=self.get_main_menu_keyboard()
                )
                
            else:
                error_message = (
                    "❌ *Complaint Submission Failed*\n\n"
                    f"Error: {submission_result.get('error', 'Unknown error')}\n\n"
                    "Please try again or contact support."
                )
                
                await query.edit_message_text(
                    error_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Clear session
            db_manager.clear_session(user_id)
            
            return MAIN_MENU
            
        except Exception as e:
            self.logger.error(f"Error in confirm_submission: {e}")
            await query.edit_message_text("❌ Error submitting complaint.")
            return MAIN_MENU
    
    async def start_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start complaint tracking process"""
        try:
            tracking_message = (
                "📊 *Track Your Complaint*\n\n"
                "Please send your complaint Reference ID to check the status.\n\n"
                "📋 The Reference ID format is usually:\n"
                "• CPGRAMS-XXXXXX-XXXX\n"
                "• MOCK-CPGRAMS-XXXXXX\n\n"
                "You can find it in the submission confirmation message."
            )
            
            keyboard = [[KeyboardButton("❌ Cancel")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                tracking_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return TRACKING_INPUT
            
        except Exception as e:
            self.logger.error(f"Error starting tracking: {e}")
            await update.message.reply_text("❌ Error starting tracking process.")
            return MAIN_MENU
    
    async def handle_tracking_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle tracking ID input"""
        try:
            text = update.message.text
            
            if text == "❌ Cancel":
                return await self.cancel_command(update, context)
            
            # Validate reference ID format
            if len(text) < 10:
                await update.message.reply_text(
                    "❌ Invalid Reference ID format. Please check and try again."
                )
                return TRACKING_INPUT
            
            # Show tracking progress
            tracking_msg = await update.message.reply_text("🔍 Tracking your complaint...")
            
            # Track complaint
            tracking_result = umang_client.track_grievance(text)
            
            await tracking_msg.delete()
            
            if tracking_result['success']:
                status_message = (
                    f"📊 *Complaint Status for {text}*\n\n"
                    f"📋 *Current Status:* {tracking_result['status']}\n"
                    f"🏢 *Department:* {tracking_result.get('department', 'N/A')}\n"
                    f"👤 *Assigned Officer:* {tracking_result.get('assigned_officer', 'N/A')}\n"
                    f"📅 *Last Updated:* {tracking_result.get('last_updated', 'N/A')}\n"
                    f"💭 *Remarks:* {tracking_result.get('remarks', 'N/A')}\n\n"
                )
                
                if tracking_result.get('expected_closure'):
                    status_message += f"⏰ *Expected Closure:* {tracking_result['expected_closure']}\n\n"
                
                # Add timeline if available
                timeline = tracking_result.get('timeline', [])
                if timeline:
                    status_message += "📅 *Progress Timeline:*\n"
                    for item in timeline[-3:]:  # Show last 3 entries
                        status_message += f"• {item['stage']} - {item['timestamp'][:10]}\n"
                
                await update.message.reply_text(
                    status_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.get_main_menu_keyboard()
                )
                
            else:
                error_message = (
                    f"❌ *Tracking Failed*\n\n"
                    f"Reference ID: {text}\n"
                    f"Error: {tracking_result.get('error', 'Not found')}\n\n"
                    "Please check the Reference ID and try again."
                )
                
                await update.message.reply_text(
                    error_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.get_main_menu_keyboard()
                )
            
            return MAIN_MENU
            
        except Exception as e:
            self.logger.error(f"Error handling tracking input: {e}")
            await update.message.reply_text("❌ Error tracking complaint.")
            return MAIN_MENU
    
    async def start_manual_complaint(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start manual complaint entry process"""
        try:
            manual_message = (
                "📝 *Manual Complaint Entry*\n\n"
                "Please describe your complaint in detail. Include:\n\n"
                "• What is the problem?\n"
                "• Where is it located? (address, area, landmarks)\n"
                "• When did it start?\n"
                "• How does it affect you or others?\n"
                "• Any other relevant details\n\n"
                "Write a comprehensive description and send it as a message."
            )
            
            keyboard = [[KeyboardButton("❌ Cancel")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                manual_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return MANUAL_COMPLAINT_INPUT
            
        except Exception as e:
            self.logger.error(f"Error starting manual complaint: {e}")
            await update.message.reply_text("❌ Error starting manual complaint process.")
            return MAIN_MENU
    
    async def handle_manual_complaint_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle manual complaint text input"""
        try:
            text = update.message.text
            user_id = update.effective_user.id
            
            if text == "❌ Cancel":
                return await self.cancel_command(update, context)
            
            if len(text) < 20:
                await update.message.reply_text(
                    "Please provide more details about your complaint (at least 20 characters)."
                )
                return MANUAL_COMPLAINT_INPUT
            
            # Process manual complaint
            processing_msg = await update.message.reply_text(
                "⏳ Processing your complaint...\n"
                "📍 Detecting location\n"
                "🏷️ Classifying complaint type"
            )
            
            # Detect location from text
            text_location = location_detector.detect_location_from_text(text)
            
            # Classify complaint
            classification = complaint_classifier.classify_complaint(text)
            
            # Combine location methods (no GPS, no manual address yet)
            location_info = location_detector.combine_location_methods(
                None, text_location
            )
            
            # Store session data
            session_data = {
                'complaint_text': text,
                'text_location': text_location,
                'classification': classification,
                'location_info': location_info,
                'step': 'manual_processed'
            }
            
            db_manager.create_or_update_session(
                user_id,
                json.dumps(session_data, default=str),
                'manual_processed'
            )
            
            await processing_msg.delete()
            
            # Show analysis results
            return await self.show_manual_analysis_results(update, context, session_data)
            
        except Exception as e:
            self.logger.error(f"Error handling manual complaint input: {e}")
            await update.message.reply_text("❌ Error processing manual complaint.")
            return MAIN_MENU
    
    async def show_manual_analysis_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, session_data: Dict) -> int:
        """Show manual complaint analysis results"""
        try:
            classification = session_data['classification']
            location_info = session_data['location_info']
            
            # Build result message
            result_message = "📝 *Manual Complaint Analysis*\n\n"
            
            # Classification Results
            category = classification['primary_category'].replace('_', ' ').title()
            result_message += f"🏷️ *Complaint Category:* {category}\n"
            result_message += f"📊 *Classification Confidence:* {classification['confidence_score']:.1f}%\n"
            result_message += f"⚡ *Priority Level:* {classification['priority_level'].title()}\n\n"
            
            # Location Results
            if location_info.get('final_address'):
                result_message += f"📍 *Detected Location:* {location_info['final_address']}\n"
                result_message += f"🎯 *Location Method:* {location_info['method_used']}\n"
                result_message += f"📊 *Location Confidence:* {location_info['confidence']}\n\n"
            else:
                result_message += "📍 *Location:* Could not detect automatically\n\n"
            
            # Suggested improvements
            suggestions = complaint_classifier.suggest_improvements(
                session_data['complaint_text'],
                classification
            )
            
            if suggestions:
                result_message += "💡 *Suggestions for improvement:*\n"
                for suggestion in suggestions:
                    result_message += f"• {suggestion}\n"
                result_message += "\n"
            
            # Create action buttons
            buttons = []
            
            if location_info.get('final_address'):
                buttons.append([InlineKeyboardButton("✅ Proceed with Complaint", callback_data="proceed_manual_complaint")])
            else:
                buttons.append([InlineKeyboardButton("📍 Add Location Manually", callback_data="add_manual_location")])
            
            buttons.extend([
                [InlineKeyboardButton("✏️ Edit Complaint Details", callback_data="edit_manual_complaint")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_complaint")]
            ])
            
            reply_markup = InlineKeyboardMarkup(buttons)
            
            await update.message.reply_text(
                result_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return COMPLAINT_REVIEW
            
        except Exception as e:
            self.logger.error(f"Error showing manual analysis results: {e}")
            await update.message.reply_text("❌ Error displaying results.")
            return MAIN_MENU

# Initialize bot handler
bot_handler = GrievanceBotHandler()

def create_conversation_handler():
    """Create the main conversation handler"""
    
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', bot_handler.start_command),
            CommandHandler('menu', bot_handler.menu_command)
        ],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_main_menu)
            ],
            WAITING_FOR_IMAGE: [
                MessageHandler(filters.PHOTO, bot_handler.handle_image_upload),
                MessageHandler(filters.TEXT & filters.Regex("^❌ Cancel$"), bot_handler.cancel_command)
            ],
            COMPLAINT_REVIEW: [
                CallbackQueryHandler(bot_handler.handle_complaint_actions)
            ],
            COMPLAINT_SUBMISSION: [
                CallbackQueryHandler(bot_handler.confirm_submission, pattern="^confirm_submission$"),
                CallbackQueryHandler(bot_handler.handle_complaint_actions)
            ],
            TRACKING_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_tracking_input)
            ],
            MANUAL_COMPLAINT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_manual_complaint_input)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', bot_handler.cancel_command),
            CommandHandler('help', bot_handler.help_command),
            CommandHandler('start', bot_handler.start_command)
        ],
        allow_reentry=True
    )

def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add conversation handler
        conv_handler = create_conversation_handler()
        application.add_handler(conv_handler)
        
        # Add command handlers that should work outside conversation
        application.add_handler(CommandHandler("help", bot_handler.help_command))
        
        # Start the bot
        logger.info("Starting Grievance Redressal Bot...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()

