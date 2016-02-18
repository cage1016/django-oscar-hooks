from django.views import generic
from django_tables2 import SingleTableMixin
from django.core.urlresolvers import reverse

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Q

from oscar.core.loading import get_classes, get_model
from oscar.views.generic import ObjectLookupView

[HookForm, HookEventFormSet, ProductClassSelectForm] \
    = get_classes(
        'hooks.dashboard.forms', [
            'HookForm',
            'HookEventFormSet',
            'ProductClassSelectForm'
        ])

[HookTable, HookLogTable] = get_classes('hooks.dashboard.tables', ['HookTable', 'HookLogTable'])

ProductClass = get_model('catalogue', 'ProductClass')

Hook = get_model('hooks', 'Hook')
HookLog = get_model('hooks', 'HookLog')
HookSingalType = get_model('hooks', 'HookSignalType')


def filter_hooks(queryset, user):
    """
    Restrict the queryset to hooks the given user has access to.
    A staff user is allowed to access all hooks.
    A non-staff user is only allowed access to a hook if they are in at
    least one stock record's partner user list.
    """
    if user.is_staff:
        return queryset

    return queryset.filter(user=user).distinct()


def filter_hook_logs(queryset, user):
    if user.is_staff:
        return queryset

    return queryset.filter(hook_event__hook__user_id=user.pk).distinct()


