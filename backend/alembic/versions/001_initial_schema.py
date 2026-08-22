"""Complete database schema for GlobeTrotter platform

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

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
        sa.Column('preferred_currency', sa.String(length=10), nullable=False, server_default='USD'),
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
        sa.Column('region', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cost_index', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('popularity_score', sa.Float(), nullable=False, server_default='8.0'),
        sa.Column('latitude', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('longitude', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)
    op.create_index(op.f('ix_cities_name'), 'cities', ['name'], unique=False)
    op.create_index(op.f('ix_cities_country'), 'cities', ['country'], unique=False)

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
        sa.Column('total_budget', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('visibility', sa.String(length=20), nullable=False, server_default='private'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_trips_id'), 'trips', ['id'], unique=False)
    op.create_index(op.f('ix_trips_user_id'), 'trips', ['user_id'], unique=False)

    # 4. trip_stops table
    op.create_table(
        'trip_stops',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('city_id', sa.String(length=36), nullable=False),
        sa.Column('arrival_date', sa.Date(), nullable=False),
        sa.Column('departure_date', sa.Date(), nullable=False),
        sa.Column('stop_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_trip_stops_id'), 'trip_stops', ['id'], unique=False)
    op.create_index(op.f('ix_trip_stops_trip_id'), 'trip_stops', ['trip_id'], unique=False)

    # 5. activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('city_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('duration_hours', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)
    op.create_index(op.f('ix_activities_city_id'), 'activities', ['city_id'], unique=False)
    op.create_index(op.f('ix_activities_category'), 'activities', ['category'], unique=False)

    # 6. itinerary_items table
    op.create_table(
        'itinerary_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_stop_id', sa.String(length=36), nullable=False),
        sa.Column('activity_id', sa.String(length=36), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('custom_cost', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trip_stop_id'], ['trip_stops.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_itinerary_items_id'), 'itinerary_items', ['id'], unique=False)
    op.create_index(op.f('ix_itinerary_items_trip_stop_id'), 'itinerary_items', ['trip_stop_id'], unique=False)
    op.create_index(op.f('ix_itinerary_items_scheduled_date'), 'itinerary_items', ['scheduled_date'], unique=False)

    # 7. expenses table
    op.create_table(
        'expenses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('estimated_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('actual_amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('paid_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['paid_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)
    op.create_index(op.f('ix_expenses_trip_id'), 'expenses', ['trip_id'], unique=False)

    # 8. budgets table
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

    # 9. favorites table
    op.create_table(
        'favorites',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('city_id', sa.String(length=36), nullable=True),
        sa.Column('activity_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('city_id IS NOT NULL OR activity_id IS NOT NULL', name='check_favorite_target'),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)

    # 10. shared_links table
    op.create_table(
        'shared_links',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('share_token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_shared_links_id'), 'shared_links', ['id'], unique=False)
    op.create_index(op.f('ix_shared_links_share_token'), 'shared_links', ['share_token'], unique=True)

    # 11. trip_collaborators table
    op.create_table(
        'trip_collaborators',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='editor'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trip_id', 'user_id', name='uq_trip_collaborator'),
    )
    op.create_index(op.f('ix_trip_collaborators_id'), 'trip_collaborators', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('trip_collaborators')
    op.drop_table('shared_links')
    op.drop_table('favorites')
    op.drop_table('budgets')
    op.drop_table('expenses')
    op.drop_table('itinerary_items')
    op.drop_table('activities')
    op.drop_table('trip_stops')
    op.drop_table('trips')
    op.drop_table('cities')
    op.drop_table('users')
