#!/usr/bin/env python3
"""
Python Topics — Batch 2
Topics: python-functional, python-type-hints
Unit 12 (Python), orders 118–119
Run: python3 scripts/gen_python_batch2.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "src/content/topics/languages"
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    {
        "id": "python-functional",
        "unit": 12,
        "order": 118,
        "title": "Python Functional Programming",
        "summary": "Leverage lambdas, map/filter/reduce, comprehensions, and higher-order functions for cleaner, side-effect-free code.",
        "prereqs": ["python-fundamentals"],
        "guide": """# Python Functional Programming — Transform, Don't Mutate

## Mental Model
Functional programming treats computation as a series of data transformations, not a sequence of state changes.
Think of a pipeline:

```
raw_data → filter → transform → reduce → result
```

Instead of a `for` loop that mutates a list, you describe *what* to produce, not *how*.

## Core Building Blocks

### Lambda Functions — Anonymous, Inline
```python
# Regular function
def double(x):
    return x * 2

# Lambda equivalent
double = lambda x: x * 2

# Typical use: as argument to another function
nums = [3, 1, 4, 1, 5]
nums.sort(key=lambda x: -x)   # sort descending
print(nums)  # [5, 4, 3, 1, 1]
```

**Rule:** Use lambdas only for simple, single-expression functions. If it needs a name or >1 line → use `def`.

### map, filter, reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map — apply function to every element
doubled = list(map(lambda x: x * 2, numbers))
# [2, 4, 6, 8, 10, 12]

# filter — keep elements where function returns True
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6]

# reduce — fold sequence to single value (left to right)
total = reduce(lambda acc, x: acc + x, numbers)
# 21  (((((1+2)+3)+4)+5)+6)
```

### Comprehensions — Preferred over map/filter
```python
# List comprehension
doubled = [x * 2 for x in numbers]
evens   = [x for x in numbers if x % 2 == 0]

# Dict comprehension
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Set comprehension
unique_lengths = {len(w) for w in ['hi', 'hello', 'hey']}
# {2, 5, 3}

# Generator expression (lazy — no [] )
total = sum(x**2 for x in range(1000))   # doesn't build list in memory
```

**Python culture:** Prefer comprehensions over `map`/`filter`. More readable, no lambda needed.

## Higher-Order Functions
```python
# A function that takes/returns functions
def apply_twice(fn, value):
    return fn(fn(value))

def add3(x):
    return x + 3

print(apply_twice(add3, 10))  # 16

# Returning a function — closure
def multiplier(factor: int):
    def multiply(x: int) -> int:
        return x * factor          # captures `factor` from outer scope
    return multiply

triple = multiplier(3)
print(triple(5))   # 15
print(triple(10))  # 30
```

## Closures — Functions that Remember
```python
def make_counter(start: int = 0):
    count = start          # captured in closure

    def increment(step: int = 1) -> int:
        nonlocal count     # tells Python: modify outer `count`, don't create local
        count += step
        return count

    return increment

counter = make_counter(10)
print(counter())    # 11
print(counter(5))   # 16
print(counter())    # 17
```

## functools Toolkit
```python
from functools import partial, lru_cache, reduce

# partial — pre-fill arguments
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)
print(square(5))  # 25
print(cube(3))    # 27

# lru_cache — memoize (cache results of pure functions)
@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(50))  # instant — cached results reused
```

## Immutability in Python
Python doesn't enforce immutability, but functional style avoids mutation:
```python
# ❌ Mutating
def double_items(lst):
    for i in range(len(lst)):
        lst[i] *= 2     # mutates in place

# ✅ Pure function — returns new list, original unchanged
def double_items(lst):
    return [x * 2 for x in lst]
```

**Pure function rule:** Same input → always same output. No side effects (no global state changes, no I/O).

## Pipeline Pattern with functools.reduce
```python
from functools import reduce

def pipeline(*fns):
    pass  # Compose functions left-to-right
    return lambda x: reduce(lambda v, f: f(v), fns, x)

