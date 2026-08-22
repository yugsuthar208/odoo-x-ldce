"""Initial database schema for GlobeTrotter

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('profile_photo', sa.String(length=512), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. cities table
    op.create_table(
        'cities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=255), nullable=False),
        sa.Column('region', sa.String(length=255), nullable=False),
        sa.Column('cost_index', sa.Float(), nullable=False),
        sa.Column('popularity_score', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)
    op.create_index(op.f('ix_cities_name'), 'cities', ['name'], unique=False)
    op.create_index(op.f('ix_cities_country'), 'cities', ['country'], unique=False)
    op.create_index(op.f('ix_cities_region'), 'cities', ['region'], unique=False)

    # 3. trips table
    op.create_table(
        'trips',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('cover_photo', sa.String(length=512), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_trips_id'), 'trips', ['id'], unique=False)
    op.create_index(op.f('ix_trips_user_id'), 'trips', ['user_id'], unique=False)

    # 4. stops table
    op.create_table(
        'stops',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('city_id', sa.String(length=36), nullable=False),
        sa.Column('arrival_date', sa.Date(), nullable=False),
        sa.Column('departure_date', sa.Date(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stops_id'), 'stops', ['id'], unique=False)
    op.create_index(op.f('ix_stops_trip_id'), 'stops', ['trip_id'], unique=False)
    op.create_index(op.f('ix_stops_city_id'), 'stops', ['city_id'], unique=False)

    # 5. activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('city_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('duration_hours', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    op.create_index(op.f('ix_activities_city_id'), 'activities', ['city_id'], unique=False)
    op.create_index(op.f('ix_activities_type'), 'activities', ['type'], unique=False)

    # 6. stop_activities table
    op.create_table(
        'stop_activities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('stop_id', sa.String(length=36), nullable=False),
        sa.Column('activity_id', sa.String(length=36), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('scheduled_time', sa.Time(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stop_id'], ['stops.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_stop_activities_id'), 'stop_activities', ['id'], unique=False)
    op.create_index(op.f('ix_stop_activities_stop_id'), 'stop_activities', ['stop_id'], unique=False)
    op.create_index(op.f('ix_stop_activities_activity_id'), 'stop_activities', ['activity_id'], unique=False)

    # 7. budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('transport_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('stay_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('meals_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('misc_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_budget_limit', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_budgets_id'), 'budgets', ['id'], unique=False)
    op.create_index(op.f('ix_budgets_trip_id'), 'budgets', ['trip_id'], unique=True)


def downgrade() -> None:
    op.drop_table('budgets')
    op.drop_table('stop_activities')
    op.drop_table('activities')
    op.drop_table('stops')
    op.drop_table('trips')
    op.drop_table('cities')
    op.drop_table('users')
