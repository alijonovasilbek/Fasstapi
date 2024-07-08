from datetime import datetime

from sqlalchemy import (Table,
                        Column,
                        Integer, String,
                        Text, MetaData, Boolean, TIMESTAMP, Date, ForeignKey,TIME)

metadata=MetaData()


todo = Table(
    'todo',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('plan', String, nullable=False),
    Column('description', Text),
    Column('created_date', TIMESTAMP, default=datetime.utcnow()),
    Column('status', Boolean, default=True),
    Column('user_id', Integer, ForeignKey('userdata.id'), nullable=False)
)

userdata = Table(
    'userdata',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('first_name', String, nullable=True),
    Column('last_name', String, nullable=True),
    Column('email', String),
    Column('username', String),
    Column('password', String),
    Column('birth_date', Date),
    Column('registered_date', TIMESTAMP, default=datetime.utcnow),
    Column('is_superuser', Boolean, default=False)

)

