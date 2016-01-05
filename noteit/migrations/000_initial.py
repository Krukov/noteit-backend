""" Peewee migrations. """

import datetime as dt
import peewee as pw
from noteit.utils import gen_key, get_alias


def migrate(migrator, database, **kwargs):
    """ Write your migrations here.

    > migrator.create_table(model)
    > migrator.drop_table(model, cascade=True)
    > migrator.add_columns(model, **fields)
    > migrator.drop_columns(models, *names, cascade=True)
    > migrator.rename_column(model, old_name, new_name)
    > migrator.rename_table(model, new_name)
    > migrator.add_index(model, *columns, unique=False)
    > migrator.drop_index(model, index_name)
    > migrator.add_not_null(model, name)
    > migrator.drop_not_null(model, name)

    """

    @migrator.create_table
    class User(pw.Model):
        username = pw.CharField(unique=True)
        password = pw.CharField()
        created = pw.DateTimeField(default=dt.datetime.now)
        active = pw.BooleanField(default=True)

    @migrator.create_table
    class Token(pw.Model):
        key = pw.PrimaryKeyField(default=gen_key, index=True)
        user = pw.ForeignKeyField(User, related_name='tokens')
        created = pw.DateTimeField(default=dt.datetime.now)


    @migrator.create_table
    class Report(pw.Model):
        traceback = pw.TextField()
        info = pw.TextField()
        user = pw.ForeignKeyField(User, null=True, related_name='reports')
        created = pw.DateTimeField(default=dt.datetime.now)


    @migrator.create_table
    class Note(pw.Model):
        text = pw.TextField()
        owner = pw.ForeignKeyField(User, related_name='notes')
        alias = pw.CharField(index=True, default=get_alias)
        active = pw.BooleanField(default=True)
        created = pw.DateTimeField(default=dt.datetime.now)

        class Meta:
            indexes = (
                (('owner', 'alias'), True),
            )
