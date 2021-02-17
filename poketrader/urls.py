from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

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
    path(
        "comparison/", poketrader.views.comparison,
        kwargs={'comparison_id': None}, name="comparison_new"),
    path(
        "comparison/<int:comparison_id>", poketrader.views.comparison,
        name="comparison"),
    path("reset/<int:comparison_id>", poketrader.views.reset, name="reset"),
    path("remove/<int:comparison_id>", poketrader.views.remove, name="remove"),
    path("delete/<int:comparison_id>", poketrader.views.delete, name="delete"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls)
]
