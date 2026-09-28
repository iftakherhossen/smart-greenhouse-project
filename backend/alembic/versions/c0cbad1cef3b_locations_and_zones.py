"""locations_and_zones

Revision ID: c0cbad1cef3b
Revises: 57c406d6595e
Create Date: 2026-09-28 18:23:56.567450

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c0cbad1cef3b"
down_revision: Union[str, Sequence[str], None] = "57c406d6595e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "locations",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "zones",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "location_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "moisture_threshold_low",
            sa.Numeric(),
            nullable=False,
        ),
        sa.Column(
            "moisture_threshold_high",
            sa.Numeric(),
            nullable=False,
        ),
        sa.Column(
            "schedule",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_zones_location_id"),
        "zones",
        ["location_id"],
        unique=False,
    )

    op.add_column(
        "devices",
        sa.Column(
            "zone_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "location_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_devices_location_id"),
        "devices",
        ["location_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_devices_zone_id"),
        "devices",
        ["zone_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_devices_zone_id_zones",
        "devices",
        "zones",
        ["zone_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_devices_location_id_locations",
        "devices",
        "locations",
        ["location_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_devices_location_id_locations",
        "devices",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_devices_zone_id_zones",
        "devices",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_devices_zone_id"),
        table_name="devices",
    )

    op.drop_index(
        op.f("ix_devices_location_id"),
        table_name="devices",
    )

    op.drop_column(
        "devices",
        "location_id",
    )

    op.drop_column(
        "devices",
        "zone_id",
    )

    op.drop_index(
        op.f("ix_zones_location_id"),
        table_name="zones",
    )

    op.drop_table("zones")

    op.drop_table("locations")