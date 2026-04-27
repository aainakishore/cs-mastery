#!/usr/bin/env python3
"""
Patch weak-guide topics (arrays, strings, linked-lists, stacks) with rich visual guides
and add a new dsa-java-trees topic covering AVL, Red-Black, Segment, B-Tree concepts.
Run: python3 scripts/patch_guides.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "content" / "topics"

# ─────────────────────────────────────────────────────────────────────────────
# ARRAYS — upgrade guide only (questions/flashcards already 20/8)
# ─────────────────────────────────────────────────────────────────────────────
ARRAYS_GUIDE = """\
# Arrays in Java

An array is a **contiguous block of memory** holding elements of the same type. Picture a row of numbered mailboxes: box 0, box 1, box 2 … Each box is the same size, so the CPU finds any box in one step — no searching needed.

```
Index:  0    1    2    3    4
       ┌────┬────┬────┬────┬────┐
Value: │  7 │  3 │ 12 │  1 │  9 │
       └────┴────┴────┴────┴────┘
        ↑                        ↑
        base address             base + 4 × (element size)
```

## Declaration and Initialisation

```java
int[] arr = new int[5];          // [0, 0, 0, 0, 0] — primitives default to 0
int[] arr = {7, 3, 12, 1, 9};   // inline initialisation
int[][] grid = new int[3][4];   // 3 rows, 4 cols — each row is its own array object
```

## Access, Update, Length

```java
int x = arr[2];        // O(1) — direct offset computation
arr[2] = 99;           // O(1) — same mechanism
int n = arr.length;    // field (not method) — no parentheses
```

## Prefix Sum — answer range queries in O(1)

Build the prefix array once, then any subarray sum is a single subtraction.

```
Original:  [1,  2,  3,  4,  5]
Prefix:    [0,  1,  3,  6, 10, 15]
           ↑ extra 0 at index 0 simplifies the formula

sum(l, r) = prefix[r+1] - prefix[l]
sum(1, 3) = prefix[4]  - prefix[1] = 10 - 1 = 9  ✓  (2+3+4)
```

```java
int[] pref = new int[n + 1];
for (int i = 0; i < n; i++) pref[i+1] = pref[i] + arr[i];
int rangeSum = pref[r+1] - pref[l];   // O(1)
```

## Kadane's Algorithm — Maximum Subarray Sum O(n)

At each index decide: 'Is it better to extend the existing run, or start fresh here?'

```
arr:         [-2,  1, -3,  4, -1,  2,  1, -5,  4]
currentSum:  [-2,  1, -2,  4,  3,  5,  6,  1,  5]
maxSum:      [-2,  1,  1,  4,  4,  5,  6,  6,  6]  ← answer = 6
```

```java
int maxSum = arr[0], cur = arr[0];
for (int i = 1; i < arr.length; i++) {
    cur    = Math.max(arr[i], cur + arr[i]);   // extend or restart
    maxSum = Math.max(maxSum, cur);
}
```

## Two-Pointer on Sorted Array — Two Sum O(n)

```
Sorted: [1, 2, 3, 7, 11, 15]   target = 9
         l                  r   sum=16 > 9 → r--
         l              r       sum=12 > 9 → r--
         l          r           sum= 8 < 9 → l++
            l       r           sum=11 > 9 → r--
            l   r               sum= 9 == 9 ✓
```

## Dutch National Flag — Sort 0s/1s/2s O(n) O(1)

Three active zones maintained by three pointers:

```
[confirmed 0s | confirmed 1s | unsorted | confirmed 2s]
              low            mid        high
```

```java
int low = 0, mid = 0, high = n - 1;
while (mid <= high) {
    if      (arr[mid] == 0) swap(arr, low++, mid++);
    else if (arr[mid] == 1) mid++;
    else                    swap(arr, mid, high--);  // mid NOT incremented
}
```

## 2D Arrays — Spiral Traversal

```
┌─────────────────┐
│  1  2  3  4  5  │  ← top row left→right
│ 16 17 18 19  6  │
│ 15 24 25 20  7  │
│ 14 23 22 21  8  │
│ 13 12 11 10  9  │  ← bottom row right→left
└─────────────────┘
Maintain 4 boundaries: top, bottom, left, right — shrink after each direction.
```

## Complexity Cheatsheet

| Operation | Time | Notes |
|---|---|---|
| Access arr[i] | O(1) | Direct memory offset |
| Search (unsorted) | O(n) | Linear scan |
| Insert at end (ArrayList) | O(1) amortised | Resize doubles capacity |
| Insert at middle | O(n) | Must shift elements |
| Prefix sum query | O(1) + O(n) preprocess | Space O(n) |
| Kadane's max subarray | O(n) | Space O(1) |

## Common Pitfalls
- Off-by-one: `< arr.length` not `<= arr.length`
- `arr2 = arr1` copies the **reference** — both point to same array; use `Arrays.copyOf`
- `int` overflow when summing many large values — cast to `long`
- `arr.length` is a field, `list.size()` is a method — don't mix them up

## Connections
- **Strings** — `char[]` is an array; many string algorithms use array indexing
- **Sliding Window** — subarray problems extend prefix sums and two-pointer
- **Sorting** — many array patterns require sorted input first
- **Two Pointers** — converging pointers work on sorted arrays
"""

# ─────────────────────────────────────────────────────────────────────────────
# STRINGS — upgrade guide
# ─────────────────────────────────────────────────────────────────────────────
STRINGS_GUIDE = """\
# Strings in Java

A Java `String` is an **immutable sequence of char values** backed by a `char[]` internally. Immutable means every 'modification' actually creates a brand-new object. Picture ice — you can't reshape it; you melt it and recast.

```
String s = "hello";
s = s + " world";    // ← "hello" object is NOT changed.
                     //   A NEW object "hello world" is created.
                     //   The old "hello" is abandoned.
```

## String vs StringBuilder — the Memory Story

```
// BAD — 1000 concatenations
String result = "";
for (int i = 0; i < 1000; i++)
    result += words[i];     // creates 1000 intermediate String objects
                            // total characters copied: 0+1+2+...+999 = O(n²)

// GOOD — StringBuilder uses a resizable char[] buffer
StringBuilder sb = new StringBuilder();
for (String word : words) sb.append(word);   // O(n) total copies
String result = sb.toString();               // one final copy
```

## Character Frequency — two strategies

```java
// Strategy 1: int[26] — for lowercase English only, O(1) array access
int[] freq = new int[26];
for (char c : s.toCharArray()) freq[c - 'a']++;

// Strategy 2: HashMap — for any character set (Unicode, mixed case, digits)
Map<Character, Integer> freq = new HashMap<>();
freq.merge(c, 1, Integer::sum);
```

