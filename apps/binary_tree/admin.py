from django.contrib import admin
from apps.binary_tree.models import BinaryTree, BinaryTreeNode

# Register your models here.
admin.site.register(BinaryTree)
admin.site.register(BinaryTreeNode)