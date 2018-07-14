from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    #默认返回2页
    page_size = 2
    page_size_query_param = 'page_size'
    #最大返回多少页
    max_page_size = 20