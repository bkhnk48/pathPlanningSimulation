from .Node import Node

class ArtificialNode(Node):
    def __init__(self, id, label=None, temporary=False):
        super().__init__(id, label)
        self.temporary = temporary  # Indicates whether the node is temporary

    def __repr__(self):
        return f"ArtificialNode(id={self.id}, label='{self.label}', temporary={self.temporary})"