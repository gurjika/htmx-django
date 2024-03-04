from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, ListView
from django.contrib.auth import get_user_model
from films.models import Films, UserFilms
from django.contrib.auth.mixins import LoginRequiredMixin
from films.forms import RegisterForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import get_max_order, reorder

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
    model = UserFilms
    template_name = 'films.html'
    context_object_name = 'films'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        return UserFilms.objects.filter(user=user).all()
    

    def get_template_names(self):
        if self.request.htmx:
            print("ok")
            return 'partials/film-list-elements.html'
        return 'films.html'
    
@login_required
def add_film(request):
    # extract the film's name from the input field
    name = request.POST.get('filmname')

    # get or create the film with the given name
    film = Films.objects.get_or_create(name=name)[0]

    if not UserFilms.objects.filter(film=film, user=request.user):
        UserFilms.objects.create(
            film=film,
            user=request.user, 
            order=get_max_order(request.user))  

    

    # add function creates relationship between user and the film
    # request.user.films.add(film)

    # return template with all of the user's films
    films = UserFilms.objects.filter(user=request.user).all()
    
    messages.success(request, f'Added {name} to the list of films')
    return render(request, 'partials/film-list.html', context={'films': films})


@login_required
@require_http_methods(['DELETE'])
def delete_film(request, pk):
    # remove the films from the user's list
    # request.user.films.remove(pk)

    UserFilms.objects.get(pk=pk).delete()

    # return the template fragment

    films = UserFilms.objects.filter(user=request.user).all()
    reorder(request.user)

    return render(request, 'partials/film-list.html', {'films': films})


def search_film(request):
    search_text = request.POST.get('search')

    user_films = UserFilms.objects.filter(user=request.user).all()
    # case insensitive ----> taxi driver == TAXI DRIVER
    results = Films.objects.filter(name__icontains=search_text).exclude(
        name__in=user_films.values_list('film__name', flat=True)
    )


    

    context = {'results': results}


    return render(request, 'partials/search-results.html', context)

def clear(request):
    return HttpResponse("")


def sort(request):
    film_pks_order = request.POST.getlist('film_order')
    films = []

    for idx, film_pk in enumerate(film_pks_order, start=1):
        userfilm = UserFilms.objects.get(pk=film_pk)
        userfilm.order = idx
        userfilm.save()
        films.append(userfilm)


    return render(request, 'partials/film-list.html', {'films': films})

@login_required
def detail(request, pk):
    userfilm = get_object_or_404(UserFilms, pk=pk)

    context = {'userfilm': userfilm}

    return render(request, 'partials/detail.html', context)


@login_required
def films_partial(request):
    films = UserFilms.objects.filter(user=request.user)

    return render(request, 'partials/film-list.html', {'films': films})



@login_required
def upload_image(request, pk):
    userfilm = get_object_or_404(UserFilms, pk=pk)

    image = request.FILES.get('image')
    userfilm.film.image.save(image.name, image)

    context = {'userfilm': userfilm}

    return render(request, 'partials/detail.html', context)