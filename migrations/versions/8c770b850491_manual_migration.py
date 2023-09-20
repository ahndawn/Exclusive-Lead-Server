"""manual migration

Revision ID: 8c770b850491
Revises: 
Create Date: 2023-09-20 11:00:06.958974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c770b850491'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # User model
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('email', sa.String),
        sa.Column('reset_token', sa.String),
        sa.Column('reset_token_expiration', sa.String),
        sa.Column('is_active', sa.Boolean, default=True)
    )
    
    # Lead model
    op.create_table(
        'lead',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('timestamp', sa.String, nullable=False),
        sa.Column('label', sa.String),
        sa.Column('firstname', sa.String),
        sa.Column('email', sa.String),
        sa.Column('phone1', sa.String),
        sa.Column('ozip', sa.String),
        sa.Column('dzip', sa.String),
        sa.Column('dcity', sa.String),
        sa.Column('dstate', sa.String),
        sa.Column('movesize', sa.String),
        sa.Column('movedte', sa.String),
        sa.Column('conversion', sa.String),
        sa.Column('validation', sa.String),
        sa.Column('notes', sa.String),
        sa.Column('sent_to_gronat', sa.String),
        sa.Column('sent_to_sheets', sa.String)
    )

    # Domain model
    op.create_table(
        'domain',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('label', sa.String),
        sa.Column('domain', sa.String),
        sa.Column('d_phone_number', sa.String),
        sa.Column('send_to_leads_api', sa.Integer),
        sa.Column('send_to_google_sheet', sa.Integer),
        sa.Column('twilio_number_validation', sa.Integer),
        sa.Column('sms_texting', sa.Integer),
        sa.Column('lead_cost', sa.String),
        sa.Column('change_moverref', sa.Boolean, default=False),
        sa.Column('moverref', sa.String)
    )
    
    # Archive model (similar to Lead)
    op.create_table(
        'archive',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('timestamp', sa.String, nullable=False),
        sa.Column('label', sa.String),
        sa.Column('firstname', sa.String),
        sa.Column('email', sa.String),
        sa.Column('phone1', sa.String),
        sa.Column('ozip', sa.String),
        sa.Column('dzip', sa.String),
        sa.Column('dcity', sa.String),
        sa.Column('dstate', sa.String),
        sa.Column('movesize', sa.String),
        sa.Column('movedte', sa.String),
        sa.Column('conversion', sa.String),
        sa.Column('validation', sa.String),
        sa.Column('notes', sa.String),
        sa.Column('sent_to_gronat', sa.String),
        sa.Column('sent_to_sheets', sa.String)
    )

def downgrade():
    op.drop_table('archive')
    op.drop_table('domain')
    op.drop_table('lead')
    op.drop_table('users')
