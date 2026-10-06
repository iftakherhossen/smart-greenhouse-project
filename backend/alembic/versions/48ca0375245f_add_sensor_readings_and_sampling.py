"""add sensor readings and sampling

Revision ID: 48ca0375245f
Revises: c0cbad1cef3b
Create Date: 2026-10-06 13:27:43.729912

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "48ca0375245f"
down_revision: Union[str, Sequence[str], None] = "c0cbad1cef3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the new columns as nullable first so existing devices
    # can be safely backfilled before making them NOT NULL.
    op.add_column(
        "devices",
        sa.Column(
            "sampling_interval_seconds",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "tracking_enabled",
            sa.Boolean(),
            nullable=True,
        ),
    )

    # Backfill the sampling interval from default_config when it
    # contains a numeric value. Otherwise use the required default
    # of 300 seconds.
    op.execute(
        """
        UPDATE devices
        SET sampling_interval_seconds =
            CASE
                WHEN jsonb_typeof(
                    default_config->'sampling_interval_seconds'
                ) = 'number'
                THEN GREATEST(
                    (default_config->>'sampling_interval_seconds')::integer,
                    5
                )
                ELSE 300
            END,
            tracking_enabled = TRUE
        """
    )

    # Make the columns required after the existing rows are populated.
    op.alter_column(
        "devices",
        "sampling_interval_seconds",
        nullable=False,
        server_default=sa.text("300"),
    )

    op.alter_column(
        "devices",
        "tracking_enabled",
        nullable=False,
        server_default=sa.text("true"),
    )

    # Create the sensor readings table.
    op.create_table(
        "sensor_readings",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Numeric(),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_sensor_readings_device_recorded_at",
        "sensor_readings",
        ["device_id", "recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_sensor_readings_device_recorded_at",
        table_name="sensor_readings",
    )

    op.drop_table("sensor_readings")

    op.drop_column("devices", "tracking_enabled")
    op.drop_column("devices", "sampling_interval_seconds")