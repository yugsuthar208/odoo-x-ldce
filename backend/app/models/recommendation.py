import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class UserPreference(Base):
    """Stores user preferences for ML personalization."""
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    preferred_transit_mode = Column(String(50), nullable=True) # flight, train, bus, cab
    travel_style = Column(String(50), nullable=True) # luxury, budget, backpacker, family
    budget_level = Column(String(50), nullable=True) # low, mid, high
    activity_preferences = Column(JSON, nullable=True) # array of strings
    interests = Column(JSON, nullable=True)
    food_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", backref="preferences")

    @property
    def preferred_transport(self) -> str:
        return self.preferred_transit_mode

    @preferred_transport.setter
    def preferred_transport(self, val: str):
        self.preferred_transit_mode = val


class Recommendation(Base):
    """Smart optimization recommendations and alternative options."""
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    
    rec_type = Column(String(50), nullable=False) # e.g., 'transit_optimization', 'stay_optimization', 'external'
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=True) # reason
    reason = Column(Text, nullable=True)
    
    current_cost = Column(Float, nullable=True)
    alternative_cost = Column(Float, nullable=True)
    estimated_saving = Column(Float, nullable=True)
    
    affected_entity = Column(String(50), nullable=True) # 'TransitLeg', 'TripStay'
    affected_entity_id = Column(String(36), nullable=True)
    action_payload = Column(JSON, nullable=True) # Action to apply
    metadata_json = Column(JSON, nullable=True)
    
    source = Column(String(50), default="rule_engine", nullable=True)
    confidence = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    trip = relationship("Trip", backref="recommendations")
    user = relationship("User")


class MLPrediction(Base):
    """Stores batch or point-in-time ML predictions for analytics."""
    __tablename__ = "ml_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    
    model_name = Column(String(100), default="budget_xgboost", nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    prediction_type = Column(String(50), nullable=False) # e.g., 'budget_forecast'
    predicted_value = Column(Float, nullable=True)
    input_features = Column(JSON, nullable=True)
    prediction = Column(JSON, nullable=True)
    features_used = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    trip = relationship("Trip")
    user = relationship("User")

