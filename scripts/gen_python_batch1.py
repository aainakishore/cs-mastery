#!/usr/bin/env python3
"""
Python Topics — Batch 1
Topics: python-oop, python-error-handling
Unit 12 (Python), orders 116–117
Run: python3 scripts/gen_python_batch1.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/languages"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "python-oop",
        "unit": 12,
        "order": 116,
        "title": "Python OOP",
        "summary": "Master classes, inheritance, dunder methods, and Pythonic object design.",
        "prereqs": ["python-fundamentals"],
        "guide": """# Python OOP — Think in Objects, Not Scripts

## Mental Model
A class is a blueprint — a cookie-cutter shape. An instance is the actual cookie.
Python doesn't enforce privacy; it trusts the programmer. That's why you'll see `_private` (convention) not a hard wall.

## Core Concepts

### Class Anatomy
```python
class Animal:
    species = "Unknown"          # class attribute — shared by all instances

    def __init__(self, name: str, sound: str):
        self.name = name         # instance attribute — unique per object
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

    def __repr__(self) -> str:   # unambiguous string for debugging
        return f"Animal(name={self.name!r})"

    def __str__(self) -> str:    # human-readable string
        return self.name

dog = Animal("Rex", "woof")
print(dog)        # Rex          ← __str__
print(repr(dog))  # Animal(name='Rex')  ← __repr__
```

## Inheritance
```
        Animal
       /      \\
    Dog        Cat
     |
  GoldenRetriever
```
```python
class Dog(Animal):
    def __init__(self, name: str):
        super().__init__(name, "woof")   # ALWAYS call super().__init__
        self.tricks: list[str] = []

    def learn(self, trick: str) -> None:
        self.tricks.append(trick)

    def speak(self) -> str:              # override
        return f"{self.name} barks loudly!"
```

### MRO — Method Resolution Order
```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass   # Diamond problem

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
# Python uses C3 linearization — left-to-right, depth-first, no repeats
```

## Dunder (Magic) Methods Cheatsheet
| Dunder | Triggered by |
|--------|-------------|
| `__init__` | `Dog(name)` |
| `__str__` | `str(obj)`, `print(obj)` |
| `__repr__` | `repr(obj)`, REPL |
| `__len__` | `len(obj)` |
| `__eq__` | `obj1 == obj2` |
| `__lt__` | `obj1 < obj2` (enables sorting) |
| `__add__` | `obj1 + obj2` |
| `__getitem__` | `obj[key]` |
| `__iter__` | `for x in obj` |
| `__enter__/__exit__` | `with obj:` |

## Properties — Controlled Attribute Access
```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius          # _underscore = "please don't touch directly"

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:       # computed property, no setter
        return self._celsius * 9/5 + 32

t = Temperature(100)
print(t.fahrenheit)   # 212.0
t.celsius = -300      # raises ValueError
```

## Class Methods vs Static Methods
```python
class Pizza:
    tax_rate = 0.08

    def __init__(self, toppings: list[str], price: float):
        self.toppings = toppings
        self.price = price

    @classmethod
    def margherita(cls) -> "Pizza":          # factory — knows about the class
        return cls(["tomato", "mozzarella"], 10.0)

    @staticmethod
    def is_vegetarian(toppings: list[str]) -> bool:   # utility — no self, no cls
        return "pepperoni" not in toppings

p = Pizza.margherita()
print(Pizza.is_vegetarian(["tomato"]))  # True
```

**Rule:** Use `@classmethod` for alternative constructors. Use `@staticmethod` for pure helpers that happen to live in the class namespace.

## Dataclasses — Less Boilerplate
```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)   # frozen = immutable, order = auto __lt__ etc
class Point:
    x: float
    y: float
    label: str = field(default="", compare=False)  # exclude from eq/order

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
print(p1 == p2)   # True  — auto __eq__
```

## Common Pitfalls
- **Mutable default argument in `__init__`**: `def __init__(self, items=[])` — all instances share the SAME list. Fix: `def __init__(self, items=None): self.items = items or []`
- **Forgetting `super().__init__()`** in multi-inheritance → parent state never set up
- **Shadowing built-ins**: `class list` or attribute `id` shadows Python's built-ins
- **`__eq__` without `__hash__`**: if you define `__eq__`, Python sets `__hash__ = None`, breaking use in sets/dicts. Fix: also define `__hash__` or use `@dataclass(unsafe_hash=True)`

