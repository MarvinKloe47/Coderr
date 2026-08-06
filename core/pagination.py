from rest_framework.pagination import PageNumberPagination


class PageSizePagination(PageNumberPagination):
    """Allow offer list clients to request a documented page size.

    The project-wide REST framework settings keep the default page size at six;
    this class only exposes the page_size query parameter.
    """

    page_size_query_param = "page_size"
