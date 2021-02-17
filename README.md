<img src="https://raw.githubusercontent.com/brandizzi/poketrader/main/poketrader/static/pokemon-logo.jpg" alt="Pokémon logo" width=200>

# PokeTrader: the peace of mind of knowing your Pokémon deal is fair

How do you know if it is fair to exchange two sets of Pokémons? Worry no more,
this web app will do it for you!

## How to use

Go to [the web app](https://hidden-reef-42234.herokuapp.com/) and use it! We
hope it is self-explanatory!

## Possible improvements

There were more time, those would be some improvements I would like to
implement:

* a type-ahead/autocomplete feature for the pokémon names; * user
authentication;

* Importing all pokemons at once;

* [caching with Memcache](https://devcenter.heroku.com/articles/django-memcache).

Some of those can be found at the
[issues](https://github.com/brandizzi/poketrader/issues).

It would probably be instructive/fun to implement the interface as a
single-page application.

## Development

### Running Locally

Make sure you have Python 3.7 [installed
locally](http://install.python-guide.org). To push to Heroku, you'll need to
install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), as
well as
[Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh

$ git clone https://github.com/brandizzi/poketrader.git $ cd poketrader
$ python3 -m venv getting-started
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py collectstatic
$ python manage.py runserver

```

You can use `heroku local` instead of `python manage.py runserver`, too.

Your app should now be running on [localhost:8000](http://localhost:8000/).

### Deploying to Heroku

```sh
$ heroku create
$ git push heroku main

$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Acknowledgements

* This application was build upon the [reference Django application from
Heroku](https://github.com/heroku/python-getting-started). I squashed their
older commits to make everything more readable for the evaluators, but they are
great and I really want to acknoledge the use of their code. If you are going
to work with Django at Heroku, this repository as well as [this
page](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true#set-up)
are great references.

* This project is part of the recruitment process at
[bxblue](https://bxblue.com.br/). They are an amazing company, as one can infer
from such a fun challenge! Take a look at [their open
positions](https://bxblue.com.br/vagas). You'll probably need to know Brazilian
Portuguese, though.
