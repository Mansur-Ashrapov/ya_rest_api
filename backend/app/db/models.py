from enum import unique
import sqlalchemy as SA

from app.db.database import metadata, engine


main_items = SA.Table(
    'main_items',
    metadata,
    SA.Column('base_id', SA.Integer, primary_key=True),
    SA.Column('id', SA.String, unique=True),
    SA.Column('url', SA.String, unique=True),
    SA.Column('date', SA.BigInteger),
    SA.Column('parent_id', SA.String),
    SA.Column('size', SA.Integer),
    SA.Column('type', SA.String),

)


history_of_item = SA.Table(
    'history_of_item',
    metadata,
    SA.Column('base_id', SA.Integer, primary_key=True),
    SA.Column('id', SA.String, SA.ForeignKey('main_items.id', onupdate='NO ACTION', ondelete='CASCADE')),
    SA.Column('url', SA.String),
    SA.Column('date', SA.BigInteger),
    SA.Column('parent_id', SA.String),
    SA.Column('size', SA.Integer),
    SA.Column('type', SA.String)
)

metadata.create_all(engine)
