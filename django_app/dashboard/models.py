from django.db import models

class Divipola(models.Model):
    id = models.AutoField(primary_key=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    codigo_divipola = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'divipola'
        managed = False

    def __str__(self):
        return f"{self.departamento} - {self.municipio or 'N/A'}"


class Causa(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    descripcion = models.CharField(max_length=255)

    class Meta:
        db_table = 'causas'
        managed = False

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Muerte(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    sexo = models.CharField(max_length=1, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    grupo_edad = models.CharField(max_length=50, null=True, blank=True)
    codigo_causa = models.CharField(max_length=10, null=True, blank=True, db_column='codigo_causa')

    class Meta:
        db_table = 'muertes'
        managed = False
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['departamento']),
            models.Index(fields=['codigo_causa']),
        ]

    def __str__(self):
        return f"Muerte {self.id} - {self.municipio} ({self.fecha})"
