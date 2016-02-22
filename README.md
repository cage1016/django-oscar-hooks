# django-oscar-hooks

django-oscar have few build-in [signals](http://django-oscar.readthedocs.org/en/latest/ref/signals.html#signals) for internal use. Sometime we need to interact oscar data with external system (ERP or License Server etc.)

Basic idea is build a UI that stock-parter can register `place_order` signals to interact data with external system.

## Features

1. you should set `ONLY ONE` user for each parter (Book-parter, Clothes-parter).
2. parter can register a hooks with multiple (signals-type --> URL) rules.
3. hooks log dashboard support.

## Screenshots

![django-oscar-hooks list](https://raw.githubusercontent.com/cage1016/django-oscar-hooks/master/screenshots/1.png)

![django-oscar-hooks edit hook](https://raw.githubusercontent.com/cage1016/django-oscar-hooks/master/screenshots/2.png)

![django-oscar-hooks edit signals](https://raw.githubusercontent.com/cage1016/django-oscar-hooks/master/screenshots/3.png)

![django-oscar-hooks logs](https://raw.githubusercontent.com/cage1016/django-oscar-hooks/master/screenshots/4.png)

## Installation

install using pip (have not published)

```sh
pip install django-oscar-hooks
```

install using github

```sh
pip install -e git+git@github.com:cage1016/django-oscar-hooks.git#egg=django-oscar-hooks
```

modify your `settings.py` and `urls.py`

__setting.py__

```python
# ...

INSTALLED_APPS =[
  ...
  'django_q',
  'hooks'
  ]

# ...

########## HOOK CONFIGRATION
from django.utils.translation import ugettext_lazy as _
OSCAR_DASHBOARD_NAVIGATION.append(
        {
          'label': _('Hooks'),
          'icon': 'icon-info',
          'children': [
            {
              'label': 'Hooks',
              'url_name': 'hook-list',
            },
            {
              'label': 'Hooks Types',
              'url_name': 'hook-class-list',
            },
            {
              'label': 'Hooks Logs',
              'url_name': 'hook-logs',
            }
          ]
        })


# redis defaults
Q_CLUSTER = {
    'redis': {
        'host': 'dockerhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'socket_timeout': None,
        'charset': 'utf-8',
        'errors': 'strict',
        'unix_socket_path': None
    }
}
########## END HOOK CONFIGRATION
```

add hooks dashboard to url-pattern

__urls.py__


```python
from hooks.dashboard.app import application as hooks_dashboard

# ...

urlpatterns = [
    ...
    url(r'^dashboard/hooks/', include(hooks_dashboard.urls)),
]
```

Running migrate to create `django_q` and `hooks` appropriate database tables and initial data.

```sh
$ manage.py migrate
```
