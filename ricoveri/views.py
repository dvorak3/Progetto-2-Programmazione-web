from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.db.models import Q

from .models import Cittadino, Ospedale

def cittadini_list(request):
    query = request.GET.get('q', '').strip()

    cittadini = Cittadino.objects.all().order_by('cognome', 'nome')

    if query:
        cittadini = cittadini.filter(
            Q(CSSN__icontains=query) |
            Q(nome__icontains=query) |
            Q(cognome__icontains=query) |
            Q(luogoNascita__icontains=query) |
            Q(indirizzo__icontains=query)
        )

    context = {
        'cittadini': cittadini,
        'query': query,
        'count': cittadini.count(),
    }

    return render(request, 'ricoveri/cittadini_list.html', context)

def ospedali_list(request):
    query = request.GET.get('q', '').strip()

    ospedali = Ospedale.objects.all().order_by('nome')

    if query:
        ospedali = ospedali.filter(
            Q(codOspedale__icontains=query) |
            Q(nome__icontains=query) |
            Q(citta__icontains=query) |
            Q(indirizzo__icontains=query) |
            Q(dirSanitario__icontains=query)
        )

    context = {
        'ospedali': ospedali,
        'query': query,
        'count': ospedali.count(),
    }

    return render(request, 'ricoveri/ospedali_list.html', context)
