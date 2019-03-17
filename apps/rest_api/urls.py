from django.conf.urls import url
from apps.rest_api.views import CommonAncestor, BinaryTrees

urlpatterns = [
    url(r'^common-ancestors$', CommonAncestor.as_view(), name='CommonAncestors'),
    url(r'^binary-tree$', BinaryTrees.as_view(), name='BinaryTree'),
]