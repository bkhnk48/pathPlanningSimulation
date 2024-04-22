class Node:
    def __init__(self, id, label=None):
        self.id = id
        self.label = label

    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"

class ArtificialNode(Node):
    def __init__(self, id, label=None, temporary=False):
        super().__init__(id, label)
        self.temporary = temporary  # Indicates whether the node is temporary

    def __repr__(self):
        return f"ArtificialNode(id={self.id}, label='{self.label}', temporary={self.temporary})"