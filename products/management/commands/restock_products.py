from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = 'Restock all products with the given quantity'

    def add_arguments(self, parser):
        parser.add_argument(
            '-q',
            '--quantity',
            type=int,
            action='store',
            dest='quantity',
            default=10,
            help='Quantity to stock',
        )

    def handle(self, *args, **options):

        for product in Product.objects.all():
            if product.unitary:
                product.stock = options['quantity']
            else:
                product.stock = options['quantity'] * 100
            product.save()