## Palindrome Check — two-pointer visualisation

```
s = "r a c e c a r"
     l             r    r==r ✓  → l++, r--
       l         r      a==a ✓  → l++, r--
         l     r        c==c ✓  → l++, r--
           l r          e==e ✓  → l++, r--
           l > r        loop ends — IS palindrome
```

```java
boolean isPalindrome(String s) {
    int l = 0, r = s.length() - 1;
    while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false;
    return true;
}
```

## Anagram Detection — sort vs frequency

```
"listen" sorted → "eilnst"
"silent" sorted → "eilnst"   ← same key → anagram ✓

Or compare int[26] frequency arrays in O(26) = O(1)
```

## KMP Pattern Matching — O(n+m)

Naive matching rescans the text from scratch after each mismatch — O(n×m).
KMP precomputes a **failure function** (how far to jump back) so each character is examined at most twice.

```
Text:    a b c a b c a b d
Pattern: a b c a b d
                     ^ mismatch at d
KMP:     jump back 3 positions (failure[5]=3) and resume — never re-read 'abc'
```

## Important API Methods

```java
s.length()              // O(1)  — field access under the hood
s.charAt(i)             // O(1)  — direct array index
s.substring(l, r)       // O(r-l) — copies characters
s.indexOf("abc")        // O(n×m) naive — returns first index or -1
s.replace('a', 'b')     // O(n)  — returns new String
s.split(",")            // O(n)  — returns String[]
s.toCharArray()         // O(n)  — returns new char[] copy
s.equals(other)         // O(n)  — content compare
s == other              // O(1)  — REFERENCE compare (WRONG for content!)
String.valueOf(42)      // int/long/char → String
```

## String Interning — the `==` trap

```java
String a = "test";            // goes into the string pool
String b = "test";            // same pool entry
String c = new String("test"); // heap object, OUTSIDE pool

a == b   → true   (same pool reference)
a == c   → false  (different objects)
a.equals(c) → true  (same content)  ← ALWAYS use equals for content
```

## Complexity Cheatsheet

| Operation | Time | Space |
|---|---|---|
| charAt(i) | O(1) | O(1) |
| substring(l,r) | O(r-l) | O(r-l) |
| String + concat | O(n) per call | O(n) new object |
| StringBuilder append | O(1) amortised | O(1) extra |
| Palindrome check | O(n) | O(1) |
| Anagram (sort) | O(n log n) | O(n) |
| Anagram (freq) | O(n) | O(1) fixed |
| KMP match | O(n+m) | O(m) |

## Common Pitfalls
- `==` checks reference identity, NOT content — always use `.equals()`
- `s.concat("x")` returns a new String and discards result if not assigned — String is immutable
- `s.toCharArray()` returns a **copy** — modifying it does not change `s`
- Using `+=` in a loop for 1000+ iterations — use StringBuilder

## Connections
- **Arrays** — `char[]` underpins String; frequency counting uses `int[26]`
- **Two Pointers** — palindrome, reverse words
- **Hashing** — anagram grouping, sliding window with frequency constraint
- **Sliding Window** — longest substring with at most k distinct characters
"""

# ─────────────────────────────────────────────────────────────────────────────
# LINKED LISTS — upgrade guide
# ─────────────────────────────────────────────────────────────────────────────
LINKED_LISTS_GUIDE = """\
# Linked Lists in Java

A linked list is a chain of **node objects** scattered anywhere in memory. Each node holds a value and a pointer (`next`) to the next node. Unlike arrays, there are no mailbox rows — nodes live wherever the heap puts them.

```
Value:   7      3     12      1    null
        ┌───┐  ┌───┐  ┌────┐  ┌───┐
        │ 7 │→ │ 3 │→ │ 12 │→ │ 1 │→ null
        └───┘  └───┘  └────┘  └───┘
         head
```

## Node Definition

```java
class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}
```

## Singly vs Doubly Linked List

```
Singly:  head → [7|→] → [3|→] → [12|→] → null
                                           (no going back)

Doubly:  head ⇌ [←|7|→] ⇌ [←|3|→] ⇌ [←|12|→] ⇌ null
                                           (navigate both ways)
```

## Reversal — the three-pointer dance

Visualise three runners on the chain: `prev`, `cur`, `next`.

```
Step 0:  null ← prev   cur=7 → 3 → 12 → null
Step 1:  null ← 7      cur=3 → 12 → null    (7.next = null)
Step 2:  null ← 7 ← 3  cur=12 → null        (3.next = 7)
Step 3:  null ← 7 ← 3 ← 12  cur=null        (12.next = 3)
Return prev (= node 12) — new head
```

```java
ListNode reverse(ListNode head) {
    ListNode prev = null, cur = head;
    while (cur != null) {
        ListNode next = cur.next;   // 1. save next BEFORE breaking the link
        cur.next = prev;            // 2. flip the arrow
        prev = cur;                 // 3. advance prev
        cur = next;                 // 4. advance cur
    }
    return prev;  // last non-null node = new head
}
```

## Fast/Slow Pointer (Floyd's Tortoise and Hare)

Two runners start at head. Slow moves 1 step, fast moves 2 steps per iteration.

**Finding the middle:**
```
List:  1 → 2 → 3 → 4 → 5
       s/f
       1    2    3
       ↑f        ↑f       fast reaches end
            ↑s          slow is at middle (3)
```

**Cycle detection:** If the list has a loop, fast eventually laps slow — they meet.
```
No cycle: fast reaches null → no cycle
Cycle:    fast == slow at some node → cycle detected
```

```java
boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) return true;
    }
    return false;
}
```

## Merge Two Sorted Lists

```
l1: 1 → 3 → 5
l2: 2 → 4 → 6

Compare heads: 1 < 2 → take from l1:  1 →
               3 > 2 → take from l2:  1 → 2 →
               3 < 4 → take from l1:  1 → 2 → 3 → …
Result: 1 → 2 → 3 → 4 → 5 → 6
```

Use a **dummy head** node — it eliminates special cases for inserting the very first node.

## Dummy Head — removes edge-case code

```java
ListNode dummy = new ListNode(0);
ListNode tail = dummy;
// ... build list by setting tail.next = newNode; tail = tail.next;
return dummy.next;  // real head
```

## K-th Node from End — one pass

```
k = 2, list: 1 → 2 → 3 → 4 → 5
lead starts k=2 steps ahead of follow:
lead:   1  2  3  4  5  null
follow: 1  2  3  4       ← when lead is null, follow = k-th from end = 4
```

## LRU Cache — LinkedList + HashMap

