from django.db import models


class Cittadino(models.Model):
    CSSN = models.CharField(max_length=16, primary_key=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    dataNascita = models.DateField()
    luogoNascita = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.cognome} {self.nome}"


class Ospedale(models.Model):
    codOspedale = models.CharField(max_length=10, primary_key=True)
    nome = models.CharField(max_length=150)
    citta = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    dirSanitario = models.CharField(max_length=16)
    latitudine = models.DecimalField(max_digits=9, decimal_places=6)
    longitudine = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.nome


class Patologia(models.Model):
    codPatologia = models.CharField(max_length=10, primary_key=True)
    nome = models.CharField(max_length=150)
    livello_rischio = models.CharField(max_length=50)

    def __str__(self):
        return self.nome


class PatologiaCronica(models.Model):
    patologia = models.OneToOneField(
        Patologia,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='codPatologia'
    )

    def __str__(self):
        return f"Cronica - {self.patologia.nome}"


class PatologiaMortale(models.Model):
    patologia = models.OneToOneField(
        Patologia,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='codPatologia'
    )

    def __str__(self):
        return f"Mortale - {self.patologia.nome}"


class Ricovero(models.Model):
    codRicovero = models.CharField(max_length=10, primary_key=True)
    ospedale = models.ForeignKey(
        Ospedale,
        on_delete=models.CASCADE,
        db_column='codOspedale'
    )
    cittadino = models.ForeignKey(
        Cittadino,
        on_delete=models.CASCADE,
        db_column='CSSN'
    )
    data = models.DateField()
    durata = models.IntegerField()
    diagnosi = models.CharField(max_length=255)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.codRicovero} - {self.cittadino}"


class PatologiaRicovero(models.Model):
    ricovero = models.ForeignKey(
        Ricovero,
        on_delete=models.CASCADE,
        db_column='codRicovero'
    )
    patologia = models.ForeignKey(
        Patologia,
        on_delete=models.CASCADE,
        db_column='codPatologia'
    )

    class Meta:
        unique_together = ('ricovero', 'patologia')

    def __str__(self):
        return f"{self.ricovero.codRicovero} - {self.patologia.nome}"