process = pipeline(
    lambda x: x.strip(),
    lambda x: x.lower(),
    lambda x: x.replace(' ', '_'),
)
print(process("  Hello World  "))  # hello_world
```

## Common Pitfalls
- **Late binding in closures**: `[lambda: i for i in range(3)]` — all lambdas capture the same `i`. Fix: `lambda i=i: i`
- **Generator exhaustion**: generators can only be iterated once. `gen = (x for x in range(5)); list(gen); list(gen)` → second list is empty
- **`reduce` with no initial value**: raises `TypeError` on empty sequence. Always provide an initializer: `reduce(fn, lst, 0)`
- **Overusing lambdas**: `map(lambda x: x.upper(), strings)` is less readable than `[s.upper() for s in strings]`

## Connections
- `python-fundamentals` — core syntax needed first
- `python-oop` — functional and OOP styles complement each other; use functional for transforms, OOP for state
- `dsa-java-dp-intro` — memoization via `@lru_cache` is the functional approach to DP
- `ts-advanced-types` — TypeScript functional patterns (map/filter/reduce) mirror Python's
""",
        "questions": [
            {"id": "pyfun-q1", "type": "mcq", "prompt": "What does `list(map(lambda x: x**2, [1,2,3]))` return?", "choices": ["[1, 4, 9]", "[2, 4, 6]", "[1, 2, 3]", "map object"], "answerIndex": 0, "explanation": "`map` applies the lambda to each element. Wrapping in `list()` materialises the generator.", "tags": ["map", "lambda"]},
            {"id": "pyfun-q2", "type": "mcq", "prompt": "What is a pure function?", "choices": ["A function with no parameters", "A function that always returns the same output for the same input and has no side effects", "A function defined with lambda", "A function inside a class"], "answerIndex": 1, "explanation": "Pure functions are deterministic and side-effect-free — the core principle of functional programming.", "tags": ["pure-functions"]},
            {"id": "pyfun-q3", "type": "codeOutput", "prompt": "What prints?", "code": "fns = [lambda: i for i in range(3)]\nprint([f() for f in fns])", "choices": ["[0, 1, 2]", "[2, 2, 2]", "[0, 0, 0]", "Error"], "answerIndex": 1, "explanation": "Late binding: all lambdas capture the variable `i`, not its value at creation time. After the loop, `i=2`, so all return 2. Fix: `lambda i=i: i`.", "tags": ["closures", "pitfalls"]},
            {"id": "pyfun-q4", "type": "mcq", "prompt": "What does `@lru_cache` do?", "choices": ["Logs function calls", "Caches return values for repeated inputs (memoization)", "Limits recursion depth", "Profiles function performance"], "answerIndex": 1, "explanation": "`@lru_cache` stores results keyed by arguments. On repeated calls with same args, returns cached value instantly — crucial for recursive algorithms.", "tags": ["lru_cache", "memoization"]},
            {"id": "pyfun-q5", "type": "codeOutput", "prompt": "What prints?", "code": "from functools import reduce\nprint(reduce(lambda acc, x: acc + x, [1,2,3,4], 0))", "choices": ["10", "0", "[1,2,3,4]", "Error"], "answerIndex": 0, "explanation": "`reduce` folds: 0+1=1, 1+2=3, 3+3=6, 6+4=10. The third argument is the initial accumulator.", "tags": ["reduce"]},
            {"id": "pyfun-q6", "type": "mcq", "prompt": "What does `nonlocal` enable in a closure?", "choices": ["Access global variables", "Modify a variable from an enclosing (but non-global) scope", "Create a new local variable", "Import from outer module"], "answerIndex": 1, "explanation": "`nonlocal` tells Python to look up the variable in the enclosing function scope, not create a new local one. Without it, assignment creates a local shadowing variable.", "tags": ["closures", "nonlocal"]},
            {"id": "pyfun-q7", "type": "mcq", "prompt": "Generator expressions vs list comprehensions: key difference?", "choices": ["Generators use (), lists use []", "Generators are lazy (compute on demand), lists eager (compute all at once)", "Both are the same", "Generators are faster for small data"], "answerIndexes": [0, 1], "explanation": "Both syntax and lazy evaluation differ. Generators use `()` and produce values one at a time, saving memory for large sequences.", "tags": ["generators"]},
            {"id": "pyfun-q8", "type": "codeOutput", "prompt": "What prints?", "code": "gen = (x * 2 for x in range(3))\nprint(list(gen))\nprint(list(gen))", "choices": ["[0, 2, 4]\\n[0, 2, 4]", "[0, 2, 4]\\n[]", "Error", "0 2 4\\n0 2 4"], "answerIndex": 1, "explanation": "Generators are exhausted after one iteration. The second `list(gen)` yields an empty list — this is a common bug.", "tags": ["generators", "pitfalls"]},
            {"id": "pyfun-q9", "type": "mcq", "prompt": "What does `partial(power, exp=2)` do?", "choices": ["Creates a new function with exp pre-set to 2", "Calls power(exp=2)", "Creates a class with exp=2", "Raises an error"], "answerIndex": 0, "explanation": "`functools.partial` returns a new callable with some arguments pre-filled. Calling `square(5)` is then like calling `power(5, exp=2)`.", "tags": ["partial", "higher-order"]},
            {"id": "pyfun-q10", "type": "mcq", "prompt": "Which is the most Pythonic way to square all even numbers in a list?", "choices": ["map(lambda x: x**2, filter(lambda x: x%2==0, nums))", "[x**2 for x in nums if x%2==0]", "reduce(lambda a,b: a+[b**2], [x for x in nums if x%2==0], [])", "list(filter(lambda x: x**2, nums))"], "answerIndex": 1, "explanation": "List comprehension with condition is the clearest and most Pythonic. Nested map/filter with lambdas is harder to read.", "tags": ["comprehensions", "best-practices"]},
            {"id": "pyfun-q11", "type": "codeOutput", "prompt": "What prints?", "code": "def make_adder(n):\n    return lambda x: x + n\n\nadd5 = make_adder(5)\nadd10 = make_adder(10)\nprint(add5(3), add10(3))", "choices": ["8 13", "3 3", "5 10", "Error"], "answerIndex": 0, "explanation": "Each call to `make_adder` creates a new closure capturing a different `n`. `add5(3)` = 3+5=8, `add10(3)` = 3+10=13.", "tags": ["closures", "higher-order"]},
            {"id": "pyfun-q12", "type": "multi", "prompt": "Which are side effects in a function?", "choices": ["Modifying a global variable", "Writing to a file", "Returning a computed value", "Printing to stdout", "Reading a function argument"], "answerIndexes": [0, 1, 3], "explanation": "Side effects are changes to state outside the function: global mutation, I/O (files, print). Returning a value and reading arguments are not side effects.", "tags": ["pure-functions", "side-effects"]},
            {"id": "pyfun-q13", "type": "mcq", "prompt": "What does `{x: x**2 for x in range(4)}` produce?", "choices": ["{0, 1, 4, 9}", "{0: 0, 1: 1, 2: 4, 3: 9}", "[0, 1, 4, 9]", "Error"], "answerIndex": 1, "explanation": "This is a dict comprehension (key: value syntax inside `{}`). Keys are 0-3, values are squares.", "tags": ["comprehensions"]},
            {"id": "pyfun-q14", "type": "mcq", "prompt": "When is a generator preferable to a list comprehension?", "choices": ["Always — generators are always faster", "When processing large sequences where you don't need all values in memory at once", "When you need to iterate multiple times", "When the function has side effects"], "answerIndex": 1, "explanation": "Generators evaluate lazily — they don't build the full list. For large datasets (files, API responses, infinite sequences), generators save significant memory.", "tags": ["generators", "performance"]},
            {"id": "pyfun-q15", "type": "codeOutput", "prompt": "What prints?", "code": "from functools import reduce\nwords = ['hello', 'world']\nresult = reduce(lambda a, b: a + ' ' + b, words)\nprint(result)", "choices": ["['hello', 'world']", "helloworld", "hello world", "Error"], "answerIndex": 2, "explanation": "`reduce` combines 'hello' and 'world' with ' ' separator → 'hello world'.", "tags": ["reduce"]},
            {"id": "pyfun-q16", "type": "mcq", "prompt": "Why is `lambda x: x.upper()` typically unnecessary in `map(lambda x: x.upper(), strings)`?", "choices": ["lambda is deprecated", "str.upper is already a method; use `map(str.upper, strings)` instead", "map doesn't accept lambdas", "str.upper doesn't work on lists"], "answerIndex": 1, "explanation": "Methods can be passed directly as callables: `map(str.upper, strings)` is cleaner. But list comprehension `[s.upper() for s in strings]` is even more Pythonic.", "tags": ["best-practices", "map"]},
            {"id": "pyfun-q17", "type": "codeOutput", "prompt": "What prints?", "code": "nums = [1, 2, 3, 4, 5]\nresult = [x for x in nums if x > 2 if x < 5]\nprint(result)", "choices": ["[3, 4]", "[1, 2, 5]", "[3, 4, 5]", "Error"], "answerIndex": 0, "explanation": "Multiple conditions in a comprehension are ANDed together: x > 2 AND x < 5 → 3 and 4.", "tags": ["comprehensions"]},
            {"id": "pyfun-q18", "type": "mcq", "prompt": "What is a closure?", "choices": ["A class with private methods", "A function that captures variables from its enclosing scope", "A function with no return value", "A decorator pattern"], "answerIndex": 1, "explanation": "A closure is a function that remembers variables from the scope where it was created, even after that scope has ended.", "tags": ["closures"]},
            {"id": "pyfun-q19", "type": "mcq", "prompt": "What does `sorted(people, key=lambda p: p['age'])` do?", "choices": ["Sorts people in place by age", "Returns a new list sorted by the 'age' value in each dict", "Modifies the original list", "Raises TypeError if age is missing"], "answerIndex": 1, "explanation": "`sorted()` returns a NEW sorted list. The `key` function extracts the comparison value from each element.", "tags": ["sorting", "lambda"]},
            {"id": "pyfun-q20", "type": "multi", "prompt": "Which are true about list comprehensions vs map/filter?", "choices": ["Comprehensions are generally more readable in Python", "map/filter are always faster", "Comprehensions can combine filter and transform in one expression", "map returns a list in Python 3", "Generator expressions are the lazy version of comprehensions"], "answerIndexes": [0, 2, 4], "explanation": "Comprehensions are preferred for readability. `map` returns a map object (not list) in Python 3. Generator expressions use `()` and are lazy.", "tags": ["comprehensions", "map"]},
        ],
        "flashcards": [
            {"id": "pyfun-fc1", "front": "lambda vs def — when to use each", "back": "`lambda`: single expression, used inline as argument (sort key, map/filter). `def`: anything with logic, multiple lines, or needs a name. If you assign lambda to variable, use `def` instead.", "tags": ["lambda"]},
            {"id": "pyfun-fc2", "front": "Late binding closure trap", "back": "`[lambda: i for i in range(3)]` — all lambdas return 2 (last value of i). Fix: `lambda i=i: i` captures the current value as default arg.", "tags": ["closures", "pitfalls"]},
            {"id": "pyfun-fc3", "front": "Generator exhaustion", "back": "Generators are single-use. After iterating, they're empty. If you need to iterate multiple times, use a list comprehension `[...]` instead of `(...)`, or call `list(gen)` once.", "tags": ["generators"]},
            {"id": "pyfun-fc4", "front": "@lru_cache use case", "back": "Pure functions called repeatedly with same args. Classic: Fibonacci, dynamic programming, expensive computations. WARNING: don't use on functions with side effects or mutable args.", "tags": ["lru_cache"]},
            {"id": "pyfun-fc5", "front": "reduce(fn, iterable, initializer)", "back": "Folds left-to-right: `reduce(lambda a,b: a+b, [1,2,3], 0)` → ((0+1)+2)+3 = 6. Always provide initializer — avoids TypeError on empty input.", "tags": ["reduce"]},
            {"id": "pyfun-fc6", "front": "Pure function rule", "back": "Same input → same output. No side effects (no global mutations, no I/O). Pure functions are testable, composable, and safe to cache.", "tags": ["pure-functions"]},
            {"id": "pyfun-fc7", "front": "nonlocal keyword", "back": "Used inside a nested function to modify a variable from an enclosing (non-global) scope. Without it, assignment creates a new local variable, shadowing the outer one.", "tags": ["closures", "nonlocal"]},
            {"id": "pyfun-fc8", "front": "partial() use case", "back": "`partial(fn, arg)` pre-fills arguments, creating a new callable. Use to specialise generic functions: `double = partial(multiply, factor=2)`. Cleaner than writing a new lambda.", "tags": ["partial"]},
        ],
        "project": {
            "brief": "Design a data processing pipeline using functional patterns. You have a stream of user event records (dicts with: user_id, event_type, timestamp, amount). Write pseudo-code (no execution needed) using map, filter, reduce, and comprehensions to: (1) Filter events from the last 30 days, (2) Exclude cancelled events, (3) Group by user_id, (4) Sum amounts per user, (5) Find the top 10 spenders. Design the pipeline composition. Discuss: Where would @lru_cache help? What makes each transform pure? How would you handle errors in a functional style?",
            "checklist": [
                {"id": "pyfun-p1", "text": "Design each pipeline stage as a pure function (filter, transform, reduce)", "weight": 20},
                {"id": "pyfun-p2", "text": "Use comprehensions or map/filter correctly for each stage", "weight": 20},
                {"id": "pyfun-p3", "text": "Compose the pipeline using reduce or a pipeline() helper", "weight": 20},
                {"id": "pyfun-p4", "text": "Identify where @lru_cache could help and justify", "weight": 20},
                {"id": "pyfun-p5", "text": "Explain how to handle malformed records functionally (without exceptions polluting pure functions)", "weight": 20},
            ],
            "hints": [
                "Use a generator for the full stream so you don't load all records into memory.",
                "The grouping step (by user_id) could use a dict comprehension or itertools.groupby after sorting.",
                "For error handling in functional style: use Result/Option pattern — transform invalid records to None, then filter(None, stream).",
                "Top-10 spenders: `sorted(user_totals.items(), key=lambda kv: kv[1], reverse=True)[:10]`",
            ],
        },
    },
    {
        "id": "python-type-hints",
        "unit": 12,
        "order": 119,
        "title": "Python Type Hints",
        "summary": "Add static type annotations to Python code for better tooling, documentation, and bug prevention.",
        "prereqs": ["python-fundamentals", "python-oop"],
        "guide": """# Python Type Hints — Document Intent, Catch Bugs Early

## Mental Model
Type hints are like commit messages for your function signatures. Python doesn't enforce them at runtime (unless you use a library like `beartype`), but tools like **mypy**, **pyright**, and your IDE use them to catch bugs before they run.

```python
def greet(name: str) -> str:   # annotated
    return "Hello, " + name

