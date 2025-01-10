from django_filters import rest_framework as filters

from .models import PartyRoom


class PartyRoomUidFilter(filters.FilterSet):
    class Meta:
        model = PartyRoom
        fields = ('uid',)


class PartyRoomFilter(filters.FilterSet):
    numOfPpl = filters.NumberFilter(method='people_range_filter')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    area = filters.CharFilter(field_name='area', lookup_expr='iexact')
    district = filters.CharFilter(field_name='district', lookup_expr="iexact")

    class Meta:
        model = PartyRoom
        fields = ('name',
                  'district',
                  'numOfPpl',
                  'area'
                  )

    def people_range_filter(self, queryset, name, value):
        return queryset.filter(**{
            'maxNumUsers__gte': value,
            'minNumUsers__lte': value
        })

    def area_filter(self, queryset, value):
        return queryset.filter(**{''})

