"""
Database models and operations for the Grievance Redressal Bot
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from config import Config

Base = declarative_base()

class User(Base):
    """User model for storing telegram user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Complaint(Base):
    """Complaint model for storing grievance information"""
    __tablename__ = 'complaints'
    
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, nullable=False)
    complaint_text = Column(Text)
    extracted_text = Column(Text)  # OCR extracted text
    category = Column(String(50))
    location_address = Column(Text)
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    image_path = Column(String(500))
    umang_reference_id = Column(String(100))
    status = Column(String(50), default='draft')  # draft, submitted, processing, resolved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
class ComplaintSession(Base):
    """Session model for tracking user complaint creation process"""
    __tablename__ = 'complaint_sessions'
    
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(Integer, nullable=False)
    session_data = Column(Text)  # JSON data for current complaint being created
    step = Column(String(50))  # current step in complaint creation process
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager class for handling database operations"""
    
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)
    
    def get_session(self):
        """Get a database session"""
        return self.Session()
    
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None, phone_number=None):
        """Create or update user record"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                # Update existing user
                user.username = username or user.username
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.phone_number = phone_number or user.phone_number
            else:
                # Create new user
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number
                )
                session.add(user)
            
            session.commit()
            # Detach from session to avoid lazy loading issues
            session.expunge(user)
            self.logger.info(f"User {telegram_id} created/updated successfully")
            return user
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error creating/updating user {telegram_id}: {e}")
            raise
        finally:
            session.close()
    
    def create_complaint(self, user_telegram_id, complaint_data):
        """Create a new complaint record"""
        session = self.get_session()
        try:
            complaint = Complaint(
                user_telegram_id=user_telegram_id,
                complaint_text=complaint_data.get('complaint_text'),
                extracted_text=complaint_data.get('extracted_text'),
                category=complaint_data.get('category'),
                location_address=complaint_data.get('location_address'),
                location_latitude=complaint_data.get('location_latitude'),
                location_longitude=complaint_data.get('location_longitude'),
                image_path=complaint_data.get('image_path'),
                status='draft'
            )
            
            session.add(complaint)
            session.commit()
            
            # Force loading of all attributes before detaching
            complaint_id = complaint.id
            
            # Detach from session to avoid lazy loading issues
            session.expunge(complaint)
            
            self.logger.info(f"Complaint created for user {user_telegram_id}")
            return complaint
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error creating complaint for user {user_telegram_id}: {e}")
            raise
        finally:
            session.close()
    
    def update_complaint(self, complaint_id, update_data):
        """Update complaint record"""
        session = self.get_session()
        try:
            complaint = session.query(Complaint).get(complaint_id)
            if complaint:
                for key, value in update_data.items():
                    if hasattr(complaint, key):
                        setattr(complaint, key, value)
                
                session.commit()
                # Detach from session to avoid lazy loading issues
                session.expunge(complaint)
                self.logger.info(f"Complaint {complaint_id} updated successfully")
                return complaint
            else:
                self.logger.warning(f"Complaint {complaint_id} not found")
                return None
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating complaint {complaint_id}: {e}")
            raise
        finally:
            session.close()
    
    def get_user_complaints(self, telegram_id):
        """Get all complaints for a user"""
        session = self.get_session()
        try:
            complaints = session.query(Complaint).filter_by(
                user_telegram_id=telegram_id
            ).order_by(Complaint.created_at.desc()).all()
            return complaints
        except Exception as e:
            self.logger.error(f"Error fetching complaints for user {telegram_id}: {e}")
            return []
        finally:
            session.close()
    
    def create_or_update_session(self, user_telegram_id, session_data, step):
        """Create or update complaint session"""
        session = self.get_session()
        try:
            complaint_session = session.query(ComplaintSession).filter_by(
                user_telegram_id=user_telegram_id
            ).first()
            
            if complaint_session:
                complaint_session.session_data = session_data
                complaint_session.step = step
                complaint_session.updated_at = datetime.utcnow()
            else:
                complaint_session = ComplaintSession(
                    user_telegram_id=user_telegram_id,
                    session_data=session_data,
                    step=step
                )
                session.add(complaint_session)
            
            session.commit()
            return complaint_session
        
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating session for user {user_telegram_id}: {e}")
            raise
        finally:
            session.close()
    
    def get_session_data(self, user_telegram_id):
        """Get complaint session data for user"""
        session = self.get_session()
        try:
            complaint_session = session.query(ComplaintSession).filter_by(
                user_telegram_id=user_telegram_id
            ).first()
            # Detach from session to avoid lazy loading issues
            if complaint_session:
                session.expunge(complaint_session)
            return complaint_session
        except Exception as e:
            self.logger.error(f"Error fetching session for user {user_telegram_id}: {e}")
            return None
        finally:
            session.close()
    
    def clear_session(self, user_telegram_id):
        """Clear complaint session for user"""
        session = self.get_session()
        try:
            complaint_session = session.query(ComplaintSession).filter_by(
                user_telegram_id=user_telegram_id
            ).first()
            if complaint_session:
                session.delete(complaint_session)
                session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error clearing session for user {user_telegram_id}: {e}")
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager()

