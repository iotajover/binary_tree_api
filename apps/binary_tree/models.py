from django.db import models

# Create your models here.
class BinaryTree(models.Model):
    root = models.ForeignKey('BinaryTreeNode', on_delete=models.CASCADE)
    order = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.root.key) + ' - ' + str(self.root.level)

class BinaryTreeNode(models.Model):
    key = models.IntegerField()
    level = models.IntegerField()
    parent = models.ForeignKey('BinaryTreeNode', related_name='tree_node_parent', on_delete=models.CASCADE, blank=True, null=True)
    left = models.ForeignKey('BinaryTreeNode', related_name='tree_node_left', on_delete=models.CASCADE, blank=True, null=True)
    right = models.ForeignKey('BinaryTreeNode', related_name='tree_node_right', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.key) + ' - ' + str(self.level)