`HashMap<key, Node>` gives O(1) lookup.
`DoublyLinkedList` gives O(1) move-to-front and evict-from-tail.
Together: O(1) get and put.

## Complexity Cheatsheet

| Operation | Time | Notes |
|---|---|---|
| Head insert / delete | O(1) | Only pointer updates |
| Tail insert (with tail ptr) | O(1) | |
| Access by index | O(n) | Must walk from head |
| Search | O(n) | |
| Reversal | O(n) O(1) space | Three pointer iterative |
| Find middle | O(n) | Fast/slow pointer |
| Cycle detection | O(n) O(1) space | Floyd's algorithm |

## Common Pitfalls
- Save `cur.next` to a temp variable **before** redirecting `cur.next` — or you lose the rest of the chain
- Always handle `head == null` and single-node lists as base cases
- Doubly linked list: must update BOTH `prev` and `next` on insert/delete
- `LinkedList` in Java is a doubly linked list — good for queue/stack, bad for random access

## Connections
- **Stacks/Queues** — both can be implemented with a linked list
- **Two Pointers** — fast/slow pointer is a two-pointer technique on a list
- **Hashing** — HashMap + linked list = O(1) LRU cache
"""

# ─────────────────────────────────────────────────────────────────────────────
# STACKS — upgrade guide
# ─────────────────────────────────────────────────────────────────────────────
STACKS_GUIDE = """\
# Stacks in Java

A stack is a **LIFO** (Last In, First Out) container. Imagine a stack of plates: you can only add or remove from the **top**. The plate you placed last is always the first one you pick up.

```
     push(C)        pop()
       ↓              ↑
   ┌───────┐      ┌───────┐
   │   C   │  →   │       │
   │   B   │      │   B   │
   │   A   │      │   A   │
   └───────┘      └───────┘
     top=C          top=B
```

## Java Implementation — prefer ArrayDeque over Stack

```java
// ✗ java.util.Stack — synchronized (legacy), avoids
// ✓ ArrayDeque used as a stack
Deque<Integer> stack = new ArrayDeque<>();
stack.push(10);        // add to TOP — O(1)
int top = stack.peek();  // view TOP without removing — O(1)
int out = stack.pop();   // remove TOP — O(1)
boolean empty = stack.isEmpty();
```

## Balanced Parentheses — matching open/close pairs

The stack remembers the most recent unmatched opener — perfect for LIFO matching.

```
Input: ( [ { } ] )

Push (  → stack: [(]
Push [  → stack: [(, []
Push {  → stack: [(, [, {]
See }   → pop {, matches → stack: [(, []
See ]   → pop [, matches → stack: [(]
See )   → pop (, matches → stack: []
Stack empty → BALANCED ✓

Input: ( ]
Push (  → stack: [(]
See ]   → pop (, mismatch! → NOT BALANCED ✗
```

```java
boolean isBalanced(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '[' || c == '{') stack.push(c);
        else {
            if (stack.isEmpty()) return false;
            char top = stack.pop();
            if ((c==')' && top!='(') || (c==']' && top!='[') || (c=='}' && top!='{'))
                return false;
        }
    }
    return stack.isEmpty();
}
```

## Monotonic Stack — Next Greater Element

Maintain a stack of **decreasing** candidates. The moment you see an element larger than the top, the top has found its 'next greater'.

```
nums:  [2, 1, 5, 3, 6, 4]
                          answer for each index:

Index 0 (2): push 2    → stack: [2]
Index 1 (1): push 1    → stack: [2, 1]
Index 2 (5): 5 > 1 → pop 1, ans[1]=5; 5 > 2 → pop 2, ans[0]=5; push 5 → stack: [5]
Index 3 (3): push 3    → stack: [5, 3]
Index 4 (6): 6 > 3 → pop 3, ans[3]=6; 6 > 5 → pop 5, ans[2]=6; push 6 → stack: [6]
Index 5 (4): push 4    → stack: [6, 4]
Remaining: ans[4]=-1, ans[5]=-1 (no next greater)

Final: [5, 5, 6, 6, -1, -1]
```

```java
int[] nextGreater(int[] nums) {
    int n = nums.length;
    int[] ans = new int[n];
    Arrays.fill(ans, -1);
    Deque<Integer> stack = new ArrayDeque<>();  // stores indices
    for (int i = 0; i < n; i++) {
        while (!stack.isEmpty() && nums[stack.peek()] < nums[i])
            ans[stack.pop()] = nums[i];
        stack.push(i);
    }
    return ans;
}
```

## Min Stack — O(1) getMin

Keep a **parallel stack** that records the minimum at each depth level.

```
Push 5: main=[5],   minStack=[5]
Push 3: main=[5,3], minStack=[5,3]
Push 7: main=[5,3,7], minStack=[5,3,3]  ← min stays 3
Pop:    main=[5,3], minStack=[5,3]       ← getMin()=3 still correct
Pop:    main=[5],   minStack=[5]         ← getMin()=5
```

## Largest Rectangle in Histogram

Use indices (not values) in the stack — you need widths, not just heights.

```
heights: [2, 1, 5, 6, 2, 3]
          0  1  2  3  4  5

When you pop height h at index i because a shorter bar arrived:
  width = current_index - stack.peek() - 1   (the left boundary)
  area  = h × width
```

## Call Stack — recursion visualised

Every function call pushes a **frame** containing local variables and return address:

```
factorial(4)
├── frame: n=4, awaiting factorial(3)
│   ├── frame: n=3, awaiting factorial(2)
│   │   ├── frame: n=2, awaiting factorial(1)
│   │   │   └── frame: n=1, returns 1         ← BASE CASE
│   │   └── returns 2
│   └── returns 6
└── returns 24
```
Too many frames → **StackOverflowError**. Fix: convert to iterative + explicit stack.

## Complexity Cheatsheet

| Operation | ArrayDeque Time |
|---|---|
| push | O(1) amortised |
| pop | O(1) |
| peek | O(1) |
| isEmpty | O(1) |
| Monotonic stack (n elements) | O(n) total — each element pushed and popped once |

## Common Pitfalls
- Calling `pop()` on empty stack → `NoSuchElementException` — always check `isEmpty()` first
- Using `java.util.Stack` in interviews — slower (synchronized) and has legacy quirks
- Monotonic stack: storing **values** when you need **indices** for distance/width calculations
- Undo/redo needs **two** stacks — one for undo history, one for redo

## Connections
- **Recursion** — the call stack IS a stack; convert any recursion to iteration with an explicit stack
- **Graphs** — iterative DFS uses an explicit stack
- **Queues** — LIFO vs FIFO; two stacks can simulate a queue
- **Monotonic Stack** — powers: next greater/smaller, histogram, stock span problems
"""

# ─────────────────────────────────────────────────────────────────────────────
# NEW TOPIC: dsa-java-trees (all tree types)
# ─────────────────────────────────────────────────────────────────────────────
TREES_GUIDE = """\
# Tree Data Structures in Java

