from rest_framework.pagination import PageNumberPagination


class MyPageNumberPagination(PageNumberPagination):
    """重写默认的分页类"""
    page_size = 2  # 默认每页显示2条
    page_query_param = 'page' # 第几页
    page_size_query_param = 'page_size'  # 每页显示多少条