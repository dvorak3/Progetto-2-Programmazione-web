from django.db import models

# Create your models here.
from django.db import models


class Cittadino(models.Model):
    cssn = models.CharField(max_length=16, primary_key=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    data_nascita = models.DateField()
    luogo_nascita = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.cognome} {self.nome}"


class Ospedale(models.Model):
    cod_ospedale = models.CharField(max_length=10, primary_key=True)
    nome = models.CharField(max_length=150)
    citta = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    dir_sanitario = models.CharField(max_length=16)
    latitudine = models.DecimalField(max_digits=9, decimal_places=6)
    longitudine = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.nome


class Patologia(models.Model):
    cod_patologia = models.CharField(max_length=10, primary_key=True)
    nome = models.CharField(max_length=150)
    descrizione = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Ricovero(models.Model):
    cod_ricovero = models.CharField(max_length=10, primary_key=True)
    cittadino = models.ForeignKey(Cittadino, on_delete=models.CASCADE)
    ospedale = models.ForeignKey(Ospedale, on_delete=models.CASCADE)
    data_inizio = models.DateField()
    data_fine = models.DateField(null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True)
    patologie = models.ManyToManyField(Patologia, blank=True)

    def __str__(self):
        return f"{self.cod_ricovero} - {self.cittadino}"
