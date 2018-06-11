# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [("company", "0002_auto_20160221_0254")]

    operations = [
        # production has been migrated, we don't need this anymore
        # migrations.RunSQL([
        #    'alter schema mehr_handwerk rename to "mehr-handwerk";',
        #    "insert into company_company values ('mehr-handwerk', 'Mehr Handwerk RENAMED', true);",
        #    "update company_access set company_id = 'mehr-handwerk' where company_id = 'mehr_handwerk';",
        #    "delete from company_company where schema = 'mehr_handwerk';",
        #    "update company_company set name = 'Mehr Handwerk' where schema = 'mehr-handwerk';"
        # ] if not settings.TESTING else [])
    ]
