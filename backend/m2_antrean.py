class Stack:
   
    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack kosong (Underflow)")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._data[-1]


class AntreanNaif:
    
    def __init__(self):
        self._data = []
        self.total_geser = 0

    def __len__(self):
        return len(self._data)

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if len(self._data) == 0:
            return None
        item = self._data.pop(0)
        geseran = len(self._data)
        self.total_geser += geseran
        return item, geseran


class AntreanMelingkar:
  
    def __init__(self, kapasitas=32768):
        self._kapasitas = kapasitas
        self._data = [None] * self._kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0

    def __len__(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self._kapasitas

    def enqueue(self, item):
        if self.is_full():
            self._gandakan_kapasitas()
        self._data[self.rear] = item
        self.rear = (self.rear + 1) % self._kapasitas
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            return None
        item = self._data[self.front]
        self._data[self.front] = None
        self.front = (self.front + 1) % self._kapasitas
        self.count -= 1
        return item, 0

    def _gandakan_kapasitas(self):
        kapasitas_baru = self._kapasitas * 2
        data_baru = [None] * kapasitas_baru
        for i in range(self.count):
            data_baru[i] = self._data[(self.front + i) % self._kapasitas]
        self._data = data_baru
        self.front = 0
        self.rear = self.count
        self._kapasitas = kapasitas_baru


def infix_ke_postfix(ekspresi):
    
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    stack = Stack()
    output = []
    
    tokens = []
    i = 0
    while i < len(ekspresi):
        kar = ekspresi[i]
        if kar.isspace():
            i += 1
            continue
        if kar.isdigit():
            num = ""
            while i < len(ekspresi) and ekspresi[i].isdigit():
                num += ekspresi[i]
                i += 1
            tokens.append(num)
            continue
        else:
            tokens.append(kar)
            i += 1

    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token == '(':
            stack.push(token)
        elif token == ')':
            while not stack.is_empty() and stack.peek() != '(':
                output.append(stack.pop())
            if not stack.is_empty() and stack.peek() == '(':
                stack.pop()
        elif token in precedence:
            while (not stack.is_empty() and stack.peek() in precedence and 
                   precedence[stack.peek()] >= precedence[token]):
                output.append(stack.pop())
            stack.push(token)

    while not stack.is_empty():
        output.append(stack.pop())

    return output


def evaluasi_postfix(postfix_tokens):
   
    stack = Stack()
    for token in postfix_tokens:
        if token.isdigit():
            stack.push(int(token))
        else:
            b = stack.pop()  
            a = stack.pop()  
            if token == '+':
                stack.push(a + b)
            elif token == '-':
                stack.push(a - b)
            elif token == '*':
                stack.push(a * b)
            elif token == '/':
                stack.push(a // b)
    return stack.pop() if not stack.is_empty() else 0