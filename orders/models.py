from django.db import models
from books.models import Book
from accounts.models import Account

# Create your models here.
class Order(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    books_bought = models.ManyToManyField(Book, through='Transaction')
    commission = models.DecimalField(decimal_places=4, max_digits=5)
    percentage_to_buy = models.DecimalField(decimal_places=4, max_digits=5)
    date_submitted = models.DateTimeField()
    date_paid = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.account.email) + ' on ' + str(self.date_submitted)

class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    subtotal = models.DecimalField(decimal_places=2, max_digits=10)
    subtotal_paid = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
    price_when_submitted = models.DecimalField(decimal_places=2, max_digits=10)
    notes = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.book) + ': ' + str(self.quantity)