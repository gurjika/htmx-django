from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, ListView
from django.contrib.auth import get_user_model
from films.models import Films
from django.contrib.auth.mixins import LoginRequiredMixin
from films.forms import RegisterForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)
    


def check_username(request):
    username = request.POST.get('username')


    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse('<div id="username-error" class="error">This exists</div>')
    else:
        return HttpResponse('<div id="username-error" class="success">available</div>')


class FilmListView(ListView):
    model = Films
    template_name = 'films.html'
    context_object_name = 'films'

    def get_queryset(self):
        user = self.request.user
        return Films.objects.filter(users=user).all()
    
@login_required
def add_film(request):
    # extract the film's name from the input field
    name = request.POST.get('filmname')

    # get or create the film with the given name
    film = Films.objects.get_or_create(name=name)[0]

    

    # add function creates relationship between user and the film
    request.user.films.add(film)

    # return template with all of the user's films
    films = request.user.films.all()
    messages.success(request, f'Added {name} to the list of films')
    return render(request, 'partials/film-list.html', context={'films': films})


@login_required
@require_http_methods(['DELETE'])
def delete_film(request, pk):
    # remove the films from the user's list
    request.user.films.remove(pk)

    # return the template fragment

    films = request.user.films.all()

    return render(request, 'partials/film-list.html', {'films': films})


def search_film(request):
    search_text = request.POST.get('search')

    user_films = request.user.films.all()
    # case insensitive ----> taxi driver == TAXI DRIVER
    results = Films.objects.filter(name__icontains=search_text).exclude(
        name__in=user_films.values_list('name', flat=True)
    )

    context = {'results': results}

    return render(request, 'partials/search-results.html', context)

def clear(request):
    return HttpResponse("")