A tree is a **hierarchical structure**: one root, no cycles, every node reachable from the root. Different tree types enforce different invariants to make specific operations fast. Choosing the right tree means knowing which invariant you need.

```
         GENERIC TREE TAXONOMY
         ┌──────────────────────────────────┐
         │           Tree                   │
         │     ┌──────┴──────┐             │
         │  Binary          N-ary           │
         │  ┌─────┴──────┐               │
         │ BST       Balanced             │
         │           ┌────┴────┐          │
         │          AVL    Red-Black       │
         │  Heaps (complete binary)        │
         │  Segment / Fenwick (implicit)   │
         │  B-Tree / B+-Tree (disk)        │
         └──────────────────────────────────┘
```

## Binary Search Tree (BST)

Invariant: **left < node < right** (all values, recursively).

```
        8
       / \\
      3   10
     / \\    \\
    1   6   14
       / \\
      4   7

In-order: 1 3 4 6 7 8 10 14  ← always sorted
```

Operations: O(log n) average, O(n) worst (degenerate/skewed tree from sorted inserts).

## AVL Tree — Self-Balancing BST

Invariant: **|height(left) - height(right)| ≤ 1** at every node (balance factor ∈ {-1, 0, 1}).

When an insert/delete breaks this, a **rotation** restores balance in O(1).

```
Insert 30 into:     20            Becomes (Left Rotation):    25
                   /  \\                                      /  \\
                  10   25                                   20   30
                         \\                                 /  \\
                          30  ← imbalance (BF=−2 at 20) 10   25

AVL height: always O(log n) → guaranteed O(log n) search, insert, delete.
```

## Red-Black Tree — Colour-Based Balance

Five invariants (including: root=black, no two consecutive reds, equal black-height on all paths) ensure height ≤ 2 log₂(n+1).

Why Java uses it: `TreeMap`, `TreeSet`, and `HashMap`'s long-chain bucket all use Red-Black trees.

```
        B(8)
       /     \\
     R(3)   B(10)
    /   \\       \\
  B(1) B(6)    R(14)
       /   \\
     R(4)  R(7)

B=Black, R=Red — satisfies all RB properties.
```

AVL vs Red-Black: AVL is more strictly balanced (faster reads), but Red-Black does fewer rotations on insert/delete (faster writes). Java chose Red-Black for its collections.

## Segment Tree — Range Queries in O(log n)

A segment tree stores aggregate values (sum, min, max) for every subarray interval.

```
Array:  [1, 3, 2, 7, 9, 11]

Segment tree (sum):
                 33 [0..5]
               /           \\
          6 [0..2]       27 [3..5]
          /      \\       /      \\
       4 [0..1] 2[2] 16 [3..4] 11[5]
       /    \\       /    \\
     1[0]  3[1]  7[3]  9[4]

Query sum(1,4) = 3+2+7+9 = 21 → O(log n) by combining at most 2log(n) nodes.
Update arr[2] = 10 → O(log n) — walk path from leaf to root.
```

## Fenwick Tree (Binary Indexed Tree) — Compact Prefix Sums

A Fenwick tree stores partial sums using bit manipulation on indices.
Simpler code than a segment tree; supports point-update + prefix-sum in O(log n).

```java
void update(int[] bit, int i, int delta) {
    for (i++; i < bit.length; i += i & (-i)) bit[i] += delta;
}
int query(int[] bit, int i) {
    int sum = 0;
    for (i++; i > 0; i -= i & (-i)) sum += bit[i];
    return sum;
}
// Range sum(l,r) = query(r) - query(l-1)
```

## Trie — Prefix Tree

Each edge is a character; each root-to-node path is a prefix.
O(L) insert, search, and startsWith (L = string length), independent of n.
(Full coverage in dsa-java-tries topic.)

## B-Tree / B+-Tree — Disk-Optimised

Used inside every relational database index (MySQL InnoDB uses B+-Tree).

```
B-TREE node holds multiple keys and pointers (degree d):
    ┌─────────────────────┐
    │  10  │  20  │  30   │   ← keys
    └──┬───┴───┬──┴───┬───┘
       ↓       ↓      ↓
   [<10]    [10-20] [>30]   ← subtrees
```

Property: all leaves at the same depth. Node holds d to 2d keys.
Why disks? Minimises I/O: one disk read fetches an entire node (many keys).

## Heap (Complete Binary Tree)

Shape: complete tree stored in array (no pointers needed).
Order: min-heap: parent ≤ children; max-heap: parent ≥ children.
O(log n) insert/extract-min. O(n) heapify.
(Full coverage in dsa-java-heaps topic.)

## Choosing the Right Tree

| Need | Use |
|---|---|
| Sorted iteration + range delete | TreeMap / TreeSet (Red-Black) |
| Priority queue (always want min/max) | PriorityQueue (min-heap) |
| Prefix search / autocomplete | Trie |
| Range sum / range min queries with updates | Segment Tree |
| Prefix sum with point updates (simpler code) | Fenwick Tree |
| Disk-based sorted index | B+-Tree |
| Height-balanced BST with fastest read | AVL Tree |

## Common Pitfalls
- Confusing BST (sorted but may be skewed) with balanced BST (AVL, RB — always O(log n))
- Segment tree: 1-indexed vs 0-indexed — fix one convention and stick to it
- Fenwick tree: `i & (-i)` isolates the lowest set bit — easy to mis-apply without visualising binary
- B-Tree vs B+-Tree: B+-Tree stores all data in leaves (leaves linked) — gives efficient range scans