greet(42)   # mypy: error: Argument 1 to "greet" has incompatible type "int"; expected "str"
```

## Basic Annotations
```python
x: int = 5
y: float = 3.14
name: str = "Alice"
active: bool = True
items: list[int] = [1, 2, 3]       # Python 3.9+ — lowercase generics
mapping: dict[str, int] = {"a": 1}
pair: tuple[int, str] = (1, "hi")
optional: int | None = None         # Python 3.10+ union syntax
```

### Function Annotations
```python
def add(a: int, b: int) -> int:
    return a + b

def no_return() -> None:
    print("side effect only")

def process(data: list[str], max_len: int = 10) -> dict[str, int]:
    return {s: len(s) for s in data if len(s) <= max_len}
```

## Optional and Union
```python
from typing import Optional, Union  # pre-3.10 style

# Optional[X] is shorthand for Union[X, None]
def find_user(user_id: int) -> Optional[str]:   # may return None
    ...

# Modern Python 3.10+ syntax
def find_user(user_id: int) -> str | None:
    ...

# Union of multiple types
def parse(value: str | int | float) -> float:
    return float(value)
```

## Collections
```python
from typing import List, Dict, Tuple, Set  # pre-3.9 (needed for older Python)

# Python 3.9+ — use built-in generics directly
def average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers)

