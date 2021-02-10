from django.urls import path, include

import poketrader.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", poketrader.views.index, name="index"),
    path("reset", poketrader.views.reset, name="reset"),
    path("remove", poketrader.views.remove, name="remove")
]