## Connections
- **Binary Trees** — all tree types are specialisations of binary or k-ary trees
- **Heaps** — complete binary tree with a different (order not search) invariant
- **Hashing** — Java's HashMap uses Red-Black trees for long collision chains
- **Graphs** — trees are acyclic connected graphs; tree algorithms generalise to graph traversal
"""

TREES_QUESTIONS = [
    {"id":"djt-q1","type":"mcq","prompt":"A BST guarantees O(log n) search when:","choices":["It stores only integers","It is balanced — height O(log n)","It has no duplicate keys","All left children are 0"],"answerIndex":1,"explanation":"An unbalanced BST (e.g. sorted inserts) degenerates to O(n) height. Balance is required for O(log n).","tags":["bst"]},
    {"id":"djt-q2","type":"mcq","prompt":"In-order traversal of a BST produces:","choices":["Pre-order sequence","Reverse sorted output","Sorted ascending output","Level-by-level output"],"answerIndex":2,"explanation":"BST invariant left<root<right means in-order (left→root→right) always yields sorted order.","tags":["bst","traversal"]},
    {"id":"djt-q3","type":"mcq","prompt":"AVL tree balance factor at every node must be:","choices":["-2, -1, 0, 1, or 2","-1, 0, or 1","Always 0","0 or 1"],"answerIndex":1,"explanation":"AVL: |height(left) - height(right)| ≤ 1. Factor outside {-1,0,1} triggers a rotation.","tags":["avl"]},
    {"id":"djt-q4","type":"mcq","prompt":"What triggers a rotation in an AVL tree?","choices":["Any insert or delete","An insert or delete that makes a node's balance factor +2 or -2","Finding a duplicate key","Reaching height > 10"],"answerIndex":1,"explanation":"When the balance factor goes outside {-1,0,1}, the tree is rebalanced via single or double rotation.","tags":["avl"]},
    {"id":"djt-q5","type":"mcq","prompt":"Java's TreeMap and TreeSet are backed by:","choices":["AVL tree","Min-heap","Red-Black tree","Skip list"],"answerIndex":2,"explanation":"Java chose Red-Black trees for its sorted collections because they require fewer rotations on insert/delete than AVL trees.","tags":["red-black","java"]},
    {"id":"djt-q6","type":"mcq","prompt":"Red-Black tree vs AVL tree — which is faster for read-heavy workloads?","choices":["Red-Black — fewer rotations","AVL — more strictly balanced so shorter, faster search paths","They are identical","Depends on key type"],"answerIndex":1,"explanation":"AVL height ≤ 1.44 log₂n vs Red-Black ≤ 2 log₂(n+1). Stricter balance = slightly faster reads.","tags":["avl","red-black"]},
    {"id":"djt-q7","type":"mcq","prompt":"A Segment Tree with n leaves answers range sum queries in:","choices":["O(n)","O(log n)","O(1)","O(n log n)"],"answerIndex":1,"explanation":"Each query visits at most 4 log n nodes by combining pre-computed interval aggregates.","tags":["segment-tree"]},
    {"id":"djt-q8","type":"mcq","prompt":"A Segment Tree point-update (change one element) runs in:","choices":["O(1)","O(log n)","O(n)","O(n log n)"],"answerIndex":1,"explanation":"Update walks from leaf to root — O(log n) nodes on the path.","tags":["segment-tree"]},
    {"id":"djt-q9","type":"mcq","prompt":"Fenwick tree (BIT) update uses the expression i += i & (-i) to:","choices":["Move to parent","Move to left child","Move to next responsible index (next ancestor in BIT structure)","Detect overflow"],"answerIndex":2,"explanation":"i & (-i) isolates the lowest set bit; adding it jumps to the next BIT node that covers index i.","tags":["fenwick"]},
    {"id":"djt-q10","type":"mcq","prompt":"Why does a B+-Tree (not B-Tree) store all data in leaf nodes?","choices":["Simpler implementation","Leaf nodes are linked — enables O(n) forward range scan without going back up","Saves space","Required by SQL standard"],"answerIndex":1,"explanation":"Linked leaves let the DB engine scan a range by following leaf pointers without re-traversing internal nodes.","tags":["b-tree"]},
    {"id":"djt-q11","type":"mcq","prompt":"A Trie stores n words of average length L. Search time for one word is:","choices":["O(n)","O(L)","O(n × L)","O(log n)"],"answerIndex":1,"explanation":"Trie navigates exactly L edges regardless of how many words are stored.","tags":["trie"]},
    {"id":"djt-q12","type":"mcq","prompt":"Heap differs from BST in that a heap:","choices":["Is always sorted","Has the root as minimum (min-heap) but does NOT support efficient arbitrary search","Requires O(n log n) build","Cannot store duplicates"],"answerIndex":1,"explanation":"Heap order: parent ≤ children (min-heap). There is no left < root < right invariant — searching is O(n).","tags":["heap","bst"]},
    {"id":"djt-q13","type":"codeOutput","prompt":"BST insert order [5,3,7,1,4]. In-order traversal output:","code":"// Build BST inserting in order: 5, 3, 7, 1, 4\n// In-order traversal","choices":["5 3 7 1 4","1 3 4 5 7","5 7 3 4 1","1 4 3 7 5"],"answerIndex":1,"explanation":"In-order of a BST always yields sorted order: 1,3,4,5,7.","tags":["bst","traversal"]},
    {"id":"djt-q14","type":"mcq","prompt":"Inserting already-sorted data into a plain BST creates:","choices":["A perfectly balanced tree","A degenerate tree (linked list) with O(n) height","An AVL tree automatically","A Red-Black tree automatically"],"answerIndex":1,"explanation":"Each new element is always inserted as the rightmost child — the tree grows as a straight line.","tags":["bst"]},
    {"id":"djt-q15","type":"mcq","prompt":"Segment Tree vs Fenwick Tree — when should you choose Fenwick?","choices":["When you need range min/max queries","When range is 2D","When you only need prefix sums with point updates — simpler code, same O(log n)","When n > 10^6"],"answerIndex":2,"explanation":"Fenwick only supports associative invertible operations (sum). Segment tree is more flexible but has more code.","tags":["segment-tree","fenwick"]},
    {"id":"djt-q16","type":"mcq","prompt":"A complete binary tree is stored in an array where index 0 is the root. The right child of index 3 is at:","choices":["6","7","8","4"],"answerIndex":2,"explanation":"right child of i = 2i+2. right child of 3 = 8.","tags":["heap","array-index"]},
    {"id":"djt-q17","type":"multi","prompt":"Which tree structures guarantee O(log n) worst-case search?","choices":["Plain BST","AVL Tree","Red-Black Tree","Segment Tree"],"answerIndexes":[1,2],"explanation":"Plain BST degenerates to O(n). Segment Tree is not a search tree — it answers range queries, not individual searches.","tags":["comparison"]},
    {"id":"djt-q18","type":"mcq","prompt":"B-Tree nodes hold multiple keys to minimise disk I/O because:","choices":["Multiple keys reduce tree height — one disk read fetches an entire 4KB node with many keys","CPUs prefer multiple keys","It avoids pointer arithmetic","Databases require sorted output"],"answerIndex":0,"explanation":"A B-Tree of degree 500 has height ~log₅₀₀(n) — drastically few disk reads vs a binary tree's log₂(n).","tags":["b-tree"]},
    {"id":"djt-q19","type":"mcq","prompt":"AVL tree single left rotation is needed when:","choices":["Left subtree is too tall — left-left case","Right subtree is too tall — right-right case","Both subtrees equal height","Root has no parent"],"answerIndex":1,"explanation":"Right-right imbalance (balance factor -2) is fixed by a single left rotation. Right-left imbalance requires a double rotation.","tags":["avl"]},
    {"id":"djt-q20","type":"mcq","prompt":"Which tree gives O(L) prefix existence check (where L = prefix length), independent of number of stored words?","choices":["BST","Red-Black Tree","Trie","Segment Tree"],"answerIndex":2,"explanation":"Trie navigates exactly L edges for any prefix query, regardless of the number of stored words n.","tags":["trie"]}
]

TREES_FLASHCARDS = [
    {"id":"djt-fc1","front":"BST invariant","back":"All left subtree values < node < all right subtree values (recursively).","tags":["bst"]},
    {"id":"djt-fc2","front":"AVL balance factor","back":"|height(left) - height(right)| ≤ 1. Violation triggers O(1) rotation.","tags":["avl"]},
    {"id":"djt-fc3","front":"Red-Black vs AVL","back":"RB: fewer rotations on write (Java collections). AVL: stricter balance = faster reads.","tags":["red-black","avl"]},
    {"id":"djt-fc4","front":"Segment Tree ops","back":"Build O(n). Query O(log n). Update O(log n). Supports non-invertible ops (min/max).","tags":["segment-tree"]},
    {"id":"djt-fc5","front":"Fenwick Tree ops","back":"Update: i += i&(-i). Query: i -= i&(-i). Both O(log n). Only invertible ops (sum).","tags":["fenwick"]},
    {"id":"djt-fc6","front":"B+-Tree advantage","back":"All data in linked leaves → range scan O(k) after O(log n) position find. Used in DB indexes.","tags":["b-tree"]},
    {"id":"djt-fc7","front":"Heap array index","back":"parent(i)=(i-1)/2. left(i)=2i+1. right(i)=2i+2. Works because heap is a complete binary tree.","tags":["heap"]},
    {"id":"djt-fc8","front":"Choosing a tree","back":"Sorted iteration→TreeMap. Priority→Heap. Prefix search→Trie. Range queries→SegTree/Fenwick. Disk→B+Tree.","tags":["comparison"]},
]

TREES_PROJECT = {
    "brief": "Write TreeTypesDemos.java with:\n1. BSTMap<K extends Comparable<K>, V> with put, get, inorderKeys\n2. fenwickSum(int[] arr) — build BIT, then answer range sum queries\n3. A short written comparison (comments) of AVL vs Red-Black for a read-heavy vs write-heavy use case\n4. A demonstration of Java's TreeMap proving O(log n) sorted iteration",
    "checklist": [
        {"id":"c1","text":"BSTMap.inorderKeys() returns keys in sorted order","weight":1},
        {"id":"c2","text":"fenwickSum correctly answers at least 3 range queries","weight":1},
        {"id":"c3","text":"Written comparison explains the rotation trade-off clearly","weight":1},
        {"id":"c4","text":"TreeMap demo shows firstKey(), lastKey(), and subMap()","weight":1}
    ],
    "hints": [
        "BST put: recurse left if key < node.key, right if key > node.key, overwrite if equal.",
        "Fenwick update: for(i++; i < bit.length; i += i & (-i)) bit[i] += delta.",
        "Fenwick query: for(i++; i > 0; i -= i & (-i)) sum += bit[i].",
    ]
}

# ─────────────────────────────────────────────────────────────────────────────
# WRITE FILES
# ─────────────────────────────────────────────────────────────────────────────
def patch_guide(filename, new_guide):
    path = OUT / filename
    data = json.loads(path.read_text())
    data["guide"] = new_guide
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Patched guide: {filename}  ({len(new_guide)} chars)")

def write_new_topic(data):
    path = OUT / f"{data['id']}.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Created: {path.name}  {len(data['questions'])}q {len(data['flashcards'])}fc {len(data['guide'])}chars")

OUT.mkdir(parents=True, exist_ok=True)

patch_guide("dsa-java-arrays.json",       ARRAYS_GUIDE)
patch_guide("dsa-java-strings.json",      STRINGS_GUIDE)
patch_guide("dsa-java-linked-lists.json", LINKED_LISTS_GUIDE)
patch_guide("dsa-java-stacks.json",       STACKS_GUIDE)

write_new_topic({
    "id":         "dsa-java-trees",
    "unit":       9,
    "order":      78,
    "title":      "Tree Data Structures in Java",
    "summary":    "BST, AVL, Red-Black, Segment Tree, Fenwick Tree, Trie, B-Tree — when to use each and how they keep operations fast.",
    "prereqs":    ["dsa-java-binary-trees", "dsa-java-heaps"],
    "guide":      TREES_GUIDE,
    "questions":  TREES_QUESTIONS,
    "flashcards": TREES_FLASHCARDS,
    "project":    TREES_PROJECT,
})

HASHING_GUIDE = """\
# Hashing in Java

