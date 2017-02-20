from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from .models import Order, Transaction
from .forms import OrderCreateForm
from webapp.settings import TIME_ZONE, EMAIL_HOST_USER
from books.search import ISBNSearch
from books.views import get_tradeable_books
from books.models import Book, BookTemplate
from accounts.models import Account
from isbnlib import is_isbn10, is_isbn13, canonical
from decimal import Decimal, ROUND_DOWN

# Create your views here.
class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'order_list'

    def get_queryset(self):
        account = self.request.user
        if account.is_admin:
            return self.model.objects.all()
        return self.model.objects.select_related('account').filter(account=account.id)

class OrderDetailView(UserPassesTestMixin, LoginRequiredMixin, generic.ListView): # detailview with list mixin or iistview with detail mixin
    model = Transaction
    template_name = 'orders/detail.html'
    context_object_name = 'order_detail'

    def test_func(self):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        return self.request.user.is_admin or self.request.user.id == order.account.id

    def get_queryset(self):
        order = self.kwargs['pk']
        return self.model.objects.select_related('order').filter(order=order)

class OrderCreateView(LoginRequiredMixin, generic.TemplateView, generic.edit.FormMixin):
    template_name = 'orders/create.html'
    context_object_name = 'transactions'
    form_class = OrderCreateForm

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if 'transactions' not in request.session or request.session['transactions'] == []:
            new_order = Order(account=request.user, commission=request.user.default_commission, percentage_to_buy=request.user.default_percentage_to_buy, date_submitted=None, date_paid=None, notes='')
            grand_total = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            grand_total_paid = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            request.session['new_order'] = new_order
            request.session['transactions'] = []
            request.session['grand_total'] = grand_total
            request.session['grand_total_paid'] = grand_total_paid
            return render(request, self.template_name, {'form': form, 'new_order': new_order, 'grand_total': grand_total, 'grand_total_paid': grand_total_paid})
        else:
            new_order = request.session['new_order']
            transactions = request.session['transactions']
            grand_total = request.session['grand_total']
            grand_total_paid = request.session['grand_total_paid']
            return render(request, self.template_name, {'form': form, 'new_order': new_order, 'transactions': transactions, 'grand_total': grand_total, 'grand_total_paid': grand_total_paid})

    def post(self, request, *args, **kwargs):
        action = request.POST['create']
        new_order = request.session['new_order']
        transactions = request.session['transactions']
        grand_total = request.session['grand_total']
        grand_total_paid = request.session['grand_total_paid']

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = {'form': form}

        if action == 'Add':
            isbn_maybe = request.POST['ISBN']
            quantity = request.POST['Quantity']

            if is_isbn10(isbn_maybe) or is_isbn13(isbn_maybe):
                isbn_raw = canonical(isbn_maybe)
                books = get_tradeable_books(isbn_raw)
                if len(books) == 0:
                    context['error'] = 'Do not buy'
                else:
                    book = books[0].as_book()
                    transaction = Transaction(book=book, subtotal=transaction_subtotal(new_order, books[0], quantity), subtotal_paid=transaction_subtotal_paid(new_order, books[0], quantity), quantity=quantity, notes='')
                    transactions.append(transaction)
                    grand_total += transaction.subtotal
                    grand_total_paid += transaction.subtotal_paid
                    request.session['transactions'] = transactions
                    request.session['grand_total'] = grand_total
                    request.session['grand_total_paid'] = grand_total_paid
            else:
                # isbn check failed
                context['error'] = 'Not ISBN'
        elif action == 'Submit':
            if transactions == []:
                context['error'] = 'You need to add at least one book.'
            else:
                return redirect('orders:confirm')
        elif action == 'Cancel':
            transactions = []
            grand_total = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            grand_total_paid = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            request.session['transactions'] = transactions
            request.session['grand_total'] = grand_total
            request.session['grand_total_paid'] = grand_total_paid
            # context['error'] = 'Cancel order'
        context['new_order'] = request.session['new_order']
        context['transactions'] = request.session['transactions']
        context['grand_total'] = request.session['grand_total']
        context['grand_total_paid'] = request.session['grand_total_paid']
        return render(request, self.template_name, context)

    def order_cancel(self, request, *args, **kwargs):
        pass

    def transaction_add(self, request, *args, **kwargs):
        pass

    def transaction_delete(self, request, *args, **kwargs):
        pass

class OrderConfirmView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'orders/confirm.html'
    context_object_name = 'transactions'

    def get(self, request, *args, **kwargs):
        new_order = request.session['new_order']
        transactions = request.session['transactions']
        grand_total = request.session['grand_total']
        grand_total_paid = request.session['grand_total_paid']
        if transactions == None or transactions == []:
            return redirect('orders:create')
        else:
            return render(request, self.template_name, {'new_order': new_order, 'transactions': transactions, 'grand_total': grand_total, 'grand_total_paid': grand_total_paid})

    def post(self, request, *args, **kwargs):
        action = request.POST['confirm']
        new_order = request.session['new_order']
        transactions = request.session['transactions']
        grand_total = request.session['grand_total']
        grand_total_paid = request.session['grand_total_paid']
        if action == 'Back':
            return redirect('orders:create')
            # return render(request, self.template_name, {'new_order': new_order, 'transactions': transactions, 'grand_total': grand_total, 'grand_total_paid': grand_total_paid, 'error': 'Back'})
        elif action == 'Confirm':
            timezone.activate(TIME_ZONE)
            new_order.date_submitted = timezone.now()
            new_order.save()
            email_subj = '[Order {0}] - {1} on {2} at {3}'.format(new_order.id, request.user, new_order.date_submitted.date(), new_order.date_submitted.time())
            email_msg = '<table><tbody><tr><th>ISBN</th><th>Title</th><th>Author</th><th>Quantity</th><th>Subtotal Paid</th><th>Subtotal</th></tr>'
            email_from = EMAIL_HOST_USER
            email_to = []
            for admin in Account.objects.filter(is_admin=True):
                email_to.append(admin.email)
            email_to.append(request.user.email)
            for transaction in transactions:
                transaction.order = new_order
                transaction.book.save()
                transaction.save()
                email_msg += '<tr><td>{isbn}</td><td>{title}</td><td>{author}</td><td>{quantity}</td><td>{subtotal_paid}</td><td>{subtotal}</td></tr>'.format(isbn=transaction.book.isbn, title=transaction.book.title, author=transaction.book.author, quantity=transaction.quantity, subtotal_paid=transaction.subtotal_paid, subtotal=transaction.subtotal)
            email_msg += '</tbody></table>'
            transactions = []
            grand_total = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            grand_total_paid = Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            request.session['transactions'] = transactions
            request.session['grand_total'] = grand_total
            request.session['grand_total_paid'] = grand_total_paid
            msg = EmailMultiAlternatives(email_subj, email_msg, email_from, email_to)
            msg.content_subtype = 'html'
            msg.send()
            # return render(request, self.template_name, {'new_order': new_order, 'transactions': transactions, 'grand_total': grand_total, 'grand_total_paid': grand_total_paid, 'error': 'Confirm'})
            return redirect('orders:list')

def transaction_subtotal(new_order, book, quantity):
    return Decimal(
        transaction_subtotal_paid(new_order, book, quantity)
        * (1 + Decimal(new_order.commission))).quantize(Decimal('.01'), rounding=ROUND_DOWN)

def transaction_subtotal_paid(new_order, book, quantity):
    return Decimal(
        Decimal(book.trade_in_value)
        * Decimal(new_order.percentage_to_buy)
        * Decimal(quantity) / 100).quantize(Decimal('.01'), rounding=ROUND_DOWN)