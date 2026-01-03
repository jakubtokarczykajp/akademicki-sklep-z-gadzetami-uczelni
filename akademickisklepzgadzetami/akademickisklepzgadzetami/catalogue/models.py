from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractCategory

class Product(AbstractProduct):
    """
    Model Produktu rozszerzający standardowy model Oscara.
    Możesz tutaj dodać specyficzne pola dla gadżetów uczelnianych.
    """

class Category(AbstractCategory):
    """
    Model Kategorii.
    """
    pass

# Ważne: importujemy pozostałe modele z Oscara, których nie nadpisujemy
from oscar.apps.catalogue.models import *