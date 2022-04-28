# django-optimistic-admin-pg

This app provides a couple of mixins to implement [optimistic concurrency](https://en.wikipedia.org/wiki/Optimistic_concurrency_control) in the Django admin leveraging
PostgreSQL specific features.

PostgreSQL implements an MVCC concurrency model, that means that rows are duplicated on update.
PostgreSQL stores an id on each row to store the transaction identifier called *xmin*.

This application provides mixins for Django *ModelForm* and *ModelAdmin* using the *xmin* value
to inhibit the saving of data via the Django admin if it has been updated in the meantime.

## Notes on safety

Please note that this application does not remove completely the races between updates via the admin
interfaces but it narrows them by a lot.

## Similar Projects

[django-concurrency](https://github.com/saxix/django-concurrency) implements the same pattern with
 *batteries included* in a *database-independent* way.

## Requirements

The app is tested on Python 3.8+ with Django 3.2 and 4.0.

## Setup

```shell
python -m pip install django-optimistic-admin-pg
```

## How to use

This application provides a couple of mixins: one for *ModelAdmin* instances and one for *ModelForm*
instances.

First a *ModelForm* inheriting from *OptimisticAdminModelFormMixin* should be used as form the
 *ModelAdmin*.
A field called *row_version* should be added to this form in order to send the row version read
from the database.
Assuming you have forms in `forms.py`:

```python
from django import forms
from optimisticadmin.mixins import OptimisticAdminModelFormMixin

class MyModelForm(OptimisticAdminModelFormMixin, forms.ModelForm):
    row_version = forms.IntegerField(required=False, widget=forms.HiddenInput())
```

Then in `admin.py` your *ModelAdmin* need to inherit from *OptimisticAdminMixin* and use the form
 implemented before:

```python
from django.contrib import admin
from optimisticadmin.mixins import OptimisticAdminMixin
from .forms import MyModelForm

@admin.register(MyModel)
class MyModelAdmin(OptimisticAdminMixin, admin.ModelAdmin):
    form = MyModelForm
```


