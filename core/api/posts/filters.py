import django_filters
from django.db.models import Q
from django_filters import CharFilter

from core.models import Post


class PostFilter(django_filters.FilterSet):
    q = CharFilter(method="search")
    author = django_filters.NumberFilter(field_name="id")

    class Meta:
        model = Post
        fields = ("author",)

    def search(self, queryset, _, value):
        query = Q(message__icontains=value)
        return queryset.filter(query).distinct()
