from django.db import models
from decimal import Decimal, ROUND_DOWN
# Create your models here.

class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, primary_key=True)
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    medium_image_url = models.CharField(max_length=255)
    large_image_url = models.CharField(max_length=255)
    sales_rank = models.IntegerField()

    def __str__(self):
        return self.title + ' - ' + self.author

class BookTemplate(Book):
    format = None
    has_trade_in = False
    trade_in_value = 0
    formatted_value = ''

    def __init__(self, book):
        Book.isbn = book.isbn
        Book.author = book.author
        Book.title = book.title
        Book.medium_image_url = book.medium_image_url
        Book.large_image_url = book.large_image_url
        Book.sales_rank = book.sales_rank
        self.format = book.binding
        self.has_trade_in = bool(book.get_attribute('IsEligibleForTradeIn'))
        self.trade_in_value = book.get_attribute('TradeInValue.Amount')
        self.formatted_value = book.get_attribute('TradeInValue.FormattedPrice')
        self.buy_price = Decimal(Decimal(self.trade_in_value) * Decimal(0.8 / 100)).quantize(Decimal('.01'), rounding=ROUND_DOWN)


    def as_book(self):
        return Book(isbn=self.isbn, author=self.author, title=self.title, medium_image_url=self.medium_image_url, large_image_url=self.large_image_url, sales_rank=self.sales_rank)