## Connections
- `python-fundamentals` → base syntax you need before OOP
- `ts-interfaces-types` → compare structural typing (TypeScript) vs nominal (Java) vs duck typing (Python)
- `dsa-java-binary-trees` → tree node classes are pure OOP in any language
""",
        "questions": [
            {"id": "pyoop-q1", "type": "mcq", "prompt": "What is the first parameter of every instance method in Python?", "choices": ["this", "self", "cls", "instance"], "answerIndex": 1, "explanation": "`self` refers to the instance. It's a convention, not a keyword — but everyone uses it.", "tags": ["oop", "methods"]},
            {"id": "pyoop-q2", "type": "mcq", "prompt": "Which dunder method is called when you do `len(obj)`?", "choices": ["__size__", "__count__", "__len__", "__length__"], "answerIndex": 2, "explanation": "`__len__` is the standard hook. Implement it to make your class work with `len()`.", "tags": ["dunder", "protocols"]},
            {"id": "pyoop-q3", "type": "mcq", "prompt": "What does `@classmethod` receive as its first argument?", "choices": ["self", "The class (cls)", "None", "The module"], "answerIndex": 1, "explanation": "`cls` receives the class itself, not an instance. This lets factory methods create instances via `cls(...)` which works correctly with subclasses.", "tags": ["classmethod", "methods"]},
            {"id": "pyoop-q4", "type": "codeOutput", "prompt": "What does this print?", "code": "class A:\n    x = 1\nclass B(A):\n    pass\nB.x = 2\nprint(A.x, B.x)", "choices": ["1 1", "2 2", "1 2", "2 1"], "answerIndex": 2, "explanation": "Setting `B.x` creates a new class attribute on B without touching A. A.x stays 1.", "tags": ["inheritance", "class-attributes"]},
            {"id": "pyoop-q5", "type": "mcq", "prompt": "What is the purpose of `__repr__`?", "choices": ["Format for logging files", "Unambiguous string for debugging/REPL", "Convert to bytes", "Create a copy"], "answerIndex": 1, "explanation": "`__repr__` should return a string that ideally could recreate the object. It's shown in the REPL and used when `__str__` is not defined.", "tags": ["dunder", "debugging"]},
            {"id": "pyoop-q6", "type": "multi", "prompt": "Which are valid ways to call a classmethod `Pizza.margherita`?", "choices": ["Pizza.margherita()", "pizza_instance.margherita()", "margherita(Pizza)", "Pizza.margherita(Pizza)"], "answerIndexes": [0, 1], "explanation": "Both the class and an instance can call a classmethod — `cls` is injected automatically in both cases. The third/fourth forms are wrong syntax.", "tags": ["classmethod"]},
            {"id": "pyoop-q7", "type": "codeOutput", "prompt": "What prints?", "code": "class Counter:\n    count = 0\n    def __init__(self):\n        Counter.count += 1\n\na = Counter()\nb = Counter()\nprint(Counter.count)", "choices": ["0", "1", "2", "Error"], "answerIndex": 2, "explanation": "Each `__init__` increments the shared class attribute. Two instances → count = 2.", "tags": ["class-attributes", "oop"]},
            {"id": "pyoop-q8", "type": "mcq", "prompt": "What does `@property` enable?", "choices": ["Makes attribute read-only permanently", "Lets you call a method like an attribute with optional setter logic", "Caches the return value", "Creates a class attribute"], "answerIndex": 1, "explanation": "`@property` turns a method into an attribute-style access. Add `@x.setter` to allow writes with validation.", "tags": ["property", "encapsulation"]},
            {"id": "pyoop-q9", "type": "mcq", "prompt": "You define `__eq__` on a class. What happens to `__hash__` by default?", "choices": ["It uses id() as before", "It's set to None (class becomes unhashable)", "It's derived from __eq__", "Nothing changes"], "answerIndex": 1, "explanation": "Python resets `__hash__ = None` when you define `__eq__` to prevent inconsistent hashing. You must define `__hash__` manually if you need the class in a set/dict.", "tags": ["dunder", "hashing"]},
            {"id": "pyoop-q10", "type": "mcq", "prompt": "What is Python's Method Resolution Order (MRO) algorithm?", "choices": ["Depth-first search", "Breadth-first search", "C3 linearization", "Right-to-left parent order"], "answerIndex": 2, "explanation": "C3 linearization ensures consistent, predictable MRO in diamond inheritance. Left-to-right, no duplicates, respects local precedence.", "tags": ["inheritance", "mro"]},
            {"id": "pyoop-q11", "type": "codeOutput", "prompt": "What does this print?", "code": "class Dog:\n    def __init__(self, name):\n        self.name = name\n    def __str__(self):\n        return self.name\n    def __repr__(self):\n        return f'Dog({self.name!r})'\n\nd = Dog('Rex')\nprint(str(d))\nprint(repr(d))", "choices": ["Rex\\nRex", "Rex\\nDog('Rex')", "Dog('Rex')\\nDog('Rex')", "Error"], "answerIndex": 1, "explanation": "`str()` calls `__str__` → 'Rex'. `repr()` calls `__repr__` → \"Dog('Rex')\".", "tags": ["dunder", "str"]},
            {"id": "pyoop-q12", "type": "mcq", "prompt": "What is wrong with: `def __init__(self, items=[])`?", "choices": ["Lists are not allowed as defaults", "The default list is shared across all instances", "It should be items=()", "Nothing is wrong"], "answerIndex": 1, "explanation": "Default mutable arguments are evaluated ONCE at function definition. All instances share the same list object. Use `items=None` then `self.items = items if items is not None else []`.", "tags": ["pitfalls", "mutability"]},
            {"id": "pyoop-q13", "type": "mcq", "prompt": "When should you use `@staticmethod` vs `@classmethod`?", "choices": ["They are interchangeable", "staticmethod when you need cls; classmethod when you don't", "staticmethod for utilities with no class/instance needed; classmethod for factories", "staticmethod only in abstract classes"], "answerIndex": 2, "explanation": "Use `@staticmethod` for pure utility functions that happen to live in the class. Use `@classmethod` when you need access to the class itself (e.g., alternative constructors).", "tags": ["classmethod", "staticmethod"]},
            {"id": "pyoop-q14", "type": "mcq", "prompt": "What does `frozen=True` in `@dataclass` do?", "choices": ["Prevents subclassing", "Makes instances immutable (no attribute assignment after init)", "Freezes class-level attributes", "Enables pickling"], "answerIndex": 1, "explanation": "Frozen dataclasses raise `FrozenInstanceError` on attribute assignment. They also become hashable automatically.", "tags": ["dataclass", "immutability"]},
            {"id": "pyoop-q15", "type": "codeOutput", "prompt": "What prints?", "code": "class Vehicle:\n    def start(self):\n        return 'vroom'\n\nclass Car(Vehicle):\n    def start(self):\n        return super().start() + '!'\n\nprint(Car().start())", "choices": ["vroom", "vroom!", "!", "Error"], "answerIndex": 1, "explanation": "`super().start()` calls `Vehicle.start()` returning 'vroom', then '!' is appended → 'vroom!'.", "tags": ["inheritance", "super"]},
            {"id": "pyoop-q16", "type": "multi", "prompt": "Which dunder methods does `@dataclass` auto-generate by default?", "choices": ["__init__", "__repr__", "__eq__", "__hash__", "__lt__"], "answerIndexes": [0, 1, 2], "explanation": "By default: `__init__`, `__repr__`, `__eq__`. `__hash__` and ordering methods (`__lt__` etc.) require `frozen=True` or `order=True`.", "tags": ["dataclass", "dunder"]},
            {"id": "pyoop-q17", "type": "mcq", "prompt": "What is duck typing in Python?", "choices": ["All objects inherit from Duck", "Type checks happen at compile time", "If an object has the required methods/attributes, it's usable regardless of its type", "Type annotations are mandatory"], "answerIndex": 2, "explanation": "If it walks like a duck and quacks like a duck, it's a duck. Python checks method existence at call time, not type identity.", "tags": ["duck-typing", "protocols"]},
            {"id": "pyoop-q18", "type": "mcq", "prompt": "The `__enter__` and `__exit__` methods enable:", "choices": ["Iteration protocol", "Context manager protocol (with statement)", "Comparison operators", "Arithmetic operators"], "answerIndex": 1, "explanation": "Implementing `__enter__` and `__exit__` lets your class be used with `with obj as x:` — ideal for resource management (files, DB connections, locks).", "tags": ["dunder", "context-manager"]},
            {"id": "pyoop-q19", "type": "codeOutput", "prompt": "What prints?", "code": "class A:\n    def method(self):\n        return 'A'\nclass B(A):\n    def method(self):\n        return 'B'\nclass C(A):\n    def method(self):\n        return 'C'\nclass D(B, C):\n    pass\nprint(D().method())", "choices": ["A", "B", "C", "Error"], "answerIndex": 1, "explanation": "MRO for D is D → B → C → A. B is checked first, so `B.method` is called → 'B'.", "tags": ["mro", "inheritance"]},
            {"id": "pyoop-q20", "type": "mcq", "prompt": "What is the difference between a class attribute and an instance attribute?", "choices": ["No difference in Python", "Class attributes are constants; instance attributes are variables", "Class attributes are shared across all instances; instance attributes are unique per instance", "Instance attributes must be defined in __init__; class attributes anywhere"], "answerIndex": 2, "explanation": "Class attributes live on the class object itself and are shared. Instance attributes live on the specific instance (set via `self.attr = ...`).", "tags": ["attributes", "oop"]},
        ],
        "flashcards": [
            {"id": "pyoop-fc1", "front": "self vs cls", "back": "`self` = the instance (used in regular methods). `cls` = the class itself (used in @classmethod). Neither is a keyword — just strong convention.", "tags": ["oop"]},
            {"id": "pyoop-fc2", "front": "When to use @property", "back": "Use when you want attribute-style access (`obj.price`) but need logic (validation, computation) on get/set. Avoids `get_price()` / `set_price()` boilerplate.", "tags": ["property"]},
            {"id": "pyoop-fc3", "front": "Mutable default argument trap", "back": "Never use mutable defaults: `def f(x=[])`. The list is created once and shared. Use `x=None` then `x = x or []` inside the function.", "tags": ["pitfalls"]},
            {"id": "pyoop-fc4", "front": "__repr__ vs __str__", "back": "`__repr__`: unambiguous, for developers, shown in REPL. `__str__`: human-readable, for users, used by print(). If only one defined, `__repr__` is used as fallback.", "tags": ["dunder"]},
            {"id": "pyoop-fc5", "front": "super() in Python", "back": "`super()` returns a proxy to the next class in MRO. Always call `super().__init__()` in subclasses to ensure parent state is initialised.", "tags": ["inheritance"]},
            {"id": "pyoop-fc6", "front": "@dataclass saves you writing", "back": "`__init__`, `__repr__`, `__eq__` automatically. Add `order=True` for comparisons, `frozen=True` for immutability + auto hashability.", "tags": ["dataclass"]},
            {"id": "pyoop-fc7", "front": "Duck typing rule", "back": "Python checks for methods at call time, not types at definition. If `obj.fly()` exists, you can call it — regardless of `obj`'s class. Enables flexible APIs.", "tags": ["duck-typing"]},
            {"id": "pyoop-fc8", "front": "__hash__ after __eq__", "back": "Defining `__eq__` sets `__hash__ = None`. You must also define `__hash__` if you want instances in sets or as dict keys. `@dataclass(frozen=True)` handles this automatically.", "tags": ["dunder", "hashing"]},
        ],
        "project": {
            "brief": "Design a small in-memory task management system using Python OOP. You have `Task` objects with title, priority (low/medium/high), status (todo/in-progress/done), and due date. Tasks belong to `Project` objects. A `TaskManager` singleton orchestrates all projects. Design the class hierarchy — no code execution needed, just think through the design decisions: Which attributes go on which class? What dunder methods add value? Should `Task` be a dataclass? How do you sort tasks by priority? What validations belong in setters? Write brief notes for each decision.",
            "checklist": [
                {"id": "pyoop-p1", "text": "Define `Task` with appropriate attributes; justify dataclass vs plain class", "weight": 20},
                {"id": "pyoop-p2", "text": "Identify which dunder methods (`__lt__`, `__eq__`, `__repr__`) to implement and why", "weight": 20},
                {"id": "pyoop-p3", "text": "Design `Project` class with methods to add/filter/sort tasks", "weight": 20},
                {"id": "pyoop-p4", "text": "Explain where validation logic lives (setter vs `__init__` vs classmethod factory)", "weight": 20},
                {"id": "pyoop-p5", "text": "Describe the `TaskManager` design — singleton pattern, class attributes, interface", "weight": 20},
            ],
            "hints": [
                "For Task, consider `@dataclass(order=True)` — add a sort_index field that maps priority to a number.",
                "Use `@property` with a setter on `status` to validate transitions (can't go from done → todo).",
                "For the singleton TaskManager, use a class attribute `_instance` and override `__new__`.",
                "Think about what `__repr__` should show for debugging vs what a user-facing `__str__` should show.",
            ],
        },
    },
    {
        "id": "python-error-handling",
        "unit": 12,
        "order": 117,
        "title": "Python Error Handling",
        "summary": "Master exceptions, context managers, and defensive programming patterns.",
        "prereqs": ["python-fundamentals"],
        "guide": """# Python Error Handling — Fail Gracefully, Not Silently

