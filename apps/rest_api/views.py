from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from apps.binary_tree.models import BinaryTree, BinaryTreeNode

# Create your views here.
class CommonAncestor(APIView):
    def get(self, request, format=None):
        """Obtiene parámetros de la URL"""
        tree_id = self.request.query_params.get('treeID', None)
        first_node = self.request.query_params.get('firstNode', None)
        second_node = self.request.query_params.get('secondNode', None)

        """Valida que se hayan mandado todos los parámetros en el URL"""
        if first_node and second_node and tree_id:
            """Carga el árbol en la estructura de árbol Tree definida para procesamiento en memoria y valida que el ID de árbol exista"""
            binary_tree_instance = loadTree(tree_id)
            if binary_tree_instance:
                """Busca y valida que los dos valores de nodo pasados como parámetro existan en la estructura de árbol cargado en memoria"""
                first_tree_node_instance = findTreeNode(binary_tree_instance.getRoot(), first_node)
                second_tree_node_instance = findTreeNode(binary_tree_instance.getRoot(), second_node)
                if first_tree_node_instance and second_tree_node_instance:
                    """Busca y retorna el ancestro común más cercano"""
                    ancestor = findAncestor(first_tree_node_instance, second_tree_node_instance)
                    data = {'ancestor['+str(first_tree_node_instance.getKey())+','+str(second_tree_node_instance.getKey())+']': str(ancestor)}
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    data = {'error': 'Some of the nodes do not exist'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {'error': 'The tree ID does not exist'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {'error': 'Incomplete Parameters'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

def findAncestor(first_tree_node, second_tree_node):
    """Busca que los padres de los dos nodos estén al mismo nivel"""
    while int(first_tree_node.existParent().getLevel()) != int(second_tree_node.existParent().getLevel()):
        if int(first_tree_node.existParent().getLevel()) > int(second_tree_node.existParent().getLevel()):
            first_tree_node = first_tree_node.existParent()
        else:
            second_tree_node = second_tree_node.existParent()
    """Teniendo los nodos al mismo nivel se utiliza el recorrido de árboles por niveles para encontrar el nodo padre compun más cercano"""
    while int(first_tree_node.existParent().getKey()) != int(second_tree_node.existParent().getKey()):
        first_tree_node = first_tree_node.existParent()
        second_tree_node = second_tree_node.existParent()
    return first_tree_node.existParent().getKey()


def findTreeNode(tree_node, key_find):
    """Recorre el árbol en preorden recusrivamente para encontrar el nodo con el key que viene del request si lo encuentra retorna el nodo de lo contrario retorna None"""
    if int(tree_node.getKey()) == int(key_find):
        return tree_node
    else:
        if tree_node.existLeft():
            find = findTreeNode(tree_node.existLeft(), key_find)
            if find:
                return find
        if tree_node.existRight():
            find = findTreeNode(tree_node.existRight(), key_find)
            if find:
                return find

def loadTree(tree_id):
    """Carga en un objeto de tipo Tree en lìnea la estructura del àrbol que se encuentra persistido en la DB"""
    tree_model = BinaryTree.objects.filter(id=tree_id)
    if len(tree_model) == 1:
        binary_tree_instance = Tree(loadTreeNode(tree_model[0].root.id, None), tree_model[0].order, tree_model[0].height)
        return binary_tree_instance
    else:
        return None

def loadTreeNode(tree_node_id, tree_node_parent):
    """Se recorre en preorden la estrutura de nodos de àrbol almacenados en la DB para cargarlos en los objetos instanciados en memoria"""
    tree_node_model = BinaryTreeNode.objects.filter(id=tree_node_id)
    if len(tree_node_model) == 1:
        binary_tree_node_instance = TreeNode(tree_node_model[0].key, None, None, None, tree_node_model[0].level)
        if tree_node_parent:
            binary_tree_node_instance.setParent(tree_node_parent)
        if tree_node_model[0].left:
            binary_tree_node_instance.setLeft(loadTreeNode(tree_node_model[0].left.id, binary_tree_node_instance))
        if tree_node_model[0].right:
            binary_tree_node_instance.setRight(loadTreeNode(tree_node_model[0].right.id, binary_tree_node_instance))
        return binary_tree_node_instance
    else:
        return None

class BinaryTrees(APIView):
    def post(self, request, format=None):
        """Obtiene JSON y parsea a objeto diccionario el mensaje de request que viene en el body"""
        jsonReq = json.dumps(request.data)
        dictReq = json.loads(jsonReq)

        """Obtiene el parámetro del diccionario que contiene la estructura del árbol"""
        try:
            tree = dictReq['tree']
            if not tree:
                tree = None
        except:
            data = {'error': 'Incomplete parameters'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if tree:
            is_error = False
            error_descr = ''
            height = 0
            """Declaración arreglos de control de nodos creados"""
            tree_node_control = []
            tree_node_instances = []
            """Crea un array en donde cada posición es la representación de una rama de árbol"""
            nodes = tree.replace(' ', '').split(',')
            """Itera sobre cada rama del árbol"""
            for a in range(len(nodes)):
                if len(nodes)-1 > height:
                    height = len(nodes)-1
                """Por cada rama del árbol obtiene los nodos que la conforman incluyendo la raíz"""
                node = nodes[a].split('-')
                """Itera sobre cada nodo de cada rama del árbol"""
                for b in range(len(node)):
                    """Valida mediante la calave del nodo si este ya fue creado"""
                    try:
                        current_index = tree_node_control.index(node[b])
                    except:
                        current_index = -1
                    """Si el nodo no existe se crea y llenan los arreglos de control"""
                    if current_index == -1:
                        """Valida que el árbol no tenga más de un nodo raíz"""
                        if a > 0 and b == 0:
                            is_error = True
                            error_descr = 'There is more than one root node with different key'
                            break
                        tree_node = TreeNode(node[b], None, None, None, b)
                        tree_node_control.append(node[b])
                        tree_node_instances.append(tree_node)
                        """Crea arbol binario"""
                        if a == 0 and b == 0:
                            tree = Tree(tree_node, 2, None)
                        """Evalua si existe nodo padre para crear la relación de parentalidad en el objeto TreeNode"""
                        try:
                            parent_index = tree_node_control.index(node[b-1])
                        except:
                            parent_index = -1
                        if parent_index >= 0:
                            parent_tree_node = tree_node_instances[parent_index]
                            tree_node.setParent(parent_tree_node)
                            if node[b] < node[b-1]:
                                if parent_tree_node.existLeft():
                                    is_error = True
                                    error_descr = 'There is more than one left child node with the same parent node'
                                    break
                                else:
                                    parent_tree_node.setLeft(tree_node)
                            elif node[b] > node[b-1]:
                                if parent_tree_node.existRight():
                                    is_error = True
                                    error_descr = 'There is more than one right child node with the same parent node'
                                    break
                                else:
                                    parent_tree_node.setRight(tree_node)
                            else:
                                is_error = True
                                error_descr = 'There is more than one node with the same key'
                                break
                if is_error:
                    break
            if is_error:
                data = {'error': error_descr}
                return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                tree.setHeight(height)
                tree_id = saveTree(tree)
                data = {'binaryTreeID': str(tree_id)}
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {'error': 'Incomplete parameters'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

def saveTree(tree):
    """Guarda en la DB a travès del modelo BinaryTree definido la estructura del àrbol y retorna el id ùnico generado"""
    tree_model = BinaryTree(root=saveTreeNode(tree.getRoot(), None), order=tree.getOrder(), height=tree.getHeight())
    tree_model.save()
    return tree_model.id

def saveTreeNode(tree_node, tree_node_parent):
    """Se recorre en preorden la estructura en onde està cargado el àrbol en lìnea y se van descargando los nodos en la DB a travès del modelo BinaryTreeNode"""
    tree_node_model = BinaryTreeNode(key=tree_node.getKey(), level=tree_node.getLevel())
    tree_node_model.save()
    if tree_node_parent:
        tree_node_model.parent = tree_node_parent
    if tree_node.existLeft():
        tree_node_model.left = saveTreeNode(tree_node.existLeft(), tree_node_model)
    if tree_node.existRight():
        tree_node_model.right = saveTreeNode(tree_node.existRight(), tree_node_model)
    tree_node_model.save()
    return tree_node_model


class TreeNode:
    def __init__(self, key, left, right, parent, level):
        self.key = key
        self.left = left
        self.right = right
        self.parent = parent
        self.level = level

    def setParent(self, parent):
        self.parent = parent

    def setLeft(self, left):
        self.left = left

    def setRight(self, right):
        self.right = right

    def existParent(self):
        return self.parent

    def existLeft(self):
        return self.left

    def existRight(self):
        return self.right

    def getKey(self):
        return self.key

    def getLevel(self):
        return self.level

class Tree:
    def __init__(self, root, order, height):
        self.root = root
        self.order = order
        self.height = height

    def getRoot(self):
        return self.root

    def getOrder(self):
        return self.order

    def getHeight(self):
        return self.height

    def setHeight(self, height):
        self.height = height