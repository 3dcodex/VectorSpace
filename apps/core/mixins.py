from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class PaginationMixin:
    """Mixin to add pagination to views"""
    paginate_by = 20
    
    def paginate_queryset(self, queryset, page):
        paginator = Paginator(queryset, self.paginate_by)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return items

class OwnerRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is the owner of the object"""
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user and not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
