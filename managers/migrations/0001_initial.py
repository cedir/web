# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medico', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userActionId', models.IntegerField()),
                ('objectTypeId', models.IntegerField()),
                ('objectId', models.IntegerField()),
                ('dateTime', models.CharField(max_length=200)),
                ('observacion', models.CharField(max_length=300)),
            ],
            options={
                'db_table': 'AuditUserActionsLog',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GrupoUsuarios',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'webData"."gruposUsuarios',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'idUsuario')),
                ('nombreUsuario', models.CharField(max_length=200, verbose_name=b'Nombre Usuario')),
                ('password', models.CharField(max_length=200, verbose_name=b'Password')),
                ('medico', models.ForeignKey(to='medico.Medico', db_column=b'idMedico')),
            ],
            options={
                'db_table': 'webData"."tblUsuarios',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='user',
            field=models.ForeignKey(to='managers.Usuario', db_column=b'userId'),
            preserve_default=True,
        ),
    ]