Hashing converts a key into an **array index** through a hash function. The goal is to spread keys uniformly so that finding, inserting, and deleting any key takes O(1) on average — without sorting anything.

```
Key "apple"  →  hashCode()  →  mod table-size  →  index 3
Key "grape"  →  hashCode()  →  mod table-size  →  index 7
Key "mango"  →  hashCode()  →  mod table-size  →  index 3  ← COLLISION with "apple"
```

## How Java HashMap Works Internally

```
Backing array (16 buckets by default):
 [0]  →  null
 [1]  →  Entry("one", 1)
 [2]  →  null
 [3]  →  Entry("apple","fruit") → Entry("mango","fruit")  ← chained (collision)
 ...
 [15] →  null

When chain length > 8 AND table size >= 64 → chain converts to a RED-BLACK TREE (O(log n) fallback)
```

```java
Map<String, Integer> map = new HashMap<>();
map.put("alice", 90);          // O(1) avg
map.get("alice");              // O(1) avg
map.getOrDefault("bob", 0);    // safe get with fallback
map.containsKey("alice");      // O(1)
map.remove("alice");           // O(1)
map.merge("word", 1, Integer::sum);  // put-or-update in one call
```

## Collision Handling — two main strategies

```
CHAINING (Java's default):
  Each bucket holds a linked list (or tree) of entries.
  Collision → just append to the chain.

  Bucket 3: [apple] → [mango] → null

OPEN ADDRESSING (linear probing):
  On collision, find the next open slot.
  Bucket 3 taken → try 4, 5, … wrap around.
  Requires careful delete (tombstone markers).
```

## Load Factor and Rehashing

