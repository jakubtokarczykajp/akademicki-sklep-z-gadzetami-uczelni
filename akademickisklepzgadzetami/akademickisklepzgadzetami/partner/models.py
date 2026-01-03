from django.db import models
from oscar.apps.partner.abstract_models import AbstractStockRecord, AbstractPartner

class Partner(AbstractPartner):
    """
    Partner to dostawca lub właściciel magazynu (np. 'Magazyn Główny AJP').
    """
    pass

class StockRecord(AbstractStockRecord):
    """
    StockRecord przechowuje informacje o cenie i ilości produktu w magazynie.
    """

# Ważne: importujemy pozostałe modele z Oscara
from oscar.apps.partner.models import *