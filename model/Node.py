class Node:
    def __init__(self, id, label=None):
        self.id = id
        self.label = label

    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"
