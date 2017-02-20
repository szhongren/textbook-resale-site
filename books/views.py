from django.views import generic
from django.shortcuts import render
from .models import Book, BookTemplate
from .forms import SearchForm
from isbnlib import is_isbn10, is_isbn13, canonical
from .search import ISBNSearch

# Create your views here.
class BookView(generic.DetailView):
    model = Book
    template_name = 'books/detail.html'

class BookSearchView(generic.TemplateView, generic.edit.FormMixin):
    template_name = 'books/search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        isbn_maybe = request.POST['ISBN']
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = {'form': form}
        if is_isbn10(isbn_maybe) or is_isbn13(isbn_maybe):
            isbn_raw = canonical(isbn_maybe)
            tradeable_books = get_tradeable_books(isbn_raw)
            if len(tradeable_books) == 0:
                context['error'] = 'Do not buy'
                context['book'] = get_books_with_isbn(isbn_raw)[0]
            else:
                context['book'] = tradeable_books[0]
        else:
            context['error'] = 'Book not found or not ISBN'
        return render(request, self.template_name, context)

def get_tradeable_books(isbn_raw):
    books = get_books_with_isbn(isbn_raw)
    return [BookTemplate(book) for book in books if book.get_attribute('IsEligibleForTradeIn')]

def get_books_with_isbn(isbn_raw):
    books = ISBNSearch(isbn_raw)
    if type(books) is list:
        return books
    else:
        return [books]