## Mental Model
An exception is an event that disrupts the normal flow. Think of it like a fire alarm: when it rings (exception raised), execution jumps to the nearest handler (except block). If nobody handles it, the program crashes.

```
Normal flow:
  try block → runs completely → else block → finally block

Exception raised in try:
  try block (partial) → except block (matching) → finally block
```

## Exception Hierarchy
```
BaseException
├── KeyboardInterrupt
├── SystemExit
└── Exception          ← catch this, not BaseException
    ├── ValueError
    ├── TypeError
    ├── AttributeError
    ├── KeyError
    ├── IndexError
    ├── FileNotFoundError  (subclass of OSError)
    ├── ZeroDivisionError
    └── RuntimeError
        └── StopIteration
```

## try / except / else / finally
```python
def read_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config not found at {path}, using defaults")
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e   # re-raise with context
    else:
        # Only runs if no exception occurred
        print("Config loaded successfully")
    finally:
        # ALWAYS runs — cleanup goes here
        print("read_config() finished")
```

**Rule:** `else` = success path. `finally` = always cleanup.

## Raising Exceptions
```python
def set_age(age: int) -> None:
    if not isinstance(age, int):
        raise TypeError(f"age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"age must be 0–150, got {age}")
    # ...
```

## Custom Exceptions — Build a Hierarchy
```python
class AppError(Exception):           # base for all app errors
    pass  # Base application error

class DatabaseError(AppError):       # specialise
    def __init__(self, message: str, query: str = ""):
        super().__init__(message)
        self.query = query

class ConnectionError(DatabaseError):
    pass

# Usage
try:
    raise ConnectionError("Timeout", query="SELECT *")
except DatabaseError as e:
    print(f"DB error: {e}, query: {e.query}")  # catches ConnectionError too
```

