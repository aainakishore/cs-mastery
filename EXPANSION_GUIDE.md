# DSA Topics Expansion Guide

## ✅ Completed (4 topics)
- dsa-java-arrays: 20q, 8fc 
- dsa-java-strings: 20q, 8fc 
- dsa-java-linked-lists: NEEDS 15 MORE QUESTIONS (currently 5)
- dsa-java-stacks: NEEDS 15 MORE QUESTIONS (currently 5, but has 8fc)

## 📝 Pattern to Follow

For each topic, you need to add **15 more questions** (from 5 to 20) and **3 more flashcards** (from 5 to 8).

### Example: How to Expand Linked-Lists

Current code in gen_dsa_topics.py (around line 218-224):
```python
[
    mcq("djll", 1, ...), 
    mcq("djll", 2, ...),
    code_output("djll", 3, ...),
    mcq("djll", 4, ...),
    multi("djll", 5, ...),
],
```

Should become:
```python
[
    mcq("djll", 1, "Head insertion in a singly linked list is:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 0, "Only a few references change.", ["linked-list"]),
    mcq("djll", 2, "Floyd's cycle detection uses:", ["Sorting", "Slow and fast pointers", "A heap", "Binary search"], 1, "The fast pointer catches the slow pointer in a cycle.", ["cycle"]),
    mcq("djll", 3, "Random access by index in a linked list is:", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 2, "You must traverse node by node.", ["complexity"]),
    code_output("djll", 4, "After reversing 1->2->3, the new head value is:", "// reverse(1->2->3) returns the new head", ["1", "2", "3", "null"], 2, "The list becomes 3->2->1.", ["reversal"]),
    multi("djll", 5, "Which references are commonly tracked during iterative reversal?", ["prev", "cur", "next", "root"], [0, 1, 2], "prev/cur/next prevent losing the rest of the list.", ["reversal"]),
    # ADD 15 MORE LIKE THESE:
    mcq("djll", 6, "Singly linked list node has:", ["Only value", "Value and next", "Value, prev, next", "Array of values"], 1, "Single forward pointer.", [" structure"]),
    mcq("djll", 7, "Doubly linked list node has:", ["Only value", "Value and next", "Value, prev, next", "Two nexts"], 2, "Bidirectional pointers.", ["structure"]),
    mcq("djll", 8, "Find middle of list (fast/slow):", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2, "Slow pointer reaches middle when fast reaches end.", ["two-pointers"]),
    # ... continue to djll-q20
],
```

### Question Types to Mix:
1. **mcq** - Multiple choice (1 answer)
2. **multi** - Multiple correct answers
3. **code_output** - What does code print?
4. **mcq** with different topics (complexity, Java API, patterns, algorithms)

### Flashcard Pattern:
From 5 cards to 8 cards. Example for linked-lists:

Current (5 cards):
```python
cards("djll", [("Singly node fields", "value and next."), ("Doubly node fields", "value, prev, next."), ...], "linked-list")
```

Expand to (8 cards):
```python
cards("djll", [
    ("Singly node fields", "value and next."), 
    ("Doubly node fields", "value, prev, next."), 
    ("Fast/slow use", "Middle or cycle detection."), 
    ("Reverse list space", "O(1) iterative."), 
    ("LinkedList in Java", "Implements List and Deque."), 
    ("Floyd cycle detect", "Fast moves 2, slow moves 1."), 
    ("Dummy node benefit", "Simplifies head insert/delete."), 
    ("K-th from end", "Two pointers k apart.")
], "linked-list")
```

## 🎯 Remaining Topics to Expand (14 topics)

Each needs +15 questions and +3 flashcards:

1. **dsa-java-queues** - Add queue patterns, BFS questions, circular queue
2. **dsa-java-hashing** - HashMap/HashSet, collision handling, load factor
3. **dsa-java-recursion** - Base cases, stack overflow, memoization
4. **dsa-java-sorting** - Quicksort, mergesort, stability, complexity
5. **dsa-java-searching** - Binary search variations, rotated arrays
6. **dsa-java-binary-trees** - Traversals, BST properties, LCA
7. **dsa-java-heaps** - PriorityQueue, heapify, top-k problems
8. **dsa-java-graphs-basics** - Adjacency representations, BFS/DFS
9. **dsa-java-graphs-advanced** - Dijkstra, topological sort, MST
10. **dsa-java-dp-intro** - Memoization vs tabulation, Fibonacci
11. **dsa-java-dp-sequences** - LCS, LIS, edit distance
12. **dsa-java-tries** - Trie operations, prefix matching
13. **dsa-java-sliding-window** - Fixed/variable window patterns
14. **dsa-java-two-pointers** - Convergence, Dutch flag

## 🔧 How to Edit gen_dsa_topics.py

1. Open `scripts/gen_dsa_topics.py`
2. Find the topic (search for `"dsa-java-queues"` for example)
3. Find its questions list (starts with `[` after the guide)
4. Replace the 5 questions with 20 questions
5. Find its flashcards (search for `cards("djq"` or similar)
6. Replace 5 flashcards with 8 flashcards
7. Save and run: `python3 scripts/gen_dsa_topics.py --overwrite`

## ✅ Verify

After each edit, run:
```bash
python3 -c "
import json
from pathlib import Path
for p in sorted(Path('src/content/topics').glob('dsa-java-*.json')):
    data = json.loads(p.read_text())
    q = len(data['questions'])
    status = '✓' if q >= 20 else '✗'
    print(f'{status} {p.name}: {q} questions')
"
```

Target: All 18 topics showing ✓ with 20 questions each.

