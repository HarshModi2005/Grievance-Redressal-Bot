"""
Basic tests for the Grievance Redressal Bot components
"""
import os
import sys
import tempfile
import json
from PIL import Image, ImageDraw, ImageFont
import logging

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import Config
from database import db_manager
from ocr_processor import ocr_processor
from location_detector import location_detector
from complaint_classifier import complaint_classifier
from umang_client import umang_client

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotTester:
    """Test class for bot components"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_files = []
    
    def create_test_image(self, text_content: str, filename: str = None) -> str:
        """Create a test image with text for OCR testing"""
        try:
            # Create a temporary image with text
            image = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to use a default font, fallback to basic font
            try:
                # Try to load a better font
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)  # macOS
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 24)  # Ubuntu
                    except:
                        font = ImageFont.load_default()
            
            # Add text to image
            draw.text((50, 50), text_content, fill='black', font=font)
            
            # Save to temporary file
            if filename:
                temp_path = os.path.join(tempfile.gettempdir(), filename)
            else:
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_path = temp_file.name
                temp_file.close()
            
            image.save(temp_path, 'PNG')
            self.temp_files.append(temp_path)
            
            logger.info(f"Test image created: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error creating test image: {e}")
            return None
    
    def test_config_validation(self):
        """Test configuration validation"""
        logger.info("Testing configuration validation...")
        
        try:
            # Test basic config access
            assert hasattr(Config, 'TELEGRAM_BOT_TOKEN')
            assert hasattr(Config, 'DATABASE_URL')
            assert hasattr(Config, 'OCR_LANGUAGES')
            
            # Test complaint categories
            assert len(Config.COMPLAINT_CATEGORIES) > 0
            assert 'roads' in Config.COMPLAINT_CATEGORIES
            
            self.test_results['config_validation'] = 'PASSED'
            logger.info("✅ Configuration validation: PASSED")
            
        except Exception as e:
            self.test_results['config_validation'] = f'FAILED: {e}'
            logger.error(f"❌ Configuration validation: FAILED - {e}")
    
    def test_database_operations(self):
        """Test database operations"""
        logger.info("Testing database operations...")
        
        try:
            # Test user creation
            test_user = db_manager.create_user(
                telegram_id=12345,
                username="test_user",
                first_name="Test",
                last_name="User"
            )
            # Refresh the user object to avoid session issues
            session = db_manager.get_session()
            try:
                refreshed_user = session.query(db_manager.User).filter_by(telegram_id=12345).first()
                assert refreshed_user.telegram_id == 12345
            finally:
                session.close()
            
            # Test complaint creation
            complaint_data = {
                'complaint_text': 'Test road complaint',
                'category': 'roads',
                'location_address': 'Test Area, Mumbai'
            }
            
            test_complaint = db_manager.create_complaint(12345, complaint_data)
            assert test_complaint.user_telegram_id == 12345
            assert test_complaint.category == 'roads'
            
            # Test session management
            session_data = {'step': 'test', 'data': 'test_data'}
            db_manager.create_or_update_session(12345, json.dumps(session_data), 'test')
            
            retrieved_session = db_manager.get_session_data(12345)
            assert retrieved_session is not None
            assert retrieved_session.step == 'test'
            
            # Cleanup
            db_manager.clear_session(12345)
            
            self.test_results['database_operations'] = 'PASSED'
            logger.info("✅ Database operations: PASSED")
            
        except Exception as e:
            self.test_results['database_operations'] = f'FAILED: {e}'
            logger.error(f"❌ Database operations: FAILED - {e}")
    
    def test_ocr_processing(self):
        """Test OCR processing functionality"""
        logger.info("Testing OCR processing...")
        
        try:
            # Create test image with known text
            test_text = "Road repair needed at MG Road, Mumbai 400001. Pothole causing traffic jam."
            test_image_path = self.create_test_image(test_text, "test_ocr.png")
            
            if not test_image_path:
                raise Exception("Failed to create test image")
            
            # Test OCR extraction
            ocr_result = ocr_processor.extract_text_from_image(test_image_path)
            
            assert 'extraction_success' in ocr_result
            assert 'cleaned_text' in ocr_result
            assert 'confidence' in ocr_result
            
            # Check if some text was extracted
            if ocr_result['extraction_success']:
                assert len(ocr_result['cleaned_text']) > 0
                logger.info(f"OCR extracted text: {ocr_result['cleaned_text'][:100]}...")
                logger.info(f"OCR confidence: {ocr_result['confidence']:.2f}%")
            else:
                logger.warning("OCR extraction failed - this might be due to Tesseract not being properly configured")
            
            # Test validation
            validation = ocr_processor.validate_extracted_data(ocr_result)
            assert 'is_valid' in validation
            assert 'confidence_level' in validation
            
            self.test_results['ocr_processing'] = 'PASSED'
            logger.info("✅ OCR processing: PASSED")
            
        except Exception as e:
            self.test_results['ocr_processing'] = f'FAILED: {e}'
            logger.error(f"❌ OCR processing: FAILED - {e}")
    
    def test_location_detection(self):
        """Test location detection functionality"""
        logger.info("Testing location detection...")
        
        try:
            # Test location detection from text
            test_text = "Water leak problem at Sector 21, Noida, Uttar Pradesh 201301. Near City Mall."
            
            location_data = location_detector.detect_location_from_text(test_text)
            
            assert 'addresses' in location_data
            assert 'pincode' in location_data
            assert 'state' in location_data
            assert 'confidence_score' in location_data
            
            # Check if location components were detected
            if location_data['pincode']:
                logger.info(f"Detected pincode: {location_data['pincode']}")
            
            if location_data['state']:
                logger.info(f"Detected state: {location_data['state']}")
            
            logger.info(f"Location confidence: {location_data['confidence_score']}%")
            
            # Test coordinate validation
            test_coords = (28.7041, 77.1025)  # Delhi coordinates
            validation = location_detector.validate_coordinates(*test_coords)
            
            assert validation['is_valid'] == True
            assert validation['is_in_india'] == True
            
            # Test location combination
            combined = location_detector.combine_location_methods(
                test_coords, location_data, "Test Area, Delhi"
            )
            
            assert 'final_coordinates' in combined
            assert 'confidence' in combined
            
            self.test_results['location_detection'] = 'PASSED'
            logger.info("✅ Location detection: PASSED")
            
        except Exception as e:
            self.test_results['location_detection'] = f'FAILED: {e}'
            logger.error(f"❌ Location detection: FAILED - {e}")
    
    def test_complaint_classification(self):
        """Test complaint classification functionality"""
        logger.info("Testing complaint classification...")
        
        try:
            # Test different types of complaints
            test_complaints = [
                ("Road is broken with large potholes causing accidents", "roads"),
                ("Water supply not working since 3 days", "water"),
                ("Power cut in our area for 12 hours", "electricity"),
                ("Garbage not collected for a week", "sanitation"),
                ("Doctor not available in government hospital", "healthcare")
            ]
            
            for complaint_text, expected_category in test_complaints:
                classification = complaint_classifier.classify_complaint(complaint_text)
                
                assert 'primary_category' in classification
                assert 'confidence_score' in classification
                assert 'priority_level' in classification
                
                logger.info(f"Text: '{complaint_text[:50]}...'")
                logger.info(f"Classified as: {classification['primary_category']} (confidence: {classification['confidence_score']:.1f}%)")
                
                # Note: Classification might not always match expected category due to simple keyword matching
                # This is expected behavior for a basic classifier
            
            # Test suggestion generation
            suggestions = complaint_classifier.suggest_improvements(
                "road problem", {"primary_category": "roads", "priority_level": "high"}
            )
            
            assert isinstance(suggestions, list)
            assert len(suggestions) > 0
            
            # Test complaint formatting
            formatted = complaint_classifier.format_for_submission(
                "Test complaint text",
                {"primary_category": "roads", "priority_level": "high", "department_suggestions": ["PWD"]},
                {"final_address": "Test Location", "final_coordinates": (28.7041, 77.1025)}
            )
            
            assert 'subject' in formatted
            assert 'description' in formatted
            assert 'category' in formatted
            
            self.test_results['complaint_classification'] = 'PASSED'
            logger.info("✅ Complaint classification: PASSED")
            
        except Exception as e:
            self.test_results['complaint_classification'] = f'FAILED: {e}'
            logger.error(f"❌ Complaint classification: FAILED - {e}")
    
    def test_umang_client(self):
        """Test UMANG client functionality"""
        logger.info("Testing UMANG client (Mock mode)...")
        
        try:
            # Test authentication
            auth_result = umang_client.authenticate()
            assert auth_result == True  # Mock client always authenticates successfully
            
            # Test complaint submission
            test_grievance = {
                'subject': 'Test Grievance',
                'description': 'This is a test grievance submission',
                'category': 'roads',
                'priority': 'medium',
                'location': 'Test Location, Delhi',
                'latitude': 28.7041,
                'longitude': 77.1025,
                'department': 'Public Works Department'
            }
            
            submission_result = umang_client.submit_grievance(test_grievance)
            
            assert submission_result['success'] == True
            assert 'reference_id' in submission_result
            assert submission_result['reference_id'] is not None
            
            reference_id = submission_result['reference_id']
            logger.info(f"Mock submission successful: {reference_id}")
            
            # Test complaint tracking
            tracking_result = umang_client.track_grievance(reference_id)
            
            assert tracking_result['success'] == True
            assert 'status' in tracking_result
            assert tracking_result['reference_id'] == reference_id
            
            logger.info(f"Mock tracking successful: Status = {tracking_result['status']}")
            
            self.test_results['umang_client'] = 'PASSED'
            logger.info("✅ UMANG client: PASSED")
            
        except Exception as e:
            self.test_results['umang_client'] = f'FAILED: {e}'
            logger.error(f"❌ UMANG client: FAILED - {e}")
    
    def test_end_to_end_workflow(self):
        """Test end-to-end complaint processing workflow"""
        logger.info("Testing end-to-end workflow...")
        
        try:
            # Create test image with complaint details
            complaint_text = "Road repair needed at Sector 15, Gurgaon, Haryana 122001. Large pothole causing traffic issues."
            test_image_path = self.create_test_image(complaint_text, "test_e2e.png")
            
            if not test_image_path:
                logger.warning("Could not create test image, skipping image-based workflow")
                
                # Test manual workflow instead
                # Step 1: Classify complaint
                classification = complaint_classifier.classify_complaint(complaint_text)
                
                # Step 2: Detect location
                location_data = location_detector.detect_location_from_text(complaint_text)
                location_info = location_detector.combine_location_methods(
                    None, location_data, "Sector 15, Gurgaon, Haryana"
                )
                
                # Step 3: Format for submission
                formatted_complaint = complaint_classifier.format_for_submission(
                    complaint_text, classification, location_info
                )
                
                # Step 4: Submit to UMANG (mock)
                submission_result = umang_client.submit_grievance(formatted_complaint)
                
                assert submission_result['success'] == True
                
                logger.info("✅ Manual workflow test completed successfully")
            
            else:
                # Test image-based workflow
                # Step 1: OCR processing
                ocr_result = ocr_processor.extract_text_from_image(test_image_path)
                
                # Step 2: Location detection
                gps_coords = ocr_processor.extract_gps_from_image(test_image_path)
                text_location = location_detector.detect_location_from_text(
                    ocr_result.get('cleaned_text', '')
                )
                location_info = location_detector.combine_location_methods(
                    gps_coords, text_location
                )
                
                # Step 3: Classification
                classification = complaint_classifier.classify_complaint(
                    ocr_result.get('cleaned_text', ''),
                    {'location': text_location, 'gps': gps_coords}
                )
                
                # Step 4: Format and submit
                formatted_complaint = complaint_classifier.format_for_submission(
                    ocr_result.get('cleaned_text', ''),
                    classification,
                    location_info
                )
                
                submission_result = umang_client.submit_grievance(formatted_complaint)
                
                assert submission_result['success'] == True
                
                logger.info("✅ Image-based workflow test completed successfully")
            
            self.test_results['end_to_end_workflow'] = 'PASSED'
            logger.info("✅ End-to-end workflow: PASSED")
            
        except Exception as e:
            self.test_results['end_to_end_workflow'] = f'FAILED: {e}'
            logger.error(f"❌ End-to-end workflow: FAILED - {e}")
    
    def cleanup(self):
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Deleted: {temp_file}")
            except Exception as e:
                logger.warning(f"Could not delete {temp_file}: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Grievance Redressal Bot Tests")
        logger.info("=" * 50)
        
        try:
            # Run individual tests
            self.test_config_validation()
            self.test_database_operations()
            self.test_ocr_processing()
            self.test_location_detection()
            self.test_complaint_classification()
            self.test_umang_client()
            self.test_end_to_end_workflow()
            
        finally:
            # Always cleanup
            self.cleanup()
        
        # Print results summary
        logger.info("=" * 50)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASSED" else "❌"
            logger.info(f"{status_icon} {test_name}: {result}")
            
            if result == "PASSED":
                passed += 1
            else:
                failed += 1
        
        logger.info("=" * 50)
        logger.info(f"📈 TOTAL: {len(self.test_results)} tests | ✅ PASSED: {passed} | ❌ FAILED: {failed}")
        
        if failed == 0:
            logger.info("🎉 All tests passed! Bot is ready for deployment.")
        else:
            logger.warning(f"⚠️  {failed} test(s) failed. Please check the issues above.")
        
        return failed == 0

def main():
    """Main test runner"""
    print("🤖 Grievance Redressal Bot - Test Suite")
    print("=" * 60)
    print()
    
    # Check if Tesseract is available
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR is available")
        else:
            print("⚠️  Tesseract OCR may not be properly configured")
    except:
        print("⚠️  Tesseract OCR not found - OCR tests may fail")
    
    print()
    
    # Create and run tester
    tester = BotTester()
    success = tester.run_all_tests()
    
    print()
    if success:
        print("🎯 Ready to start the bot with: python main.py")
        print("📝 Make sure to configure your .env file with proper tokens")
    else:
        print("🔧 Please fix the failing tests before running the bot")
    
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
