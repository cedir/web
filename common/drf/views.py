from rest_framework import viewsets
from rest_framework import permissions, authentication
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CajaPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

#class CedirViewSet(viewsets.ModelViewSet):
#    permission_classes = (permissions.IsAdminUser,)
#    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication,)
#    pass

