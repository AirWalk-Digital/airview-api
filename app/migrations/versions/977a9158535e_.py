"""empty message

Revision ID: 977a9158535e
Revises:
Create Date: 2022-04-19 15:37:29.740671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '977a9158535e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('environment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('abbreviation', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('abbreviation', name='uq_environment')
    )
    op.create_table('system',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('stage', sa.Enum('BUILD', 'MONITOR', name='systemstage'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', name='uq_system')
    )
    op.create_table('application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('application_type', sa.Enum('BUSINESS_APPLICATION', 'TECHNICAL_SERVICE', 'APPLICATION_SERVICE', name='applicationtype'), nullable=False),
    sa.Column('environment_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['environment_id'], ['environment.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['application.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('technical_control',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('reference', sa.String(length=500), nullable=False),
    sa.Column('control_action', sa.Enum('LOG', 'INCIDENT', 'TASK', 'VULNERABILITY', name='technicalcontrolaction'), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('severity', sa.Enum('HIGH', 'MEDIUM', 'LOW', name='technicalcontrolseverity'), nullable=False),
    sa.Column('quality_model', sa.Enum('LOG_EXCELLENCE', 'SECURITY', 'RELIABILITY', 'PERFORMANCE_EFFICIENCY', 'COST_OPTIMISATION', 'PORTABILITY', 'USABILITY_AND_COMPATIBILITY', name='qualitymodel'), nullable=False),
    sa.Column('ttl', sa.Integer(), nullable=True),
    sa.Column('is_blocking', sa.Boolean(), nullable=False),
    sa.Column('can_delete_resources', sa.Boolean(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['technical_control.id'], ),
    sa.ForeignKeyConstraint(['system_id'], ['system.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('system_id', 'reference', name='uq_technical_control')
    )
    op.create_table('application_reference',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=500), nullable=False),
    sa.Column('reference', sa.String(length=500), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('application_id', 'type', name='uq_application_type'),
    sa.UniqueConstraint('type', 'reference', name='uq_application_reference')
    )
    op.create_table('application_technical_control',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('technical_control_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.ForeignKeyConstraint(['technical_control_id'], ['technical_control.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('application_id', 'technical_control_id', name='uq_application_technical_control')
    )
    op.create_table('exclusion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('application_technical_control_id', sa.Integer(), nullable=False),
    sa.Column('summary', sa.String(), nullable=False),
    sa.Column('mitigation', sa.String(), nullable=False),
    sa.Column('impact', sa.Integer(), nullable=False),
    sa.Column('probability', sa.Integer(), nullable=False),
    sa.Column('is_limited_exclusion', sa.Boolean(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['application_technical_control_id'], ['application_technical_control.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('monitored_resource',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reference', sa.String(length=500), nullable=False),
    sa.Column('monitoring_state', sa.Enum('FLAGGED', 'SUPPRESSED', 'FIXED_AUTO', 'FIXED_OTHER', 'MONITORING', 'CANCELLED', 'UNRESPONSIVE', name='monitoredresourcestate'), nullable=False),
    sa.Column('type', sa.Enum('UNKNOWN', 'VIRTUAL_MACHINE', 'CONTAINER', 'NETWORK', 'REPOSITORY', 'PIPELINE', 'OBJECT_STORAGE', 'DATABASE', 'FUNCTION', 'STORAGE', name='monitoredresourcetype'), nullable=False),
    sa.Column('last_modified', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
    sa.Column('exclusion_id', sa.Integer(), nullable=True),
    sa.Column('exclusion_state', sa.Enum('NONE', 'PENDING', 'ACTIVE', name='exclusionstate'), nullable=True),
    sa.Column('additional_data', sa.String(length=8000), nullable=False),
    sa.Column('application_technical_control_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['application_technical_control_id'], ['application_technical_control.id'], ),
    sa.ForeignKeyConstraint(['exclusion_id'], ['exclusion.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('application_technical_control_id', 'reference', name='uq_monitored_resource')
    )
    op.create_table('monitored_resource_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('monitored_resource_id', sa.Integer(), nullable=False),
    sa.Column('reference', sa.String(length=50), nullable=True),
    sa.Column('request_timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['monitored_resource_id'], ['monitored_resource.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monitored_resource_ticket')
    op.drop_table('monitored_resource')
    op.drop_table('exclusion')
    op.drop_table('application_technical_control')
    op.drop_table('application_reference')
    op.drop_table('technical_control')
    op.drop_table('application')
    op.drop_table('system')
    op.drop_table('environment')
    # ### end Alembic commands ###