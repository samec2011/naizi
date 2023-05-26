import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Команда для заполнения данными БД ингредиентам "
        "или тегами из CSV файла. "
        "Для ингредиентов: "
        ">>> python manage.py importcsv "
        "--filename 'ingredients.csv' "
        "--model_name 'Ingredient' "
        "Для тегов: "
        ">>> python manage.py importcsv "
        "--filename 'tags.csv' "
        "--model_name 'Tag' "
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            type=str,
            help="имя файла (ingredients.csv или tags.csv)",
        )
        parser.add_argument(
            "--model_name",
            type=str,
            help="название модели  (Ingredient или Tag)",
        )

    def get_csv_file(self, filename):
        return os.path.join(settings.BASE_DIR, "data", filename)

    def handle(self, *args, **options):
        filename = options["filename"]
        model_name = options["model_name"]
        file_path = self.get_csv_file(filename)
        self.stdout.write(self.style.SUCCESS(f"Чтение: {file_path}"))
        _model = apps.get_model("recipes", model_name)
        _model.objects.all().delete()
        try:
            with open(file_path, "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file, delimiter=",")
                bulk_create_data = (
                    _model(name=row[0], measurement_unit=row[1])
                    for row in reader
                )
                if "tags.csv" in filename:
                    bulk_create_data = (
                        _model(name=row[0], color=row[1], slug=row[2])
                        for row in reader
                    )
                _model.objects.bulk_create(bulk_create_data)
                line_count = _model.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"{line_count} данные добавлены в {model_name}"
                )
            )
        except FileNotFoundError:
            raise CommandError(f"Файл {file_path} не найден")
