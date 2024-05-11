class Node:
    def __init__(self, ID):
        self.ID = ID

    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"