```
AppError
└── DatabaseError
    └── ConnectionError   ← specific, caught by DatabaseError handler too
```

## Context Managers — The `with` Statement
```python
# File auto-closes even if exception occurs
with open("data.txt") as f:
    content = f.read()

# Custom context manager — class style
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self                    # available as `as` target

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        print(f"Elapsed: {elapsed:.3f}s")
        return False                   # False = don't suppress exceptions

with Timer() as t:
    expensive_operation()

# Context manager via decorator (simpler)
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire()
    try:
        yield resource             # code inside `with` runs here
    finally:
        release(resource)          # always cleanup
```

## Exception Chaining
```python
try:
    result = int("abc")
except ValueError as e:
    raise RuntimeError("Failed to parse config") from e
    # ^ attaches original exception as __cause__
    # traceback shows both: "The above exception was the direct cause of..."
```

**Rule:** Always chain when re-raising — preserves the root cause for debugging.

## Common Pitfalls
- **Bare `except:`** catches everything including `KeyboardInterrupt` and `SystemExit` — use `except Exception:`
- **Swallowing exceptions silently**: `except: pass` — bugs become invisible. At minimum log them.
- **Catching too broadly**: `except Exception` when you only expected `ValueError` hides unexpected bugs
- **Not cleaning up**: forgetting `finally` or `with` leaves resources open (files, DB connections, locks)
- **Raising `Exception("message")` directly** — prefer a specific type (ValueError, TypeError) or a custom exception
- **`except (A, B):` vs `except A, B:`** — the latter is Python 2 syntax and silently does something else in Python 3

