from django.db import models
from django.db.models import Expression


class XMin(Expression):
    """Props to https://linuxtut.com/en/d24d7a1c70aaae871ffd/"""

    output_field = models.PositiveIntegerField()

    def as_postgresql(self, compiler, connection):
        return f'"{compiler.query.base_table}"."xmin"', ()
