from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient

DATA_DIR = settings.BASE_DIR / 'data'


class Command(BaseCommand):

    help = "Загружает ингредиенты в БД из csv"

    def handle(self, *args, **options):
        with open(
            DATA_DIR / 'ingredients.csv', encoding='utf-8'
        ) as ingredients:
            for row in DictReader(ingredients):
                instance = Ingredient(**row)
                instance.save()