## LBYL vs EAFP
```python
# LBYL — Look Before You Leap (C/Java style)
if key in d:
    value = d[key]

# EAFP — Easier to Ask Forgiveness than Permission (Pythonic)
try:
    value = d[key]
except KeyError:
    value = default
```
Python culture prefers EAFP — it's often faster (one lookup vs two) and handles race conditions better.

## Connections
- `python-oop` — custom exceptions are classes; `__enter__/__exit__` are dunder methods
- `python-fundamentals` — base syntax needed first
- `observability` — structured exception logging is the foundation of good observability
""",
        "questions": [
            {"id": "pyeh-q1", "type": "mcq", "prompt": "Which block ALWAYS executes, whether an exception occurred or not?", "choices": ["except", "else", "finally", "raise"], "answerIndex": 2, "explanation": "`finally` always runs — on success, on exception, even if a `return` is hit inside `try`. Use it for cleanup.", "tags": ["try-except", "finally"]},
            {"id": "pyeh-q2", "type": "mcq", "prompt": "What does the `else` block in a try/except execute?", "choices": ["When an exception is caught", "When no exception occurs in the try block", "Always", "When finally completes"], "answerIndex": 1, "explanation": "`else` runs only if the `try` block completed without raising any exception. It separates 'success logic' from 'error handling logic'.", "tags": ["try-except", "else"]},
            {"id": "pyeh-q3", "type": "codeOutput", "prompt": "What prints?", "code": "try:\n    x = 1/0\nexcept ZeroDivisionError:\n    print('A')\nelse:\n    print('B')\nfinally:\n    print('C')", "choices": ["A", "B C", "A C", "C"], "answerIndex": 2, "explanation": "ZeroDivisionError is raised → except prints 'A' → else is SKIPPED → finally always prints 'C'. Output: A\\nC.", "tags": ["try-except"]},
            {"id": "pyeh-q4", "type": "mcq", "prompt": "What is the problem with `except: pass`?", "choices": ["Syntax error in Python 3", "Catches all exceptions including KeyboardInterrupt, silently hiding bugs", "Only works for RuntimeError", "It re-raises the exception"], "answerIndex": 1, "explanation": "Bare `except:` (or `except Exception: pass`) swallows everything. You'll never know when bugs occur. Always at minimum log the exception.", "tags": ["pitfalls", "exception-handling"]},
            {"id": "pyeh-q5", "type": "mcq", "prompt": "How do you create a custom exception hierarchy?", "choices": ["Decorate a function with @exception", "Inherit from Exception (or a subclass)", "Use the `error` keyword", "Override __raise__"], "answerIndex": 1, "explanation": "Custom exceptions are regular classes that inherit from `Exception` or a more specific base. This lets you catch by hierarchy.", "tags": ["custom-exceptions"]},
            {"id": "pyeh-q6", "type": "codeOutput", "prompt": "What prints?", "code": "try:\n    raise ValueError('bad')\nexcept TypeError:\n    print('type')\nexcept ValueError:\n    print('value')\nexcept Exception:\n    print('general')", "choices": ["type", "value", "general", "value\\ngeneral"], "answerIndex": 1, "explanation": "Python checks except clauses in order. ValueError matches the second clause → 'value' prints. The third clause is NOT reached.", "tags": ["exception-matching"]},
            {"id": "pyeh-q7", "type": "mcq", "prompt": "What does `raise ValueError('x') from e` do?", "choices": ["Replaces e with ValueError", "Chains exceptions — ValueError's __cause__ is set to e, traceback shows both", "Silences e", "Converts e to ValueError"], "answerIndex": 1, "explanation": "Exception chaining with `from e` sets `__cause__`, so the traceback shows the original error and the new one. Crucial for debugging.", "tags": ["exception-chaining"]},
            {"id": "pyeh-q8", "type": "mcq", "prompt": "What does `__enter__` return in a context manager?", "choices": ["self always", "None always", "The value bound to the `as` variable", "The exception if any"], "answerIndex": 2, "explanation": "`__enter__`'s return value is what gets assigned to the variable after `as`. Returning `self` is common but not required.", "tags": ["context-manager"]},
            {"id": "pyeh-q9", "type": "mcq", "prompt": "`__exit__(self, exc_type, exc_val, exc_tb)` — returning True does what?", "choices": ["Re-raises the exception", "Suppresses the exception (swallows it)", "Logs the exception", "Does nothing"], "answerIndex": 1, "explanation": "Returning a truthy value from `__exit__` suppresses the exception. Returning False (or None) lets it propagate. Usually you want False.", "tags": ["context-manager"]},
            {"id": "pyeh-q10", "type": "multi", "prompt": "Which are good practices for exception handling?", "choices": ["Catch the most specific exception type", "Use `except Exception: pass` to be safe", "Chain exceptions with `raise X from e`", "Use `with` for resource management", "Catch BaseException for all errors"], "answerIndexes": [0, 2, 3], "explanation": "Specific catches, exception chaining, and context managers are best practices. Bare `pass` and catching `BaseException` are anti-patterns.", "tags": ["best-practices"]},
            {"id": "pyeh-q11", "type": "mcq", "prompt": "What is EAFP in Python?", "choices": ["Error And Failure Prevention", "Easier to Ask Forgiveness than Permission — try first, handle exception if it fails", "Exception Aware Function Pattern", "Every Action Fails Predictably"], "answerIndex": 1, "explanation": "EAFP is the Pythonic style: try the operation and catch exceptions, rather than checking preconditions first (LBYL). Often faster and handles race conditions better.", "tags": ["eafp", "best-practices"]},
            {"id": "pyeh-q12", "type": "codeOutput", "prompt": "What prints?", "code": "def f():\n    try:\n        return 1\n    finally:\n        return 2\n\nprint(f())", "choices": ["1", "2", "1\\n2", "Error"], "answerIndex": 1, "explanation": "`finally` always runs, and if it contains a `return`, that value wins over the `try` block's return. Returning from `finally` is usually a bug.", "tags": ["finally", "pitfalls"]},
            {"id": "pyeh-q13", "type": "mcq", "prompt": "What is `@contextmanager` from contextlib?", "choices": ["Decorator to auto-catch exceptions", "Decorator to turn a generator function into a context manager", "Class for managing multiple contexts", "Replaces try/finally"], "answerIndex": 1, "explanation": "The `@contextmanager` decorator turns a generator function into a context manager. Code before `yield` = `__enter__`, code after = `__exit__`.", "tags": ["context-manager"]},
            {"id": "pyeh-q14", "type": "mcq", "prompt": "You have `except (ValueError, TypeError) as e:`. What does it catch?", "choices": ["Only ValueError", "Only TypeError", "Both ValueError and TypeError (either one)", "ValueError then TypeError in sequence"], "answerIndex": 2, "explanation": "A tuple of exception types catches any matching one. The caught exception is bound to `e`.", "tags": ["exception-matching"]},
            {"id": "pyeh-q15", "type": "codeOutput", "prompt": "What prints?", "code": "class MyError(ValueError):\n    pass\n\ntry:\n    raise MyError('oops')\nexcept ValueError as e:\n    print('caught:', e)", "choices": ["Error not caught", "caught: oops", "caught: MyError", "ValueError: oops"], "answerIndex": 1, "explanation": "`MyError` inherits from `ValueError`, so `except ValueError` catches it too. Exception hierarchy enables catching by base class.", "tags": ["custom-exceptions", "inheritance"]},
            {"id": "pyeh-q16", "type": "mcq", "prompt": "When should you define a custom exception class?", "choices": ["Never — use built-in exceptions always", "When callers need to distinguish your library's errors from others", "Only in large codebases", "When you need extra attributes on the exception"], "answerIndexes": [1, 3], "explanation": "Both are valid reasons. Custom exceptions allow fine-grained catching and can carry structured data (e.g., error codes, HTTP status).", "tags": ["custom-exceptions"]},
            {"id": "pyeh-q17", "type": "mcq", "prompt": "What is wrong: `except Exception, e:`?", "choices": ["Nothing, valid Python 3", "Python 2 syntax — use `except Exception as e:` in Python 3", "Must specify exception type", "Catches too broadly"], "answerIndex": 1, "explanation": "The comma syntax is Python 2. Python 3 requires `as`. Using the comma in Python 3 silently does something different (and wrong).", "tags": ["syntax", "pitfalls"]},
            {"id": "pyeh-q18", "type": "mcq", "prompt": "A `with` statement guarantees:", "choices": ["The block runs without exceptions", "The `__exit__` method always runs, even if an exception occurs", "The resource is never shared", "The block runs in a new thread"], "answerIndex": 1, "explanation": "`__exit__` (and therefore cleanup) always runs after a `with` block — success or exception. This is why file/lock/connection management should use `with`.", "tags": ["context-manager"]},
            {"id": "pyeh-q19", "type": "codeOutput", "prompt": "What is `e.__cause__` after: `try: int('x') \\nexcept ValueError as e: raise RuntimeError('bad') from e`?", "choices": ["None", "The ValueError instance", "The RuntimeError instance", "AttributeError"], "answerIndex": 1, "explanation": "Using `from e` sets `__cause__` on the new exception to the original exception. The traceback shows both.", "tags": ["exception-chaining"]},
            {"id": "pyeh-q20", "type": "multi", "prompt": "Which exceptions does `except Exception:` NOT catch?", "choices": ["ValueError", "KeyboardInterrupt", "SystemExit", "ZeroDivisionError", "GeneratorExit"], "answerIndexes": [1, 2, 4], "explanation": "`KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` inherit from `BaseException` but NOT `Exception`. This is intentional so they can't be accidentally swallowed.", "tags": ["exception-hierarchy"]},
        ],
        "flashcards": [
            {"id": "pyeh-fc1", "front": "try/except/else/finally order", "back": "`try`: attempt. `except`: handle error. `else`: runs only on success. `finally`: ALWAYS runs (cleanup). Remember: else = happy path, finally = guaranteed cleanup.", "tags": ["try-except"]},
            {"id": "pyeh-fc2", "front": "When to use `with` statement", "back": "Any time you acquire a resource that must be released: files, DB connections, locks, network sockets. `with` guarantees `__exit__` runs even on exception.", "tags": ["context-manager"]},
            {"id": "pyeh-fc3", "front": "EAFP vs LBYL", "back": "EAFP (Pythonic): try it, catch the exception. LBYL: check before you act. Prefer EAFP — less race-prone, often faster (one lookup instead of two).", "tags": ["best-practices"]},
            {"id": "pyeh-fc4", "front": "Exception chaining syntax", "back": "`raise NewError('msg') from original_error` — sets `__cause__`, shows both in traceback. Always chain when re-raising to preserve root cause.", "tags": ["exception-chaining"]},
            {"id": "pyeh-fc5", "front": "Custom exception rule", "back": "Inherit from `Exception` (not `BaseException`). Create a base `class AppError(Exception)` for your library, then specialise. Callers can catch by base class.", "tags": ["custom-exceptions"]},
            {"id": "pyeh-fc6", "front": "@contextmanager pattern", "back": "Generator function: code before `yield` = setup (`__enter__`). `yield value` = what `as` receives. Code after `yield` (in `finally`) = teardown (`__exit__`).", "tags": ["context-manager"]},
            {"id": "pyeh-fc7", "front": "Bare except trap", "back": "`except:` (no type) or `except BaseException:` catches Ctrl+C and SystemExit. Always use `except Exception:` minimum. Prefer specific types.", "tags": ["pitfalls"]},
            {"id": "pyeh-fc8", "front": "__exit__ return value", "back": "Return `True` to suppress the exception (swallow it). Return `False` or `None` to let it propagate. Usually return `False` — silently swallowing exceptions hides bugs.", "tags": ["context-manager"]},
        ],
        "project": {
            "brief": "Design the error handling strategy for a file-processing pipeline. The pipeline reads CSV files, validates rows, transforms data, and writes results. Errors can occur at: file open, CSV parsing, row validation, transformation, and write. Design: (1) a custom exception hierarchy for each failure type, (2) which exceptions to catch vs let propagate, (3) where to use context managers, (4) how to report errors without crashing the whole pipeline (process 1000 rows, collect errors, report at end). Think through each decision without writing working code — just map out the error flow.",
            "checklist": [
                {"id": "pyeh-p1", "text": "Define custom exception hierarchy (AppError base + 3+ subclasses for different failure stages)", "weight": 20},
                {"id": "pyeh-p2", "text": "Identify which operations need `with` statements and why", "weight": 20},
                {"id": "pyeh-p3", "text": "Design the error collection strategy — catch per-row errors, accumulate, report at end", "weight": 20},
                {"id": "pyeh-p4", "text": "Decide what gets logged vs re-raised vs silently skipped (with justification)", "weight": 20},
                {"id": "pyeh-p5", "text": "Show exception chaining: where you'd use `raise X from e` and why", "weight": 20},
            ],
            "hints": [
                "Think of a hierarchy: PipelineError → FileError, ParseError, ValidationError, TransformError, WriteError",
                "File open and write both need `with open(...)` — context managers prevent resource leaks even on partial failure.",
                "For per-row error collection: catch ValidationError per row, append to an errors list, continue processing. Raise at the end if errors: raise PipelineError(f'{len(errors)} rows failed') from errors[0]",
                "Use exception chaining when wrapping lower-level errors: `raise ParseError('CSV malformed') from csv_exception`",
            ],
        },
    },
]


def write_topic(topic: dict, overwrite: bool = False) -> None:
    folder = OUT
    path = folder / f"{topic['id']}.json"
    if path.exists() and not overwrite:
        qs = len(topic.get("questions", []))
        if qs >= 20:
            print(f"  SKIP {path.name} (already has {qs} questions)")
            return
    path.write_text(json.dumps(topic, indent=2, ensure_ascii=False))
    print(f"  WROTE {path.name} ({len(topic.get('questions', []))} questions, {len(topic.get('flashcards', []))} flashcards)")


if __name__ == "__main__":
    import sys
    overwrite = "--overwrite" in sys.argv
    print(f"Writing Python batch 1 topics to {OUT}/ ...")
    for t in TOPICS:
        write_topic(t, overwrite=overwrite)
    print("Done.")