def group_by_first(items: list[tuple[str, int]]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for key, val in items:
        result.setdefault(key, []).append(val)
    return result
```

## TypeVar — Generic Functions
```python
from typing import TypeVar

T = TypeVar('T')

def first(items: list[T]) -> T:   # works for any type
    return items[0]

x: int = first([1, 2, 3])         # T inferred as int
y: str = first(["a", "b"])        # T inferred as str
```

## Protocol — Structural Typing (Duck Typing with Types)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...   # any class with a draw() method qualifies

class Circle:
    def draw(self) -> None:
        print("O")

class Square:
    def draw(self) -> None:
        print("■")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())  # ✓ — Circle has draw()
render(Square())  # ✓ — Square has draw()
```

Protocols are structural — you don't need to explicitly inherit or register. This is type-safe duck typing.

## Callable Type Hints
```python
from typing import Callable

def apply(fn: Callable[[int, int], int], a: int, b: int) -> int:
    return fn(a, b)

apply(lambda x, y: x + y, 3, 4)  # ✓
```
`Callable[[ArgTypes...], ReturnType]`

## TypedDict — Typed Dictionaries
```python
from typing import TypedDict

class UserRecord(TypedDict):
    id: int
    name: str
    email: str
    age: int | None

def get_name(user: UserRecord) -> str:
    return user["name"]   # IDE knows "name" exists and is str
```

## Literal and Final
```python
from typing import Literal, Final

Direction = Literal["north", "south", "east", "west"]

def move(direction: Direction) -> None:
    ...

move("north")   # ✓
move("up")      # mypy error: not a valid Literal

MAX_SIZE: Final = 100   # constant — reassignment is a type error
```

## Common Patterns
```python
# Self-referential types
class Node:
    def __init__(self, value: int, next: "Node | None" = None):
        self.value = value
        self.next = next

# Overloaded functions (different signatures)
from typing import overload

@overload
def process(x: int) -> int: ...
@overload
def process(x: str) -> str: ...
def process(x):              # actual implementation (no annotation needed)
    if isinstance(x, int):
        return x * 2
    return x.upper()
```

## Running mypy
```bash
pip install mypy
mypy src/              # check all files
mypy --strict src/     # strict mode — catches more issues
```

## Common Pitfalls
- **`list` vs `List`**: In Python 3.9+, use `list[int]` directly. Pre-3.9 needs `from typing import List; List[int]`
- **`Any` escapes checking**: `from typing import Any; x: Any` — mypy ignores it. Avoid in production code
- **Forward references**: If a class references itself, use a string: `"Node | None"` or `from __future__ import annotations`
- **Overly complex annotations**: If your annotation needs 3 lines, consider a `TypeAlias` or `TypedDict`
- **Ignoring `None` returns**: if a function can return `None`, annotate it! Not checking return values causes `AttributeError` at runtime

## Connections
- `python-oop` — type hints integrate with class design (TypedDict, Protocol, TypeVar)
- `ts-fundamentals` — TypeScript type system is richer; compare structural typing approaches
- `python-fundamentals` — base syntax needed first
""",
        "questions": [
            {"id": "pyth-q1", "type": "mcq", "prompt": "What does `def f(x: int) -> str:` declare?", "choices": ["x must be int at runtime", "x is expected to be int, return is expected to be str — checked by type checkers, not enforced by Python", "Creates a typed class", "Converts x to int automatically"], "answerIndex": 1, "explanation": "Type hints are advisory — Python doesn't enforce them at runtime. They're for type checkers (mypy, pyright) and IDE tooling.", "tags": ["basics", "type-hints"]},
            {"id": "pyth-q2", "type": "mcq", "prompt": "What is `Optional[str]` equivalent to?", "choices": ["str | bool", "str | None", "str | ...", "Optional means the parameter has a default value"], "answerIndex": 1, "explanation": "`Optional[X]` is shorthand for `Union[X, None]` — the value can be X or None.", "tags": ["optional", "union"]},
            {"id": "pyth-q3", "type": "codeOutput", "prompt": "What does Python do at runtime if you call `greet(42)` where `def greet(name: str) -> str`?", "choices": ["Raises TypeError", "Raises AttributeError", "Runs without error (type hints not enforced)", "Returns 42"], "answerIndex": 2, "explanation": "Python ignores type hints at runtime. Only type checkers like mypy catch this. The function will try to run and may raise an error only if `str` operations are called on `42`.", "tags": ["runtime", "type-hints"]},
            {"id": "pyth-q4", "type": "mcq", "prompt": "How do you annotate a function that accepts either int or str?", "choices": ["def f(x: int | str):", "def f(x: (int, str)):", "def f(x: any):", "def f(int x, str x):"], "answerIndex": 0, "explanation": "Python 3.10+ uses `X | Y` union syntax. Pre-3.10 uses `Union[int, str]` from typing.", "tags": ["union"]},
            {"id": "pyth-q5", "type": "mcq", "prompt": "What is a TypeVar used for?", "choices": ["Declaring global variables", "Creating generic functions that work with any type while preserving type information", "Creating runtime type checking", "Type aliases"], "answerIndex": 1, "explanation": "`TypeVar` enables generic functions. `T = TypeVar('T')` means 'some specific type that will be determined at call time'. The type checker infers T from the argument.", "tags": ["generics", "typevar"]},
            {"id": "pyth-q6", "type": "mcq", "prompt": "What does `Protocol` from typing enable?", "choices": ["Multiple inheritance", "Structural subtyping — any class with the required methods satisfies the protocol", "Abstract base classes", "Runtime interface checking"], "answerIndex": 1, "explanation": "Protocol enables structural typing (duck typing with type safety). A class satisfies a Protocol if it has the required methods/attributes — no explicit inheritance needed.", "tags": ["protocol", "structural-typing"]},
            {"id": "pyth-q7", "type": "codeOutput", "prompt": "Is this valid type annotation? `items: list[int | str] = [1, 'hello', 2]`", "choices": ["Yes, valid Python 3.10+", "No, lists must be homogeneous", "Yes but only with from typing import List", "No, int and str can't be mixed"], "answerIndex": 0, "explanation": "`list[int | str]` declares a list that can contain both ints and strings. This is valid Python 3.10+ syntax.", "tags": ["union", "collections"]},
            {"id": "pyth-q8", "type": "mcq", "prompt": "What is `Final` from typing used for?", "choices": ["Marking abstract methods", "Declaring constants — type checkers raise error if reassigned", "Finalizing class hierarchy (no subclassing)", "Type aliases"], "answerIndex": 1, "explanation": "`Final` marks a name as a constant. `MAX: Final = 100` — mypy will flag any code that tries to reassign `MAX`.", "tags": ["final", "constants"]},
            {"id": "pyth-q9", "type": "mcq", "prompt": "What is `TypedDict` useful for?", "choices": ["Creating typed tuples", "Typing dictionaries with known string keys and specific value types", "Runtime dict validation", "Replacing dataclasses"], "answerIndex": 1, "explanation": "`TypedDict` gives type checkers information about dict structure. IDEs can autocomplete keys and catch typos. Useful when you can't refactor to dataclasses.", "tags": ["typeddict"]},
            {"id": "pyth-q10", "type": "mcq", "prompt": "What is the issue with using `Any` in type annotations?", "choices": ["It's slower at runtime", "It disables type checking for that value — bugs can hide", "It's not valid Python syntax", "It only works for primitive types"], "answerIndex": 1, "explanation": "`Any` essentially opts out of type checking. mypy won't flag type errors involving `Any` values. Use it sparingly — only for truly dynamic code.", "tags": ["any", "pitfalls"]},
            {"id": "pyth-q11", "type": "mcq", "prompt": "How do you annotate a function parameter that accepts a callback `fn(int, int) -> bool`?", "choices": ["fn: function", "fn: Callable[[int, int], bool]", "fn: (int, int) -> bool", "fn: lambda int, int: bool"], "answerIndex": 1, "explanation": "`Callable[[ArgType1, ArgType2, ...], ReturnType]` is the correct annotation for callable objects.", "tags": ["callable"]},
            {"id": "pyth-q12", "type": "codeOutput", "prompt": "What does `x: int | None = None` mean?", "choices": ["x is None only", "x can be int or None, currently None", "x is int with default None", "Syntax error"], "answerIndex": 1, "explanation": "The annotation says x can be `int` or `None`. The `= None` is the default value. This is the standard pattern for optional parameters.", "tags": ["optional", "union"]},
            {"id": "pyth-q13", "type": "mcq", "prompt": "In Python 3.9+, how do you annotate a list of strings?", "choices": ["List[str]", "list[str]", "List<str>", "ArrayList[str]"], "answerIndex": 1, "explanation": "Python 3.9+ allows built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]`. Pre-3.9 needed `from typing import List; List[str]`.", "tags": ["collections", "generics"]},
            {"id": "pyth-q14", "type": "mcq", "prompt": "Forward reference in type hints: when do you need `\"Node | None\"`?", "choices": ["Always in Python 3.10+", "When the referenced class is defined after the annotation in the same file", "For all self-referential types in all Python versions", "Never needed — Python resolves it automatically"], "answerIndex": 2, "explanation": "Self-referential types (like a Node pointing to another Node) require string quotes in all Python versions unless you add `from __future__ import annotations` at the top of the file.", "tags": ["forward-references"]},
            {"id": "pyth-q15", "type": "multi", "prompt": "Which are valid uses of type hints?", "choices": ["Function parameter annotations", "Return type annotations", "Variable annotations at module level", "Runtime type enforcement", "IDE autocompletion and documentation"], "answerIndexes": [0, 1, 2, 4], "explanation": "All except runtime enforcement. Python doesn't enforce type hints at runtime by default. The others are all valid uses.", "tags": ["basics"]},
            {"id": "pyth-q16", "type": "mcq", "prompt": "What does `Literal['north', 'south', 'east', 'west']` do?", "choices": ["Creates an enum", "Restricts the value to exactly those string literals", "Imports compass directions", "Creates a type alias for str"], "answerIndex": 1, "explanation": "`Literal` restricts acceptable values to specific constants. Type checkers flag any other string as an error.", "tags": ["literal"]},
            {"id": "pyth-q17", "type": "mcq", "prompt": "What is `--strict` mode in mypy?", "choices": ["Faster checking", "Enables many additional checks: disallows Any, requires all functions to be annotated, etc.", "Only checks public APIs", "Adds runtime enforcement"], "answerIndex": 1, "explanation": "`mypy --strict` enables flags like `--disallow-any-generics`, `--disallow-untyped-defs`, `--warn-return-any`. Stricter = fewer type-safety holes.", "tags": ["mypy", "tooling"]},
            {"id": "pyth-q18", "type": "codeOutput", "prompt": "What does mypy report for: `def f(x: int) -> str: return x`?", "choices": ["No error", "error: Incompatible return value type (got int, expected str)", "error: x must be converted first", "error: Missing return statement"], "answerIndex": 1, "explanation": "The function returns an `int` but is annotated to return `str`. mypy catches this mismatch.", "tags": ["mypy", "return-types"]},
            {"id": "pyth-q19", "type": "mcq", "prompt": "What is `TypeAlias` used for?", "choices": ["Creating runtime type objects", "Giving a complex type a readable name for reuse", "Subtyping built-in types", "Marking deprecated types"], "answerIndex": 1, "explanation": "`UserId = TypeAlias = int` gives a semantic name to `int`. Now you can use `UserId` in annotations to document intent without runtime overhead.", "tags": ["type-alias"]},
            {"id": "pyth-q20", "type": "multi", "prompt": "Which statements about Python type hints are true?", "choices": ["They are enforced at runtime by default", "They improve IDE autocompletion", "mypy and pyright are static type checkers", "They serve as documentation", "They must be added to all Python files"], "answerIndexes": [1, 2, 3], "explanation": "Type hints are NOT enforced at runtime (1 false), NOT mandatory (5 false). They do improve tooling (2), enable static checking (3), and document intent (4).", "tags": ["basics"]},
        ],
        "flashcards": [
            {"id": "pyth-fc1", "front": "Optional[X] vs X | None", "back": "Same thing. `Optional[X]` is from `typing` (pre-3.10). `X | None` is modern Python 3.10+ syntax. Both mean the value can be X or None.", "tags": ["optional"]},
            {"id": "pyth-fc2", "front": "TypeVar use case", "back": "Generic functions: `T = TypeVar('T')` then `def first(items: list[T]) -> T`. The type checker infers what T is at each call site, preserving type safety without losing flexibility.", "tags": ["generics"]},
            {"id": "pyth-fc3", "front": "Protocol vs ABC", "back": "Protocol: structural (duck typing) — any class with required methods qualifies, no inheritance needed. ABC: nominal — must explicitly inherit. Protocol is more Pythonic.", "tags": ["protocol"]},
            {"id": "pyth-fc4", "front": "When type hints run (runtime vs static)", "back": "Type hints are NOT enforced at runtime by default. They're checked by static tools (mypy, pyright) and used by IDEs. Runtime enforcement requires `beartype` or `pydantic`.", "tags": ["basics"]},
            {"id": "pyth-fc5", "front": "list[int] vs List[int]", "back": "Python 3.9+: use `list[int]`, `dict[str, int]` directly. Pre-3.9: import `from typing import List, Dict`. Or use `from __future__ import annotations` for all Pythons.", "tags": ["collections"]},
            {"id": "pyth-fc6", "front": "TypedDict use case", "back": "When you have dict-shaped data with known keys (API responses, config). Gives type checker key-level type info. Prefer dataclasses for new code; use TypedDict for existing dict-heavy code.", "tags": ["typeddict"]},
            {"id": "pyth-fc7", "front": "Callable annotation format", "back": "`Callable[[ArgType1, ArgType2], ReturnType]`. For any callable: `Callable[..., ReturnType]`. For no args: `Callable[[], ReturnType]`.", "tags": ["callable"]},
            {"id": "pyth-fc8", "front": "Forward reference — when needed", "back": "Self-referential types: `next: \"Node | None\"` (string). OR add `from __future__ import annotations` at file top to make all annotations lazy strings. Needed for circular references.", "tags": ["forward-references"]},
        ],
        "project": {
            "brief": "You're designing a type-annotated API client library for a REST service. The client methods return typed response objects. Design the type annotations for: (1) A `UserAPI` class with `get_user(id: int) -> ?` and `list_users(filter: ?) -> ?`, (2) A paginated response wrapper, (3) An error response type, (4) A callback for event hooks `on_response(response) -> None`. Consider: TypedDict vs dataclass for responses, Optional vs union for nullable fields, Callable for hooks, TypeVar for generic pagination wrapper. Write the type signatures — no implementations needed.",
            "checklist": [
                {"id": "pyth-p1", "text": "Define response types using TypedDict or dataclass with correct field annotations", "weight": 20},
                {"id": "pyth-p2", "text": "Use Optional/Union correctly for nullable fields and error responses", "weight": 20},
                {"id": "pyth-p3", "text": "Create a generic PaginatedResponse[T] using TypeVar", "weight": 20},
                {"id": "pyth-p4", "text": "Annotate callback hooks using Callable with correct signature", "weight": 20},
                {"id": "pyth-p5", "text": "Justify TypedDict vs dataclass for each response type (at least one of each)", "weight": 20},
            ],
            "hints": [
                "For paginated responses: `T = TypeVar('T'); class PaginatedResponse(Generic[T]): items: list[T]; total: int; page: int`",
                "Error response could be `class APIError(TypedDict): code: int; message: str; details: dict[str, Any] | None`",
                "Callback: `ResponseHook = Callable[[dict[str, Any], int], None]` — takes response body and status code",
                "Use `Literal` for HTTP methods: `method: Literal['GET', 'POST', 'PUT', 'DELETE']`",
            ],
        },
    },
]


def write_topic(topic: dict, overwrite: bool = False) -> None:
    path = OUT / f"{topic['id']}.json"
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
    print(f"Writing Python batch 2 topics to {OUT}/ ...")
    for t in TOPICS:
        write_topic(t, overwrite=overwrite)
    print("Done.")