```
load factor = entries / buckets

Java default: initial capacity=16, load factor=0.75
When entries > 16 × 0.75 = 12 → REHASH:
  • Allocate new array (double size = 32)
  • Re-hash every entry into new positions
  • O(n) cost, but amortised O(1) per insert overall
```

## HashSet — just a HashMap with dummy values

```java
Set<String> seen = new HashSet<>();
seen.add("alice");          // O(1)
seen.contains("alice");     // O(1)
seen.remove("alice");       // O(1)

// Detect duplicates in O(n):
boolean hasDuplicate(int[] arr) {
    Set<Integer> seen = new HashSet<>();
    for (int x : arr) if (!seen.add(x)) return true;
    return false;
}
```

## Frequency Counting Pattern

```java
// Count word frequencies:
Map<String, Integer> freq = new HashMap<>();
for (String word : words)
    freq.merge(word, 1, Integer::sum);

// Top-K frequent: pair with a min-heap of size k
PriorityQueue<Map.Entry<String,Integer>> pq =
    new PriorityQueue<>(Comparator.comparingInt(Map.Entry::getValue));
for (var e : freq.entrySet()) {
    pq.offer(e);
    if (pq.size() > k) pq.poll();
}
```

## Two-Sum with HashMap — O(n)

```
nums = [2, 7, 11, 15], target = 9

i=0: need = 9-2 = 7, map does not have 7 → store {2:0}
i=1: need = 9-7 = 2, map HAS 2 at index 0 → return [0, 1]  ✓
```

```java
int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need)) return new int[]{seen.get(need), i};
        seen.put(nums[i], i);
    }
    return new int[]{-1, -1};
}
```

## Complexity Cheatsheet

| Operation | HashMap Average | HashMap Worst | TreeMap |
|---|---|---|---|
| get / put / remove | O(1) | O(n) (all in one bucket) | O(log n) |
| containsKey | O(1) | O(n) | O(log n) |
| Iteration | O(n) | O(n) | O(n) |

Use **TreeMap** when you need sorted key order. Use **HashMap** for pure O(1) operations.

## Common Pitfalls
- Using mutable objects as keys — hashCode/equals must be consistent; mutable key changes can make entries unreachable
- Comparing values with `==` instead of `.equals()` — objects need `.equals()` for content comparison
- Forgetting to override both `hashCode()` AND `equals()` in custom key classes
- `ConcurrentModificationException` — never modify a map while iterating it with `entrySet()` iterator; use `removeIf` or iterate a copy

## Connections
- **Arrays** — `int[26]` or `int[128]` is a fast fixed-size 'hash map' for bounded char sets
- **Heaps** — frequency map + min-heap solves Top-K in O(n log k)
- **Tries** — alternative to HashMap when prefix lookups are needed
- **Hashing + Linked List** — LRU cache uses HashMap for O(1) lookup + doubly linked list for O(1) eviction
"""

QUEUES_GUIDE = """\
# Queues and Deques in Java

A queue is **FIFO** (First In, First Out). Think of a checkout line at a supermarket: the first customer to join is the first to be served. Elements enter at the rear and leave from the front.

```
Enqueue (add to rear)                Dequeue (remove from front)
        ↓                                    ↑
  rear ──────────────────────── front
       │ C │ B │ A │               A leaves first (arrived first)
  rear ──────────────────────── front
```

## Java API — prefer ArrayDeque over LinkedList

```java
Queue<Integer> q = new ArrayDeque<>();

q.offer(1);         // add to rear — returns false if capacity exceeded (never for ArrayDeque)
q.add(2);           // add to rear — throws on failure
int front = q.peek();   // view front WITHOUT removing — null if empty
int out   = q.poll();   // remove front — null if empty
q.remove();             // remove front — throws NoSuchElementException if empty
q.isEmpty();
q.size();
```

## ArrayDeque — the Swiss army knife

A Deque (Double-Ended Queue) allows insert/remove at **both** ends:

```
addFirst(X) ──→ [X | A | B | C] ←── addLast(Y) → [X | A | B | C | Y]
removeFirst() returns X            removeLast() returns Y
```

```java
Deque<Integer> dq = new ArrayDeque<>();
dq.addFirst(1);    // push to front
dq.addLast(2);     // push to rear
dq.removeFirst();  // pop front
dq.removeLast();   // pop rear
dq.peekFirst();    dq.peekLast();

// Use as Stack:  push/pop/peek  (front operations)
// Use as Queue:  offer/poll     (addLast / removeFirst)
```

## Circular Queue — wrapping indices in an array

```
capacity = 5, initial front=0, rear=0, size=0

Enqueue A,B,C:  [A|B|C| | ]   front=0, rear=3, size=3
Dequeue A,B:    [ | |C| | ]   front=2, rear=3, size=1
Enqueue D,E,F:  [F| |C|D|E]   front=2, rear=1, size=4 ← wraps!

Wrap formula:  rear = (rear + 1) % capacity
               front = (front + 1) % capacity
```

```java
class CircularQueue {
    int[] arr; int front, size, cap;
    CircularQueue(int k) { arr = new int[k]; cap = k; }
    boolean enqueue(int val) {
        if (size == cap) return false;
        arr[(front + size) % cap] = val;
        size++; return true;
    }
    int dequeue() {
        if (size == 0) return -1;
        int v = arr[front];
        front = (front + 1) % cap; size--; return v;
    }
    boolean isFull()  { return size == cap; }
    boolean isEmpty() { return size == 0; }
}
```

## BFS — the queue's killer application

BFS expands outward from the source **one ring at a time**, like ripples in water.
Every node at distance k is processed before any at distance k+1.

```
Graph:  0──1──3
        |  |
        2──4

BFS from 0:
Queue: [0]      → process 0 → enqueue 1, 2 → Queue: [1,2]
Queue: [1,2]    → process 1 → enqueue 3, 4 → Queue: [2,3,4]
Queue: [2,3,4]  → process 2 (no new) → Queue: [3,4]
…
Distances: {0:0, 1:1, 2:1, 3:2, 4:2}
```

Mark visited **when enqueuing**, not when dequeuing — prevents duplicates.

## Level-Order Tree Traversal

Snapshot the queue size at the start of each outer loop iteration — that count tells you how many nodes are on the **current level**.

```java
Queue<TreeNode> q = new ArrayDeque<>();
if (root != null) q.offer(root);
while (!q.isEmpty()) {
    int levelSize = q.size();        // ← snapshot: exactly one level's worth
    for (int i = 0; i < levelSize; i++) {
        TreeNode n = q.poll();
        process(n);
        if (n.left  != null) q.offer(n.left);
        if (n.right != null) q.offer(n.right);
    }
}
```

## Sliding Window Maximum with Monotonic Deque

