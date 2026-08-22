"""complete_architectural_upgrade_schema

Revision ID: d34a2519ea7f
Revises: b055be664320
Create Date: 2026-08-22 15:11:17.173611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd34a2519ea7f'
down_revision: Union[str, None] = 'b055be664320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. trips table
    op.add_column('trips', sa.Column('budget_currency', sa.String(length=10), server_default='INR', nullable=False))

    # 2. transit_legs table
    op.add_column('transit_legs', sa.Column('travel_date', sa.Date(), nullable=True))
    op.add_column('transit_legs', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column('transit_legs', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 3. transit_options table
    op.add_column('transit_options', sa.Column('label', sa.String(length=255), nullable=True))
    op.add_column('transit_options', sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True))
    op.add_column('transit_options', sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False))
    op.add_column('transit_options', sa.Column('metadata_json', sa.JSON(), nullable=True))
    op.add_column('transit_options', sa.Column('source', sa.String(length=50), server_default='generated', nullable=True))
    op.add_column('transit_options', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 4. stays table
    op.add_column('stays', sa.Column('provider', sa.String(length=100), nullable=True))
    op.add_column('stays', sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False))
    op.add_column('stays', sa.Column('metadata_json', sa.JSON(), nullable=True))
    op.add_column('stays', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 5. trip_stays table
    op.add_column('trip_stays', sa.Column('trip_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_trip_stays_trip_id', 'trip_stays', 'trips', ['trip_id'], ['id'], ondelete='CASCADE')
    op.add_column('trip_stays', sa.Column('nightly_cost', sa.Float(), server_default='0.0', nullable=False))
    op.add_column('trip_stays', sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False))
    op.add_column('trip_stays', sa.Column('is_estimate', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('trip_stays', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column('trip_stays', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 6. user_preferences table
    op.add_column('user_preferences', sa.Column('budget_level', sa.String(length=50), nullable=True))
    op.add_column('user_preferences', sa.Column('interests', sa.JSON(), nullable=True))
    op.add_column('user_preferences', sa.Column('food_preferences', sa.JSON(), nullable=True))
    op.add_column('user_preferences', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.add_column('user_preferences', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False))

    # 7. recommendations table
    op.add_column('recommendations', sa.Column('user_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_recommendations_user_id', 'recommendations', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.add_column('recommendations', sa.Column('entity_type', sa.String(length=50), nullable=True))
    op.add_column('recommendations', sa.Column('entity_id', sa.String(length=36), nullable=True))
    op.add_column('recommendations', sa.Column('reason', sa.Text(), nullable=True))
    op.add_column('recommendations', sa.Column('score', sa.Float(), nullable=True))
    op.add_column('recommendations', sa.Column('source', sa.String(length=50), server_default='rule_engine', nullable=True))
    op.add_column('recommendations', sa.Column('metadata_json', sa.JSON(), nullable=True))
    op.add_column('recommendations', sa.Column('expires_at', sa.DateTime(), nullable=True))

    # 8. ml_predictions table
    op.add_column('ml_predictions', sa.Column('user_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_ml_predictions_user_id', 'ml_predictions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.add_column('ml_predictions', sa.Column('model_name', sa.String(length=100), server_default='budget_xgboost', nullable=False))
    op.add_column('ml_predictions', sa.Column('model_version', sa.String(length=50), server_default='1.0.0', nullable=False))
    op.add_column('ml_predictions', sa.Column('input_features', sa.JSON(), nullable=True))
    op.add_column('ml_predictions', sa.Column('prediction', sa.JSON(), nullable=True))


def downgrade() -> None:
    # 8. ml_predictions table
    op.drop_constraint('fk_ml_predictions_user_id', 'ml_predictions', type_='foreignkey')
    op.drop_column('ml_predictions', 'prediction')
    op.drop_column('ml_predictions', 'input_features')
    op.drop_column('ml_predictions', 'model_version')
    op.drop_column('ml_predictions', 'model_name')
    op.drop_column('ml_predictions', 'user_id')

    # 7. recommendations table
    op.drop_constraint('fk_recommendations_user_id', 'recommendations', type_='foreignkey')
    op.drop_column('recommendations', 'expires_at')
    op.drop_column('recommendations', 'metadata_json')
    op.drop_column('recommendations', 'source')
    op.drop_column('recommendations', 'score')
    op.drop_column('recommendations', 'reason')
    op.drop_column('recommendations', 'entity_id')
    op.drop_column('recommendations', 'entity_type')
    op.drop_column('recommendations', 'user_id')

    # 6. user_preferences table
    op.drop_column('user_preferences', 'updated_at')
    op.drop_column('user_preferences', 'created_at')
    op.drop_column('user_preferences', 'food_preferences')
    op.drop_column('user_preferences', 'interests')
    op.drop_column('user_preferences', 'budget_level')

    # 5. trip_stays table
    op.drop_constraint('fk_trip_stays_trip_id', 'trip_stays', type_='foreignkey')
    op.drop_column('trip_stays', 'updated_at')
    op.drop_column('trip_stays', 'created_at')
    op.drop_column('trip_stays', 'is_estimate')
    op.drop_column('trip_stays', 'currency')
    op.drop_column('trip_stays', 'nightly_cost')
    op.drop_column('trip_stays', 'trip_id')

    # 4. stays table
    op.drop_column('stays', 'created_at')
    op.drop_column('stays', 'metadata_json')
    op.drop_column('stays', 'currency')
    op.drop_column('stays', 'provider')

    # 3. transit_options table
    op.drop_column('transit_options', 'created_at')
    op.drop_column('transit_options', 'source')
    op.drop_column('transit_options', 'metadata_json')
    op.drop_column('transit_options', 'currency')
    op.drop_column('transit_options', 'estimated_duration_minutes')
    op.drop_column('transit_options', 'label')

    # 2. transit_legs table
    op.drop_column('transit_legs', 'updated_at')
    op.drop_column('transit_legs', 'created_at')
    op.drop_column('transit_legs', 'travel_date')

    # 1. trips table
    op.drop_column('trips', 'budget_currency')

