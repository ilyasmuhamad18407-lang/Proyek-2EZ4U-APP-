# backend/m1_pesanan.py

class Array:
    def __init__(self, capacity=4):
        self.capacity = capacity
        self.size = 0 
        self.data = [None] * self.capacity

    def _resize(self):
        new_capacity = self.capacity * 2
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def get(self, i):
        if 0 <= i < self.size:
            return self.data[i]
        return None

    def tambah_reguler(self, v):
        if self.size == self.capacity:
            self._resize()
        self.data[self.size] = v
        self.size += 1

    def tambah_prioritas(self, v):
        if self.size == self.capacity:
            self._resize()
        
        tengah = self.size // 2
        

        for i in range(self.size, tengah, -1):
            self.data[i] = self.data[i-1]
            
        self.data[tengah] = v
        self.size += 1

    def tambah_vip(self, v):
        if self.size == self.capacity:
            self._resize()
            
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i-1]
            
        self.data[0] = v
        self.size += 1

    def hapus(self, i):
        if 0 <= i < self.size:
            deleted_val = self.data[i]
            for j in range(i, self.size - 1):
                self.data[j] = self.data[j+1]
            self.data[self.size - 1] = None
            self.size -= 1
            return deleted_val
        return None


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get(self, i):
        if i < 0 or i >= self.size:
            return None
        current = self.head
        for _ in range(i):
            current = current.next
        return current.value

    def tambah_reguler(self, v):
        new_node = Node(v)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def tambah_prioritas(self, v):
        if self.size == 0:
            self.tambah_reguler(v)
            return
            
        new_node = Node(v)
        tengah = self.size // 2
        
        if tengah == 0:
            self.tambah_vip(v)
            return
            
        current = self.head
        for _ in range(tengah - 1):
            current = current.next
            
        new_node.next = current.next
        current.next = new_node
        self.size += 1

    def tambah_vip(self, v):
        new_node = Node(v)
        new_node.next = self.head
        self.head = new_node
        if self.size == 0:
            self.tail = new_node
        self.size += 1

    def hapus(self, i):
        if i < 0 or i >= self.size:
            return None
            
        if i == 0:
            deleted_val = self.head.value
            self.head = self.head.next
            if self.size == 1:
                self.tail = None
            self.size -= 1
            return deleted_val
            
        current = self.head
        for _ in range(i - 1):
            current = current.next
            
        deleted_val = current.next.value
        current.next = current.next.next
        
        if i == self.size - 1:
            self.tail = current
            
        self.size -= 1
        return deleted_val