Maintain a **decreasing deque** of indices. Front = current window maximum.

```
nums = [1,3,-1,-3,5,3,6,7],  k=3

Window [1,3,-1]: deque=[1(idx1)]  max=3
Window [3,-1,-3]: deque=[1(idx1),4(idx…)]  after evictions max=3
…
O(n) total: each element pushed and popped at most once.
```

## Complexity Cheatsheet

| Operation | ArrayDeque |
|---|---|
| offer / add (rear) | O(1) amortised |
| poll / remove (front) | O(1) |
| peek | O(1) |
| BFS (V vertices, E edges) | O(V+E) |
| Level-order traversal | O(n) |
| Sliding window max | O(n) |

## Common Pitfalls
- `poll()` returns `null` on empty queue — use `isEmpty()` before polling, or use `remove()` if you want an exception
- LinkedList vs ArrayDeque: LinkedList allocates a node object per element (slower, more GC pressure); prefer ArrayDeque
- BFS: marking visited **after** polling (too late) lets the same node be enqueued multiple times

## Connections
- **Stacks** — LIFO counterpart; ArrayDeque can be both
- **Trees** — level-order traversal IS BFS on a tree
- **Graphs** — BFS finds shortest path (hop count) in unweighted graphs
- **Sliding Window** — monotonic deque optimises fixed-window max/min to O(n)
"""

RECURSION_GUIDE = """\
# Recursion in Java

Recursion is a function that calls **itself** with a smaller version of the same problem. Every recursive solution has two parts:

1. **Base case** — the smallest problem you can answer directly (no more calls needed)
2. **Recursive case** — break the problem down and rely on a self-call to handle the rest

```
factorial(4)
  └─ 4 × factorial(3)
           └─ 3 × factorial(2)
                    └─ 2 × factorial(1)
                              └─ 1  ← BASE CASE (return immediately)
                    returns 2×1 = 2
           returns 3×2 = 6
  returns 4×6 = 24
```

## The Call Stack — what really happens

Each function call pushes a **frame** (local variables + return address) onto the call stack. When a function returns, its frame is popped.

```
Stack grows ↓ during recursion, shrinks ↑ during return:

PUSH:  [fact(4)] → [fact(4)][fact(3)] → [fact(4)][fact(3)][fact(2)] → … → base case
POP:   base returns 1 → fact(2) computes 2 → fact(3) computes 6 → fact(4) computes 24
```

**StackOverflowError** occurs when the stack runs out of space — usually from infinite recursion or depth > ~10,000.

## Fibonacci — the overlapping subproblems problem

```
fib(5)
├── fib(4)
│   ├── fib(3)  ← computed again below ↓
│   └── fib(2)
└── fib(3)      ← DUPLICATE — fib(3) computed twice!
    ├── fib(2)
    └── fib(1)

Without caching: O(2^n) calls
With memoization: each fib(k) computed exactly once → O(n)
```

```java
int fib(int n, int[] memo) {
    if (n <= 1) return n;                         // base case
    if (memo[n] != -1) return memo[n];            // cached
    return memo[n] = fib(n-1, memo) + fib(n-2, memo);  // store before returning
}
```

## Three Recursion Patterns

```
PATTERN 1 — Linear (head recursion):
  process(list) = do(head) + process(tail)
  Example: sum of array, factorial

PATTERN 2 — Binary (divide-and-conquer):
  solve(arr) = merge(solve(left half), solve(right half))
  Example: merge sort, binary search

PATTERN 3 — Backtracking:
  explore(path) = for each choice:
                    add choice to path
                    explore(path)      ← go deeper
                    remove choice      ← undo (backtrack)
  Example: permutations, N-Queens, Sudoku
```

## Backtracking Visualised — Permutations of [1,2,3]

```
                   []
          /         |         \\
        [1]        [2]        [3]
       /   \\      /   \\      /   \\
    [1,2] [1,3] [2,1] [2,3] [3,1] [3,2]
      |     |     |     |     |     |
   [1,2,3][1,3,2][2,1,3][2,3,1][3,1,2][3,2,1]  ← 6 leaves = 3! permutations
```

```java
void permute(int[] nums, int start, List<List<Integer>> res) {
    if (start == nums.length) { res.add(/* collect */); return; }
    for (int i = start; i < nums.length; i++) {
        swap(nums, start, i);          // choose
        permute(nums, start + 1, res); // explore
        swap(nums, start, i);          // undo (backtrack)
    }
}
```

## Memoization vs Tabulation

```
MEMOIZATION (top-down): write recursive function, cache results
  ✓ Easy to derive — code mirrors the recurrence
  ✗ Call stack overhead; risk of StackOverflow for deep n

TABULATION (bottom-up): fill array from smallest to largest
  ✓ No recursion — no stack overhead
  ✓ Easier to space-optimise
  ✗ Must determine fill order manually
```

## Tail Recursion — last call is the recursive call

```java
// NOT tail recursive — multiplication happens AFTER the recursive call returns
int factorial(int n) { return n * factorial(n-1); }

// Tail recursive — accumulator holds result, no work after recursive call
int factorial(int n, int acc) { return n == 0 ? acc : factorial(n-1, n * acc); }
// Java does NOT optimise tail calls (unlike Haskell/Scala) — still risks StackOverflow
// Solution for deep recursion: convert to iterative manually
```

## When to Use Recursion vs Iteration

| Prefer recursion | Prefer iteration |
|---|---|
| Problem is naturally hierarchical (trees, graphs) | Simple loops over arrays |
| Backtracking / exhaustive search | When depth could exceed ~10k frames |
| Divide-and-conquer | Performance-critical inner loops |
| Code clarity matters more than micro-optimisation | When tail-call elimination isn't guaranteed (Java) |

## Common Pitfalls
- Missing base case → infinite recursion → StackOverflowError
- Base case is wrong (e.g. `n == 1` instead of `n <= 1`) → handles n=0 incorrectly
- Forgetting to **undo** the choice in backtracking → incorrect results
- Using -1 as memo sentinel when -1 is a valid answer → always recomputes

## Connections
- **Stacks** — recursion uses the call stack; iterative DFS/backtracking replaces it with an explicit Deque
- **Trees** — almost every tree problem is naturally recursive (base case = null node)
- **DP** — memoized recursion IS top-down DP
- **Divide and Conquer** — merge sort, quick sort, and binary search are recursive split-and-combine algorithms
"""

patch_guide("dsa-java-hashing.json",   HASHING_GUIDE)
patch_guide("dsa-java-queues.json",    QUEUES_GUIDE)
patch_guide("dsa-java-recursion.json", RECURSION_GUIDE)

print("\nAll done.")