class HookListView(SingleTableMixin, generic.TemplateView):
    """
      Dashboard view of the hook list.
      Supports the permission-based dashboard.
    """

    template_name = 'hooks/dashboard/hook_list.html'
    productclass_form_class = ProductClassSelectForm

    table_class = HookTable
    context_table_name = 'hooks'

    def get_context_data(self, **kwargs):
        ctx = super(HookListView, self).get_context_data(**kwargs)
        # ctx['form'] = self.form
        ctx['productclass_form_class'] = self.productclass_form_class()
        return ctx

    def get_table(self, **kwargs):
        if 'recently_edited' in self.request.GET:
            kwargs.update(dict(orderable=False))

        table = super(HookListView, self).get_table(**kwargs)
        return table

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_form_kwargs(self):
        kwargs = super(HookListView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        """
        Build the queryset for this list
        """
        queryset = Hook.objects.all()
        queryset = filter_hooks(queryset, self.request.user)
        # queryset = queryset.annotate(Count('hookevent'))
        return queryset


class HookDeleteView(generic.DeleteView):
    template_name = 'hooks/dashboard/hook_delete.html'
    model = Hook
    context_object_name = 'hook'

    def get_queryset(self):
        """
        Filter products that the user doesn't have permission to update
        """
        q = Hook.objects.all()
        q = filter_hooks(q, self.request.user)
        return q

    def get_context_data(self, **kwargs):
        ctx = super(HookDeleteView, self).get_context_data(**kwargs)
        ctx['title'] = _("Delete hook?")
        return ctx

    def delete(self, request, *args, **kwargs):
        # We override the core delete method and don't call super in order to
        # apply more sophisticated logic around handling child products.
        # Calling super makes it difficult to test if the product being deleted
        # is the last child.

        self.object = self.get_object()

        # This also deletes any child products.
        self.object.delete()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        When deleting child products, this view redirects to editing the
        parent product. When deleting any other product, it redirects to the
        product list view.
        """
        msg = _("Deleted hook '%s'") % self.object.name
        messages.success(self.request, msg)
        return reverse('hook-list')


class HookCreateUpdateView(generic.UpdateView):
    template_name = 'hooks/dashboard/hook_update.html'
    model = Hook
    context_object_name = 'hook'

    form_class = HookForm
    hookevent_formset = HookEventFormSet

    def __init__(self, *args, **kwargs):
        super(HookCreateUpdateView, self).__init__(**kwargs)
        self.formsets = {
            'hookevent_formset': self.hookevent_formset,
        }

    def get_queryset(self):
        """
        Filter products that the user doesn't have permission to update
        """
        return filter_hooks(Hook.objects.all(), self.request.user)

    def get_object(self, queryset=None):
        """
        This parts allows generic.UpdateView to handle creating products as
        well. The only distinction between an UpdateView and a CreateView
        is that self.object is None. We emulate this behavior.

        This method is also responsible for setting self.product_class and
        self.parent.
        """
        self.creating = 'pk' not in self.kwargs
        if self.creating:
            hook_class_slug = self.kwargs.get('hook_class_slug')
            self.product_class = get_object_or_404(ProductClass, slug=hook_class_slug)
            return None  # success

        else:
            hook = super(HookCreateUpdateView, self).get_object(queryset)
            self.product_class = hook.get_product_class()
            return hook

    def get_context_data(self, *args, **kwargs):
        ctx = super(HookCreateUpdateView, self).get_context_data(**kwargs)
        ctx['product_class'] = self.product_class
        ctx["title"] = self.get_title()

        for ctx_name, formset_class in self.formsets.items():
            if ctx_name not in ctx:
                ctx[ctx_name] = formset_class(self.product_class,
                                              self.request.user,
                                              instance=self.object)

        return ctx

    def get_title(self):
        if self.creating:
            return _('Create new %(product_class)s hook') % {'product_class': self.product_class.name}

        else:
            return self.object.name

    def get_form_kwargs(self):
        kwargs = super(HookCreateUpdateView, self).get_form_kwargs()
        kwargs['product_class'] = self.product_class
        kwargs['user'] = self.request.user
        return kwargs

    def process_all_forms(self, form):
        if self.creating and form.is_valid():
            self.object = form.save()
            self.object.user = self.request.user

        formsets = {}
        for ctx_name, formset_class in self.formsets.items():
            formsets[ctx_name] = formset_class(self.product_class,
                                               self.request.user,
                                               self.request.POST,
                                               self.request.FILES,
                                               instance=self.object)

        is_valid = form.is_valid() and all([formset.is_valid() for formset in formsets.values()])

        cross_form_validation_result = self.clean(form, formsets)
        if is_valid and cross_form_validation_result:
            return self.forms_valid(form, formsets)
        else:
            return self.forms_invalid(form, formsets)

    form_valid = form_invalid = process_all_forms

    def clean(self, form, formsets):
        """
        Perform any cross-form/formset validation. If there are errors, attach
        errors to a form or a form field so that they are displayed to the user
        and return False. If everything is valid, return True. This method will
        be called regardless of whether the individual forms are valid.
        """
        return True

    def forms_valid(self, form, formsets):
        """
        Save all changes and display a success url.
        When creating the first child product, this method also sets the new
        parent's structure accordingly.
        """
        # a just created product was already saved in process_all_forms()
        self.object = form.save()

        # Save formsets
        for formset in formsets.values():
            formset.save()

        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, formsets):
        # delete the temporary product again
        if self.creating and self.object and self.object.pk is not None:
            self.object.delete()
            self.object = None

        messages.error(self.request,
                       _("Your submitted data was not valid - please "
                         "correct the errors below"))
        ctx = self.get_context_data(form=form, **formsets)
        return self.render_to_response(ctx)

    def get_url_with_querystring(self, url):
        url_parts = [url]
        if self.request.GET.urlencode():
            url_parts += [self.request.GET.urlencode()]

        return "?".join(url_parts)

    def get_success_url(self):
        """
        Renders a success message and redirects depending on the button:
        - Standard case is pressing "Save"; redirects to the product list
        - When "Save and continue" is pressed, we stay on the same page
        - When "Create (another) child product" is pressed, it redirects
          to a new product creation page
        """

        msg = render_to_string(
                'dashboard/catalogue/messages/product_saved.html',
                {
                    'product': self.object,
                    'creating': self.creating,
                    'request': self.request
                })
        messages.success(self.request, msg, extra_tags="safe noicon")

        action = self.request.POST.get('action')
        if action == 'continue':
            url = reverse('hook', kwargs={"pk": self.object.id})
        else:
            url = reverse('hook-list')
        return self.get_url_with_querystring(url)


class HookCreateRedirectView(generic.RedirectView):
    permanent = False
    productclass_form_class = ProductClassSelectForm

    def get_product_create_url(self, product_class):
        """ Allow site to provide custom URL """
        return reverse('hook-create',
                       kwargs={'hook_class_slug': product_class.slug})

    def get_invalid_product_class_url(self):
        messages.error(self.request, _("Please choose a hook type"))
        return reverse('hook-list')

    def get_redirect_url(self, **kwargs):
        form = self.productclass_form_class(self.request.GET)
        if form.is_valid():
            product_class = form.cleaned_data['product_class']
            return self.get_product_create_url(product_class)

        else:
            return self.get_invalid_product_class_url()


class HookLogsView(SingleTableMixin, generic.TemplateView):
    template_name = 'hooks/dashboard/hook_log.html'
    table_class = HookLogTable
    context_table_name = 'hooklogs'

    def get_context_data(self, **kwargs):
        ctx = super(HookLogsView, self).get_context_data(**kwargs)
        return ctx

    def get_table(self, **kwargs):
        table = super(HookLogsView, self).get_table(**kwargs)
        return table

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        """
        Build the queryset for this list
        """
        queryset = HookLog.objects.all()
        return filter_hook_logs(queryset, self.request.user)


class SingalTypeLookupView(ObjectLookupView):
    model = HookSingalType

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.model.objects.all()

        return self.model.objects.exclude(name="user_registered")

    def lookup_filter(self, qs, term):
        return qs.filter(Q(name__icontains=term))
