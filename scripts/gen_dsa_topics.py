#!/usr/bin/env python3
"""Generate DSA-in-Java topic JSON files for CS Mastery.

This script intentionally writes to src/content/topics. The older gen_stubs.py
writes next to itself, which is why it is not the right tool for app topic files.

Usage:
  python3 scripts/gen_dsa_topics.py
  python3 scripts/gen_dsa_topics.py --overwrite
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = ROOT / "src" / "content" / "topics"


def code(lang: str, body: str) -> str:
    return f"```{lang}\n{body.strip()}\n```"


def guide(title: str, intro: str, sections: list[tuple[str, str]], pitfalls: list[str], connections: list[str]) -> str:
    parts = [f"# {title}", intro]
    for heading, body in sections:
        parts.append(f"## {heading}\n{body}")
    parts.append("## Common Pitfalls\n" + "\n".join(f"- {p}" for p in pitfalls))
    parts.append("## Connections\n" + "\n".join(f"- **{c.split(':', 1)[0]}**{':' + c.split(':', 1)[1] if ':' in c else ''}" for c in connections))
    return "\n\n".join(parts)


def mcq(prefix: str, n: int, prompt: str, choices: list[str], answer: int, explanation: str, tags: list[str]) -> dict[str, Any]:
    return {
        "id": f"{prefix}-q{n}",
        "type": "mcq",
        "prompt": prompt,
        "choices": choices,
        "answerIndex": answer,
        "explanation": explanation,
        "tags": tags,
    }


def code_output(prefix: str, n: int, prompt: str, snippet: str, choices: list[str], answer: int, explanation: str, tags: list[str]) -> dict[str, Any]:
    return {
        "id": f"{prefix}-q{n}",
        "type": "codeOutput",
        "prompt": prompt,
        "code": snippet.strip(),
        "choices": choices,
        "answerIndex": answer,
        "explanation": explanation,
        "tags": tags,
    }


def multi(prefix: str, n: int, prompt: str, choices: list[str], answers: list[int], explanation: str, tags: list[str]) -> dict[str, Any]:
    return {
        "id": f"{prefix}-q{n}",
        "type": "multi",
        "prompt": prompt,
        "choices": choices,
        "answerIndexes": answers,
        "explanation": explanation,
        "tags": tags,
    }


def cards(prefix: str, items: list[tuple[str, str]], tag: str) -> list[dict[str, Any]]:
    return [
        {"id": f"{prefix}-fc{i}", "front": front, "back": back, "tags": [tag]}
        for i, (front, back) in enumerate(items, 1)
    ]


def project(brief: str, checklist: list[str], hints: list[str]) -> dict[str, Any]:
    return {
        "brief": brief,
        "checklist": [
            {"id": f"c{i}", "text": text, "weight": 1}
            for i, text in enumerate(checklist, 1)
        ],
        "hints": hints,
    }


def topic(
    sid: str,
    order: int,
    title: str,
    summary: str,
    prereqs: list[str],
    guide_text: str,
    questions: list[dict[str, Any]],
    flashcards: list[dict[str, Any]],
    project_data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": sid,
        "unit": 9,
        "order": order,
        "title": title,
        "summary": summary,
        "prereqs": prereqs,
        "guide": guide_text,
        "questions": questions,
        "flashcards": flashcards,
        "project": project_data,
    }


TOPICS: list[dict[str, Any]] = [
    topic(
        "dsa-java-arrays",
        60,
        "Arrays in Java",
        "Array operations, 2D arrays, and common interview patterns such as prefix sums and Kadane's algorithm.",
        [],
        guide(
            "Arrays in Java",
            "Arrays are fixed-size, zero-indexed containers with O(1) indexed access. They are the base for many DSA patterns.",
            [
                ("Declaration and Access", code("java", "int[] nums = {1, 2, 3};\nint first = nums[0];\nint[][] grid = new int[3][4];")),
                ("Prefix Sums", code("java", "int[] pref = new int[nums.length + 1];\nfor (int i = 0; i < nums.length; i++) pref[i + 1] = pref[i] + nums[i];\nint range = pref[r + 1] - pref[l];")),
                ("2D Traversal", code("java", "for (int r = 0; r < grid.length; r++) {\n    for (int c = 0; c < grid[r].length; c++) {\n        process(grid[r][c]);\n    }\n}")),
            ],
            ["Forgetting arrays are fixed length", "Using <= arr.length instead of < arr.length", "Summing into int when long is needed"],
            ["Strings: char arrays and StringBuilder", "Sliding Window: contiguous subarrays", "Two Pointers: sorted array scans"],
        ),
        [
            mcq("dja", 1, "What is the time complexity of arr[i] access?", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 0, "Array index access is direct offset computation.", ["arrays"]),
            mcq("dja", 2, "What is the default value in a new int[3]?", ["null", "0", "undefined", "garbage"], 1, "Primitive int array cells default to 0.", ["java", "arrays"]),
            code_output("dja", 3, "What prints?", "int[] a = {4, 5, 6};\nSystem.out.println(a.length);", ["2", "3", "4", "Error"], 1, "length is the number of elements.", ["arrays"]),
            mcq("dja", 4, "Prefix sums are mainly used to answer which query quickly?", ["Range sum", "Sorting", "Hash collision", "Tree height"], 0, "After preprocessing, range sums are O(1).", ["prefix-sum"]),
            multi("dja", 5, "Which are common array patterns?", ["Two pointers", "Prefix sum", "Kadane", "DNS lookup"], [0, 1, 2], "All three are standard array problem patterns.", ["patterns"]),
            mcq("dja", 6, "Kadane's algorithm solves:", ["Sorting", "Maximum subarray sum", "Binary search", "Graph traversal"], 1, "Kadane finds max contiguous subarray sum in O(n).", ["kadane"]),
            mcq("dja", 7, "In Java, arrays are:", ["Value types", "Objects on heap", "Always sorted", "Dynamic size"], 1, "Arrays are objects, variable holds reference.", ["java"]),
            code_output("dja", 8, "Output?", "int[] arr = new int[3];\nSystem.out.println(arr[1]);", ["null", "0", "undefined", "Error"], 1, "Primitive int defaults to 0.", ["java"]),
            mcq("dja", 9, "Two-pointer on sorted array for two-sum is:", ["O(n^2)", "O(n log n)", "O(n)", "O(1)"], 2, "Each pointer moves once through array = O(n).", ["two-pointers"]),
            mcq("dja", 10, "Dutch National Flag sorts 0s/1s/2s in:", ["O(n log n)", "O(n^2)", "O(n)", "O(n) space"], 2, "3-pointer single pass = O(n) time O(1) space.", ["dutch-flag"]),
            mcq("dja", 11, "Array rotation by k using reverse takes:", ["O(n^2)", "O(n) time O(1) space", "O(n) space", "O(k)"], 1, "Three reversal passes in-place.", ["rotation"]),
            code_output("dja", 12, "Output?", "int[][] m = {{1,2},{3,4}};\nSystem.out.println(m[1][0]);", ["1", "2", "3", "4"], 2, "m[1][0] = row 1, col 0 = 3.", ["2d-arrays"]),
            mcq("dja", 13, "Find duplicate in array (1 to n) with O(1) space:", ["Sort", "HashMap", "Floyd cycle", "Binary search"], 2, "Treat values as pointers for cycle detection.", ["floyd"]),
            mcq("dja", 14, "Arrays.sort() uses:", ["Bubble", "Merge for primitives", "Dual-pivot quicksort for primitives", "Heap"], 2, "Java uses dual-pivot quicksort for primitives.", ["sorting"]),
            mcq("dja", 15, "arr[5] on int[5] throws:", ["NullPointer", "ArrayIndexOutOfBounds", "IllegalArgument", "StackOverflow"], 1, "Valid indices 0-4, index 5 is out of bounds.", ["exceptions"]),
            mcq("dja", 16, "To copy array properly:", ["arr2 = arr1", "Arrays.copyOf(arr, len)", "clone always works", "arraycopy deep copies"], 1, "Arrays.copyOf creates independent copy.", ["copying"]),
            mcq("dja", 17, "Merge intervals: first step is:", ["Sort by end", "Sort by start", "Sort by length", "Use stack"], 1, "Sort by start, then merge overlapping.", ["intervals"]),
            mcq("dja", 18, "Prefix sum space complexity:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2, "Stores n+1 values = O(n) space.", ["complexity"]),
            mcq("dja", 19, "int[] vs Integer[]:", ["Same", "int[] primitive, Integer[] objects", "Just naming", "Both on stack"], 1, "int[] cache-friendly, Integer[] boxed objects.", ["types"]),
            mcq("dja", 20, "Arrays.sort() best case:", ["O(1)", "O(n)", "O(n log n)", "O(n^2)"], 2, "Primitive quicksort is O(n log n) even when sorted.", ["complexity"]),
        ],
        cards("dja", [("Array access complexity", "O(1) by index."), ("Unsorted array search", "O(n)."), ("2D row count", "matrix.length."), ("2D column count", "matrix[0].length when rectangular."), ("Prefix sum formula", "sum(l,r)=pref[r+1]-pref[l]."), ("Kadane's algorithm", "Max subarray: currentSum = max(arr[i], currentSum+arr[i])."), ("Dutch flag pattern", "3 pointers: low, mid, high for 0/1/2 sorting."), ("Array rotation trick", "Rotate by k: reverse all, reverse[0,k), reverse[k,n).")], "arrays"),
        project("Build an ArrayPatterns.java utility with prefix sums, rotate-by-k, max subarray, and spiral traversal.", ["Implements prefix sum range queries", "Implements rotate by k using reversals", "Implements Kadane's algorithm", "Handles empty/small inputs"], ["Normalize k with k %= n.", "Kadane should initialize from nums[0] when non-empty."]),
    ),
    topic(
        "dsa-java-strings",
        61,
        "Strings in Java",
        "StringBuilder, immutability, character counting, and common string algorithms.",
        ["dsa-java-arrays"],
        guide(
            "Strings in Java",
            "Java String is immutable. For repeated edits, use StringBuilder; for counting, use arrays or HashMap depending on character set.",
            [
                ("String vs StringBuilder", code("java", "StringBuilder sb = new StringBuilder();\nfor (String word : words) sb.append(word);\nString joined = sb.toString();")),
                ("Frequency Count", code("java", "int[] freq = new int[26];\nfor (char ch : s.toCharArray()) freq[ch - 'a']++;")),
                ("Palindrome Check", code("java", "boolean isPal(String s) {\n    int l = 0, r = s.length() - 1;\n    while (l < r) if (s.charAt(l++) != s.charAt(r--)) return false;\n    return true;\n}")),
            ],
            ["Building strings with += inside loops", "Confusing == with equals()", "Ignoring Unicode when problem is not limited to ASCII"],
            ["Arrays: char[] and frequency arrays", "Hashing: anagrams and sets", "Two Pointers: palindrome checks"],
        ),
        [
            mcq("djs", 1, "Why prefer StringBuilder in repeated concatenation loops?", ["It sorts text", "It avoids creating many intermediate String objects", "It is immutable", "It hashes faster"], 1, "StringBuilder mutates an internal buffer.", ["strings"]),
            mcq("djs", 2, "Which method compares String contents?", ["==", "equals", "compareRef", "same"], 1, "equals checks value equality; == checks reference identity.", ["java"]),
            code_output("djs", 3, "What prints?", "StringBuilder sb = new StringBuilder(\"ab\");\nsb.append('c');\nSystem.out.println(sb.toString());", ["ab", "abc", "cab", "Error"], 1, "append mutates the builder.", ["StringBuilder"]),
            mcq("djs", 4, "A lowercase English-letter frequency table usually has size:", ["10", "26", "52", "128"], 1, "There are 26 lowercase English letters.", ["frequency"]),
            multi("djs", 5, "Which problems often use string hashing/counting?", ["Anagrams", "First unique character", "Duplicate words", "Heap sort"], [0, 1, 2], "These require remembering seen characters or counts.", ["hashing", "strings"]),
            mcq("djs", 6, "Strings in Java are:", ["Mutable", "Immutable", "Dynamic", "Primitives"], 1, "String objects cannot be modified after creation.", ["immutability"]),
            code_output("djs", 7, "Output?", "String s = \"abc\";\ns.concat(\"def\");\nSystem.out.println(s);", ["abc", "abcdef", "def", "null"], 0, "concat returns new String, doesn't modify s.", ["immutability"]),
            mcq("djs", 8, "s.charAt(i) complexity:", ["O(1)", "O(log n)", "O(n)", "O(i)"], 0, "Direct array access internally.", ["complexity"]),
            mcq("djs", 9, "KMP pattern matching runs in:", ["O(n*m)", "O(n+m)", "O(n log m)", "O(m^2)"], 1, "Linear preprocessing + linear search.", ["kmp"]),
            code_output("djs", 10, "Output?", "String s = \"hello\";\nSystem.out.println(s.substring(1,4));", ["hel", "ell", "ello", "llo"], 1, "substring(1,4) = [1,4) = indices 1,2,3.", ["substring"]),
            mcq("djs", 11, "Two strings are anagrams if:", ["Equal", "Same chars, same frequency", "Same length", "Same first char"], 1, "Identical character counts.", ["anagrams"]),
            mcq("djs", 12, "s.toCharArray() creates:", ["A view", "A new char[] copy", "Lazy reference", "Internal array ref"], 1, "Returns new copied char array.", ["strings"]),
            mcq("djs", 13, "String intern pool:", ["Speeds concatenation", "Reuses identical literals", "Only for numbers", "Stores all Strings"], 1, "Literal strings share references.", ["intern"]),
            code_output("djs", 14, "Output?", "String a = \"test\";\nString b = \"test\";\nSystem.out.println(a == b);", ["true", "false", "Error", "null"], 0, "Both point to same interned object.", ["intern"]),
            mcq("djs", 15, "s.indexOf(\"abc\") returns:", ["Boolean", "First index or -1", "Last index", "Count"], 1, "Starting index of first occurrence or -1.", ["strings"]),
            mcq("djs", 16, "To reverse string efficiently:", ["String +=", "new StringBuilder(s).reverse().toString()", "String.reverse()", "Collections.reverse"], 1, "StringBuilder has reverse() method.", ["reversal"]),
            mcq("djs", 17, "Palindrome two-pointer check:", ["O(n^2)", "O(n log n)", "O(n)", "O(1)"], 2, "Compare from both ends, meet in middle.", ["palindrome"]),
            mcq("djs", 18, "For 1000 concatenations, StringBuilder is better because:", ["Less memory", "String += is O(n^2)", "Thread safe", "Compiler optimizes"], 1, "Each += creates new object and copies.", ["performance"]),
            multi("djs", 19, "Which are O(n) string ops?", ["length()", "substring()", "indexOf()", "charAt()"], [1, 2], "substring copies, indexOf scans. length/charAt are O(1).", ["complexity"]),
            mcq("djs", 20, "s.split(' ') complexity:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2, "Must scan entire string for delimiters.", ["complexity"]),
        ],
        cards("djs", [("String mutability", "String is immutable."), ("Use StringBuilder when", "Repeated append/delete operations."), ("String equality", "Use equals() for content."), ("charAt complexity", "O(1)."), ("Anagram technique", "Compare frequency counts."), ("Palindrome check", "Two pointers from both ends."), ("KMP complexity", "O(n+m) pattern matching."), ("String intern", "Literals share references in pool.")], "strings"),
        project("Create StringAlgorithms.java with reverseWords, isPalindrome, groupAnagrams, and firstUniqueChar.", ["Uses StringBuilder appropriately", "Uses equals for string comparison", "Handles empty strings", "Includes frequency-based anagram logic"], ["For groupAnagrams, sorted string keys or 26-count keys both work.", "Trim and split carefully for word reversal."]),
    ),
    topic(
        "dsa-java-linked-lists",
        62,
        "Linked Lists in Java",
        "Singly/doubly linked lists, reversal, middle node, merge, and cycle detection.",
        ["dsa-java-arrays"],
        guide(
            "Linked Lists in Java",
            "A linked list stores nodes connected by references. It trades O(1) random access for cheap pointer updates when the node is known.",
            [
                ("Node Class", code("java", "class ListNode {\n    int val;\n    ListNode next;\n    ListNode(int val) { this.val = val; }\n}")),
                ("Reverse a List", code("java", "ListNode reverse(ListNode head) {\n    ListNode prev = null, cur = head;\n    while (cur != null) {\n        ListNode next = cur.next;\n        cur.next = prev;\n        prev = cur;\n        cur = next;\n    }\n    return prev;\n}")),
                ("Cycle Detection", code("java", "boolean hasCycle(ListNode head) {\n    ListNode slow = head, fast = head;\n    while (fast != null && fast.next != null) {\n        slow = slow.next;\n        fast = fast.next.next;\n        if (slow == fast) return true;\n    }\n    return false;\n}")),
            ],
            ["Losing next before rewiring", "Not checking null and one-node lists", "Forgetting to update both prev and next in doubly lists"],
            ["Stacks/Queues: linked implementations", "Two Pointers: fast/slow", "Hashing: alternative cycle detection"],
        ),
        [
            mcq("djll", 1, "Head insertion in a singly linked list is:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 0, "Only a few references change.", ["linked-list"]),
            mcq("djll", 2, "Floyd's cycle detection uses:", ["Sorting", "Slow and fast pointers", "A heap", "Binary search"], 1, "The fast pointer catches the slow pointer in a cycle.", ["cycle"]),
            mcq("djll", 3, "Random access by index in a linked list is:", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 2, "You must traverse node by node.", ["complexity"]),
            code_output("djll", 4, "After reversing 1->2->3, the new head value is:", "// reverse(1->2->3) returns the new head", ["1", "2", "3", "null"], 2, "The list becomes 3->2->1.", ["reversal"]),
            multi("djll", 5, "Which references are tracked during iterative reversal?", ["prev", "cur", "next", "root"], [0, 1, 2], "prev/cur/next prevent losing the rest of the list.", ["reversal"]),
            mcq("djll", 6, "Singly linked list node contains:", ["Only value", "Value and next", "Value, prev, next", "Array of values"], 1, "One forward reference only.", ["structure"]),
            mcq("djll", 7, "Doubly linked list node contains:", ["Only value", "Value and next", "Value, prev, next", "Two nexts"], 2, "Bidirectional references.", ["structure"]),
            mcq("djll", 8, "Find middle of list with fast/slow pointers — complexity:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2, "Slow reaches middle when fast reaches end.", ["two-pointers"]),
            mcq("djll", 9, "Iterative reverse space complexity:", ["O(n)", "O(log n)", "O(1)", "O(n^2)"], 2, "Three pointer variables only.", ["complexity"]),
            mcq("djll", 10, "Merge two sorted lists — time complexity:", ["O(n*m)", "O(n+m)", "O(n log m)", "O(1)"], 1, "Single pass through both lists.", ["merging"]),
            mcq("djll", 11, "Java LinkedList implements:", ["List only", "Deque only", "List and Deque", "Map"], 2, "Can be used as list or double-ended queue.", ["java"]),
            mcq("djll", 12, "Tail append without a tail pointer — complexity:", ["O(1)", "O(log n)", "O(n)", "Impossible"], 2, "Must traverse to the last node.", ["complexity"]),
            mcq("djll", 13, "Floyd: if slow and fast meet, a cycle:", ["Does not exist", "Definitely exists", "May exist", "Is only detected once"], 1, "They only meet if fast laps slow inside a cycle.", ["floyd"]),
            mcq("djll", 14, "To find cycle start after Floyd detection:", ["Impossible", "Move one pointer to head, advance both one step at a time", "Count list length", "Use HashMap"], 1, "Math proves they meet again exactly at the cycle start.", ["floyd"]),
            mcq("djll", 15, "Delete a node given only a pointer to it (not the last node):", ["Impossible", "Copy next node's value, skip next node", "Use prev pointer", "Traverse from head"], 1, "Overwrite with next data then skip next.", ["deletion"]),
            mcq("djll", 16, "Find k-th node from end in one pass:", ["Impossible", "Two pointers k indices apart", "Reverse then index", "Count then subtract"], 1, "Advance lead pointer k steps, then move both until lead reaches end.", ["two-pointers"]),
            mcq("djll", 17, "Dummy/sentinel head node helps because:", ["It speeds up traversal", "Simplifies insert/delete at head — no special case", "Required by Java", "Saves memory"], 1, "Head pointer always stays valid.", ["technique"]),
            code_output("djll", 18, "List before: 1->2->3. Delete node with value 2. Result:", "// deleteMiddle(1->2->3)", ["1->3", "2->3", "1->2", "null"], 0, "Node 2 is removed by relinking 1 to 3.", ["deletion"]),
            mcq("djll", 19, "LRU cache uses doubly linked list + HashMap to achieve:", ["O(log n) get and put", "O(1) get and put", "O(n) get, O(1) put", "O(1) get, O(n) put"], 1, "Map gives O(1) lookup; list gives O(1) reorder.", ["lru"]),
            mcq("djll", 20, "Best case for linked list over array:", ["Random access", "Finding max", "Insert/delete in the middle when you already hold the node", "Sorting"], 2, "O(1) pointer rewire vs O(n) array shift.", ["comparison"]),
        ],
        cards("djll", [("Singly node fields", "value and next."), ("Doubly node fields", "value, prev, next."), ("Fast/slow use", "Middle node or cycle detection."), ("Reverse list — space", "O(1) iterative; O(n) recursive (call stack)."), ("Java LinkedList", "Implements both List and Deque."), ("Floyd two-phase", "Phase 1: detect. Phase 2: move one ptr to head, step both by 1 to find start."), ("Dummy head", "Eliminates special-case logic for head insert/delete."), ("K-th from end", "Two pointers: advance lead k steps, then move both until lead hits null.")], "linked-list"),
        project("Implement MyLinkedList with addFirst, addLast, removeFirst, reverse, and hasCycle tests.", ["Defines ListNode cleanly", "Handles empty list cases", "Implements iterative reverse", "Implements Floyd cycle detection"], ["Use a dummy node to simplify insert/delete near head.", "Save next before changing cur.next."]),
    ),
    topic(
        "dsa-java-stacks",
        63,
        "Stacks in Java",
        "Stack using arrays/LinkedList/ArrayDeque, monotonic stack, and expression parsing.",
        ["dsa-java-arrays", "dsa-java-linked-lists"],
        guide(
            "Stacks in Java",
            "A stack is LIFO: the last item pushed is the first popped. In Java interviews, prefer Deque over legacy Stack.",
            [
                ("ArrayDeque Stack", code("java", "Deque<Integer> st = new ArrayDeque<>();\nst.push(10);\nint top = st.peek();\nint removed = st.pop();")),
                ("Balanced Parentheses", code("java", "for (char ch : s.toCharArray()) {\n    if (ch == '(') st.push(ch);\n    else if (ch == ')' && (st.isEmpty() || st.pop() != '(')) return false;\n}\nreturn st.isEmpty();")),
                ("Monotonic Stack", code("java", "Deque<Integer> st = new ArrayDeque<>();\nfor (int i = 0; i < nums.length; i++) {\n    while (!st.isEmpty() && nums[st.peek()] < nums[i]) ans[st.pop()] = nums[i];\n    st.push(i);\n}")),
            ],
            ["Calling pop on an empty stack", "Using java.util.Stack by habit", "Storing values when indices are needed for widths/distances"],
            ["Recursion: implicit call stack", "Graphs: iterative DFS", "Heaps: different priority removal rule"],
        ),
        [
            mcq("djst", 1, "Stack removal order is:", ["FIFO", "LIFO", "Sorted", "Random"], 1, "Last In, First Out.", ["stack"]),
            mcq("djst", 2, "Preferred Java stack implementation for most interviews:", ["Vector", "ArrayDeque", "TreeMap", "PriorityQueue"], 1, "ArrayDeque is fast and implements Deque.", ["java"]),
            code_output("djst", 3, "What prints?", "Deque<Integer> s = new ArrayDeque<>();\ns.push(1); s.push(2);\nSystem.out.println(s.pop());", ["1", "2", "null", "Error"], 1, "2 was pushed last, so it pops first.", ["stack"]),
            mcq("djst", 4, "Monotonic stacks are useful for:", ["Next greater element", "Binary search only", "Hash collisions", "String equality"], 0, "They maintain increasing/decreasing candidates.", ["monotonic-stack"]),
            multi("djst", 5, "Which are stack applications?", ["Balanced parentheses", "DFS", "Undo history", "Dijkstra relaxation order"], [0, 1, 2], "Dijkstra typically uses a priority queue, not a plain stack.", ["applications"]),
            mcq("djst", 6, "push/pop/peek on ArrayDeque are:", ["O(log n)", "O(n)", "O(1)", "O(n log n)"], 2, "Array-backed deque does front/rear operations in amortized O(1).", ["complexity"]),
            mcq("djst", 7, "java.util.Stack vs ArrayDeque:", ["Stack is faster", "ArrayDeque is faster — Stack is synchronized (legacy)", "Both identical", "Stack for production"], 1, "Stack's synchronization overhead makes it slower for single-thread use.", ["java"]),
            mcq("djst", 8, "Balanced parentheses uses a stack because:", ["Recursion is hard", "Must match the most recent unmatched opening bracket", "Less memory", "Required by language spec"], 1, "LIFO ensures open brackets are matched in the correct order.", ["parentheses"]),
            mcq("djst", 9, "Monotonic increasing stack pops when:", ["New element is larger", "New element is smaller", "Stack is full", "Never"], 1, "Pop smaller candidates to maintain increasing order.", ["monotonic"]),
            mcq("djst", 10, "For next-greater-element, the stack stores:", ["Values only", "Indices (to fill result array by position)", "Both", "Neither"], 1, "Indices are needed to assign answers in result[].", ["nge"]),
            mcq("djst", 11, "Evaluate postfix '3 4 + 2 *':", ["14", "11", "10", "Error"], 0, "(3+4)*2 = 14.", ["postfix"]),
            mcq("djst", 12, "Min stack — O(1) getMin strategy:", ["Scan on every call", "Keep a parallel stack of running minimums", "Sort on push", "Binary search"], 1, "Second stack tracks min at each push depth.", ["minstack"]),
            mcq("djst", 13, "Largest rectangle in histogram optimal solution:", ["O(n^2) brute force", "O(n) monotonic stack", "O(n log n) segment tree", "O(n) prefix sums"], 1, "Stack tracks bars whose rectangles are still extending rightward.", ["histogram"]),
            mcq("djst", 14, "Iterative DFS with explicit stack vs recursive DFS:", ["Different traversal order", "Explicit stack mirrors the call stack — same logic", "Explicit stack uses more memory", "Recursive is always better"], 1, "Both use LIFO; recursion uses the call stack implicitly.", ["dfs"]),
            code_output("djst", 15, "Output?", "Deque<Integer> s = new ArrayDeque<>();\ns.push(1); s.push(2); s.push(3);\ns.pop();\nSystem.out.println(s.peek());", ["1", "2", "3", "null"], 1, "pop() removes 3; peek() sees 2.", ["stack"]),
            mcq("djst", 16, "Infix-to-postfix conversion uses a stack to:", ["Store operands", "Manage operator precedence and associativity", "Sort tokens", "Detect syntax errors"], 1, "Higher-precedence operators are flushed before lower ones.", ["infix"]),
            mcq("djst", 17, "Stack overflow from recursion happens because:", ["Array is too small", "Each call frame is pushed — deep recursion exhausts call stack memory", "Stack is unsorted", "pop() is missing"], 1, "JVM default stack is usually ~512 KB–1 MB.", ["overflow"]),
            mcq("djst", 18, "Undo/redo in a text editor is modelled by:", ["One queue", "One stack", "Two stacks — undo stack and redo stack", "Doubly linked list"], 2, "Undo pops from undo stack and pushes to redo stack.", ["undo"]),
            mcq("djst", 19, "Stock span problem (days since last higher price) uses:", ["Prefix sums", "Monotonic stack", "Sorting", "Segment tree"], 1, "Stack stores indices of bars with descending prices.", ["span"]),
            mcq("djst", 20, "Call stack in Java grows when:", ["A variable is declared", "A method is invoked", "An array is accessed", "A loop iterates"], 1, "Each method call pushes a new frame onto the call stack.", ["call-stack"]),
        ],
        cards("djst", [("LIFO", "Last In, First Out."), ("push", "Add to top."), ("pop", "Remove top."), ("peek", "Read top without removing."), ("Monotonic stack stores", "Candidates in sorted order, often indices."), ("Min stack trick", "Keep parallel stack of minimums."), ("ArrayDeque for stack", "Faster than java.util.Stack."), ("DFS uses", "Stack (explicit or recursion call stack).")], "stack"),
        project("Build StackProblems.java with validParentheses, nextGreaterElement, minStack, and largestRectangleHistogram.", ["Uses ArrayDeque", "Checks empty before pop", "Uses indices for histogram widths", "Includes tests for duplicates"], ["For MinStack, keep a second stack of minimums.", "Add a sentinel 0 height to flush histograms."]),
    ),
    topic(
        "dsa-java-queues",
        64,
        "Queues and Deques in Java",
        "Queue, deque, circular queue, BFS level-order traversal, and sliding window maximum.",
        ["dsa-java-stacks"],
        guide(
            "Queues and Deques in Java",
            "A queue is FIFO (First In, First Out). Java's preferred implementations are ArrayDeque for general use and LinkedList when you need null support.",
            [
                ("Queue Basics", code("java", "Queue<Integer> q = new ArrayDeque<>();\nq.offer(1);   // add to rear — returns false on failure\nq.add(2);     // add to rear — throws on failure\nint front = q.peek();   // view front\nint out   = q.poll();   // remove front (null if empty)\nq.remove();   // remove front (throws if empty)")),
                ("Deque — Double-Ended Queue", code("java", "Deque<Integer> dq = new ArrayDeque<>();\ndq.addFirst(1);   // push to front\ndq.addLast(2);    // push to rear\ndq.removeFirst(); // pop front\ndq.removeLast();  // pop rear\ndq.peekFirst();\ndq.peekLast();\n// Use as Stack: push/pop/peek (front)\n// Use as Queue: offer/poll (rear→front)")),
                ("Circular Queue from Array", code("java", "class CircularQueue {\n    int[] arr; int front, rear, size, cap;\n    CircularQueue(int k) { arr = new int[k]; cap = k; }\n    boolean enqueue(int val) {\n        if (size == cap) return false;\n        arr[rear] = val;\n        rear = (rear + 1) % cap;  // wrap\n        size++; return true;\n    }\n    int dequeue() {\n        if (size == 0) return -1;\n        int v = arr[front];\n        front = (front + 1) % cap; size--; return v;\n    }\n}")),
                ("BFS Template", code("java", "Queue<Node> q = new ArrayDeque<>();\nSet<Node> visited = new HashSet<>();\nq.offer(start); visited.add(start);\nwhile (!q.isEmpty()) {\n    Node cur = q.poll();\n    for (Node nb : cur.neighbors)\n        if (visited.add(nb)) q.offer(nb);\n}")),
                ("Level-Order Tree Traversal", code("java", "Queue<TreeNode> q = new ArrayDeque<>();\nif (root != null) q.offer(root);\nwhile (!q.isEmpty()) {\n    int sz = q.size();          // nodes on this level\n    for (int i = 0; i < sz; i++) {\n        TreeNode n = q.poll();\n        if (n.left  != null) q.offer(n.left);\n        if (n.right != null) q.offer(n.right);\n    }\n}")),
                ("Sliding Window Maximum with Deque", code("java", "// Maintain decreasing deque of indices\nDeque<Integer> dq = new ArrayDeque<>();\nfor (int i = 0; i < nums.length; i++) {\n    while (!dq.isEmpty() && dq.peekFirst() < i - k + 1)\n        dq.pollFirst();   // evict out-of-window\n    while (!dq.isEmpty() && nums[dq.peekLast()] < nums[i])\n        dq.pollLast();    // remove smaller candidates\n    dq.offerLast(i);\n    if (i >= k - 1) result[i - k + 1] = nums[dq.peekFirst()];\n}")),
            ],
            ["Using LinkedList instead of ArrayDeque (slower due to node allocation)", "Calling poll() without isEmpty() check — returns null, not exception", "Forgetting the modulo wrap in circular queue index arithmetic", "Not using a visited set in BFS — causes infinite loops on cyclic graphs"],
            ["Stacks: LIFO counterpart", "Trees: level-order traversal", "Graphs: BFS shortest path in unweighted graphs", "Sliding Window: deque gives O(1) window max/min"],
        ),
        [
            mcq("djq", 1, "Queue removal order is:", ["LIFO", "FIFO", "Sorted ascending", "Random"], 1, "First In, First Out — items leave in the order they arrived.", ["queue"]),
            mcq("djq", 2, "Preferred Java Queue implementation:", ["java.util.Stack", "LinkedList", "ArrayDeque", "TreeSet"], 2, "ArrayDeque has better cache locality and no node overhead.", ["java"]),
            code_output("djq", 3, "What prints?", "Queue<Integer> q = new ArrayDeque<>();\nq.offer(1); q.offer(2); q.offer(3);\nSystem.out.println(q.poll());", ["3", "2", "1", "null"], 2, "poll() removes the front element, which is 1 (first added).", ["queue"]),
            mcq("djq", 4, "offer() vs add() on a Queue:", ["No difference", "offer() returns false on failure; add() throws an exception", "offer() is slower", "add() is deprecated"], 1, "offer() is preferred for bounded queues.", ["queue"]),
            mcq("djq", 5, "BFS uses a queue because:", ["It is faster than DFS", "It processes nodes level by level (FIFO order)", "Queues use less memory", "Recursion requires a queue"], 1, "FIFO ensures all distance-k nodes are visited before distance-k+1.", ["bfs"]),
            mcq("djq", 6, "Circular queue index wrap-around formula:", ["idx++", "(idx + 1) % capacity", "idx * 2 % capacity", "capacity - idx"], 1, "Modulo constrains the index within [0, capacity).", ["circular-queue"]),
            mcq("djq", 7, "poll() on an empty Queue returns:", ["0", "-1", "null", "Throws NoSuchElementException"], 2, "poll() returns null; remove() would throw.", ["queue"]),
            mcq("djq", 8, "Deque stands for:", ["Dynamic Entry Queue", "Double-Ended Queue", "Duplicate Elimination Queue", "Distributed Efficient Queue"], 1, "Supports insert/remove at both front and rear.", ["deque"]),
            code_output("djq", 9, "Output?", "Deque<Integer> dq = new ArrayDeque<>();\ndq.addFirst(10); dq.addLast(20);\nSystem.out.println(dq.removeFirst());", ["20", "10", "null", "Error"], 1, "addFirst(10) places 10 at front; removeFirst() takes it.", ["deque"]),
            mcq("djq", 10, "Level-order tree traversal uses a queue to:", ["Sort nodes by value", "Process each level before descending to the next", "Find cycles", "Build a min-heap"], 1, "Queue FIFO order mirrors level-by-level processing.", ["bfs", "trees"]),
            mcq("djq", 11, "Snapshot q.size() at the start of each BFS iteration lets you:", ["Measure total nodes", "Process exactly one level per outer loop iteration", "Speed up BFS", "Detect cycles"], 1, "size() at that moment equals the number of nodes on the current level.", ["bfs"]),
            mcq("djq", 12, "BFS guarantees shortest path in:", ["Any weighted graph", "Unweighted graphs only", "DAGs only", "Trees only"], 1, "Equal edge weights mean BFS distance = hop count = shortest path.", ["bfs"]),
            mcq("djq", 13, "To find the sliding-window maximum in O(n), use:", ["Sorted array", "Max-heap", "Monotonic decreasing deque", "Two pointers"], 2, "Deque stores candidate indices in decreasing value order; front is always the max.", ["deque", "sliding-window"]),
            mcq("djq", 14, "A Deque can replace:", ["ArrayList", "Both a Stack and a Queue", "HashMap", "PriorityQueue"], 1, "addFirst/removeFirst = stack; addLast/removeFirst = queue.", ["deque"]),
            multi("djq", 15, "Which real-world systems model a queue?", ["CPU task scheduler", "Printer spooler", "Browser undo history", "Web server request queue"], [0, 1, 3], "Undo history is LIFO (stack). The others are FIFO queues.", ["applications"]),
            mcq("djq", 16, "Queue push/pop/peek all run in:", ["O(log n)", "O(n)", "O(1)", "O(n log n)"], 2, "ArrayDeque front/rear operations are amortized O(1).", ["complexity"]),
            mcq("djq", 17, "To avoid infinite loops in BFS on a graph:", ["Limit iterations", "Mark nodes visited before enqueuing", "Use a priority queue", "Sort adjacency lists"], 1, "A visited set prevents re-enqueuing already-seen nodes.", ["bfs"]),
            code_output("djq", 18, "Output?", "Queue<String> q = new ArrayDeque<>();\nq.offer(\"a\"); q.offer(\"b\");\nq.poll();\nSystem.out.println(q.peek());", ["a", "b", "null", "Error"], 1, "poll() removes 'a'; peek() sees 'b' without removing it.", ["queue"]),
            mcq("djq", 19, "Circular queue is full when:", ["rear == front", "size == capacity", "front == -1", "rear == capacity - 1"], 1, "Track size separately to distinguish full from empty.", ["circular-queue"]),
            mcq("djq", 20, "LinkedList vs ArrayDeque for a queue:", ["LinkedList is faster", "ArrayDeque is faster due to array locality", "They are identical", "LinkedList uses less memory"], 1, "ArrayDeque avoids per-node heap allocation; better cache performance.", ["performance"]),
        ],
        cards("djq", [
            ("Queue order", "FIFO — First In, First Out."),
            ("offer / poll / peek", "offer: add rear. poll: remove front (null if empty). peek: view front."),
            ("Deque", "Double-Ended Queue. add/remove at both ends. Use as stack or queue."),
            ("BFS core pattern", "offer start → while not empty: poll → process → offer unvisited neighbours."),
            ("Circular queue wrap", "(index + 1) % capacity — keeps pointer inside the array bounds."),
            ("Level-order by level", "Snapshot q.size() before inner loop to process exactly one level."),
            ("Sliding window max", "Monotonic decreasing deque of indices; front is window maximum."),
            ("ArrayDeque vs LinkedList", "ArrayDeque is faster (array locality, no node allocation).")
        ], "queue"),
        project(
            "Implement three things in QueueLab.java:\n1. A CircularQueue class backed by an int[] (enqueue, dequeue, isFull, isEmpty).\n2. A method levelOrder(TreeNode root) returning List<List<Integer>>.\n3. A method maxSlidingWindow(int[] nums, int k) using a deque.\nInclude a main() with small test cases for each.",
            ["CircularQueue handles wrap-around correctly with modulo", "levelOrder groups nodes by level using q.size() snapshot", "maxSlidingWindow evicts out-of-window indices from deque front", "All three handle empty/edge inputs without exceptions"],
            ["Circular queue: track size separately — avoids front==rear ambiguity.", "Level-order: take levelSize = q.size() before the inner for loop.", "Sliding window: poll front when index - front > k - 1."],
        ),
    ),
]


def add_more_topics() -> None:
    specs = [
        # dsa-java-queues moved to inline TOPICS above
        # dsa-java-hashing expanded inline below
        ("dsa-java-searching", 68, "Searching Algorithms in Java", "Binary search, lower/upper bound, and rotated sorted arrays.", ["dsa-java-sorting"], "searching", "int l = 0, r = nums.length - 1;\nwhile (l <= r) {\n    int m = l + (r - l) / 2;\n    if (nums[m] == target) return m;\n    if (nums[m] < target) l = m + 1; else r = m - 1;\n}", "binary search"),
        ("dsa-java-binary-trees", 69, "Binary Trees in Java", "Traversals, height, LCA, and BST operations.", ["dsa-java-recursion", "dsa-java-queues"], "trees", "void inorder(TreeNode root) {\n    if (root == null) return;\n    inorder(root.left);\n    visit(root);\n    inorder(root.right);\n}", "recursive traversal"),
        ("dsa-java-heaps", 70, "Heaps and PriorityQueue in Java", "PriorityQueue, min/max heaps, top-k, and heap sort.", ["dsa-java-binary-trees", "dsa-java-sorting"], "heaps", "PriorityQueue<Integer> minHeap = new PriorityQueue<>();\nPriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());", "priority removal"),
        ("dsa-java-graphs-basics", 71, "Graph Basics in Java", "Adjacency list/matrix representations plus BFS and DFS.", ["dsa-java-queues", "dsa-java-recursion"], "graphs", "List<List<Integer>> g = new ArrayList<>();\nfor (int i = 0; i < n; i++) g.add(new ArrayList<>());\ng.get(u).add(v);", "adjacency list"),
        ("dsa-java-graphs-advanced", 72, "Advanced Graph Algorithms in Java", "Dijkstra, Bellman-Ford, and topological sort.", ["dsa-java-graphs-basics", "dsa-java-heaps"], "graphs-advanced", "PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));\npq.offer(new int[]{source, 0});", "weighted shortest paths"),
        ("dsa-java-dp-intro", 73, "Dynamic Programming Intro in Java", "Memoization vs tabulation using Fibonacci and knapsack-style states.", ["dsa-java-recursion", "dsa-java-arrays"], "dp", "int fib(int n, int[] memo) {\n    if (n <= 1) return n;\n    if (memo[n] != -1) return memo[n];\n    return memo[n] = fib(n - 1, memo) + fib(n - 2, memo);\n}", "overlapping subproblems"),
        ("dsa-java-dp-sequences", 74, "DP on Sequences in Java", "LCS, LIS, edit distance, and sequence state design.", ["dsa-java-dp-intro", "dsa-java-strings"], "dp-sequences", "int[][] dp = new int[m + 1][n + 1];\nfor (int i = 1; i <= m; i++)\n  for (int j = 1; j <= n; j++)\n    dp[i][j] = a.charAt(i-1) == b.charAt(j-1) ? 1 + dp[i-1][j-1] : Math.max(dp[i-1][j], dp[i][j-1]);", "two-dimensional state"),
        ("dsa-java-tries", 75, "Tries in Java", "Trie insert/search, prefix queries, and autocomplete.", ["dsa-java-strings", "dsa-java-hashing"], "tries", "class TrieNode {\n    TrieNode[] child = new TrieNode[26];\n    boolean word;\n}", "prefix tree"),
        ("dsa-java-sliding-window", 76, "Sliding Window in Java", "Fixed and variable-size window patterns for arrays and strings.", ["dsa-java-arrays", "dsa-java-strings"], "sliding-window", "int sum = 0;\nfor (int r = 0; r < nums.length; r++) {\n    sum += nums[r];\n    if (r >= k) sum -= nums[r - k];\n}", "contiguous window"),
        ("dsa-java-two-pointers", 77, "Two Pointers in Java", "Two-pointer patterns, Dutch national flag, intervals, and partitioning.", ["dsa-java-arrays", "dsa-java-sorting"], "two-pointers", "int l = 0, r = nums.length - 1;\nwhile (l < r) {\n    int sum = nums[l] + nums[r];\n    if (sum < target) l++; else if (sum > target) r--; else return true;\n}", "converging pointers"),
    ]
    for sid, order, title, summary, prereqs, tag, snippet, key_phrase in specs:
        prefix = "".join(part[0] for part in sid.replace("dsa-java-", "dj-").split("-"))[:8]
        TOPICS.append(topic(
            sid,
            order,
            title,
            summary,
            prereqs,
            guide(
                title,
                f"This topic focuses on {summary[0].lower() + summary[1:]}",
                [
                    ("Core Java Pattern", code("java", snippet)),
                    ("When to Use It", f"Use this when the problem signals **{key_phrase}**, repeated state, or a direct data-structure fit."),
                    ("Complexity Mindset", "Always identify the operation you repeat most often, then choose the structure or algorithm that makes that operation cheap."),
                ],
                ["Skipping empty input checks", "Using the right idea but with off-by-one boundaries", "Forgetting to state time and space complexity"],
                ["Arrays/Strings: common input forms", "Recursion/Stacks/Queues: traversal control", "Hashing/Heaps: faster lookup or priority choices"],
            ),
            [
                mcq(prefix, 1, f"The central idea in {title} is most closely related to:", [key_phrase, "CSS selectors", "HTTP status codes", "Package installation"], 0, f"{title} is a DSA topic centered on {key_phrase}.", [tag]),
                mcq(prefix, 2, "Which habit prevents many interview bugs?", ["Ignore edge cases", "Trace a tiny example", "Use global state always", "Skip complexity analysis"], 1, "Tracing exposes boundary mistakes early.", [tag, "debugging"]),
                code_output(prefix, 3, "What concept does this snippet demonstrate?", snippet, [key_phrase, "database indexing", "thread scheduling", "CSS layout"], 0, "The code is the standard Java skeleton for this topic.", [tag, "java"]),
                mcq(prefix, 4, "What should you communicate after coding a DSA solution?", ["Only the final answer", "Time and space complexity", "Your editor theme", "Nothing"], 1, "Complexity explains scalability.", ["complexity"]),
                multi(prefix, 5, f"Good practice while solving {title} problems includes:", ["Clarify constraints", "Handle edge cases", "Choose data structures intentionally", "Mutate inputs without checking if allowed"], [0, 1, 2], "Constraints, edge cases, and data-structure choice drive correct solutions.", [tag, "process"]),
            ],
            cards(prefix, [("Core signal", key_phrase), ("First step", "Clarify constraints and input size."), ("Java habit", "Use library collections intentionally."), ("Complexity", "State time and space after coding."), ("Debugging", "Trace a small example by hand.")], tag),
            project(f"Create a Java practice class for {title} with 3-5 solved methods and small main-method examples.", ["Implements the core pattern", "Includes at least three representative problems", "Handles edge cases", "Documents time and space complexity"], ["Start with the smallest brute force, then optimize.", "Write one tiny input where the answer is obvious."]),
        ))

    # ── HASHING ──────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-hashing", 65,
        "Hashing in Java",
        "HashMap, HashSet, frequency counting, collision handling, load factor, and common interview patterns.",
        ["dsa-java-arrays", "dsa-java-strings"],
        guide(
            "Hashing in Java",
            "Hash tables provide average O(1) put/get/remove. Java supplies HashMap, HashSet, LinkedHashMap (insertion-order), and TreeMap (sorted). Choosing the right one is half the battle.",
            [
                ("HashMap basics", code("java", "Map<String, Integer> map = new HashMap<>();\nmap.put(\"a\", 1);\nmap.getOrDefault(\"b\", 0);     // 0 if absent\nmap.containsKey(\"a\");         // true\nmap.remove(\"a\");\n// Iterate entries\nfor (Map.Entry<String,Integer> e : map.entrySet())\n    System.out.println(e.getKey() + \" = \" + e.getValue());")),
                ("HashSet — O(1) membership", code("java", "Set<Integer> seen = new HashSet<>();\nseen.add(5);\nif (!seen.add(5)) System.out.println(\"duplicate\"); // add returns false\nseen.contains(3); // false\nseen.remove(5);")),
                ("Frequency counting pattern", code("java", "Map<Character, Integer> freq = new HashMap<>();\nfor (char c : s.toCharArray())\n    freq.put(c, freq.getOrDefault(c, 0) + 1);\n// Or with merge:\nfreq.merge(c, 1, Integer::sum);")),
                ("Two-sum with O(n) HashMap", code("java", "Map<Integer, Integer> seen = new HashMap<>();\nfor (int i = 0; i < nums.length; i++) {\n    int complement = target - nums[i];\n    if (seen.containsKey(complement))\n        return new int[]{seen.get(complement), i};\n    seen.put(nums[i], i);\n}")),
                ("Collision handling internals", "Java HashMap uses **chaining** per bucket (linked list upgrading to a red-black tree when a bucket grows past 8 entries). When the map's **load factor** (size / capacity) exceeds 0.75, the table **rehashes** — doubles capacity and re-inserts all entries — costing O(n) amortised over all inserts."),
                ("Ordered variants", code("java", "// LinkedHashMap — maintains insertion order\nMap<String,Integer> linked = new LinkedHashMap<>();\n// TreeMap — keys always sorted (O(log n) ops)\nMap<String,Integer> sorted = new TreeMap<>();\nString first = sorted.firstKey();")),
            ],
            ["Using mutable objects as keys without overriding hashCode() + equals()", "Modifying a map while iterating over it (ConcurrentModificationException)", "Confusing HashMap (unordered), LinkedHashMap (insertion-ordered), TreeMap (sorted)", "Forgetting getOrDefault() and using a null check + manual insert instead"],
            ["Arrays/Strings: character frequency with int[26] or HashMap", "Two Pointers: HashMap for O(n) two-sum instead of O(n^2) brute force", "Graphs: HashSet as visited set in BFS/DFS", "Tries: alternative prefix data structure when key space is large"],
        ),
        [
            mcq("djh", 1, "Average time complexity of HashMap get() / put():", ["O(n)", "O(log n)", "O(1)", "O(n log n)"], 2, "Hash function maps key to bucket in constant time on average.", ["complexity"]),
            mcq("djh", 2, "HashMap vs HashSet:", ["Identical", "HashMap stores key-value pairs; HashSet stores unique keys only", "HashSet is faster", "HashMap forbids duplicates"], 1, "HashSet is backed by a HashMap with a dummy value.", ["java"]),
            code_output("djh", 3, "Output?", "Map<String,Integer> m = new HashMap<>();\nm.put(\"x\", 1);\nSystem.out.println(m.getOrDefault(\"y\", 99));", ["1", "null", "99", "0"], 2, "Key 'y' is absent — getOrDefault returns the fallback 99.", ["java"]),
            mcq("djh", 4, "Default load factor of Java HashMap:", ["0.5", "0.75", "1.0", "2.0"], 1, "Rehash triggers when size > capacity × 0.75.", ["load-factor"]),
            mcq("djh", 5, "Java HashMap collision strategy:", ["Open addressing / linear probing", "Chaining — linked list per bucket, tree above threshold", "Double hashing", "Cuckoo hashing"], 1, "Buckets use a linked list; long chains convert to a red-black tree at length 8.", ["collision"]),
            mcq("djh", 6, "Custom class as a HashMap key requires:", ["Nothing extra", "Override hashCode() and equals()", "Implement Comparable", "Be declared final"], 1, "hashCode locates the bucket; equals resolves collisions within it.", ["keys"]),
            mcq("djh", 7, "HashMap iteration order:", ["Always sorted by key", "Insertion order", "Unpredictable / arbitrary", "Sorted by value"], 2, "Use LinkedHashMap for insertion order or TreeMap for sorted keys.", ["ordering"]),
            code_output("djh", 8, "Output?", "Map<Integer,String> m = new HashMap<>();\nm.put(1, \"a\"); m.put(1, \"b\");\nSystem.out.println(m.get(1));", ["a", "b", "null", "Error"], 1, "Second put overwrites the first — one entry per key.", ["java"]),
            mcq("djh", 9, "HashSet.add() returns false when:", ["Set is full", "Element already present", "Element is null", "Always after first add"], 1, "Returns false on duplicate — useful for one-line visited checks.", ["hashset"]),
            mcq("djh", 10, "HashMap worst-case per-operation complexity (Java 8+):", ["O(1)", "O(log n) — tree bins", "O(n)", "O(n^2)"], 1, "Long-chain buckets convert to red-black trees → O(log n) worst case.", ["collision"]),
            mcq("djh", 11, "Which Map preserves insertion order?", ["HashMap", "LinkedHashMap", "TreeMap", "IdentityHashMap"], 1, "LinkedHashMap maintains a doubly-linked list across entries.", ["java"]),
            mcq("djh", 12, "Best structure to count word frequencies over arbitrary strings:", ["int[]", "HashMap<String,Integer>", "PriorityQueue", "Stack"], 1, "Arbitrary string keys require a hash map.", ["frequency"]),
            mcq("djh", 13, "Rehashing doubles capacity when:", ["Every insertion", "Load factor threshold exceeded", "A collision occurs", "Called explicitly"], 1, "Threshold = capacity × loadFactor (default 0.75).", ["rehash"]),
            code_output("djh", 14, "Output?", "Set<Integer> s = new HashSet<>();\ns.add(3); s.add(3); s.add(5);\nSystem.out.println(s.size());", ["1", "2", "3", "4"], 1, "Duplicate 3 is ignored — set has {3,5}, size 2.", ["hashset"]),
            mcq("djh", 15, "map.getOrDefault(k, v) advantage over map.get(k):", ["Faster lookup", "Returns v instead of null when key absent — avoids NPE", "Inserts the key automatically", "Works on null keys only"], 1, "Avoids manual null checks; the idiomatic frequency-count pattern.", ["java"]),
            mcq("djh", 16, "For grouping anagrams, best HashMap key strategy:", ["First character of each string", "String length", "Sorted string as key", "Hash of character sum"], 2, "Sorting produces the same canonical key for all anagrams of the same letters.", ["anagrams"]),
            mcq("djh", 17, "TreeMap differs from HashMap in:", ["It is faster", "Keys always sorted, O(log n) per operation", "Allows null keys", "Thread-safe by default"], 1, "Backed by a red-black tree — sorted but slower than HashMap.", ["treemap"]),
            mcq("djh", 18, "Detect first duplicate in O(n) time O(n) space:", ["Sort then scan", "Two nested loops", "Insert into HashSet; if add() returns false, it is the duplicate", "Prefix sum"], 2, "add() returns false on the first duplicate; no need to scan twice.", ["patterns"]),
            mcq("djh", 19, "ConcurrentModificationException during map iteration is caused by:", ["Map is empty", "Map is structurally modified during iteration", "Key is null", "Value is null"], 1, "Use Iterator.remove() or iterate over a snapshot/copy.", ["exceptions"]),
            mcq("djh", 20, "Space complexity of a HashMap storing n entries:", ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2, "One slot per entry plus bucket array overhead.", ["complexity"]),
        ],
        cards("djh", [
            ("HashMap avg complexity", "put / get / containsKey / remove — all O(1) average."),
            ("getOrDefault pattern", "map.getOrDefault(key, 0) + 1 — the standard frequency-count idiom."),
            ("Collision strategy", "Chaining: linked list per bucket; converts to red-black tree at length 8."),
            ("Load factor default", "0.75 — rehash (double capacity) when size > capacity × 0.75."),
            ("Custom key rule", "Override both hashCode() and equals() for correctness."),
            ("LinkedHashMap", "Like HashMap but preserves insertion order; use for LRU cache."),
            ("TreeMap", "Sorted key order, O(log n) ops. firstKey() / lastKey() / subMap()."),
            ("Two-sum O(n) trick", "Store complement → index in HashMap; single pass, no sorting needed.")
        ], "hashing"),
        project(
            "Write HashingLab.java with four methods:\n1. twoSum(int[] nums, int target) → int[]\n2. groupAnagrams(String[] strs) → List<List<String>>\n3. firstUniqueChar(String s) → int\n4. longestConsecutiveSequence(int[] nums) → int\nInclude a main() with test cases for each.",
            ["twoSum uses a single-pass HashMap (O(n))", "groupAnagrams uses sorted-string canonical key", "firstUniqueChar uses LinkedHashMap or int[26] frequency array", "longestConsecutiveSequence uses HashSet for O(n) — no sorting"],
            ["longestConsecutive: put all numbers in a HashSet, then for each number with no left-neighbour (n-1 absent) start counting upward.", "groupAnagrams: Arrays.sort(s.toCharArray()) gives the same key for all anagrams.", "firstUniqueChar: scan once to build frequency, scan again to find first with count 1."],
        ),
    ))

    # ── RECURSION ─────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-recursion", 66,
        "Recursion in Java",
        "Base cases, recursive cases, call stack frames, tail recursion, memoization, and backtracking.",
        ["dsa-java-stacks"],
        guide(
            "Recursion in Java",
            "Recursion solves problems by reducing them to a smaller instance of the same problem. Every recursive method needs a base case that stops the recursion and a recursive case that makes progress toward it.",
            [
                ("Anatomy of a recursive method", code("java", "int factorial(int n) {\n    if (n <= 1) return 1;         // ① base case — stops recursion\n    return n * factorial(n - 1);  // ② recursive case — reduces n toward base\n}")),
                ("Fibonacci — naive O(2^n) vs memoised O(n)", code("java", "// Naive — recomputes subproblems exponentially\nint fib(int n) {\n    if (n <= 1) return n;\n    return fib(n-1) + fib(n-2);\n}\n\n// Memoised — cache in int[] passed as parameter\nint fib(int n, int[] memo) {\n    if (n <= 1) return n;\n    if (memo[n] != 0) return memo[n];\n    return memo[n] = fib(n-1, memo) + fib(n-2, memo);\n}")),
                ("Call stack frames", code("java", "// Each call pushes a frame:\n//   factorial(4) → factorial(3) → factorial(2) → factorial(1)\n// Frames accumulate until base case, then unwind.\n// Deep recursion (>~5000 frames) → StackOverflowError\n// Fix: convert to iterative + explicit stack, or increase -Xss")),
                ("Backtracking template", code("java", "void permute(char[] arr, int start, List<String> res) {\n    if (start == arr.length) { res.add(new String(arr)); return; }\n    for (int i = start; i < arr.length; i++) {\n        swap(arr, start, i);            // choose\n        permute(arr, start + 1, res);   // explore\n        swap(arr, start, i);            // un-choose (backtrack)\n    }\n}")),
                ("Fast power O(log n)", code("java", "double power(double x, int n) {\n    if (n == 0) return 1;\n    double half = power(x, n / 2);\n    return n % 2 == 0 ? half * half : half * half * x;\n}")),
            ],
            ["Missing base case → infinite recursion → StackOverflowError", "Base case placed after the recursive call (unreachable)", "Not backtracking (undoing state) before trying the next branch", "Using naive recursion for overlapping subproblems — use memoization"],
            ["Stacks: call stack = implicit LIFO stack of frames", "DP: memoization is top-down dynamic programming", "Trees/Graphs: DFS is naturally recursive", "Backtracking: recursion + undo step for combinatorial search"],
        ),
        [
            mcq("djr", 1, "Every recursive function must have:", ["A loop", "A base case", "A void return type", "A static modifier"], 1, "Without a base case recursion never terminates.", ["fundamentals"]),
            mcq("djr", 2, "Naive Fibonacci recursion time complexity:", ["O(n)", "O(n log n)", "O(2^n)", "O(n^2)"], 2, "Each call branches into two — the call tree has 2^n nodes.", ["complexity"]),
            code_output("djr", 3, "Output?", "int f(int n) {\n    if (n == 0) return 0;\n    return 1 + f(n - 1);\n}\nSystem.out.println(f(4));", ["0", "3", "4", "5"], 2, "f(4)=1+f(3)=1+1+f(2)=…=4.", ["tracing"]),
            mcq("djr", 4, "Memoization stores:", ["Input arguments only", "Results of subproblem calls keyed by input", "Call stack frames", "Random values"], 1, "Cache answers so each unique input is solved only once.", ["memoization"]),
            mcq("djr", 5, "StackOverflowError in recursion is caused by:", ["Heap exhaustion", "Recursion depth exceeding JVM stack memory", "Array index out of bounds", "Null dereference"], 1, "Each frame consumes stack memory; too-deep recursion exhausts it.", ["overflow"]),
            mcq("djr", 6, "Memoised Fibonacci time complexity:", ["O(2^n)", "O(n^2)", "O(n)", "O(log n)"], 2, "Each of the n distinct inputs is computed exactly once.", ["memoization"]),
            mcq("djr", 7, "The call stack is:", ["A heap-allocated list", "A LIFO stack of activation frames", "A queue", "A hash map"], 1, "Method calls push frames; returns pop them — LIFO order.", ["call-stack"]),
            code_output("djr", 8, "Output?", "void count(int n) {\n    if (n == 0) return;\n    System.out.print(n + \" \");\n    count(n - 1);\n}\ncount(3);", ["1 2 3", "3 2 1", "0 1 2 3", "3"], 1, "Prints before recursing: 3, then 2, then 1.", ["order"]),
            mcq("djr", 9, "Backtracking is recursion that:", ["Never terminates", "Undoes the last choice then tries the next alternative", "Always finds the globally optimal solution", "Uses BFS"], 1, "Explore → recurse → un-choose (backtrack) → try next.", ["backtracking"]),
            mcq("djr", 10, "Converting recursion to iterative requires:", ["A queue always", "An explicit stack mirroring call frames", "A hash map", "Sorting first"], 1, "Explicit stack replicates LIFO frame behaviour.", ["iterative"]),
            mcq("djr", 11, "Recursive merge sort time complexity:", ["O(n)", "O(n log n)", "O(n^2)", "O(2^n)"], 1, "log n split levels, each doing O(n) merge work.", ["sorting"]),
            mcq("djr", 12, "Overlapping subproblems in a recursive solution signal:", ["No optimisation possible", "Use greedy algorithm", "Dynamic programming opportunity", "Sort the input first"], 2, "Memoize or tabulate to avoid exponential recomputation.", ["dp"]),
            code_output("djr", 13, "Output?", "int sum(int n) {\n    if (n <= 0) return 0;\n    return n + sum(n - 2);\n}\nSystem.out.println(sum(5));", ["6", "9", "15", "5"], 1, "sum(5)=5+sum(3)=5+3+sum(1)=5+3+1=9.", ["tracing"]),
            mcq("djr", 14, "fast power(x, n) using divide-and-conquer runs in:", ["O(n)", "O(log n)", "O(n^2)", "O(2^n)"], 1, "Halve n each step — O(log n) multiplications.", ["fast-power"]),
            multi("djr", 15, "Which problems are naturally recursive?", ["Tree traversal", "Tower of Hanoi", "Bubble sort", "Generating permutations"], [0, 1, 3], "These have self-similar substructure. Bubble sort is an iterative comparison.", ["applications"]),
            mcq("djr", 16, "In backtracking, what must happen after the recursive call?", ["Nothing", "Undo the choice made before the call", "Add result to output immediately", "Break out of the loop"], 1, "Restoring state before trying the next choice is the 'back' in backtracking.", ["backtracking"]),
            code_output("djr", 17, "Output?", "void dfs(int n) {\n    if (n == 0) { System.out.print(\"done \"); return; }\n    dfs(n - 1);\n    System.out.print(n + \" \");\n}\ndfs(3);", ["done 1 2 3", "3 2 1 done", "done 3 2 1", "1 2 3 done"], 0, "Base case prints first as recursion unwinds: done 1 2 3.", ["order"]),
            mcq("djr", 18, "Typical safe recursion depth in Java (default stack):", ["~100", "~1 000", "~5 000–10 000", "Unlimited"], 2, "Depends on frame size; increase with -Xss JVM flag.", ["overflow"]),
            mcq("djr", 19, "Recursive binary search space complexity:", ["O(n)", "O(log n) — call stack depth", "O(1)", "O(n log n)"], 1, "Each halving adds one frame; log n frames maximum.", ["binary-search"]),
            mcq("djr", 20, "return fib(n-1) + fib(n-2) without memoization computes fib(2):", ["Once", "Twice", "Exponentially many times", "log n times"], 2, "Overlapping subproblems cause exponential duplicate work.", ["memoization"]),
        ],
        cards("djr", [
            ("Recursion structure", "Base case (stop) + recursive case (reduce toward base)."),
            ("Naive Fibonacci complexity", "O(2^n) — exponential due to overlapping subproblems."),
            ("Memoization", "Cache subproblem results by input. Fibonacci drops from O(2^n) → O(n)."),
            ("StackOverflowError", "Recursion too deep — exceeded JVM stack. Fix: iterative + explicit stack."),
            ("Backtracking", "choose → recurse → un-choose. Explores all candidates, prunes dead ends."),
            ("Call stack frame", "Holds: local variables, parameters, return address."),
            ("Fast power", "power(x, n/2)² — O(log n) multiplications via divide-and-conquer."),
            ("Overlapping subproblems", "Same sub-inputs solved repeatedly → memoize (top-down DP).")
        ], "recursion"),
        project(
            "Write RecursionLab.java with five methods:\n1. factorial(int n)\n2. fibonacci(int n) — memoised with int[] memo\n3. powerFast(double x, int n) — O(log n)\n4. permutations(String s) — backtracking, return List<String>\n5. floodFill(int[][] grid, int r, int c, int colour)\nInclude main() with test cases for each.",
            ["factorial handles n=0 and n=1 correctly", "fibonacci uses memo array passed as parameter, not a field", "powerFast handles n=0 and negative n", "permutations uses swap-based backtracking", "floodFill terminates on boundary and same-colour cells"],
            ["powerFast: if n%2==0, compute half = power(x,n/2) once and return half*half.", "Permutations: swap chars[start] with chars[i], recurse on start+1, then swap back.", "FloodFill base case: out-of-bounds OR grid[r][c] != originalColour."],
        ),
    ))

    # ── SORTING ───────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-sorting", 67,
        "Sorting Algorithms in Java",
        "Merge sort, quick sort, heap sort, stability, complexity table, and Arrays.sort internals.",
        ["dsa-java-recursion", "dsa-java-arrays"],
        guide(
            "Sorting Algorithms in Java",
            "Sorting underpins binary search, interval merging, two-pointer problems, and much more. Know each algorithm's time/space complexity, stability, and when to prefer one over another. Java's standard library uses dual-pivot Quicksort for primitives and TimSort for objects.",
            [
                ("Merge Sort — stable, O(n log n) guaranteed", code("java", "void mergeSort(int[] a, int l, int r) {\n    if (l >= r) return;\n    int m = l + (r - l) / 2;\n    mergeSort(a, l, m);\n    mergeSort(a, m + 1, r);\n    merge(a, l, m, r);  // combine two sorted halves\n}\n// Time: O(n log n) best/avg/worst\n// Space: O(n) auxiliary array\n// Stable: YES")),
                ("Quick Sort — fast in practice, O(n²) worst case", code("java", "void quickSort(int[] a, int l, int r) {\n    if (l >= r) return;\n    int p = partition(a, l, r);  // Lomuto: pivot = a[r]\n    quickSort(a, l, p - 1);\n    quickSort(a, p + 1, r);\n}\n// Time: O(n log n) avg, O(n²) worst (sorted input + bad pivot)\n// Space: O(log n) call stack avg\n// Stable: NO")),
                ("Heap Sort — O(n log n) worst, in-place", code("java", "void heapSort(int[] a) {\n    int n = a.length;\n    // Build max-heap bottom-up\n    for (int i = n/2 - 1; i >= 0; i--) heapify(a, n, i);\n    // Extract max one by one\n    for (int i = n - 1; i > 0; i--) {\n        swap(a, 0, i);\n        heapify(a, i, 0);\n    }\n}\n// Time: O(n log n) always\n// Space: O(1)\n// Stable: NO")),
                ("Complexity comparison table",
                 "| Algorithm  | Best      | Average   | Worst     | Space    | Stable |\n"
                 "|------------|-----------|-----------|-----------|----------|--------|\n"
                 "| Bubble     | O(n)      | O(n²)     | O(n²)     | O(1)     | Yes    |\n"
                 "| Selection  | O(n²)     | O(n²)     | O(n²)     | O(1)     | No     |\n"
                 "| Insertion  | O(n)      | O(n²)     | O(n²)     | O(1)     | Yes    |\n"
                 "| Merge      | O(n lg n) | O(n lg n) | O(n lg n) | O(n)     | Yes    |\n"
                 "| Quick      | O(n lg n) | O(n lg n) | O(n²)     | O(log n) | No     |\n"
                 "| Heap       | O(n lg n) | O(n lg n) | O(n lg n) | O(1)     | No     |\n"
                 "| Counting   | O(n+k)    | O(n+k)    | O(n+k)    | O(k)     | Yes    |"),
                ("Java Arrays.sort and Comparator", code("java", "// Primitives → dual-pivot Quicksort (fast, NOT stable)\nArrays.sort(intArray);\n\n// Objects → TimSort (stable, adaptive — O(n) on nearly-sorted)\nArrays.sort(strArray);\n\n// Custom order with Comparator\nArrays.sort(people, Comparator.comparingInt(p -> p.age));\nArrays.sort(people, (a, b) -> a.name.compareTo(b.name));")),
            ],
            ["Assuming Arrays.sort is stable for int[] — it uses Quicksort (NOT stable)",
             "Off-by-one in Lomuto partition: pivot ends at index p, not p-1",
             "Not handling many duplicates in Quicksort — degrades to O(n²) without 3-way partition",
             "Using O(n log n) comparison sort when counting sort (O(n+k)) is applicable"],
            ["Arrays: sorting is a prerequisite for binary search and interval problems",
             "Recursion: merge sort and quick sort are recursive divide-and-conquer",
             "Heaps: heap sort uses the heap data structure directly",
             "Two Pointers: after sorting, merge and Dutch-flag patterns apply naturally"],
        ),
        [
            mcq("dso", 1, "Merge sort worst-case time complexity:", ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"], 1, "Always splits into equal halves and merges — O(n log n) regardless of input.", ["merge-sort"]),
            mcq("dso", 2, "Quick sort worst-case time complexity:", ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 1, "Occurs when the pivot is always the smallest or largest element (e.g. sorted input with last-element pivot).", ["quick-sort"]),
            mcq("dso", 3, "Which of these sorting algorithms is stable?", ["Quick sort", "Heap sort", "Merge sort", "Selection sort"], 2, "Stable = equal elements keep their original relative order. Merge sort never swaps equal elements past each other.", ["stability"]),
            mcq("dso", 4, "Arrays.sort(int[]) in Java uses:", ["Merge sort", "Bubble sort", "Dual-pivot Quicksort", "Heap sort"], 2, "Java uses Yaroslavskiy's dual-pivot Quicksort for primitive arrays — fast but NOT stable.", ["java"]),
            mcq("dso", 5, "Arrays.sort(String[]) in Java uses:", ["Quicksort", "TimSort (merge + insertion)", "Bubble sort", "Radix sort"], 1, "Object arrays use TimSort — stable and adaptive, O(n) on nearly-sorted data.", ["java"]),
            mcq("dso", 6, "Merge sort space complexity:", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 2, "Requires an O(n) auxiliary array to hold merged results.", ["complexity"]),
            mcq("dso", 7, "Heap sort space complexity:", ["O(n)", "O(log n)", "O(1)", "O(n log n)"], 2, "Sorts in-place — only the O(log n) heapify call stack, considered O(1) extra.", ["complexity"]),
            mcq("dso", 8, "Bubble sort best case with an early-exit flag (already sorted):", ["O(n²)", "O(n log n)", "O(n)", "O(1)"], 2, "Zero swaps occur on the first pass — the flag exits immediately after O(n) comparisons.", ["bubble-sort"]),
            mcq("dso", 9, "Quick sort with a random pivot achieves on average:", ["O(n²)", "O(n log n)", "O(n)", "O(n log² n)"], 1, "Random pivot keeps partitions balanced in expectation.", ["quick-sort"]),
            mcq("dso", 10, "Counting sort time complexity:", ["O(n log n)", "O(n²)", "O(n + k)", "O(k log k)"], 2, "One pass to count (O(n)), one pass over range (O(k)), one pass to output (O(n)).", ["counting-sort"]),
            multi("dso", 11, "Which algorithms guarantee O(n log n) worst-case?", ["Bubble sort", "Merge sort", "Heap sort", "Quick sort"], [1, 2], "Quick sort degrades to O(n²) worst case. Merge and heap are always O(n log n).", ["complexity"]),
            mcq("dso", 12, "Stability is important when:", ["Sorting primitive integers", "The sort key is the only field", "Multiple sort passes must preserve prior ordering of equal elements", "Input is completely random"], 2, "E.g. sort by department then by salary — second sort must be stable to keep department order.", ["stability"]),
            mcq("dso", 13, "Lomuto partition scheme uses which element as pivot?", ["First", "Middle", "Last", "Median-of-three"], 2, "Lomuto always picks a[r] (last element) as the pivot.", ["quick-sort"]),
            code_output("dso", 14, "After one full pass of bubble sort on [5, 3, 1, 4]:", "// one complete left-to-right pass comparing adjacent pairs", ["[1, 3, 4, 5]", "[3, 1, 4, 5]", "[1, 5, 3, 4]", "[3, 5, 1, 4]"], 1, "Swaps: (5,3)→[3,5,1,4], (5,1)→[3,1,5,4], (5,4)→[3,1,4,5]. Max bubbles to end.", ["bubble-sort"]),
            mcq("dso", 15, "TimSort is a hybrid of:", ["Radix + counting", "Merge sort + insertion sort", "Heap + merge", "Quick + heap"], 1, "Runs insertion sort on small natural runs then merges them — excellent for real-world nearly-sorted data.", ["timsort"]),
            mcq("dso", 16, "To sort objects by a field in Java:", ["Cast field to int and subtract", "Pass a Comparator to Arrays.sort", "Use == operator", "Sort the field array separately"], 1, "Arrays.sort(arr, Comparator.comparingInt(o -> o.field)) is idiomatic.", ["java"]),
            mcq("dso", 17, "3-way partition (Dutch National Flag) variant of Quicksort is best when:", ["All elements are distinct", "There are many duplicate elements equal to the pivot", "Array is already sorted", "Array contains floats"], 1, "Groups all pivot-equal elements in the middle, skipping them in recursive calls.", ["quick-sort"]),
            mcq("dso", 18, "Merge sort is preferred over quick sort when:", ["In-place sorting is required", "Stability is required OR worst-case guarantee matters", "Memory is very scarce", "Data fits entirely in CPU cache"], 1, "Merge provides stability and O(n log n) worst case at the cost of O(n) extra space.", ["comparison"]),
            mcq("dso", 19, "For sorting 8 elements inside TimSort, Java uses:", ["Merge sort", "Quick sort", "Heap sort", "Insertion sort"], 3, "Insertion sort has very low overhead for tiny arrays — TimSort uses it on small runs.", ["timsort"]),
            code_output("dso", 20, "Arrays.sort on int[] {3,1,2} — sort is:", "int[] arr = {3,1,2};\nArrays.sort(arr);\nSystem.out.println(Arrays.toString(arr));", ["[3, 1, 2]", "[1, 2, 3]", "[1, 3, 2]", "Error"], 1, "Arrays.sort sorts in ascending order by default.", ["java"]),
        ],
        cards("dso", [
            ("Merge sort", "O(n log n) always. Stable. O(n) extra space. Divide → recurse → merge."),
            ("Quick sort", "O(n log n) avg, O(n²) worst. NOT stable. O(log n) stack space. Use random pivot."),
            ("Heap sort", "O(n log n) always. NOT stable. O(1) extra. Build max-heap then extract."),
            ("Arrays.sort — primitives", "Dual-pivot Quicksort: fast in practice, NOT stable."),
            ("Arrays.sort — objects", "TimSort: stable, adaptive, O(n) on nearly-sorted data."),
            ("Stability definition", "Equal elements keep their original relative order after sorting."),
            ("Counting sort", "O(n+k) for integers in [0, k). Non-comparison — beats O(n log n) lower bound."),
            ("Comparator pattern", "Arrays.sort(arr, (a,b) -> a.field - b.field) — custom sort key in one line.")
        ], "sorting"),
        project(
            "Write SortingLab.java with:\n1. mergeSort(int[] a) — recursive, in-place via auxiliary array\n2. quickSort(int[] a) — random pivot to avoid O(n²) on sorted input\n3. topKFrequent(int[] nums, int k) — HashMap + min-heap of size k\n4. A main() that times mergeSort vs Arrays.sort on a shuffled 100 000-element array.",
            ["mergeSort passes all correctness tests including duplicates", "quickSort uses random pivot (Math.random() or swap with random index before partition)", "topKFrequent returns exactly k most frequent elements", "Timing output shows both complete in < 200 ms on 100k elements"],
            ["mergeSort: allocate the temp array once at the top level — pass it down to avoid repeated allocation.", "quickSort: swap arr[l + random % (r-l+1)] with arr[r] before calling Lomuto partition.", "topKFrequent: min-heap of size k — add every element, then poll when pq.size() > k."],
        ),
    ))

    # ── SEARCHING ─────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-searching", 68,
        "Searching Algorithms in Java",
        "Binary search intuition, boundary variants (lower/upper bound), rotated arrays, and when NOT to binary search.",
        ["dsa-java-sorting"],
        guide(
            "Searching Algorithms in Java",
            "Binary search is deceptively simple to describe but easy to get wrong at the boundaries. The key mental model: **at every step you are cutting the search space in half and deciding which half to discard**. You must be able to prove your loop terminates and that you never discard the answer.",
            [
                ("Classic binary search — visualise the shrinking window", code("java", "// [l ............. m ............. r]\n// If nums[m] == target → found at m\n// If nums[m] < target  → answer is RIGHT of m  → l = m + 1\n// If nums[m] > target  → answer is LEFT  of m  → r = m - 1\nint binarySearch(int[] nums, int target) {\n    int l = 0, r = nums.length - 1;\n    while (l <= r) {\n        int m = l + (r - l) / 2;   // avoids int overflow vs (l+r)/2\n        if (nums[m] == target) return m;\n        if (nums[m] < target)  l = m + 1;\n        else                   r = m - 1;\n    }\n    return -1;  // not found\n}")),
                ("Lower bound — first index where nums[i] >= target", code("java", "// Picture: [< target | >= target]\n// We want the LEFT boundary of the >= region.\nint lowerBound(int[] nums, int target) {\n    int l = 0, r = nums.length;  // r = length (open right bound)\n    while (l < r) {              // loop ends when l == r\n        int m = l + (r - l) / 2;\n        if (nums[m] < target) l = m + 1;  // m is too small, discard left\n        else                  r = m;       // m could be the answer, keep it\n    }\n    return l;  // l == r == first position with nums[i] >= target\n}")),
                ("Upper bound — first index where nums[i] > target", code("java", "// Picture: [<= target | > target]\n// Shift condition: discard when nums[m] <= target.\nint upperBound(int[] nums, int target) {\n    int l = 0, r = nums.length;\n    while (l < r) {\n        int m = l + (r - l) / 2;\n        if (nums[m] <= target) l = m + 1;\n        else                   r = m;\n    }\n    return l;  // first position with nums[i] > target\n}\n// Count of target = upperBound(target) - lowerBound(target)")),
                ("Rotated sorted array — which half is sorted?", code("java", "// [4 5 6 | 1 2 3]  — rotation breaks global sort but ONE half is always sorted.\n// Key insight: compare nums[l] and nums[m] to find the sorted half,\n// then check if target lies inside it.\nint searchRotated(int[] nums, int target) {\n    int l = 0, r = nums.length - 1;\n    while (l <= r) {\n        int m = l + (r - l) / 2;\n        if (nums[m] == target) return m;\n        if (nums[l] <= nums[m]) {          // LEFT half is sorted\n            if (nums[l] <= target && target < nums[m]) r = m - 1;\n            else l = m + 1;\n        } else {                           // RIGHT half is sorted\n            if (nums[m] < target && target <= nums[r]) l = m + 1;\n            else r = m - 1;\n        }\n    }\n    return -1;\n}")),
                ("Binary search on the ANSWER — think outside the array", code("java", "// Problem: find minimum capacity so you can ship packages in D days.\n// Answer space: [max(packages), sum(packages)]\n// Predicate: canShip(capacity, packages, D) — monotonic in capacity.\nint lo = max(packages), hi = sum(packages);\nwhile (lo < hi) {\n    int mid = lo + (hi - lo) / 2;\n    if (canShip(mid)) hi = mid;   // mid works — try smaller\n    else              lo = mid + 1; // mid too small — go bigger\n}\nreturn lo;  // smallest capacity that works")),
            ],
            [
                "Using (l + r) / 2 when l and r are large ints — overflows. Use l + (r-l)/2.",
                "Off-by-one: loop condition l <= r vs l < r — wrong choice causes infinite loop or missing answer.",
                "Setting r = m-1 vs r = m — crucial difference between classic search and lower-bound variants.",
                "Assuming binary search only works on arrays — it works on any MONOTONIC predicate over an ordered space.",
            ],
            [
                "Sorting: binary search requires a sorted (or partially ordered) input",
                "Two Pointers: both use left/right indices but two-pointer doesn't halve; they converge",
                "DP: sometimes binary search finds the transition point in a monotonic DP table",
                "Rotated arrays: combine binary search with the observation that one half is always sorted",
            ],
        ),
        [
            mcq("dse", 1, "Binary search time complexity on a sorted array of n elements:", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1, "Each step discards half the remaining elements — log₂n steps maximum.", ["complexity"]),
            mcq("dse", 2, "Why write m = l + (r - l) / 2 instead of m = (l + r) / 2?", ["It runs faster", "Prevents integer overflow when l and r are large", "It rounds up instead of down", "Required by Java"], 1, "l + r can exceed Integer.MAX_VALUE when both are large; l + (r-l)/2 stays safe.", ["overflow"]),
            mcq("dse", 3, "Binary search loop condition l <= r vs l < r:", ["Always interchangeable", "l <= r: classic exact-match search; l < r: boundary/lower-bound variants", "l < r is always safer", "Only l <= r is correct"], 1, "Classic search exits when element found or space empty (l > r). Boundary variants exit when l == r — the answer.", ["boundaries"]),
            code_output("dse", 4, "Binary search on [1,3,5,7,9], target=6. Returns:", "int[] a = {1,3,5,7,9};\n// binarySearch(a, 6)", ["-1", "2", "3", "4"], 0, "6 is not in the array. l crosses r without finding it → return -1.", ["tracing"]),
            mcq("dse", 5, "Lower bound returns:", ["Any index of target", "The FIRST index where nums[i] >= target", "The LAST index where nums[i] == target", "The count of target"], 1, "Visualise array split: [< target | >= target]. Lower bound finds the left edge of the right region.", ["lower-bound"]),
            mcq("dse", 6, "Upper bound returns:", ["The last index of target", "The first index where nums[i] > target", "The count of target", "The middle index"], 1, "Visualise: [<= target | > target]. Upper bound finds the left edge of the strictly-greater region.", ["upper-bound"]),
            mcq("dse", 7, "To count occurrences of target in a sorted array:", ["Linear scan O(n)", "upperBound(target) - lowerBound(target)", "Binary search + expand left/right", "Sort then scan"], 1, "The difference of both bounds gives the count in O(log n).", ["count"]),
            mcq("dse", 8, "In a rotated sorted array [4,5,6,1,2,3], you compare nums[l] and nums[m] to:", ["Find the pivot index", "Determine which half is sorted so you can decide where to search", "Calculate mid correctly", "Detect duplicates"], 1, "If nums[l] <= nums[m] the left half is sorted; otherwise the right half is sorted.", ["rotated"]),
            code_output("dse", 9, "Search for 1 in [4,5,6,1,2,3]. Which half does the algorithm search first?", "// l=0 r=5 m=2, nums[m]=6\n// nums[l]=4 <= nums[m]=6 → left half [4,5,6] is sorted\n// Is 1 in [4..6)? No → go right", ["Left half [4,5,6]", "Right half [1,2,3]", "Both halves simultaneously", "Neither — returns -1 immediately"], 1, "Left half is sorted [4,5,6]; 1 is not in it, so search moves to the right half.", ["rotated"]),
            mcq("dse", 10, "Binary search requires the input to be:", ["Sorted in ascending order only", "Monotonically ordered — sorted ascending OR the predicate is monotonic", "An array specifically", "Free of duplicates"], 1, "Binary search generalises to any monotonic predicate — not just sorted arrays.", ["generalisation"]),
            mcq("dse", 11, "Binary search on the answer space means:", ["Searching inside the array for the answer", "Applying binary search over the RANGE of possible answers using a feasibility predicate", "Using two binary searches simultaneously", "Only valid for integer answers"], 1, "If feasibility(x) is monotonic (false…false…true…true), binary search finds the transition.", ["answer-space"]),
            mcq("dse", 12, "Find square root of n (integer) using binary search. The answer space is:", ["[0, n]", "[0, n/2]", "[1, n]", "[0, n²]"], 0, "lo=0, hi=n. Predicate: is mid*mid <= n? Largest mid satisfying it is floor(√n).", ["answer-space"]),
            mcq("dse", 13, "In lower-bound, the loop condition is l < r (not l <= r) because:", ["It is a convention", "Loop exits when l == r pointing to the answer — no equality check needed mid-loop", "It runs one fewer iteration", "It handles duplicates better"], 1, "When l == r both pointers are at the same answer location — no need to keep narrowing.", ["lower-bound"]),
            multi("dse", 14, "Which of these are valid binary search applications?", ["Find first bad version in a sequence", "Find peak element in a unimodal array", "Find median of two sorted arrays", "Find maximum in an unsorted array"], [0, 1, 2], "Unsorted max requires O(n) linear scan. The others have a monotonic or halving structure.", ["applications"]),
            mcq("dse", 15, "Setting r = m (not r = m-1) in lower-bound is necessary because:", ["m-1 could go negative", "m might BE the answer — discarding it would lose it", "It makes the loop faster", "Only even-sized arrays need it"], 1, "In boundary variants you can't discard m because it may be the leftmost valid index.", ["boundaries"]),
            code_output("dse", 16, "lower_bound([1,2,2,2,3], target=2) returns:", "// first index where nums[i] >= 2", ["0", "1", "2", "3"], 1, "Index 1 is the first position where nums[i] >= 2.", ["lower-bound"]),
            mcq("dse", 17, "Rotated sorted array [3,4,5,1,2]: nums[l]=3, nums[m]=5, nums[r]=2. Which half is sorted?", ["Right half [1,2]", "Left half [3,4,5]", "Neither", "Both"], 1, "nums[l]=3 <= nums[m]=5 → left half [3,4,5] is sorted.", ["rotated"]),
            mcq("dse", 18, "Why does binary search on 'minimum days to make m bouquets' work?", ["Array is sorted", "feasibility(days) is monotonic — more days always makes it easier", "The array has no duplicates", "It uses a heap internally"], 1, "Classic answer-space binary search: predicate transitions from false to true at one threshold.", ["answer-space"]),
            code_output("dse", 19, "Binary search iterations to find target in array of size 1 000 000:", "// log2(1_000_000) ≈ ?", ["10", "20", "100", "500"], 1, "log₂(1 000 000) ≈ 19.9 → at most 20 iterations.", ["complexity"]),
            mcq("dse", 20, "When binary search returns l after a lower-bound search:", ["l is always the target index", "l is the insertion point — where target would be inserted to keep array sorted", "l could be past the array end", "Both B and C are correct"], 3, "l == nums.length if target is larger than all elements — always bounds-check before accessing nums[l].", ["boundaries"]),
        ],
        cards("dse", [
            ("Binary search complexity", "O(log n) — halves the search space each step."),
            ("Overflow-safe midpoint", "m = l + (r - l) / 2  — never overflows unlike (l+r)/2."),
            ("Classic vs boundary search", "Classic: l<=r, return m on hit. Boundary: l<r, r=m (keep candidate), exit when l==r."),
            ("Lower bound", "First index where nums[i] >= target. Splits array: [< target | >= target]."),
            ("Upper bound", "First index where nums[i] > target. Count of target = upper - lower."),
            ("Rotated array key insight", "One half is ALWAYS sorted. Compare nums[l] vs nums[m] to identify which one."),
            ("Binary search on answer", "Define feasibility predicate. If it is monotonic, binary search finds the tipping point."),
            ("Off-by-one mantra", "Ask: 'Can I discard m?' If m could be the answer, use r=m not r=m-1."),
        ], "searching"),
        project(
            "Write SearchingLab.java with:\n1. binarySearch(int[] nums, int target) → int  (classic)\n2. lowerBound(int[] nums, int target) → int\n3. upperBound(int[] nums, int target) → int\n4. searchRotated(int[] nums, int target) → int\n5. minCapacityToShip(int[] weights, int days) → int  (answer-space binary search)\nInclude main() tests covering: target absent, all-duplicates, single element, rotated at index 0.",
            ["binarySearch returns -1 when target absent", "lowerBound returns nums.length when target > all elements", "upperBound - lowerBound gives correct count of duplicates", "searchRotated handles rotation at every position including index 0", "minCapacityToShip finds the exact minimum — not just any valid capacity"],
            ["lowerBound: loop is l < r, update r = m (not m-1) when nums[m] >= target.", "searchRotated: the condition nums[l] <= nums[m] correctly identifies the sorted left half.", "minCapacityToShip: lo = max(weights) (must carry heaviest), hi = sum(weights) (one day)."],
        ),
    ))

    # ── BINARY TREES ──────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-binary-trees", 69,
        "Binary Trees in Java",
        "Tree anatomy, DFS traversals (in/pre/post/level), height, diameter, BST properties, and Lowest Common Ancestor.",
        ["dsa-java-recursion", "dsa-java-queues"],
        guide(
            "Binary Trees in Java",
            "Picture a family tree upside-down: one root at the top, each node has at most two children (left and right), and every node except the root has exactly one parent. There are no cycles. This shape makes recursion feel natural — almost every tree problem solves itself once you ask: 'What should I do at *this* node, and what should I ask my children?'",
            [
                ("Node definition and shape intuition", code("java", "class TreeNode {\n    int val;\n    TreeNode left, right;\n    TreeNode(int val) { this.val = val; }\n}\n\n// Visual:\n//        4          ← root (depth 0)\n//       / \\\n//      2   6        ← depth 1\n//     / \\ / \\\n//    1  3 5  7      ← depth 2 (leaves)")),
                ("The four traversals — when does each node get visited?", code("java", "// IN-order   (Left → Root → Right)  → sorted output for BST\n// PRE-order   (Root → Left → Right)  → copy/serialise tree\n// POST-order  (Left → Right → Root)  → delete tree, calc subtree sizes\n// LEVEL-order (BFS, level by level)  → find depth, zigzag print\n\nvoid inorder(TreeNode n) {\n    if (n == null) return;\n    inorder(n.left);\n    visit(n);         // ← comes BETWEEN children → sorted\n    inorder(n.right);\n}\nvoid preorder(TreeNode n) {\n    if (n == null) return;\n    visit(n);         // ← comes BEFORE children → root first\n    preorder(n.left);\n    preorder(n.right);\n}\nvoid postorder(TreeNode n) {\n    if (n == null) return;\n    postorder(n.left);\n    postorder(n.right);\n    visit(n);         // ← comes AFTER children → bottom-up\n}")),
                ("Height and diameter — the two most common recursive patterns", code("java", "// HEIGHT: longest path from node down to any leaf\nint height(TreeNode n) {\n    if (n == null) return -1;  // empty tree height = -1\n    return 1 + Math.max(height(n.left), height(n.right));\n}\n\n// DIAMETER: longest path between ANY two nodes (may not pass through root)\n// Key insight: at each node, the best path through it = leftHeight + rightHeight + 2\nint maxDiameter = 0;\nint diameter(TreeNode n) {\n    if (n == null) return -1;\n    int l = diameter(n.left),  r = diameter(n.right);\n    maxDiameter = Math.max(maxDiameter, l + r + 2);  // path through n\n    return 1 + Math.max(l, r);  // return height to parent\n}")),
                ("BST properties — the sorted invariant", code("java", "// A BST satisfies: for every node N,\n//   ALL values in left subtree  < N.val\n//   ALL values in right subtree > N.val\n//\n// Visual BST:         8\n//                   /   \\\n//                  3     10\n//                 / \\      \\\n//                1   6      14\n//                   / \\\n//                  4   7\n//\n// In-order traversal → [1, 3, 4, 6, 7, 8, 10, 14]  ← always sorted!\n\n// Validate BST: pass down min/max bounds\nboolean isValid(TreeNode n, long min, long max) {\n    if (n == null) return true;\n    if (n.val <= min || n.val >= max) return false;\n    return isValid(n.left, min, n.val)\n        && isValid(n.right, n.val, max);\n}")),
                ("Lowest Common Ancestor (LCA)", code("java", "// LCA of p and q = deepest node that has BOTH p and q in its subtree.\n//\n// Mental model: imagine two people climbing up the tree independently.\n// The first node where their paths MERGE is the LCA.\n//\n// Recursive intuition:\n//   • If current node IS p or q → return it (it could be LCA itself)\n//   • Search left subtree, search right subtree\n//   • If BOTH sides return non-null → current node is LCA\n//   • Otherwise → return whichever side found something\nTreeNode lca(TreeNode root, TreeNode p, TreeNode q) {\n    if (root == null || root == p || root == q) return root;\n    TreeNode left  = lca(root.left,  p, q);\n    TreeNode right = lca(root.right, p, q);\n    if (left != null && right != null) return root;  // split here\n    return left != null ? left : right;\n}")),
                ("Level-order — BFS on a tree gives you depth information for free", code("java", "List<List<Integer>> levelOrder(TreeNode root) {\n    List<List<Integer>> res = new ArrayList<>();\n    if (root == null) return res;\n    Queue<TreeNode> q = new ArrayDeque<>();\n    q.offer(root);\n    while (!q.isEmpty()) {\n        int sz = q.size();          // nodes on THIS level\n        List<Integer> level = new ArrayList<>();\n        for (int i = 0; i < sz; i++) {\n            TreeNode n = q.poll();\n            level.add(n.val);\n            if (n.left  != null) q.offer(n.left);\n            if (n.right != null) q.offer(n.right);\n        }\n        res.add(level);\n    }\n    return res;\n}")),
            ],
            [
                "Not checking null before accessing node.left or node.right",
                "Height vs depth confusion: height counts edges DOWN from a node; depth counts edges UP from root",
                "Diameter problem: forgetting to track a global max — the best diameter may not pass through the root",
                "BST validation: checking only the immediate parent is wrong — you must propagate the valid range (min/max bounds) down",
                "LCA on BST: simpler O(log n) version exists (walk left if both < root, right if both > root) — use it when the tree is confirmed BST",
            ],
            [
                "Recursion: tree problems ARE recursion — almost always base case = null node",
                "Queues: level-order traversal is BFS using a queue",
                "Arrays: in-order of BST produces a sorted array — connect to searching/sorting",
                "Graphs: a tree is a connected acyclic undirected graph — tree algorithms generalise to graphs",
            ],
        ),
        [
            mcq("djbt", 1, "In-order traversal of a BST produces:", ["Random order", "Reverse sorted order", "Sorted ascending order", "Pre-order sequence"], 2, "BST invariant: left < root < right. In-order visits left→root→right, naturally yielding sorted output.", ["bst", "traversal"]),
            mcq("djbt", 2, "Pre-order traversal visits nodes in order:", ["Left → Root → Right", "Left → Right → Root", "Root → Left → Right", "Right → Root → Left"], 2, "Root is visited BEFORE its children — useful for copying or serialising the tree structure.", ["traversal"]),
            code_output("djbt", 3, "In-order traversal of this BST: root=4, left=2, right=6:", "//     4\n//    / \\\n//   2   6", ["4 2 6", "2 4 6", "2 6 4", "4 6 2"], 1, "In-order: left(2) → root(4) → right(6) → [2, 4, 6].", ["traversal", "tracing"]),
            mcq("djbt", 4, "Post-order traversal is naturally suited for:", ["Printing the tree top-down", "Serialising a tree", "Computing subtree sizes or deleting nodes", "Level-by-level output"], 2, "Post-order visits children BEFORE the parent — you have full subtree results before processing the node.", ["traversal"]),
            mcq("djbt", 5, "Height of a single-node tree is:", ["-1", "0", "1", "2"], 1, "Height = number of edges on the longest path to a leaf. A leaf has no edges below it → height 0.", ["height"]),
            mcq("djbt", 6, "Height of an empty tree (null) is conventionally:", ["-1", "0", "1", "undefined"], 0, "Returning -1 for null makes the formula height(node) = 1 + max(h(left), h(right)) work cleanly.", ["height"]),
            code_output("djbt", 7, "Height of root=1 → left=2 → left=3 (linear chain)?", "//  1\n//   \\\n//    2\n//     \\\n//      3", ["1", "2", "3", "0"], 1, "Path: 1→2→3 = 2 edges. height = 2.", ["height", "tracing"]),
            mcq("djbt", 8, "The diameter of a binary tree is:", ["Height × 2", "Number of nodes", "Longest path between any two nodes (may not pass through root)", "Depth of the deepest leaf"], 2, "The diameter can arc through any node — its computation tracks the best left-height + right-height + 2 at each node.", ["diameter"]),
            mcq("djbt", 9, "BST validation using only checking node vs its direct parent (e.g. node.val > node.parent.val) is:", ["Correct", "Correct for balanced trees only", "Incorrect — must propagate valid min/max bounds down the tree", "Correct if tree is complete"], 2, "A right child's left subtree could violate the ancestor's upper bound. Example: 10→(right)5 is caught by parent but 10→(right)15→(left)6 is valid locally but 6 > 10 is not.", ["bst", "validation"]),
            mcq("djbt", 10, "LCA of nodes 4 and 7 in a BST with root 8, left subtree rooted at 3 is:", ["8", "3", "3 (since both 4 and 7 are in 3's subtree)", "4"], 2, "Both 4 and 7 are in 3's subtree (3 < both < 8). Since they split at 6 (left=4, right=7), LCA is 6 — but if tree matches the guide diagram, both are under 6, so LCA = 6.", ["lca"]),
            mcq("djbt", 11, "In the LCA recursive algorithm, if both left and right recursive calls return non-null, it means:", ["Node is a leaf", "Current node is below both p and q", "p and q are in DIFFERENT subtrees — current node is their LCA", "Only one of p/q was found"], 2, "When both sides find a target node, the current node is exactly where the paths diverge — it is the LCA.", ["lca"]),
            mcq("djbt", 12, "Level-order traversal uses a queue rather than recursion because:", ["Recursion is too slow", "Queue gives FIFO order — nodes at depth k are processed before depth k+1", "Trees cannot be recursed level-by-level", "It avoids stack overflow"], 1, "FIFO order naturally enforces processing one breadth level at a time.", ["level-order"]),
            mcq("djbt", 13, "Snapshotting q.size() before the inner loop in level-order lets you:", ["Speed up the traversal", "Process all nodes of exactly one level per outer iteration", "Detect cycles", "Sort nodes by value"], 1, "The snapshot captures how many nodes are on the current level before new children are enqueued.", ["level-order"]),
            mcq("djbt", 14, "A balanced binary tree of n nodes has height approximately:", ["n", "n/2", "log₂ n", "√n"], 2, "Each level doubles the nodes — log₂n levels for n nodes.", ["height", "complexity"]),
            mcq("djbt", 15, "BST search time complexity on a balanced BST:", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1, "Each comparison halves the remaining nodes — identical to binary search.", ["bst", "complexity"]),
            mcq("djbt", 16, "A degenerate (skewed) BST has worst-case search complexity:", ["O(log n)", "O(n)", "O(n log n)", "O(1)"], 1, "Inserting sorted data into a plain BST produces a linked list — all operations become O(n).", ["bst", "complexity"]),
            multi("djbt", 17, "Which traversals can reconstruct a unique binary tree?", ["Pre-order alone", "Pre-order + In-order", "Post-order + In-order", "Level-order + In-order"], [1, 2, 3], "In-order alone or pre/post alone are insufficient — you need in-order paired with another traversal to uniquely reconstruct.", ["reconstruction"]),
            mcq("djbt", 18, "The path from root to any node in a BST compared to binary search on a sorted array:", ["Completely different algorithms", "Structurally identical — both discard half the search space at each step using the same key comparison", "BST is always faster", "Binary search is always faster"], 1, "BST search IS binary search but on a pointer-linked structure instead of an index-addressable array.", ["bst", "insight"]),
            code_output("djbt", 19, "Pre-order of: root=1, left=2, right=3, 2.left=4, 2.right=5:", "//     1\n//    / \\\n//   2   3\n//  / \\\n// 4   5", ["1 2 3 4 5", "4 2 5 1 3", "1 2 4 5 3", "4 5 2 3 1"], 2, "Pre-order: root(1) → left subtree pre-order(2→4→5) → right subtree(3) = [1,2,4,5,3].", ["traversal", "tracing"]),
            mcq("djbt", 20, "Symmetric tree check (mirror of itself) uses:", ["Only in-order traversal", "Pre-order compared to reverse pre-order", "Recursive check: left.val==right.val AND left.left mirrors right.right AND left.right mirrors right.left", "Post-order on both halves"], 2, "Mirror symmetry requires comparing outer children (left.left vs right.right) and inner children (left.right vs right.left) simultaneously.", ["symmetry"]),
        ],
        cards("djbt", [
            ("In-order traversal", "Left → Root → Right. On a BST this yields sorted ascending output."),
            ("Pre-order traversal", "Root → Left → Right. Visits root first — use to copy or serialise."),
            ("Post-order traversal", "Left → Right → Root. Visits root last — use for subtree-size and deletion."),
            ("Height formula", "height(null) = -1.  height(node) = 1 + max(height(left), height(right))."),
            ("Diameter insight", "Best path through node n = leftHeight + rightHeight + 2. Track global max."),
            ("BST invariant", "ALL left subtree values < node.val < ALL right subtree values."),
            ("LCA algorithm", "If both subtrees return non-null → current node is LCA. Else return whichever found something."),
            ("Level-order trick", "Snapshot levelSize = q.size() before inner loop to process exactly one level."),
        ], "trees"),
        project(
            "Write TreeLab.java with:\n1. inorder / preorder / postorder — return List<Integer>\n2. height(TreeNode root) → int\n3. diameterOfBinaryTree(TreeNode root) → int\n4. isValidBST(TreeNode root) → boolean  (min/max bounds approach)\n5. lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) → TreeNode\n6. levelOrder(TreeNode root) → List<List<Integer>>\nInclude main() tests: a balanced BST, a skewed tree, and a tree where diameter does NOT pass through root.",
            ["inorder of a BST returns sorted list", "height of null returns -1, single node returns 0", "diameterOfBinaryTree uses a single DFS pass with global max (no re-traversal)", "isValidBST passes Long.MIN_VALUE / Long.MAX_VALUE as initial bounds", "LCA correctly handles p or q being an ancestor of the other", "levelOrder returns correct sublists for each depth"],
            ["Diameter: return height from the recursive helper, update global maxDiameter as a side effect.", "isValidBST: use long bounds (not int) to handle Integer.MIN_VALUE and Integer.MAX_VALUE node values.", "LCA: the base case 'if (root == p || root == q) return root' handles the ancestor case correctly."],
        ),
    ))

    # ── HEAPS ─────────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-heaps", 70,
        "Heaps and PriorityQueue in Java",
        "Min/max heap shape and order properties, heapify, PriorityQueue API, top-k, k-way merge, and median of a stream.",
        ["dsa-java-binary-trees", "dsa-java-sorting"],
        guide(
            "Heaps and PriorityQueue in Java",
            "A heap is a **complete binary tree** stored compactly in an array where every parent is 'better' than its children. 'Better' means smaller in a min-heap and larger in a max-heap. The practical payoff: you can always read the best element in O(1) and remove it in O(log n) — which is exactly what a priority queue needs.",
            [
                ("Shape + order — the two heap invariants", code("java", "// SHAPE: complete binary tree — every level filled left-to-right\n// So it is stored perfectly in an array with no wasted slots:\n//\n//         1          index 0\n//       /   \\\n//      3     2        index 1, 2\n//     / \\   / \\\n//    7   4  5   6     index 3, 4, 5, 6\n//\n// Parent of i  →  (i - 1) / 2\n// Left child   →  2*i + 1\n// Right child  →  2*i + 2\n//\n// MIN-HEAP ORDER: heap[parent] <= heap[child]  (root = global minimum)\n// MAX-HEAP ORDER: heap[parent] >= heap[child]  (root = global maximum)")),
                ("Java PriorityQueue — min-heap by default", code("java", "// Min-heap (natural order)\nPriorityQueue<Integer> minH = new PriorityQueue<>();\nminH.offer(5); minH.offer(1); minH.offer(3);\nminH.peek();    // 1  — O(1), does NOT remove\nminH.poll();    // 1  — O(log n), removes minimum\n\n// Max-heap (reverse order)\nPriorityQueue<Integer> maxH = new PriorityQueue<>(Comparator.reverseOrder());\n\n// Custom objects — sort by frequency descending\nPriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> b[1] - a[1]);")),
                ("Heapify — build a heap from an array in O(n)", code("java", "// Naive: insert n elements one by one → O(n log n)\n// Smart: sift-down starting from the LAST non-leaf upward → O(n)\n//\n// Why O(n)? Most nodes are near the bottom with short sift-down paths.\n// The math: sum of all sift-down work = O(n)  (not O(n log n)).\n//\nvoid buildHeap(int[] a) {\n    int n = a.length;\n    for (int i = n / 2 - 1; i >= 0; i--)  // last non-leaf = n/2-1\n        siftDown(a, n, i);\n}")),
                ("Top-K pattern — keep a heap of size k", code("java", "// Top-K LARGEST elements — use a MIN-heap of size k.\n// Mental model: the min-heap is a 'bouncer' that keeps only the\n// k biggest seen so far. Anything smaller than the heap's min gets rejected.\n//\nint[] topKLargest(int[] nums, int k) {\n    PriorityQueue<Integer> minH = new PriorityQueue<>();\n    for (int n : nums) {\n        minH.offer(n);\n        if (minH.size() > k) minH.poll();  // evict the current minimum\n    }\n    // minH now contains exactly the k largest elements\n    return minH.stream().mapToInt(Integer::intValue).toArray();\n}\n// Time: O(n log k)   Space: O(k)")),
                ("Median of a data stream — two heaps", code("java", "// Trick: keep a MAX-heap for the lower half and a MIN-heap for the upper half.\n// Balance them so sizes differ by at most 1.\n//\n//  lower (max-heap): [1, 2, 3]    upper (min-heap): [4, 5, 6]\n//                          ↑ max of lower ≤ min of upper ↑\n//\n// Median = average of both tops (even count) or top of larger heap (odd count).\nPriorityQueue<Integer> lower = new PriorityQueue<>(Comparator.reverseOrder());\nPriorityQueue<Integer> upper = new PriorityQueue<>();\n\nvoid addNum(int num) {\n    lower.offer(num);\n    upper.offer(lower.poll());     // balance: push lower's max to upper\n    if (upper.size() > lower.size()) lower.offer(upper.poll()); // keep lower >= upper\n}\ndouble findMedian() {\n    return lower.size() > upper.size()\n        ? lower.peek()\n        : (lower.peek() + upper.peek()) / 2.0;\n}")),
                ("K-way merge — merge k sorted lists in O(n log k)", code("java", "// Put the FIRST element of each list into a min-heap.\n// Every poll() gives the global minimum; then push the next element\n// from the same list. Repeat until heap is empty.\n//\nList<Integer> mergeKSorted(int[][] lists) {\n    // heap stores: [value, listIndex, elementIndex]\n    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));\n    for (int i = 0; i < lists.length; i++)\n        if (lists[i].length > 0) pq.offer(new int[]{lists[i][0], i, 0});\n    List<Integer> res = new ArrayList<>();\n    while (!pq.isEmpty()) {\n        int[] cur = pq.poll();\n        res.add(cur[0]);\n        int next = cur[2] + 1;\n        if (next < lists[cur[1]].length)\n            pq.offer(new int[]{lists[cur[1]][next], cur[1], next});\n    }\n    return res;\n}")),
            ],
            [
                "Confusing peek() (O(1), no removal) with poll() (O(log n), removes root)",
                "Using a max-heap for top-K largest — counterintuitive but correct: min-heap lets you evict the smallest quickly",
                "Forgetting that Java PriorityQueue is a MIN-heap by default",
                "Assuming heapify (buildHeap) is O(n log n) — it is actually O(n) because lower nodes do less work",
                "Index arithmetic: parent = (i-1)/2, left child = 2i+1, right child = 2i+2 — off-by-one off-by-one off-by-one",
            ],
            [
                "Binary Trees: a heap is a complete binary tree stored in an array",
                "Sorting: heap sort uses heapify + n extractions — O(n log n) in-place",
                "Graphs: Dijkstra's algorithm replaces a visited array with a min-heap on distances",
                "Sliding Window: some window problems use a heap when you need fast max/min updates",
            ],
        ),
        [
            mcq("djhp", 1, "A min-heap guarantees:", ["The array is fully sorted", "The root is the smallest element", "Each level is sorted left to right", "Left child < right child always"], 1, "Only the root is guaranteed to be the global minimum. The rest of the heap is partially ordered.", ["min-heap"]),
            mcq("djhp", 2, "Java PriorityQueue default ordering:", ["Max-heap (largest first)", "Min-heap (smallest first)", "Insertion order", "Random"], 1, "PriorityQueue<Integer> uses natural Comparable order — smallest element at the head.", ["java"]),
            code_output("djhp", 3, "Output?", "PriorityQueue<Integer> pq = new PriorityQueue<>();\npq.offer(5); pq.offer(1); pq.offer(3);\nSystem.out.println(pq.poll());", ["5", "3", "1", "null"], 2, "Min-heap: poll() returns and removes the smallest element — 1.", ["java", "tracing"]),
            mcq("djhp", 4, "For top-K LARGEST elements, use:", ["Max-heap of all n elements, poll k times", "Min-heap of size k — evict minimum when size exceeds k", "Sort descending, take first k", "Both A and B are O(n log k) for large n"], 1, "Min-heap of size k: heap's root is the *smallest of the top-k*. New element replaces it if larger. Space O(k), time O(n log k).", ["top-k"]),
            mcq("djhp", 5, "Building a heap from n elements using sift-down (heapify) takes:", ["O(n log n)", "O(n)", "O(n²)", "O(log n)"], 1, "Sift-down from index n/2-1 down to 0. Most nodes are near leaves with short paths — total work sums to O(n).", ["heapify"]),
            mcq("djhp", 6, "In a heap array, the parent of element at index i is at:", ["i / 2", "(i - 1) / 2", "i * 2", "i - 1"], 1, "Zero-indexed: parent(i) = (i-1)/2. Left child = 2i+1, right child = 2i+2.", ["array-index"]),
            code_output("djhp", 7, "What is the parent index of element at index 5?", "// zero-indexed heap array\n// parent(5) = ?", ["1", "2", "3", "4"], 1, "(5 - 1) / 2 = 2 (integer division).", ["array-index", "tracing"]),
            mcq("djhp", 8, "peek() vs poll() on a PriorityQueue:", ["Both remove the root", "peek() reads root in O(1) without removing; poll() removes root in O(log n)", "poll() is O(1)", "peek() is O(log n)"], 1, "peek = look at the best without removing; poll = remove and restore heap order via sift-down.", ["java"]),
            mcq("djhp", 9, "After poll() removes the root from a min-heap, heap order is restored by:", ["Re-building the whole heap", "Moving the last element to root and sifting it down", "Sorting the array", "Swapping root with its smaller child repeatedly upward"], 1, "Sift-down: compare with children, swap with smaller child, repeat until heap property restored. O(log n).", ["heapify"]),
            mcq("djhp", 10, "Heap sort time and space complexity:", ["O(n log n) time, O(n) space", "O(n log n) time, O(1) space", "O(n) time, O(1) space", "O(n²) time, O(1) space"], 1, "Build heap O(n) + n extractions each O(log n) = O(n log n). In-place — O(1) extra space.", ["heap-sort"]),
            mcq("djhp", 11, "Median of a data stream uses two heaps because:", ["One heap is not enough memory", "Max-heap holds lower half, min-heap holds upper half — their tops bracket the median in O(1)", "Two heaps are faster than sorting", "It avoids duplicates"], 1, "Splitting the stream at the median lets you read it in O(1) without sorting all data.", ["median"]),
            mcq("djhp", 12, "In the two-heap median approach, the size invariant to maintain is:", ["Both heaps always equal size", "Lower half size >= upper half size, differ by at most 1", "Upper half always larger", "Sizes can differ by any amount"], 1, "Keeping sizes within 1 ensures the median is either the top of the larger heap or average of both tops.", ["median"]),
            mcq("djhp", 13, "K-way merge of k sorted lists with total n elements using a heap runs in:", ["O(n)", "O(n log n)", "O(n log k)", "O(k log n)"], 2, "Each of the n elements is inserted and removed from a heap of size k — O(log k) per element.", ["k-way-merge"]),
            multi("djhp", 14, "Which real problems map naturally to a min-heap?", ["Dijkstra's shortest path", "Scheduling tasks by earliest deadline", "Finding the k-th largest element", "Checking if a graph is bipartite"], [0, 1, 2], "Graph bipartiteness uses BFS/DFS coloring, not a heap. The others need fast minimum extraction.", ["applications"]),
            mcq("djhp", 15, "Inserting into a heap (offer/add) works by:", ["Adding to root and sifting down", "Adding at the END and sifting UP to restore heap order", "Binary search to find insertion position", "Re-heapifying the whole array"], 1, "Append to end (preserves shape), then sift-up: swap with parent while smaller than parent. O(log n).", ["insert"]),
            code_output("djhp", 16, "Max-heap creation in Java:", "PriorityQueue<Integer> maxH =\n    new PriorityQueue<>(Comparator.reverseOrder());\nmaxH.offer(3); maxH.offer(7); maxH.offer(1);\nSystem.out.println(maxH.peek());", ["1", "3", "7", "null"], 2, "reverseOrder() makes largest element the root — peek() returns 7.", ["java"]),
            mcq("djhp", 17, "To find the k-th largest element in an unsorted array optimally:", ["Sort descending O(n log n)", "Max-heap poll k times O(n + k log n)", "Min-heap of size k O(n log k)", "Linear scan O(n) with QuickSelect"], 2, "O(n log k) min-heap is better than full sort when k << n. QuickSelect O(n) avg exists but heap is simpler.", ["top-k"]),
            mcq("djhp", 18, "A complete binary tree with height h has at most how many nodes?", ["h²", "2^h", "2^(h+1) - 1", "h * log h"], 2, "Each level i has 2^i nodes; summing levels 0 to h gives 2^(h+1) - 1.", ["shape"]),
            mcq("djhp", 19, "Dijkstra's algorithm uses a min-heap to:", ["Store all graph edges", "Always process the unvisited node with the current shortest known distance", "Detect cycles", "Count connected components"], 1, "Greedy: the min-heap ensures the next node processed has the definitively shortest path.", ["applications"]),
            mcq("djhp", 20, "Why can't we efficiently search for an arbitrary element in a heap?", ["Heaps don't support search", "Heap order is weaker than BST order — only parent-child relationship is guaranteed, not left-right", "It would take O(n log n)", "Only the root can be accessed"], 1, "A heap only guarantees parent ≤ children; arbitrary search requires O(n) scan unlike a BST's O(log n).", ["heap-vs-bst"]),
        ],
        cards("djhp", [
            ("Heap invariants", "SHAPE: complete binary tree. ORDER: parent ≤ children (min) or parent ≥ children (max)."),
            ("Array index formulas", "parent(i) = (i-1)/2.  left(i) = 2i+1.  right(i) = 2i+2."),
            ("Java PriorityQueue", "Min-heap by default. Max-heap: new PriorityQueue<>(Comparator.reverseOrder())."),
            ("peek vs poll", "peek(): O(1) read root. poll(): O(log n) remove root + sift-down."),
            ("Top-K largest", "Use MIN-heap of size k. New element replaces heap min if larger. O(n log k)."),
            ("Heapify (buildHeap)", "Sift-down from index n/2-1 to 0. O(n) total — not O(n log n)."),
            ("Median of stream", "Max-heap (lower half) + min-heap (upper half). Balance sizes ±1. Median = tops."),
            ("K-way merge", "Min-heap of k heads. poll → append to result → push next from same list. O(n log k)."),
        ], "heaps"),
        project(
            "Write HeapsLab.java with:\n1. topKLargest(int[] nums, int k) → int[]  using a min-heap of size k\n2. kthLargest(int[] nums, int k) → int  (same approach, return just the k-th)\n3. mergeKSorted(int[][] lists) → List<Integer>  k-way merge\n4. MedianFinder class with addNum(int) and findMedian() → double\nInclude main() tests: k=1, k=n, streams with even and odd counts.",
            ["topKLargest evicts heap min only when size exceeds k", "mergeKSorted handles empty sublists without NullPointerException", "MedianFinder addNum always rebalances so |lower.size()-upper.size()| <= 1", "findMedian returns a double (not int) — handles even-count averaging correctly"],
            ["topKLargest: after processing all elements, drain the min-heap into result — it comes out in ascending order.", "mergeKSorted: store [value, listIdx, elemIdx] in heap so you know which list to advance.", "MedianFinder: always push to lower first, then rebalance — this guarantees lower.max <= upper.min."],
        ),
    ))

    # ── GRAPHS BASICS ─────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-graphs-basics", 71,
        "Graph Basics in Java",
        "Adjacency list vs matrix, directed/undirected/weighted, BFS (shortest hops), DFS (explore fully), and cycle detection.",
        ["dsa-java-queues", "dsa-java-recursion"],
        guide(
            "Graph Basics in Java",
            "A graph is just a collection of **nodes (vertices)** connected by **edges**. Unlike a tree, edges can point anywhere — there is no root, no parent-child direction requirement, and cycles are allowed. Think of a city road map: intersections are nodes, roads are edges. Your job with most graph problems is to move through that map systematically without getting lost or going in circles.",
            [
                ("Representations — adjacency list vs adjacency matrix", code("java", "// ADJACENCY LIST — standard choice for sparse graphs\n// Space: O(V + E)   Edge lookup: O(degree)\n//\n//  Graph:  0──1──2\n//          |     |\n//          3─────┘\n//\nList<List<Integer>> adj = new ArrayList<>();\nfor (int i = 0; i < 4; i++) adj.add(new ArrayList<>());\nadj.get(0).add(1); adj.get(1).add(0);  // undirected: add both directions\nadj.get(1).add(2); adj.get(2).add(1);\nadj.get(2).add(3); adj.get(3).add(2);\nadj.get(0).add(3); adj.get(3).add(0);\n\n// ADJACENCY MATRIX — good for dense graphs or when edge lookup must be O(1)\n// Space: O(V²)\nint[][] matrix = new int[4][4];\nmatrix[0][1] = matrix[1][0] = 1;  // undirected edge 0-1")),
                ("BFS — explore level by level, like ripples in a pond", code("java", "// BFS gives you the SHORTEST PATH in hops (unweighted graphs).\n// Picture: drop a stone in water — the ripple front expands one ring at a time.\n// Nodes on ring k are all exactly k hops from the source.\n//\nint[] bfs(List<List<Integer>> adj, int src, int n) {\n    int[] dist = new int[n];\n    Arrays.fill(dist, -1);\n    dist[src] = 0;\n    Queue<Integer> q = new ArrayDeque<>();\n    q.offer(src);\n    while (!q.isEmpty()) {\n        int u = q.poll();\n        for (int v : adj.get(u)) {\n            if (dist[v] == -1) {     // not yet visited\n                dist[v] = dist[u] + 1;\n                q.offer(v);\n            }\n        }\n    }\n    return dist;  // dist[v] = shortest hops from src to v\n}")),
                ("DFS — dive deep first, backtrack when stuck", code("java", "// DFS explores one branch as far as possible before trying another.\n// Picture: navigating a maze — you go straight until a dead end,\n// then backtrack to the last junction and try a different turn.\n//\n// Recursive DFS\nvoid dfs(List<List<Integer>> adj, boolean[] visited, int u) {\n    visited[u] = true;\n    for (int v : adj.get(u)) {\n        if (!visited[v]) dfs(adj, visited, v);\n    }\n}\n\n// Iterative DFS (explicit stack — same effect, avoids stack overflow on huge graphs)\nvoid dfsIterative(List<List<Integer>> adj, int src, int n) {\n    boolean[] visited = new boolean[n];\n    Deque<Integer> stack = new ArrayDeque<>();\n    stack.push(src);\n    while (!stack.isEmpty()) {\n        int u = stack.pop();\n        if (visited[u]) continue;\n        visited[u] = true;\n        for (int v : adj.get(u)) if (!visited[v]) stack.push(v);\n    }\n}")),
                ("Connected components — run BFS/DFS from every unvisited node", code("java", "// Each call to dfs() from an unvisited node discovers one full component.\n// Like flood-fill: colour one island, then find the next uncoloured cell.\nint countComponents(List<List<Integer>> adj, int n) {\n    boolean[] visited = new boolean[n];\n    int components = 0;\n    for (int i = 0; i < n; i++) {\n        if (!visited[i]) {\n            dfs(adj, visited, i);  // marks entire component\n            components++;\n        }\n    }\n    return components;\n}")),
                ("Cycle detection — undirected vs directed", code("java", "// UNDIRECTED: during DFS, if you reach a visited node that is NOT your parent → cycle\nboolean hasCycleUndirected(List<List<Integer>> adj, int u, int parent, boolean[] vis) {\n    vis[u] = true;\n    for (int v : adj.get(u)) {\n        if (!vis[v]) { if (hasCycleUndirected(adj, v, u, vis)) return true; }\n        else if (v != parent) return true;  // visited & not parent → back edge → cycle\n    }\n    return false;\n}\n\n// DIRECTED: use 3-state coloring\n// WHITE(0) = unvisited, GRAY(1) = in current DFS path, BLACK(2) = fully processed\n// Back edge (white→gray) means cycle\nboolean hasCycleDirected(List<List<Integer>> adj, int u, int[] color) {\n    color[u] = 1;  // GRAY — currently exploring\n    for (int v : adj.get(u)) {\n        if (color[v] == 1) return true;       // back edge → cycle\n        if (color[v] == 0 && hasCycleDirected(adj, v, color)) return true;\n    }\n    color[u] = 2;  // BLACK — done\n    return false;\n}")),
            ],
            [
                "Forgetting to mark a node visited BEFORE enqueuing (BFS) — causes duplicate processing",
                "Undirected graph: not adding edges in BOTH directions when building adjacency list",
                "Cycle detection: in undirected graphs, the parent node looks like a back-edge — must track parent to avoid false positive",
                "Using adjacency matrix for very sparse graphs — wastes O(V²) space",
                "Directed vs undirected cycle detection: they need different algorithms (back-edge check vs 3-colour DFS)",
            ],
            [
                "Queues: BFS is level-order traversal using a queue",
                "Recursion/Stacks: DFS uses the call stack (or an explicit stack)",
                "Trees: a tree is a special graph (connected, acyclic) — tree algorithms are graph algorithms in disguise",
                "Heaps: Dijkstra replaces the BFS queue with a min-heap for weighted shortest paths",
            ],
        ),
        [
            mcq("djgb", 1, "Adjacency list space complexity for a graph with V vertices and E edges:", ["O(V²)", "O(V + E)", "O(E²)", "O(V × E)"], 1, "Each vertex stores its neighbour list. Total entries across all lists = E (directed) or 2E (undirected).", ["representation"]),
            mcq("djgb", 2, "Adjacency matrix space complexity:", ["O(V + E)", "O(V²)", "O(E log V)", "O(V)"], 1, "Stores a V×V grid — one cell per possible edge regardless of whether it exists.", ["representation"]),
            mcq("djgb", 3, "When is an adjacency matrix preferred over an adjacency list?", ["Always — O(1) edge lookup", "When the graph is dense (E ≈ V²) or O(1) edge existence check is critical", "When memory is limited", "When the graph is a tree"], 1, "Dense graphs fill most of the matrix anyway. O(1) hasEdge(u,v) vs O(degree) for list.", ["representation"]),
            mcq("djgb", 4, "BFS guarantees shortest path in:", ["Any graph", "Unweighted graphs — path with fewest hops", "Weighted graphs", "DAGs only"], 1, "BFS processes nodes level-by-level; level k = all nodes exactly k hops away. First time reached = shortest hop count.", ["bfs"]),
            code_output("djgb", 5, "BFS from node 0 in graph: 0-1, 0-2, 1-3. Visit order:", "// adjacency list:\n// 0: [1, 2]\n// 1: [0, 3]\n// 2: [0]\n// 3: [1]", ["0 1 2 3", "0 1 3 2", "0 2 1 3", "0 3 1 2"], 0, "Queue: [0] → process 0 → enqueue 1,2 → [1,2] → process 1 → enqueue 3 → [2,3] → process 2 → [3] → process 3. Order: 0,1,2,3.", ["bfs", "tracing"]),
            mcq("djgb", 6, "DFS explores a graph by:", ["Processing all neighbours before going deeper", "Going as deep as possible along one path before backtracking", "Always using a queue", "Visiting in sorted order"], 1, "DFS dives to the bottom of one branch, then backtracks to explore other branches — like navigating a maze.", ["dfs"]),
            mcq("djgb", 7, "Mark a node visited in BFS:", ["After polling it", "When enqueuing it — BEFORE it enters the queue", "At the end of the loop", "Only if it has neighbours"], 1, "Marking when enqueuing prevents the same node from being added to the queue multiple times.", ["bfs"]),
            mcq("djgb", 8, "DFS time complexity on a graph with V vertices and E edges:", ["O(V)", "O(E)", "O(V + E)", "O(V × E)"], 2, "Every vertex is visited once (O(V)) and every edge is examined once (O(E)).", ["complexity"]),
            mcq("djgb", 9, "To count connected components in an undirected graph:", ["Run BFS once from node 0", "Run BFS/DFS from every unvisited node; count how many times you start a new traversal", "Check if any node has degree 0", "Sort nodes by degree"], 1, "Each fresh traversal start discovers one new component. Component count = number of starts.", ["components"]),
            mcq("djgb", 10, "In undirected cycle detection via DFS, a cycle is found when:", ["A node is visited twice total", "You reach a visited node that is not the direct parent of the current node", "The stack is empty", "A node has degree > 2"], 1, "The parent edge looks like a back-edge — exclude it. Any OTHER visited neighbour means a cycle.", ["cycle"]),
            mcq("djgb", 11, "In directed graph cycle detection, 3-colour DFS uses GRAY to mean:", ["Unvisited", "Fully processed", "Currently on the active DFS path", "Visited in a previous component"], 2, "GRAY = in the current recursion stack. Meeting a GRAY node means we found a back-edge = cycle.", ["cycle"]),
            mcq("djgb", 12, "A directed graph with no cycles is called:", ["A tree", "A bipartite graph", "A DAG (Directed Acyclic Graph)", "A complete graph"], 2, "DAG: Directed Acyclic Graph. Topological sort is only possible on DAGs.", ["dag"]),
            mcq("djgb", 13, "Bipartite graph check can be done with:", ["DFS only", "BFS 2-colouring — try to colour graph with 2 colours so no adjacent nodes share a colour", "Cycle detection", "Topological sort"], 1, "BFS/DFS assigns alternating colours; if any edge connects same-colour nodes, graph is not bipartite.", ["bipartite"]),
            code_output("djgb", 14, "DFS from 0 in: 0→1, 0→2, 1→3. Visit order (recursive, process neighbours left-to-right):", "// 0: [1, 2]\n// 1: [3]\n// 2: []\n// 3: []", ["0 1 2 3", "0 2 1 3", "0 1 3 2", "0 3 1 2"], 2, "DFS: visit 0 → go to 1 → go to 3 (dead end, backtrack) → backtrack to 0 → go to 2. Order: 0,1,3,2.", ["dfs", "tracing"]),
            mcq("djgb", 15, "An undirected graph is connected if:", ["Every node has at least one edge", "BFS/DFS from any single node visits ALL vertices", "No vertex has degree > 1", "The adjacency matrix is symmetric"], 1, "Connected = one component. Single BFS/DFS should colour every vertex.", ["connectivity"]),
            mcq("djgb", 16, "Iterative DFS uses an explicit stack instead of recursion to:", ["Run faster", "Process nodes in BFS order", "Avoid StackOverflowError on very deep/large graphs", "Save memory always"], 2, "Recursive DFS can overflow the JVM call stack on graphs with millions of nodes. Explicit stack uses heap memory.", ["dfs"]),
            mcq("djgb", 17, "In a directed graph, edge u→v means:", ["v is also connected back to u", "You can travel from u to v but NOT necessarily from v to u", "u and v are in the same component", "u has higher priority than v"], 1, "Directed = one-way street. Reachability is asymmetric.", ["directed"]),
            multi("djgb", 18, "Which traversals can detect cycles in a graph?", ["BFS with visited set", "DFS with visited set (undirected)", "DFS with 3-colour state (directed)", "Topological sort — cycle exists if not all nodes processed"], [1, 2, 3], "BFS with just visited set detects connectivity but needs parent-tracking to detect undirected cycles reliably.", ["cycle"]),
            mcq("djgb", 19, "Flood fill (paint bucket tool) is which graph algorithm?", ["Dijkstra", "BFS or DFS on a grid graph", "Topological sort", "Union-Find"], 1, "Grid cells are nodes; adjacent cells sharing the same colour are edges. BFS/DFS fills the connected region.", ["applications"]),
            mcq("djgb", 20, "BFS vs DFS — which uses more memory for a wide, shallow graph?", ["DFS always uses more", "BFS — its queue can hold an entire level which may be very wide", "Same always", "Depends on edge weights"], 1, "BFS queue grows to the width of the current frontier. DFS stack depth equals the longest path — short for shallow graphs.", ["complexity"]),
        ],
        cards("djgb", [
            ("Adjacency list", "List<List<Integer>>. Space O(V+E). Best for sparse graphs (most real graphs)."),
            ("Adjacency matrix", "int[V][V]. Space O(V²). O(1) edge lookup. Best for dense graphs."),
            ("BFS = ripples", "Queue + visited set. Level k = all nodes exactly k hops away. Shortest path (unweighted)."),
            ("DFS = maze explorer", "Stack/recursion + visited set. Goes deep first, backtracks at dead ends."),
            ("Visit-before-enqueue", "Mark node visited when adding to BFS queue — prevents duplicate entries."),
            ("Connected components", "Count how many fresh BFS/DFS starts are needed to visit all nodes."),
            ("Undirected cycle", "DFS: back-edge to a visited non-parent node = cycle."),
            ("Directed cycle (3-colour)", "WHITE=unvisited, GRAY=in stack, BLACK=done. GRAY neighbour = cycle."),
        ], "graphs"),
        project(
            "Write GraphsLab.java using adjacency list (List<List<Integer>>):\n1. buildGraph(int n, int[][] edges, boolean directed) → List<List<Integer>>\n2. bfsShortestHops(graph, int src) → int[]  (distances from src)\n3. countComponents(graph, int n) → int\n4. hasCycleUndirected(graph, int n) → boolean\n5. isBipartite(graph, int n) → boolean  (BFS 2-colouring)\nInclude main() tests: disconnected graph, graph with cycle, bipartite grid, star graph.",
            ["buildGraph adds both directions for undirected", "bfsShortestHops marks visited on enqueue not on poll", "countComponents starts fresh DFS for each unvisited node", "hasCycleUndirected tracks parent to avoid false positive on the back-edge", "isBipartite returns false as soon as any edge connects same-colour nodes"],
            ["bfsShortestHops: initialise dist[] = -1, set dist[src]=0 before enqueueing src.", "hasCycleUndirected: pass parent=-1 for the initial call.", "isBipartite: use int[] color = -1/0/1. Start BFS, assign 0 to src, alternate 1-color for neighbours."],
        ),
    ))

    # ── GRAPHS ADVANCED ───────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-graphs-advanced", 72,
        "Advanced Graph Algorithms in Java",
        "Dijkstra's shortest path, topological sort (Kahn's BFS + DFS), Bellman-Ford, and Minimum Spanning Tree (Prim/Kruskal).",
        ["dsa-java-graphs-basics", "dsa-java-heaps"],
        guide(
            "Advanced Graph Algorithms in Java",
            "Once you can navigate a graph (BFS/DFS), the next leap is answering *weighted* questions: 'What is the cheapest route?' and *ordering* questions: 'What tasks must come before others?' These algorithms each solve a specific shape of problem — understanding WHEN to use each is as important as HOW to implement it.",
            [
                ("Dijkstra — cheapest path from one source", code("java", "// Mental model: you're expanding a 'settled frontier' outward.\n// At each step, pick the UNSETTLED node with the cheapest known distance\n// (greedy). A min-heap makes this O((V+E) log V).\n//\n// Key invariant: once a node is polled from the heap, its distance is FINAL.\n// This is why Dijkstra fails with NEGATIVE weights — a future negative edge\n// could improve an already-settled distance.\n//\nint[] dijkstra(List<List<int[]>> adj, int src, int n) {\n    int[] dist = new int[n];\n    Arrays.fill(dist, Integer.MAX_VALUE);\n    dist[src] = 0;\n    // heap entry: [distance, node]\n    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));\n    pq.offer(new int[]{0, src});\n    while (!pq.isEmpty()) {\n        int[] cur = pq.poll();\n        int d = cur[0], u = cur[1];\n        if (d > dist[u]) continue;  // stale entry — skip\n        for (int[] edge : adj.get(u)) {\n            int v = edge[0], w = edge[1];\n            if (dist[u] + w < dist[v]) {\n                dist[v] = dist[u] + w;\n                pq.offer(new int[]{dist[v], v});\n            }\n        }\n    }\n    return dist;\n}")),
                ("Topological Sort — ordering tasks with dependencies", code("java", "// A topological order lists nodes so that every directed edge u→v\n// has u BEFORE v in the list.  Only possible on DAGs (no cycles).\n//\n// KAHN'S ALGORITHM (BFS-based — intuitive)\n// Think of it like peeling an onion: remove all nodes with no incoming\n// dependencies first, which exposes the next 'layer' of ready tasks.\nList<Integer> topoSortKahn(List<List<Integer>> adj, int n) {\n    int[] inDegree = new int[n];\n    for (int u = 0; u < n; u++)\n        for (int v : adj.get(u)) inDegree[v]++;\n    Queue<Integer> q = new ArrayDeque<>();\n    for (int i = 0; i < n; i++) if (inDegree[i] == 0) q.offer(i);\n    List<Integer> order = new ArrayList<>();\n    while (!q.isEmpty()) {\n        int u = q.poll();\n        order.add(u);\n        for (int v : adj.get(u)) if (--inDegree[v] == 0) q.offer(v);\n    }\n    return order.size() == n ? order : Collections.emptyList(); // empty = cycle detected\n}")),
                ("Topological Sort — DFS post-order reversal", code("java", "// DFS topo: visit all dependencies FIRST, then push current node to stack.\n// Reverse the stack at the end → topological order.\n// Why? Post-order means 'I'm done with everything that depends on me first.'\nvoid dfsTopoSort(List<List<Integer>> adj, int u, boolean[] vis, Deque<Integer> stack) {\n    vis[u] = true;\n    for (int v : adj.get(u)) if (!vis[v]) dfsTopoSort(adj, v, vis, stack);\n    stack.push(u);  // push AFTER all descendants are done\n}")),
                ("Bellman-Ford — handles negative weights", code("java", "// Relax ALL edges V-1 times. Each pass can extend shortest paths by one more hop.\n// Run one more pass: if any distance still improves → negative cycle exists.\n//\n// Mental model: imagine water slowly finding its lowest level —\n// it takes at most V-1 steps to propagate cheapest costs across V nodes.\nint[] bellmanFord(int n, int[][] edges, int src) {  // edges: [u, v, weight]\n    int[] dist = new int[n];\n    Arrays.fill(dist, Integer.MAX_VALUE);\n    dist[src] = 0;\n    for (int i = 0; i < n - 1; i++)           // V-1 relaxation passes\n        for (int[] e : edges)\n            if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]])\n                dist[e[1]] = dist[e[0]] + e[2];\n    // V-th pass: detect negative cycle\n    for (int[] e : edges)\n        if (dist[e[0]] != Integer.MAX_VALUE && dist[e[0]] + e[2] < dist[e[1]])\n            return null;  // negative cycle\n    return dist;\n}")),
                ("Minimum Spanning Tree — cheapest connected backbone", code("java", "// MST = subset of edges connecting ALL vertices with minimum total weight, no cycles.\n//\n// KRUSKAL'S (sort edges, use Union-Find to avoid cycles):\n// Picture: sort all roads by cost, greedily add cheapest that don't form a loop.\n//\n// PRIM'S (grow one tree using a min-heap — similar to Dijkstra):\n// Picture: start at any node, always add the cheapest edge that connects\n// a NEW node to the already-grown tree.\n//\n// Kruskal outline:\nArrays.sort(edges, Comparator.comparingInt(e -> e[2]));\nUnionFind uf = new UnionFind(n);\nint mstWeight = 0;\nfor (int[] e : edges) {\n    if (uf.union(e[0], e[1])) {   // only add if it doesn't form a cycle\n        mstWeight += e[2];\n    }\n}")),
            ],
            [
                "Using Dijkstra on a graph with negative edge weights — it gives wrong answers; use Bellman-Ford instead",
                "Not skipping stale heap entries in Dijkstra (d > dist[u] check) — causes redundant processing",
                "Topological sort on a graph with a cycle — Kahn's detects this (output size < n); plain DFS topo does not detect it automatically",
                "Bellman-Ford: running only V-2 relaxation passes (need exactly V-1)",
                "MST vs shortest path: MST minimises total edge weight tree-wide; Dijkstra minimises distance from one source — they are different problems",
            ],
            [
                "Heaps: Dijkstra needs a min-heap; Prim's MST also uses one",
                "Graphs BFS/DFS: Kahn's topo sort is BFS on a DAG; DFS topo uses post-order",
                "Union-Find: Kruskal's MST uses Union-Find for O(α(n)) cycle detection",
                "DP: Bellman-Ford and Floyd-Warshall are essentially DP on graphs",
            ],
        ),
        [
            mcq("djga", 1, "Dijkstra's algorithm finds:", ["All spanning trees", "Shortest paths from one source to all vertices in a weighted graph", "Minimum spanning tree", "Topological order"], 1, "Single-source shortest path on graphs with non-negative edge weights.", ["dijkstra"]),
            mcq("djga", 2, "Dijkstra fails with negative edge weights because:", ["The heap can't store negative numbers", "Once a node is settled its distance is considered final — a later negative edge could improve it", "It doesn't visit all nodes", "Negative weights cause infinite loops"], 1, "The greedy invariant breaks: a 'settled' node could be reached more cheaply via a not-yet-settled node + negative edge.", ["dijkstra"]),
            mcq("djga", 3, "Dijkstra time complexity with a binary min-heap:", ["O(V²)", "O(E log V)", "O((V + E) log V)", "O(VE)"], 2, "Each vertex is extracted once O(V log V) and each edge may trigger a heap update O(E log V).", ["complexity"]),
            code_output("djga", 4, "Dijkstra from node 0: edges 0→1(4), 0→2(1), 2→1(2). Shortest dist to node 1:", "// 0 --4--> 1\n// 0 --1--> 2 --2--> 1\n// Direct: 4   Via 2: 1+2=3", ["4", "3", "2", "1"], 1, "Path 0→2→1 costs 1+2=3 < direct edge 4. Dijkstra finds 3.", ["dijkstra", "tracing"]),
            mcq("djga", 5, "The 'stale entry skip' check (if d > dist[u] continue) in Dijkstra is needed because:", ["The heap has a bug", "A node can be re-added to the heap with a better distance; old entries become outdated", "It improves average complexity", "Negative weights require it"], 1, "When a shorter path is found, the old heap entry is not removed — it's simply ignored when polled.", ["dijkstra"]),
            mcq("djga", 6, "Topological sort is only valid on:", ["Any directed graph", "Undirected graphs", "DAGs — Directed Acyclic Graphs", "Complete graphs"], 2, "A cycle means there is no valid ordering (A before B before A is impossible).", ["topo-sort"]),
            mcq("djga", 7, "Kahn's algorithm starts by enqueuing nodes with:", ["The most outgoing edges", "In-degree zero — no prerequisites", "The smallest values", "All leaf nodes"], 1, "Nodes with no incoming edges have no dependencies — they can be processed first.", ["topo-sort"]),
            mcq("djga", 8, "If Kahn's algorithm finishes with output size < n, it means:", ["Some nodes are unreachable", "A cycle exists in the graph", "The graph is disconnected", "In-degree calculation was wrong"], 1, "Cyclic nodes can never reach in-degree 0 — they are never enqueued.", ["topo-sort", "cycle"]),
            code_output("djga", 9, "Topological sort of: A→C, B→C, C→D. One valid order:", "// A and B have no prerequisites\n// C needs both A and B\n// D needs C", ["C A B D", "A B C D", "D C A B", "A C B D"], 1, "A and B (in-degree 0) come first, then C (after both done), then D. A B C D is valid.", ["topo-sort", "tracing"]),
            mcq("djga", 10, "DFS topological sort pushes a node to the result stack:", ["Before visiting its neighbours", "After ALL its descendants are fully processed (post-order)", "Alphabetically", "When first visited"], 1, "Post-order ensures all nodes that depend on u are already in the stack before u is pushed.", ["topo-sort"]),
            mcq("djga", 11, "Bellman-Ford runs how many edge-relaxation passes?", ["1", "log V", "V - 1", "V"], 2, "Shortest paths use at most V-1 edges. One pass extends paths by one hop, so V-1 passes cover all possible paths.", ["bellman-ford"]),
            mcq("djga", 12, "Bellman-Ford detects negative cycles by:", ["Counting visited nodes", "Running a V-th relaxation pass — if any distance still improves, a negative cycle exists", "Checking for negative edge weights", "Using DFS"], 1, "After V-1 passes all shortest paths are final. Improvement in pass V means a negative cycle allows infinite cost reduction.", ["bellman-ford"]),
            mcq("djga", 13, "Dijkstra vs Bellman-Ford — when to use which:", ["Always Dijkstra (faster)", "Dijkstra for non-negative weights (faster); Bellman-Ford when negative weights exist", "Bellman-Ford always (safer)", "Same — always interchangeable"], 1, "Dijkstra O((V+E)log V) beats Bellman-Ford O(VE) but requires non-negative weights.", ["comparison"]),
            mcq("djga", 14, "A Minimum Spanning Tree of a graph with V vertices has exactly:", ["V edges", "V - 1 edges", "E edges", "V + 1 edges"], 1, "A spanning tree on V nodes always has exactly V-1 edges — minimum to stay connected without a cycle.", ["mst"]),
            mcq("djga", 15, "Kruskal's MST algorithm adds edges in order of:", ["Random order", "Decreasing weight", "Increasing weight — greedily pick cheapest that don't form a cycle", "Alphabetical node order"], 2, "Sort edges ascending, add each if it connects two different components (Union-Find check).", ["mst", "kruskal"]),
            mcq("djga", 16, "Prim's MST algorithm is most similar to:", ["Bellman-Ford", "Kahn's topological sort", "Dijkstra — both grow a 'settled' set using a min-heap on edge costs", "DFS"], 2, "Both use a min-heap to greedily pick the cheapest next step; Dijkstra minimises cumulative path, Prim minimises single edge.", ["mst", "prim"]),
            mcq("djga", 17, "Union-Find is used in Kruskal's because:", ["It sorts edges", "It detects whether adding an edge creates a cycle in O(α(n)) time", "It computes MST weight", "It replaces the heap"], 1, "Two nodes in the same component means adding an edge between them creates a cycle.", ["kruskal", "union-find"]),
            multi("djga", 18, "Which graph problems require a min-heap for efficient solution?", ["Dijkstra's shortest path", "Prim's MST", "Kahn's topological sort", "Bellman-Ford"], [0, 1], "Kahn's uses a plain queue (BFS on in-degrees). Bellman-Ford iterates all edges — no heap needed.", ["applications"]),
            mcq("djga", 19, "Course schedule problem (can all courses be completed given prerequisites?) maps to:", ["BFS shortest path", "Dijkstra with weighted courses", "Topological sort — cycle detection on a DAG", "MST of course graph"], 2, "Prerequisites are directed edges. If the dependency graph has a cycle, not all courses can be taken.", ["applications"]),
            mcq("djga", 20, "Floyd-Warshall finds:", ["Single-source shortest paths", "Minimum spanning tree", "All-pairs shortest paths in O(V³)", "Topological order"], 2, "DP on all (source, destination) pairs. Works with negative weights (not negative cycles). O(V³) time O(V²) space.", ["floyd-warshall"]),
        ],
        cards("djga", [
            ("Dijkstra", "Single-source shortest path. Min-heap. O((V+E)log V). Non-negative weights only."),
            ("Dijkstra stale skip", "if (d > dist[u]) continue — ignore outdated heap entries."),
            ("Topological sort", "Order nodes so every edge u→v has u before v. Only on DAGs."),
            ("Kahn's algorithm", "BFS on in-degrees. Enqueue in-degree-0 nodes. Output size < n → cycle."),
            ("Bellman-Ford", "V-1 relaxation passes. Handles negative weights. V-th pass detects negative cycle."),
            ("MST definition", "V-1 edges connecting all V nodes with minimum total weight, no cycles."),
            ("Kruskal's MST", "Sort edges by weight, add if no cycle (Union-Find check). O(E log E)."),
            ("Prim's MST", "Grow tree from one node via min-heap on edge costs. Like Dijkstra for MST."),
        ], "graphs-advanced"),
        project(
            "Write AdvancedGraphsLab.java:\n1. dijkstra(List<List<int[]>> adj, int src, int n) → int[]\n2. topoSortKahn(List<List<Integer>> adj, int n) → List<Integer>  (empty list if cycle)\n3. canFinish(int numCourses, int[][] prerequisites) → boolean  (course schedule)\n4. bellmanFord(int n, int[][] edges, int src) → int[]  (null if negative cycle)\nInclude main() tests: graph with shorter indirect path, DAG, cyclic graph, graph with negative edge.",
            ["dijkstra skips stale heap entries", "topoSortKahn returns empty list when cycle detected (output.size() < n)", "canFinish reuses Kahn's cycle detection logic", "bellmanFord returns null on negative cycle detection in V-th pass"],
            ["dijkstra: adj entries are int[]{neighbour, weight}. Initialise all dist[] to Integer.MAX_VALUE.", "topoSortKahn: build inDegree[] by scanning all adjacency lists before starting BFS.", "bellmanFord: guard against Integer.MAX_VALUE + weight overflow with a != MAX_VALUE check."],
        ),
    ))

    # ── DP INTRO ──────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-dp-intro", 73,
        "Dynamic Programming Intro in Java",
        "Overlapping subproblems, optimal substructure, memoization (top-down) vs tabulation (bottom-up), Fibonacci, climbing stairs, coin change.",
        ["dsa-java-recursion", "dsa-java-arrays"],
        guide(
            "Dynamic Programming Intro in Java",
            "Dynamic Programming (DP) is not a data structure or an algorithm — it is a **problem-solving technique**. The core idea: if a recursive solution recomputes the same sub-answers over and over, *remember* those answers (memoize or tabulate) and reuse them. The result is often an exponential-time brute force transformed into polynomial time.",
            [
                ("The two DP signals — recognise them first", "Before writing any code, ask two questions:\n\n**1. Overlapping subproblems** — does the recursion tree compute the same inputs repeatedly?\n\n```\nfib(5)\n├── fib(4)           fib(3) computed here\n│   ├── fib(3)        ↑ already computed above\n│   └── fib(2)\n└── fib(3)   ← DUPLICATE — this is the signal\n```\n\n**2. Optimal substructure** — can the best answer to a big problem be built from best answers to smaller problems? (Shortest path: yes. Longest simple path: no.)"),
                ("Memoization — top-down, lazy, recursive", code("java", "// Top-down: start from the big problem, recurse down, cache on the way back up.\n// Think of it as: 'solve it recursively, but write the answer on a sticky note\n// so you never solve the same sub-problem twice.'\n//\nint fib(int n, int[] memo) {\n    if (n <= 1) return n;\n    if (memo[n] != -1) return memo[n];     // sticky note already exists\n    return memo[n] = fib(n-1, memo) + fib(n-2, memo);  // write and return\n}\n// Usage: int[] memo = new int[n+1]; Arrays.fill(memo, -1); fib(n, memo);\n// Time: O(n)   Space: O(n) array + O(n) call stack")),
                ("Tabulation — bottom-up, eager, iterative", code("java", "// Bottom-up: fill a table from the smallest sub-problems up to the answer.\n// No recursion. Think of it as: 'fill in a spreadsheet row by row.\n// Each cell needs only the cells already filled.'\n//\nint fib(int n) {\n    if (n <= 1) return n;\n    int[] dp = new int[n + 1];\n    dp[0] = 0; dp[1] = 1;\n    for (int i = 2; i <= n; i++)\n        dp[i] = dp[i-1] + dp[i-2];\n    return dp[n];\n}\n// Space optimised: only need last 2 values\nint fibO1(int n) {\n    if (n <= 1) return n;\n    int a = 0, b = 1;\n    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }\n    return b;\n}\n// Time: O(n)   Space: O(1)")),
                ("Climbing Stairs — first 1D DP pattern", code("java", "// Problem: n stairs, each step 1 or 2. How many distinct ways to reach top?\n// At stair i, you came from i-1 (one step) or i-2 (two steps).\n// dp[i] = dp[i-1] + dp[i-2]  ← same recurrence as Fibonacci!\n//\n//  n=4:  dp = [1, 1, 2, 3, 5]\n//         0   1  2  3  4   ← index\n//  ways to reach stair 4 = 5\nint climbStairs(int n) {\n    if (n <= 2) return n;\n    int a = 1, b = 2;\n    for (int i = 3; i <= n; i++) { int c = a + b; a = b; b = c; }\n    return b;\n}")),
                ("Coin Change — first 'unbounded knapsack' pattern", code("java", "// Problem: fewest coins from denominations[] to make amount.\n// dp[i] = min coins to make amount i\n// For each coin, if coin <= i: dp[i] = min(dp[i], dp[i - coin] + 1)\n//\n// Visualise: building a table left to right.\n// dp[0] = 0 (base: 0 coins needed for amount 0)\n// dp[i] = infinity initially → updated when a coin fits\nint coinChange(int[] coins, int amount) {\n    int[] dp = new int[amount + 1];\n    Arrays.fill(dp, amount + 1);  // sentinel 'infinity'\n    dp[0] = 0;\n    for (int i = 1; i <= amount; i++)\n        for (int coin : coins)\n            if (coin <= i) dp[i] = Math.min(dp[i], dp[i - coin] + 1);\n    return dp[amount] > amount ? -1 : dp[amount];\n}")),
            ],
            [
                "Confusing memoization (top-down) with tabulation (bottom-up) — both are DP, different implementation styles",
                "Forgetting the base cases in the DP table — dp[0] is almost always the foundation everything else builds on",
                "Using -1 as a memo sentinel when -1 is a valid answer — choose a sentinel that cannot be a valid result",
                "Not identifying overlapping subproblems first — applying DP to a problem without them gains nothing",
                "Coin change: filling dp[i] with 0 as 'infinity' makes finding the minimum impossible",
            ],
            [
                "Recursion: memoization IS recursion + caching — understanding recursion is the prerequisite",
                "Arrays: tabulation stores the DP table in an array — array indexing is fundamental",
                "Graphs: Dijkstra and Bellman-Ford are DP on graphs (optimal substructure of paths)",
                "Searching: binary search on DP tables is a common optimisation for O(n log n) LIS",
            ],
        ),
        [
            mcq("djdp", 1, "Dynamic Programming is applicable when a problem has:", ["Only one solution path", "Overlapping subproblems AND optimal substructure", "No recursive structure", "Only integer inputs"], 1, "Both properties must hold: subproblems repeat AND the global optimum can be built from subproblem optima.", ["fundamentals"]),
            mcq("djdp", 2, "Overlapping subproblems means:", ["The problem has duplicate input data", "The recursion tree computes the same inputs multiple times", "The problem has multiple valid answers", "Sub-arrays overlap in memory"], 1, "Naive Fibonacci computes fib(2) an exponential number of times — that is the overlap.", ["fundamentals"]),
            mcq("djdp", 3, "Memoization transforms naive Fibonacci from O(2^n) to O(n) because:", ["It sorts the recursion tree", "Each of the n unique sub-problems is solved exactly once and cached", "It eliminates the base case", "The call stack shrinks"], 1, "Cache lookup is O(1) — every unique fib(k) is computed once, giving n unique computations.", ["memoization"]),
            code_output("djdp", 4, "Tabulated Fibonacci dp[] for n=5:", "// dp[0]=0, dp[1]=1, dp[i]=dp[i-1]+dp[i-2]\nint[] dp = new int[6];\ndp[0]=0; dp[1]=1;\nfor(int i=2;i<=5;i++) dp[i]=dp[i-1]+dp[i-2];\nSystem.out.println(dp[5]);", ["3", "5", "8", "4"], 1, "dp = [0,1,1,2,3,5]. dp[5] = 5.", ["tabulation", "tracing"]),
            mcq("djdp", 5, "Tabulation (bottom-up) advantage over memoization (top-down):", ["Always faster in theory", "No recursion overhead or call-stack risk; easier to apply space optimisation", "Handles negative inputs better", "Requires less code"], 1, "Iterative table fills with no call-stack depth; also you can reduce space once old states are no longer needed.", ["tabulation"]),
            mcq("djdp", 6, "Space-optimised Fibonacci uses O(1) space instead of O(n) by:", ["Using bit manipulation", "Keeping only the last two computed values", "Sorting the array first", "Using a HashSet"], 1, "dp[i] depends only on dp[i-1] and dp[i-2] — two variables suffice.", ["space-optimisation"]),
            mcq("djdp", 7, "Climbing stairs (1 or 2 steps) recurrence is:", ["dp[i] = dp[i-1] * dp[i-2]", "dp[i] = dp[i-1] + dp[i-2]", "dp[i] = 2 * dp[i-1]", "dp[i] = dp[i/2] + 1"], 1, "At stair i you arrived from i-1 or i-2 — total ways = sum of ways to reach those two stairs.", ["climbing-stairs"]),
            code_output("djdp", 8, "Climbing stairs n=4. Answer:", "// dp[1]=1, dp[2]=2, dp[3]=3, dp[4]=5", ["3", "4", "5", "8"], 2, "Ways: {1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2} = 5.", ["climbing-stairs", "tracing"]),
            mcq("djdp", 9, "Coin change dp[] initial fill value should be:", ["0", "-1", "amount + 1 (a safe infinity beyond any valid answer)", "Integer.MAX_VALUE always"], 2, "Using amount+1 avoids overflow when doing min(dp[i], dp[i-coin]+1). Valid answer is always <= amount.", ["coin-change"]),
            mcq("djdp", 10, "Coin change inner loop iterates over:", ["All amounts from 0 to amount", "All coins for each amount i", "All amounts for each coin (also valid — same result)", "Only prime coins"], 1, "For each target amount i, try every coin — pick the one that gives the fewest total coins.", ["coin-change"]),
            mcq("djdp", 11, "Optimal substructure means:", ["The problem can be split into independent subproblems", "The optimal solution to the big problem contains optimal solutions to its subproblems", "Greedy always works", "All subproblems have the same size"], 1, "The coin change optimum for amount 11 builds on the optimum for amount 11-coin — that is optimal substructure.", ["fundamentals"]),
            mcq("djdp", 12, "A memo sentinel value of -1 is UNSAFE when:", ["-1 is returned for 'not found'", "All valid answers are non-negative", "-1 is a valid answer to a subproblem", "The array is large"], 2, "If a subproblem can genuinely return -1, using -1 as sentinel causes you to recompute it unnecessarily.", ["memoization"]),
            mcq("djdp", 13, "0/1 knapsack differs from coin change in that each item:", ["Has no weight", "Can be used UNLIMITED times (coin change) vs exactly ONCE (0/1 knapsack)", "Must be sorted first", "Has no value"], 1, "Unbounded: inner loop can reuse same coin. 0/1: must iterate items in outer loop and capacity backward.", ["knapsack"]),
            multi("djdp", 14, "Which are valid 1D DP problems?", ["Fibonacci sequence", "Climbing stairs", "Coin change (min coins)", "All-pairs shortest paths"], [0, 1, 2], "All-pairs shortest paths (Floyd-Warshall) is 2D DP. The others use a single 1D array.", ["patterns"]),
            mcq("djdp", 15, "The 'state' in a DP problem represents:", ["The current index only", "All information needed to compute the answer from this point forward without looking backward", "The recursion depth", "The number of function calls"], 1, "State definition is the hardest part of DP. Example: (index, remaining capacity) for knapsack.", ["state"]),
            mcq("djdp", 16, "House robber: dp[i] = max money from first i houses, can't rob adjacent. Recurrence:", ["dp[i] = dp[i-1] + nums[i]", "dp[i] = max(dp[i-1], dp[i-2] + nums[i])", "dp[i] = dp[i-2] + dp[i-1]", "dp[i] = nums[i] + dp[i-3]"], 1, "At house i: either skip it (dp[i-1]) or rob it (dp[i-2] + nums[i]).", ["house-robber"]),
            code_output("djdp", 17, "House robber on [2,7,9,3,1]. Max:", "// dp[0]=2, dp[1]=7\n// dp[2]=max(7, 2+9)=11\n// dp[3]=max(11, 7+3)=11\n// dp[4]=max(11, 11+1)=12", ["11", "12", "13", "9"], 1, "Rob houses 0,2,4: 2+9+1=12.", ["house-robber", "tracing"]),
            mcq("djdp", 18, "Top-down DP call stack depth for fib(1000) could cause:", ["Heap out of memory", "StackOverflowError — 1000 recursive frames deep", "Array index out of bounds", "Nothing — Java handles it"], 1, "JVM default stack handles ~5000–10000 frames. fib(1000) is fine, but fib(100000) could fail. Tabulation avoids this.", ["overflow"]),
            mcq("djdp", 19, "'Can I reach the last index?' (Jump Game) uses DP where dp[i] means:", ["Number of jumps from i", "Whether index i is reachable from index 0", "Max jump length at i", "Distance to end"], 1, "dp[i] = true if any previous reachable index j had jump >= i-j.", ["jump-game"]),
            mcq("djdp", 20, "Greedy works for some problems where DP does — when should you prefer greedy?", ["Always, it is faster", "When a locally optimal choice provably leads to a global optimum (e.g. coin change with canonical denominations)", "Never — DP is always correct", "When the input is sorted"], 1, "Greedy coin change works for {1,5,10,25} but fails for arbitrary denominations — DP is the safe general solution.", ["greedy-vs-dp"]),
        ],
        cards("djdp", [
            ("Two DP signals", "1. Overlapping subproblems (same inputs recomputed). 2. Optimal substructure (big optimum built from sub-optima)."),
            ("Memoization (top-down)", "Recurse normally; cache result before returning. Uses call stack + memo array."),
            ("Tabulation (bottom-up)", "Fill a dp[] table from base cases up. No recursion. Easier to space-optimise."),
            ("Space optimisation", "When dp[i] only needs dp[i-1] and dp[i-2], use two variables instead of array."),
            ("Coin change pattern", "dp[0]=0, dp[i]=min(dp[i-coin]+1) for all coins. Init dp[1..n] = amount+1 (infinity)."),
            ("Climbing stairs recurrence", "dp[i] = dp[i-1] + dp[i-2]. Same as Fibonacci. dp[1]=1, dp[2]=2."),
            ("State definition", "All info needed to solve a subproblem without looking backward. Hardest DP step."),
            ("0/1 vs unbounded knapsack", "0/1: each item used once (iterate capacity backward). Unbounded: reuse allowed (forward)."),
        ], "dp"),
        project(
            "Write DPIntroLab.java with:\n1. fibonacci(int n) — tabulation, O(n) time O(1) space\n2. climbStairs(int n) — tabulation O(1) space\n3. coinChange(int[] coins, int amount) → int  (-1 if impossible)\n4. rob(int[] nums) → int  (house robber)\n5. canJump(int[] nums) → boolean  (Jump Game — greedy DP)\nInclude main() tests: coin change impossible case, house robber single element, jump game with zero gap.",
            ["fibonacci uses only two variables, no array", "climbStairs correctly handles n=1 and n=2 base cases", "coinChange initialises dp[1..amount] to amount+1 (not MAX_VALUE)", "rob handles empty array and single-element array", "canJump tracks maxReach and returns false if i > maxReach"],
            ["coinChange: if dp[amount] > amount after filling, return -1.", "rob: iterate with two variables prev2, prev1 for O(1) space.", "canJump: maxReach = max(maxReach, i + nums[i]). If i > maxReach at any point, return false."],
        ),
    ))

    # ── DP SEQUENCES ──────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-dp-sequences", 74,
        "DP on Sequences in Java",
        "Longest Common Subsequence (LCS), Longest Increasing Subsequence (LIS), Edit Distance — 2D DP table intuition and space optimisation.",
        ["dsa-java-dp-intro", "dsa-java-strings"],
        guide(
            "DP on Sequences in Java",
            "Sequence DP problems ask about relationships *between* two strings or *within* one sequence. The key mental shift from 1D DP: you now build a **2D table** where rows represent one sequence and columns represent another, and each cell answers a sub-question about prefixes of both.",
            [
                ("LCS — Longest Common Subsequence", code("java", "// A subsequence keeps relative order but skips characters.\n// 'ACE' is a subsequence of 'ABCDE'.\n//\n// dp[i][j] = LCS length of s1[0..i-1] and s2[0..j-1]\n//\n// Visualise the table for s1='ABCD', s2='ACBD':\n//       ''  A  C  B  D\n//  ''  [ 0  0  0  0  0 ]\n//   A  [ 0  1  1  1  1 ]\n//   B  [ 0  1  1  2  2 ]\n//   C  [ 0  1  2  2  2 ]\n//   D  [ 0  1  2  2  3 ]  ← LCS = 3\n//\nint lcs(String s1, String s2) {\n    int m = s1.length(), n = s2.length();\n    int[][] dp = new int[m+1][n+1];\n    for (int i = 1; i <= m; i++)\n        for (int j = 1; j <= n; j++)\n            if (s1.charAt(i-1) == s2.charAt(j-1))\n                dp[i][j] = 1 + dp[i-1][j-1];  // chars match: extend diagonal\n            else\n                dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);  // skip one char\n    return dp[m][n];\n}")),
                ("LIS — Longest Increasing Subsequence", code("java", "// Within ONE array, find the longest subsequence where each element is STRICTLY larger.\n// [1, 3, 2, 4] → LIS = [1, 2, 4] or [1, 3, 4], length 3.\n//\n// O(n²) DP approach:\n// dp[i] = length of LIS ending at index i\n//\n//  nums: [1, 3, 2, 4]\n//  dp:   [1, 2, 2, 3]   ← dp[3]=3 because 4 extends either [1,3] or [1,2]\nint lisN2(int[] nums) {\n    int n = nums.length, max = 1;\n    int[] dp = new int[n];\n    Arrays.fill(dp, 1);\n    for (int i = 1; i < n; i++)\n        for (int j = 0; j < i; j++)\n            if (nums[j] < nums[i]) { dp[i] = Math.max(dp[i], dp[j]+1); max = Math.max(max, dp[i]); }\n    return max;\n}\n\n// O(n log n) via patience sorting (binary search on 'tails' array)\nint lisNLogN(int[] nums) {\n    List<Integer> tails = new ArrayList<>();\n    for (int n : nums) {\n        int pos = Collections.binarySearch(tails, n);\n        if (pos < 0) pos = -(pos + 1);\n        if (pos == tails.size()) tails.add(n);\n        else tails.set(pos, n);\n    }\n    return tails.size();\n}")),
                ("Edit Distance (Levenshtein)", code("java", "// Minimum operations (insert / delete / replace) to transform word1 into word2.\n//\n// dp[i][j] = edit distance between word1[0..i-1] and word2[0..j-1]\n//\n// Visualise 'horse' → 'ros':\n//       ''  r  o  s\n//  ''  [ 0  1  2  3 ]\n//   h  [ 1  1  2  3 ]\n//   o  [ 2  2  1  2 ]\n//   r  [ 3  2  2  2 ]\n//   s  [ 4  3  3  2 ]\n//   e  [ 5  4  4  3 ]  ← edit distance = 3\n//\nint editDistance(String w1, String w2) {\n    int m = w1.length(), n = w2.length();\n    int[][] dp = new int[m+1][n+1];\n    for (int i = 0; i <= m; i++) dp[i][0] = i;  // delete all of w1\n    for (int j = 0; j <= n; j++) dp[0][j] = j;  // insert all of w2\n    for (int i = 1; i <= m; i++)\n        for (int j = 1; j <= n; j++)\n            if (w1.charAt(i-1) == w2.charAt(j-1))\n                dp[i][j] = dp[i-1][j-1];          // no operation needed\n            else\n                dp[i][j] = 1 + Math.min(dp[i-1][j-1],   // replace\n                                Math.min(dp[i-1][j],      // delete from w1\n                                         dp[i][j-1]));   // insert into w1\n    return dp[m][n];\n}")),
                ("Space optimisation — rolling row", code("java", "// LCS and edit distance only look at the previous row.\n// Replace dp[m+1][n+1] with two 1D arrays: prev[] and curr[].\nint lcsSpaceOptimised(String s1, String s2) {\n    int m = s1.length(), n = s2.length();\n    int[] prev = new int[n+1], curr = new int[n+1];\n    for (int i = 1; i <= m; i++) {\n        for (int j = 1; j <= n; j++)\n            curr[j] = s1.charAt(i-1) == s2.charAt(j-1)\n                ? 1 + prev[j-1]\n                : Math.max(prev[j], curr[j-1]);\n        int[] tmp = prev; prev = curr; curr = tmp;  // swap\n        Arrays.fill(curr, 0);\n    }\n    return prev[n];\n}\n// Space: O(n) instead of O(m*n)")),
            ],
            [
                "Confusing subsequence (order preserved, can skip) with substring (must be contiguous)",
                "LCS: forgetting that dp[i][j] uses 1-indexed characters — dp[i][j] corresponds to s1[i-1] and s2[j-1]",
                "LIS O(n²): not initialising dp[i]=1 (every element is an LIS of length 1 by itself)",
                "Edit distance: forgetting base cases dp[i][0]=i and dp[0][j]=j (cost of deleting/inserting everything)",
                "Space optimisation: swapping prev and curr incorrectly — forgetting to clear the new curr after swapping",
            ],
            [
                "DP Intro: 2D sequences DP is a direct extension of 1D tabulation — same fill-table logic",
                "Strings: LCS and edit distance operate on characters — s.charAt(i-1) is the standard accessor",
                "Binary Search: LIS O(n log n) uses binary search on the 'patience sorting' tails array",
                "Recursion: the recursive formulation is always easier to derive first, then convert to tabulation",
            ],
        ),
        [
            mcq("djds", 1, "A subsequence differs from a substring in that:", ["It must be contiguous", "It preserves relative order but may skip characters", "It must have the same length", "It only works on sorted arrays"], 1, "'ACE' is a subsequence of 'ABCDE' (skips B and D). 'ABC' is both a subsequence AND a substring.", ["fundamentals"]),
            mcq("djds", 2, "LCS dp[i][j] when s1[i-1] == s2[j-1]:", ["dp[i][j] = dp[i-1][j] + 1", "dp[i][j] = 1 + dp[i-1][j-1]", "dp[i][j] = dp[i][j-1]", "dp[i][j] = dp[i-1][j-1]"], 1, "Characters match — extend the LCS of both prefixes by 1. The diagonal cell represents the shared common prefix.", ["lcs"]),
            mcq("djds", 3, "LCS dp[i][j] when s1[i-1] != s2[j-1]:", ["dp[i][j] = 0", "dp[i][j] = dp[i-1][j-1]", "dp[i][j] = max(dp[i-1][j], dp[i][j-1])", "dp[i][j] = min(dp[i-1][j], dp[i][j-1])"], 2, "Characters don't match — the LCS is the best we can do by skipping one character from either string.", ["lcs"]),
            code_output("djds", 4, "LCS of 'AB' and 'AB':", "// dp table (2x2 + borders)\n// chars match at every position", ["0", "1", "2", "3"], 2, "Both strings are identical — LCS = full length = 2.", ["lcs", "tracing"]),
            mcq("djds", 5, "LCS of 'ABC' and 'DEF' is:", ["3", "1", "0", "6"], 2, "No characters in common — LCS = 0.", ["lcs"]),
            mcq("djds", 6, "LIS dp[i] (O(n²) approach) is initialised to:", ["0 for all i", "1 for all i — every element is an LIS of length 1 on its own", "nums[i] for all i", "-1 as sentinel"], 1, "The minimum valid LIS ending at any index is just the element itself — length 1.", ["lis"]),
            code_output("djds", 7, "LIS length of [3, 1, 2, 4]:", "// LIS could be [1,2,4] or [3,4]\n// longest increasing subsequence", ["2", "3", "4", "1"], 1, "[1,2,4] has length 3. [3,4] has length 2. LIS = 3.", ["lis", "tracing"]),
            mcq("djds", 8, "LIS O(n log n) (patience sorting) replaces the inner O(n) loop with:", ["Hashing", "Binary search on a 'tails' array to find insertion position", "Sorting the array first", "A priority queue"], 1, "tails[i] = smallest tail element of all increasing subsequences of length i+1. Binary search finds where to place each element.", ["lis"]),
            mcq("djds", 9, "Edit distance base case dp[i][0] = i means:", ["i characters match", "Cost of converting first i characters of w1 to empty string = delete all i", "No operations needed", "Insert i characters"], 1, "Transforming a prefix of length i to an empty string requires i deletions.", ["edit-distance"]),
            mcq("djds", 10, "Edit distance when w1[i-1] == w2[j-1]:", ["dp[i][j] = dp[i-1][j-1] + 1", "dp[i][j] = dp[i-1][j-1]  (no operation needed)", "dp[i][j] = 0", "dp[i][j] = min of three options"], 1, "Characters already match — no operation needed. Inherit from the diagonal.", ["edit-distance"]),
            mcq("djds", 11, "Edit distance operations mapped to table directions:", ["Left = insert, Up = delete, Diagonal = replace/match", "Left = delete, Up = insert, Diagonal = replace/match", "All three directions = replace", "Diagonal only for equal chars"], 0, "dp[i][j-1]+1 = insert into w1 (move right in w2). dp[i-1][j]+1 = delete from w1 (move down in w1). dp[i-1][j-1]+1 = replace.", ["edit-distance"]),
            code_output("djds", 12, "Edit distance between 'ab' and 'ab':", "// identical strings", ["0", "1", "2", "4"], 0, "Identical strings need 0 operations.", ["edit-distance"]),
            mcq("djds", 13, "Edit distance between 'a' and 'b':", ["0", "1", "2", "3"], 1, "One replace operation transforms 'a' to 'b'.", ["edit-distance"]),
            mcq("djds", 14, "Space complexity of 2D DP table for strings of length m and n:", ["O(m + n)", "O(m × n)", "O(max(m,n))", "O(1)"], 1, "Full 2D table has (m+1)×(n+1) cells.", ["complexity"]),
            mcq("djds", 15, "Space-optimised LCS/edit-distance uses two 1D arrays because:", ["The problem is 1D", "Each cell dp[i][j] only depends on dp[i-1][j-1], dp[i-1][j], dp[i][j-1] — only the previous row needed", "Java doesn't allow large 2D arrays", "The strings are short"], 1, "Previous row = prev[], current row = curr[]. After each outer loop iteration, swap them.", ["space-optimisation"]),
            mcq("djds", 16, "LCS length also equals:", ["Length of shorter string", "len(s1) + len(s2) - edit_distance_with_only_insert_delete", "LIS length of merged array", "Number of matching characters at same positions"], 1, "This relationship (LCS = (m+n-editDist)/2 when only inserts/deletes) connects the two problems.", ["insight"]),
            multi("djds", 17, "Which are 2D DP problems?", ["LCS", "Coin change", "Edit distance", "0/1 Knapsack"], [0, 2, 3], "Coin change is 1D DP (amount is the only state dimension). The others use two state dimensions.", ["patterns"]),
            mcq("djds", 18, "Shortest Common Supersequence (SCS) length of s1 and s2:", ["len(s1) + len(s2)", "len(s1) + len(s2) - LCS(s1,s2)", "LCS(s1,s2)", "edit_distance(s1,s2)"], 1, "SCS includes all characters of both strings. Characters in LCS appear once (not twice), so subtract LCS.", ["scs"]),
            mcq("djds", 19, "LIS on a strictly decreasing array [5,4,3,2,1]:", ["5", "0", "1", "3"], 2, "No two elements satisfy nums[i] < nums[j]. Every LIS has length 1.", ["lis"]),
            mcq("djds", 20, "To reconstruct the actual LCS string (not just length):", ["Re-run the algorithm with extra memory", "Trace back through the dp table from dp[m][n] to dp[0][0]: diagonal means match, left/up means skip", "Sort both strings and find common chars", "Use a HashMap"], 1, "Backtrack: if s1[i]==s2[j] → include char, go diagonal. Else go in direction of larger neighbour.", ["reconstruction"]),
        ],
        cards("djds", [
            ("Subsequence vs substring", "Subsequence: skip chars, keep order. Substring: contiguous block."),
            ("LCS recurrence", "Match: dp[i][j]=1+dp[i-1][j-1]. No match: dp[i][j]=max(dp[i-1][j], dp[i][j-1])."),
            ("LIS O(n²)", "dp[i]=1 initially. For j<i: if nums[j]<nums[i], dp[i]=max(dp[i], dp[j]+1)."),
            ("LIS O(n log n)", "Patience sorting: binary search on tails[] to place each element. Length = tails.size()."),
            ("Edit distance recurrence", "Match: dp[i][j]=dp[i-1][j-1]. Else: 1+min(replace diagonal, delete up, insert left)."),
            ("Edit distance base cases", "dp[i][0]=i (delete i chars). dp[0][j]=j (insert j chars)."),
            ("Space optimisation", "2D table → two 1D arrays (prev, curr). Swap after each row. O(n) space."),
            ("Backtracking 2D DP", "To reconstruct answer: trace from dp[m][n] backward following the recurrence decisions."),
        ], "dp-sequences"),
        project(
            "Write DPSequencesLab.java with:\n1. lcs(String s1, String s2) → int\n2. lcsString(String s1, String s2) → String  (reconstruct actual LCS)\n3. lis(int[] nums) → int  (O(n²) DP)\n4. lisNLogN(int[] nums) → int  (O(n log n) patience sort)\n5. editDistance(String w1, String w2) → int\nInclude main() tests: empty strings, identical strings, fully different strings, decreasing array for LIS.",
            ["lcs returns 0 for empty strings or completely different strings", "lcsString correctly backtracks through dp table to build the LCS", "lis initialises dp[i]=1 for all i before the nested loops", "lisNLogN uses Collections.binarySearch returning negative insertion point", "editDistance handles empty strings via base case initialisation"],
            ["lcsString: start at dp[m][n], if chars match add to front of result and go diagonal, else go in direction of larger cell.", "lisNLogN: Collections.binarySearch returns -(insertion_point)-1 for missing elements; pos = -(pos+1) converts it.", "editDistance: fill dp[i][0]=i and dp[0][j]=j before the main double loop."],
        ),
    ))

    # ── TRIES ─────────────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-tries", 75,
        "Tries in Java",
        "Trie node structure, insert/search/startsWith, autocomplete, word search, and when to prefer Trie over HashMap.",
        ["dsa-java-strings", "dsa-java-hashing"],
        guide(
            "Tries in Java",
            "A Trie (pronounced 'try', from re**trie**val) is a tree where **each edge represents one character** and **each node represents a prefix**. Walking from the root to any node spells out a prefix. Walking to a node marked as a word-end spells out a complete word. This structure makes prefix queries — 'does anything start with XY?' — O(length of prefix), regardless of how many words are stored.",
            [
                ("Node structure and shape", code("java", "// Each node has up to 26 children (one per lowercase letter)\n// and a boolean flag marking 'a word ends here'.\n//\n// Visualise inserting 'cat', 'car', 'dog':\n//\n//        root\n//       /    \\\n//      c      d\n//      |      |\n//      a      o\n//     / \\     |\n//    t*  r*   g*     (* = isEnd true)\n//\n// 'ca' is a prefix but NOT a word (isEnd=false at 'a' node)\n// 'cat' IS a word  (isEnd=true  at 't' node)\n\nclass TrieNode {\n    TrieNode[] children = new TrieNode[26];  // index = ch - 'a'\n    boolean isEnd = false;\n}")),
                ("Insert — walk the path, create nodes on demand", code("java", "class Trie {\n    private final TrieNode root = new TrieNode();\n\n    void insert(String word) {\n        TrieNode cur = root;\n        for (char ch : word.toCharArray()) {\n            int idx = ch - 'a';\n            if (cur.children[idx] == null)\n                cur.children[idx] = new TrieNode();  // create if missing\n            cur = cur.children[idx];\n        }\n        cur.isEnd = true;  // mark the final node as a complete word\n    }\n}\n// Time: O(L)  where L = word length\n// Space: O(L) new nodes in worst case")),
                ("Search vs startsWith — spot the one-character difference", code("java", "// SEARCH: does the FULL word exist?\nboolean search(String word) {\n    TrieNode cur = root;\n    for (char ch : word.toCharArray()) {\n        int idx = ch - 'a';\n        if (cur.children[idx] == null) return false;  // prefix broken\n        cur = cur.children[idx];\n    }\n    return cur.isEnd;  // ← must be a complete word\n}\n\n// STARTSSWITH: does any stored word begin with this prefix?\nboolean startsWith(String prefix) {\n    TrieNode cur = root;\n    for (char ch : prefix.toCharArray()) {\n        int idx = ch - 'a';\n        if (cur.children[idx] == null) return false;\n        cur = cur.children[idx];\n    }\n    return true;  // ← just reaching the node is enough, no isEnd check\n}")),
                ("Autocomplete — collect all words under a prefix node", code("java", "List<String> autocomplete(String prefix) {\n    TrieNode cur = root;\n    for (char ch : prefix.toCharArray()) {\n        int idx = ch - 'a';\n        if (cur.children[idx] == null) return Collections.emptyList();\n        cur = cur.children[idx];\n    }\n    // DFS from 'cur' collecting all words\n    List<String> results = new ArrayList<>();\n    dfs(cur, new StringBuilder(prefix), results);\n    return results;\n}\n\nvoid dfs(TrieNode node, StringBuilder sb, List<String> res) {\n    if (node.isEnd) res.add(sb.toString());\n    for (int i = 0; i < 26; i++) {\n        if (node.children[i] != null) {\n            sb.append((char)('a' + i));\n            dfs(node.children[i], sb, res);\n            sb.deleteCharAt(sb.length() - 1);  // backtrack\n        }\n    }\n}")),
                ("When Trie beats HashMap", "| Operation | HashMap | Trie |\n|---|---|---|\n| Exact word lookup | O(L) avg | O(L) |\n| Prefix existence | O(total words × L) | O(L) |\n| Autocomplete | O(total words × L) | O(L + output) |\n| Sorted word iteration | O(n log n) | O(n) in-order DFS |\n\n**Use Trie when:** you need prefix queries, autocomplete, spellcheck, or IP routing.\n**Use HashMap when:** only exact lookups and inserts — simpler and lower constant factors."),
            ],
            [
                "Forgetting cur.isEnd = true after the loop in insert — the word is stored as a path but not marked as a complete word",
                "Confusing search() and startsWith() — search requires isEnd=true; startsWith just needs the path to exist",
                "Using HashMap<Character, TrieNode> as children — correct but slower than TrieNode[26]; use array for lowercase-only alphabets",
                "Not backtracking the StringBuilder in DFS autocomplete — causes words to accumulate incorrectly",
                "Assuming delete is simple — deleting a word may require removing shared prefix nodes only if no other word uses them",
            ],
            [
                "Strings: every Trie operation processes one character at a time — O(L) where L is string length",
                "Hashing: Trie is an alternative to HashMap<String,...> when prefix queries matter",
                "Recursion/Backtracking: autocomplete DFS uses backtracking (StringBuilder undo)",
                "Graphs/Trees: a Trie is a rooted tree — DFS traversal collects all stored words",
            ],
        ),
        [
            mcq("djtr", 1, "Each node in a Trie represents:", ["A complete word", "A single character", "A prefix — the path from root to this node spells the prefix", "An alphabet index"], 2, "The node itself doesn't store a character — the EDGE leading to it does. The node represents the prefix formed by that path.", ["structure"]),
            mcq("djtr", 2, "Trie insert time complexity for a word of length L:", ["O(1)", "O(L)", "O(n) where n is total stored words", "O(L log n)"], 1, "Walk L edges, creating nodes where missing. Only L steps regardless of how many words exist.", ["complexity"]),
            mcq("djtr", 3, "startsWith() differs from search() by:", ["Being faster", "Not checking isEnd — just verifying the prefix path exists", "Checking parent nodes", "Using BFS instead of DFS"], 1, "A prefix doesn't need to be a complete word — reaching the last prefix character node is sufficient.", ["search"]),
            code_output("djtr", 4, "Insert 'cat'. search('ca') returns:", "// Trie has only 'cat' inserted\n// search checks isEnd at final node", ["true", "false", "null", "Error"], 1, "'ca' path exists but the node at 'a' has isEnd=false — 'ca' was never inserted as a complete word.", ["search", "tracing"]),
            code_output("djtr", 5, "Insert 'cat'. startsWith('ca') returns:", "// Trie has only 'cat'\n// startsWith just needs the path", ["true", "false", "null", "Error"], 0, "The path c→a exists in the Trie — startsWith returns true without checking isEnd.", ["search", "tracing"]),
            mcq("djtr", 6, "Space complexity of a Trie storing n words of average length L:", ["O(n)", "O(L)", "O(n × L) worst case", "O(26^L)"], 2, "Each character of each word potentially needs a node — O(n×L) nodes total in the worst case (no shared prefixes).", ["complexity"]),
            mcq("djtr", 7, "Space usage improves when stored words share:", ["The same length", "Common prefixes — shared prefix nodes are reused", "No characters in common", "The same suffix"], 1, "'cat', 'car', 'cab' share the path c→a — that prefix is stored ONCE, not three times.", ["space"]),
            mcq("djtr", 8, "Autocomplete starting from a prefix node uses:", ["BFS to find the shortest words", "DFS with backtracking to collect all words in the subtree", "Binary search on stored words", "In-order traversal"], 1, "DFS explores every branch; backtracking the StringBuilder undoes the character added for each branch.", ["autocomplete"]),
            mcq("djtr", 9, "In the TrieNode[26] children array, the index for character 'c' is:", ["2", "3", "'c' - 'a' = 2", "ASCII value of 'c'"], 2, "'a'→0, 'b'→1, 'c'→2. Formula: ch - 'a'.", ["structure"]),
            mcq("djtr", 10, "A Trie node with isEnd=true means:", ["It has no children", "A complete word ends at this node", "It is the root", "It has exactly one child"], 1, "isEnd=true marks that the prefix spelled by the root-to-this-node path is a stored word. Children may still exist (e.g. 'cat' and 'cats').", ["structure"]),
            multi("djtr", 11, "Which operations is a Trie faster at than a HashSet<String>?", ["Exact word lookup", "Prefix existence check", "Autocomplete (list all words with prefix)", "Counting total stored words"], [1, 2], "Exact lookup is O(L) for both. Prefix check and autocomplete are O(L + output) for Trie vs O(n×L) scan for HashSet.", ["comparison"]),
            mcq("djtr", 12, "Word Search II (find all dictionary words in a grid) uses Trie because:", ["It makes DFS faster by pruning: branch abandoned when no word starts with current path", "Grids require tree structures", "HashMap can't store characters", "It avoids visited arrays"], 1, "Trie allows pruning — if the current board path is not a prefix of any dictionary word, stop immediately.", ["applications"]),
            mcq("djtr", 13, "Inserting 'app' into a Trie that already has 'apple':", ["Replaces 'apple'", "Creates new nodes a,p,p", "Reuses the existing a→p→p path, just marks isEnd=true at the second 'p' node", "Throws duplicate error"], 2, "The shared prefix is already there — only isEnd changes at the word boundary node.", ["insert"]),
            mcq("djtr", 14, "Trie sorted word iteration (DFS in children order 0→25) produces:", ["Random order", "Reverse alphabetical", "Alphabetical order — 'a' children before 'b'", "Length-sorted order"], 2, "Iterating children[0] to children[25] is alphabetical order — Trie gives sorted enumeration for free.", ["traversal"]),
            mcq("djtr", 15, "Deleting a word from a Trie is complex because:", ["Trie nodes can't be removed", "You must not delete nodes that are shared by other words or are prefixes of other words", "The root must be rebuilt", "isEnd cannot be set to false"], 1, "Only remove the node if it has no children AND is not a prefix of another word — requires careful post-order DFS.", ["delete"]),
            mcq("djtr", 16, "HashMap<Character,TrieNode> vs TrieNode[26] for children:", ["HashMap is always better", "TrieNode[26] uses more memory but gives O(1) child access; HashMap saves space for sparse alphabets", "TrieNode[26] is O(log 26) access", "No practical difference"], 1, "26-element array is O(1) index. HashMap adds hashing overhead but uses less memory when alphabet is large or sparse.", ["implementation"]),
            code_output("djtr", 17, "Trie with 'bear','bell','bid','bull','buy'. startsWith('b') returns:", "// All words start with 'b'", ["true", "false", "5", "null"], 0, "Path b exists — startsWith('b') is true. All stored words share the 'b' prefix.", ["tracing"]),
            mcq("djtr", 18, "Longest common prefix of all words in a Trie is found by:", ["Comparing all word pairs", "Walking from root until a node branches (children > 1) or hits isEnd", "Sorting words and comparing first and last", "BFS level-order to the deepest level"], 1, "Follow the single-child chain from root — the moment a node has 2+ children or isEnd=true, the common prefix ends.", ["applications"]),
            mcq("djtr", 19, "A compressed Trie (Radix tree) reduces space by:", ["Removing duplicate words", "Merging chains of single-child nodes into one edge label", "Hashing each word", "Sorting children arrays"], 1, "Instead of one node per character, a chain is compressed into one edge with a string label. Fewer nodes, same lookup time.", ["variants"]),
            mcq("djtr", 20, "After inserting 'cats' into a Trie that has 'cat', search('cat') returns:", ["false — 'cats' overwrote it", "true — isEnd at 't' node is unchanged; 'cats' added a new 's' child", "Error — prefix conflict", "null"], 1, "Both words coexist: the 't' node stays isEnd=true, and a new 's' child is added below it.", ["insert", "insight"]),
        ],
        cards("djtr", [
            ("Trie node", "children: TrieNode[26]  (index = ch-'a').  isEnd: boolean."),
            ("Insert", "Walk path, create missing nodes. Set isEnd=true at last node. O(L)."),
            ("search vs startsWith", "search: reach end AND isEnd==true. startsWith: just reach end node."),
            ("Shared prefix", "'cat','car','cab' share c→a path — stored once. Space benefit of Trie."),
            ("Autocomplete", "Navigate to prefix node, then DFS with StringBuilder backtracking."),
            ("When to use Trie", "Prefix queries, autocomplete, spellcheck, word-search grid pruning."),
            ("Alphabetical order", "DFS children[0..25] in order → words come out alphabetically."),
            ("isEnd subtlety", "isEnd=true AND has children = valid word that is also a prefix (e.g. 'cat' in 'cats')."),
        ], "tries"),
        project(
            "Write TrieLab.java implementing a Trie class with:\n1. insert(String word)\n2. search(String word) → boolean\n3. startsWith(String prefix) → boolean\n4. autocomplete(String prefix) → List<String>  (sorted)\n5. longestCommonPrefix(String[] words) → String\nInclude main() tests: prefix of another word ('cat'/'cats'), empty prefix autocomplete (all words), single character words.",
            ["insert correctly sets isEnd=true only at the final character node", "search returns false for a prefix that was never inserted as a full word", "startsWith returns true for any prefix of any inserted word", "autocomplete uses DFS with StringBuilder backtracking — no duplicates", "longestCommonPrefix walks the single-child chain until branch or isEnd"],
            ["autocomplete: pass 'new StringBuilder(prefix)' to DFS so the prefix is already in the builder.", "longestCommonPrefix: insert all words, then walk from root following the only child at each step.", "search vs startsWith: the ONLY code difference is 'return cur.isEnd' vs 'return true' at the end."],
        ),
    ))

    # ── SLIDING WINDOW ────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-sliding-window", 76,
        "Sliding Window in Java",
        "Fixed-size and variable-size window patterns, max/min subarray, longest substring with constraints, and the shrink-when-invalid template.",
        ["dsa-java-arrays", "dsa-java-strings"],
        guide(
            "Sliding Window in Java",
            "The sliding window technique replaces a naive O(n²) nested loop with a single O(n) pass by maintaining a 'window' — a contiguous subarray or substring — and **sliding** it across the input. Instead of recomputing everything from scratch for each position, you add the new right element and remove the old left element, updating your answer incrementally.",
            [
                ("Fixed-size window — the moving frame", code("java", "// Problem: maximum sum of any k consecutive elements.\n//\n// Picture: a frame of width k sliding right one step at a time.\n// [1  3  -1 | -3  5  3  6  7]   window sum = 3\n//  [1  3  -1  -3 | 5  3  6  7]  slide: add 5, remove 1\n//\nint maxSumFixedWindow(int[] nums, int k) {\n    int windowSum = 0, maxSum = Integer.MIN_VALUE;\n    for (int r = 0; r < nums.length; r++) {\n        windowSum += nums[r];                    // expand right\n        if (r >= k) windowSum -= nums[r - k];   // shrink left (evict oldest)\n        if (r >= k - 1) maxSum = Math.max(maxSum, windowSum);\n    }\n    return maxSum;\n}\n// Time: O(n)   Space: O(1)")),
                ("Variable-size window — the elastic frame", code("java", "// Problem: longest substring without repeating characters.\n//\n// The window EXPANDS right whenever possible.\n// The window SHRINKS from the left whenever a constraint is violated.\n//\n// Picture hand holding a rubber band over the string:\n//   a b c a b c b b\n//   [a b c]            valid, expand\n//   [a b c a]          'a' duplicate! shrink from left until valid\n//     [b c a]          valid again, keep expanding\n//\nint lengthOfLongestSubstring(String s) {\n    Map<Character, Integer> freq = new HashMap<>();\n    int l = 0, maxLen = 0;\n    for (int r = 0; r < s.length(); r++) {\n        char c = s.charAt(r);\n        freq.merge(c, 1, Integer::sum);           // add right char\n        while (freq.get(c) > 1) {                 // constraint violated\n            char leftChar = s.charAt(l++);\n            freq.merge(leftChar, -1, Integer::sum); // shrink left\n        }\n        maxLen = Math.max(maxLen, r - l + 1);\n    }\n    return maxLen;\n}")),
                ("Template: shrink-when-invalid", code("java", "// Universal variable window skeleton:\n//\n// int l = 0;\n// State state = initial;\n// int answer = initial;\n//\n// for (int r = 0; r < n; r++) {\n//     update(state, nums[r]);         // 1. incorporate right element\n//     while (invalid(state)) {        // 2. shrink until valid\n//         remove(state, nums[l++]);\n//     }\n//     answer = best(answer, r-l+1);   // 3. window is valid — update answer\n// }\n//\n// The 'state' might be: a frequency map, a running sum, a count of distinct chars, etc.\n// The key insight: because r only moves right and l only moves right, each element\n// enters and leaves the window at most once → O(n) total.")),
                ("Minimum window substring — classic hard variant", code("java", "// Find shortest substring of s containing all chars of t.\n// State: how many chars of t are 'satisfied' (count >= needed).\nString minWindow(String s, String t) {\n    int[] need = new int[128], have = new int[128];\n    for (char c : t.toCharArray()) need[c]++;\n    int satisfied = 0, required = 0;\n    for (int x : need) if (x > 0) required++;\n    int l = 0, minLen = Integer.MAX_VALUE, start = 0;\n    for (int r = 0; r < s.length(); r++) {\n        char rc = s.charAt(r);\n        have[rc]++;\n        if (need[rc] > 0 && have[rc] == need[rc]) satisfied++; // newly met\n        while (satisfied == required) {           // all chars covered — try shrink\n            if (r - l + 1 < minLen) { minLen = r - l + 1; start = l; }\n            char lc = s.charAt(l++);\n            have[lc]--;\n            if (need[lc] > 0 && have[lc] < need[lc]) satisfied--;\n        }\n    }\n    return minLen == Integer.MAX_VALUE ? \"\" : s.substring(start, start + minLen);\n}")),
                ("Key decisions before coding", "When you see a sliding-window problem, answer these three questions:\n1. **What is my window state?**  (sum, frequency map, distinct-count, …)\n2. **When is the window valid/invalid?**  (sum < target, duplicate present, more than k distinct chars, …)\n3. **Am I maximising or minimising the window size?**\n   - Maximise → while(invalid) shrink, then update answer\n   - Minimise → while(valid) record answer then shrink"),
            ],
            [
                "Fixed window: using if (r >= k-1) windowSum -= nums[r-k+1] with wrong offset — always verify the eviction index",
                "Variable window: updating the answer INSIDE the while-shrink loop instead of after it",
                "Not using a frequency map when the constraint involves character counts — a simple int[] won't track multiplicity correctly",
                "Using two nested for-loops instead of the l/r two-pointer approach — same idea but O(n²)",
                "Minimise-window: forgetting to record the answer BEFORE shrinking (the moment the window is valid)",
            ],
            [
                "Arrays/Strings: the input is almost always a contiguous array or string",
                "Two Pointers: sliding window IS a two-pointer technique — l and r both move rightward",
                "Hashing: frequency maps inside the window state are HashMap or int[] depending on character set",
                "Deque: sliding-window maximum uses a monotonic deque for O(n) max within each window position",
            ],
        ),
        [
            mcq("djsw", 1, "Sliding window improves nested-loop O(n²) to O(n) because:", ["It uses binary search", "Each element enters and leaves the window at most once — l and r only move right", "It sorts the array first", "It uses extra O(n) space always"], 1, "l only increments, r only increments — total moves across both pointers ≤ 2n = O(n).", ["complexity"]),
            mcq("djsw", 2, "Fixed-size window: to evict the oldest element when window size exceeds k, remove:", ["nums[r]", "nums[l]", "nums[r - k]  (element that is now k positions behind r)", "The smallest element"], 2, "When r=k, the element that fell out is nums[r-k] = nums[0]. Pattern: windowSum -= nums[r-k].", ["fixed-window"]),
            code_output("djsw", 3, "Max sum of window k=3 on [2,1,5,1,3,2]:", "// windows: [2,1,5]=8  [1,5,1]=7  [5,1,3]=9  [1,3,2]=6", ["8", "7", "9", "6"], 2, "Window [5,1,3] gives sum 9 — the maximum.", ["fixed-window", "tracing"]),
            mcq("djsw", 4, "Variable window: the window shrinks when:", ["r reaches the end", "The window state violates the problem constraint", "The window is larger than k", "Always after every expansion"], 1, "Shrink left until the window becomes valid again — then expand right and repeat.", ["variable-window"]),
            mcq("djsw", 5, "Longest substring without repeating characters — window state is:", ["Running sum", "Frequency map of characters in the window", "Max element seen", "Count of vowels"], 1, "A character is 'repeating' when its frequency in the window exceeds 1.", ["variable-window"]),
            code_output("djsw", 6, "Longest substring without repeats in 'abcabcbb':", "// windows: abc(3), bca(3), cab(3), abc(3), bcb(3)→shrink, cb(2), b(1)\n// max length:", ["2", "3", "4", "5"], 1, "The longest window without a repeat is 'abc' = length 3.", ["variable-window", "tracing"]),
            mcq("djsw", 7, "Window size formula using left and right pointers:", ["r - l", "r - l + 1", "r + l", "r * l"], 1, "A window from index l to r (inclusive) contains r - l + 1 elements.", ["mechanics"]),
            mcq("djsw", 8, "When minimising window size (e.g. minimum window substring), update the answer:", ["Before expanding right", "Inside the shrink loop — each valid window that fits is a candidate minimum", "After the outer loop", "Only when l == 0"], 1, "Every time the window is valid (all required chars present), check if it is smaller than the current best, then try shrinking more.", ["minimise"]),
            mcq("djsw", 9, "When maximising window size, update the answer:", ["Inside the shrink loop", "After the shrink loop — when the window is as large as it can be while still valid", "Before expanding", "Only at r = n-1"], 1, "After shrinking to restore validity, the window is the largest valid window ending at r.", ["maximise"]),
            mcq("djsw", 10, "Maximum number of vowels in a substring of length k uses:", ["Variable window", "Fixed window of exactly size k", "Binary search on answer", "Two separate arrays"], 1, "Window size is fixed at k — slide it and count vowels entering/leaving.", ["fixed-window"]),
            mcq("djsw", 11, "Minimum size subarray sum >= target variable window expands right until sum >= target, then:", ["Stops", "Records length and shrinks left to find a smaller valid window", "Resets l to 0", "Doubles k"], 1, "While sum >= target: record current window length as candidate minimum, then remove left element.", ["minimise"]),
            code_output("djsw", 12, "Min subarray length with sum >= 7 on [2,3,1,2,4,3]:", "// [4,3]=7 len=2  ← minimum\n// [2,3,1,2]=8 len=4\n// [3,1,2,4]=10 etc.", ["1", "2", "3", "4"], 1, "Subarray [4,3] sums to 7 with length 2 — the minimum.", ["minimise", "tracing"]),
            mcq("djsw", 13, "Sliding window maximum (max of every k-width window) optimal solution:", ["Sort each window O(nk)", "Fixed window O(n) with prefix max", "Monotonic deque O(n) — front always holds max of current window", "Binary search on sorted windows"], 2, "Deque stores candidate indices in decreasing value order; front = current window max. Each element pushed/popped once = O(n).", ["deque"]),
            mcq("djsw", 14, "Fruit Into Baskets (at most 2 distinct fruit types, max fruits collected) maps to:", ["Fixed window of size 2", "Variable window: longest subarray with at most 2 distinct values", "Counting sort", "Greedy pick-largest"], 1, "State = frequency map of fruits in window. Shrink when distinct count > 2.", ["variable-window", "applications"]),
            mcq("djsw", 15, "Minimum window substring 'satisfied' counter tracks:", ["How many characters of t are in the window", "How many distinct characters of t have their required frequency met", "Window length", "Number of chars in s scanned"], 1, "satisfied increments only when have[c] exactly reaches need[c] — not on every occurrence.", ["min-window"]),
            multi("djsw", 16, "Which problems are solved with a variable sliding window?", ["Longest substring with at most k distinct chars", "Maximum sum subarray of fixed size k", "Minimum window containing all target chars", "Longest subarray with sum at most S"], [0, 2, 3], "Fixed-size max sum uses fixed window. The other three have a variable constraint requiring dynamic resizing.", ["applications"]),
            mcq("djsw", 17, "Character frequency tracking inside a window uses int[128] (ASCII) instead of HashMap when:", ["Window is small", "Character set is limited to ASCII — array gives O(1) access with less overhead", "HashMap is deprecated", "The string is sorted"], 1, "For known bounded character sets (ASCII, lowercase letters), int[] is faster and simpler than HashMap.", ["implementation"]),
            mcq("djsw", 18, "After adding nums[r] to the window and shrinking (if needed), window [l, r] is guaranteed:", ["Maximum possible size", "The largest valid window ending at index r", "Sorted order", "Size exactly k"], 1, "l was moved just enough to restore validity — making [l,r] the biggest valid window with right boundary r.", ["invariant"]),
            code_output("djsw", 19, "Longest subarray with sum <= 5 on [3,1,2,4,1]:", "// l=0,r=0: sum=3 ok, len=1\n// r=1: sum=4 ok, len=2\n// r=2: sum=6 > 5 → shrink: remove 3 → sum=3, l=1, len=2\n// r=3: sum=7 > 5 → shrink: remove 1 → sum=6 > 5 → remove 2 → sum=4, l=3, len=1\n// r=4: sum=5 ok, len=2\n// max len:", ["1", "2", "3", "4"], 1, "Maximum valid window length seen is 2 (e.g. [3,1] or [1,4] after shrink or [4,1]).", ["variable-window", "tracing"]),
            mcq("djsw", 20, "Sliding window is NOT the right technique when:", ["Array elements are positive", "You need a non-contiguous subsequence or the subproblem structure is not monotonic", "The array is sorted", "Window state is a running sum"], 1, "Sliding window requires: contiguous window AND monotonic validity (adding elements only makes constraint harder/easier, not arbitrary). Non-contiguous problems use DP.", ["when-not-to-use"]),
        ],
        cards("djsw", [
            ("Fixed window template", "Add nums[r]. If r >= k: remove nums[r-k]. If r >= k-1: update answer."),
            ("Variable window template", "Expand r. While invalid: shrink l. Update answer after while loop."),
            ("Window size", "r - l + 1 elements when window spans indices [l, r] inclusive."),
            ("O(n) guarantee", "l and r each move right at most n times — total work is O(n)."),
            ("Maximise vs minimise", "Maximise: update after shrink. Minimise: update INSIDE while(valid) then shrink."),
            ("State choices", "Running sum (int), frequency map (int[128] or HashMap), distinct count (int)."),
            ("Sliding window max", "Monotonic decreasing deque of indices. Front = current window maximum."),
            ("Monotonicity requirement", "Sliding window works when adding elements monotonically tightens/loosens constraint."),
        ], "sliding-window"),
        project(
            "Write SlidingWindowLab.java with:\n1. maxSumFixed(int[] nums, int k) → int\n2. lengthOfLongestSubstringKDistinct(String s, int k) → int\n3. minSizeSubarraySum(int[] nums, int target) → int  (return 0 if none)\n4. maxSlidingWindow(int[] nums, int k) → int[]  (monotonic deque)\n5. minWindowSubstring(String s, String t) → String\nInclude main() tests: k=1, k=n, target larger than total sum, t longer than s.",
            ["maxSumFixed handles k > nums.length gracefully", "lengthOfLongestSubstringKDistinct shrinks until distinct count <= k", "minSizeSubarraySum returns 0 when no subarray meets target", "maxSlidingWindow evicts front when index out of window, back when value smaller than new element", "minWindowSubstring uses satisfied counter — only increments when frequency exactly meets requirement"],
            ["maxSlidingWindow: evict dq.peekFirst() when dq.peekFirst() < r - k + 1.", "minWindowSubstring: have[c]-- then check if have[c] < need[c] AFTER the decrement before deciding to decrement satisfied.", "lengthOfLongestSubstringKDistinct: remove from map when count reaches 0 to keep map.size() == distinct count."],
        ),
    ))

    # ── TWO POINTERS ──────────────────────────────────────────────────────────
    TOPICS.append(topic(
        "dsa-java-two-pointers", 77,
        "Two Pointers in Java",
        "Converging pointers (two-sum, palindrome), same-direction pointers (remove duplicates, fast/slow), Dutch National Flag 3-way partition, and interval merging.",
        ["dsa-java-arrays", "dsa-java-sorting"],
        guide(
            "Two Pointers in Java",
            "The two-pointer technique places two index variables into an array or string and moves them strategically — usually toward each other or in the same direction — to avoid a nested O(n²) loop. The core insight: **sorted order or a known invariant lets you decide which pointer to move without trying all combinations**.",
            [
                ("Pattern 1 — Converging pointers on a sorted array", code("java", "// Picture two people walking toward each other from opposite ends.\n// If their sum is too small → left person steps right (increases sum).\n// If their sum is too large → right person steps left (decreases sum).\n// They meet exactly when no valid pair remains.\n//\n// Two Sum (sorted array):\nint[] twoSum(int[] nums, int target) {\n    int l = 0, r = nums.length - 1;\n    while (l < r) {\n        int sum = nums[l] + nums[r];\n        if      (sum == target) return new int[]{l, r};\n        else if (sum < target)  l++;  // need bigger sum → advance left\n        else                    r--;  // need smaller sum → retreat right\n    }\n    return new int[]{-1, -1};  // no pair found\n}\n// Time: O(n)   Space: O(1)  (vs O(n²) brute force)")),
                ("Pattern 2 — Same-direction pointers (fast/slow)", code("java", "// One pointer (fast) races ahead finding 'useful' elements;\n// the other (slow) marks where the next useful element should be placed.\n//\n// Remove duplicates from sorted array in-place:\n// slow = last position of deduplicated region\n// fast = scanner looking for new unique values\n//\n// [1, 1, 2, 3, 3, 4]\n//  s                        slow=0\n//     f                     nums[f]=1 == nums[s] → skip\n//        f                  nums[f]=2 != nums[s] → place at ++slow\n// [1, 2, 2, 3, 3, 4] (slow=1, continue...)\nint removeDuplicates(int[] nums) {\n    int slow = 0;\n    for (int fast = 1; fast < nums.length; fast++)\n        if (nums[fast] != nums[slow]) nums[++slow] = nums[fast];\n    return slow + 1;  // new length\n}")),
                ("Pattern 3 — Dutch National Flag (3-way partition)", code("java", "// Sort an array of 0s, 1s, and 2s in O(n) time O(1) space.\n//\n// Three regions maintained at every step:\n//  [0...low-1]   all 0s  (confirmed)\n//  [low...mid-1] all 1s  (confirmed)\n//  [mid...high]  unknown (unsorted territory)\n//  [high+1...n-1] all 2s  (confirmed)\n//\n// Visual: three hands squeezing inward until mid > high.\n//\nvoid sortColors(int[] nums) {\n    int low = 0, mid = 0, high = nums.length - 1;\n    while (mid <= high) {\n        if      (nums[mid] == 0) swap(nums, low++, mid++);  // 0: expand left zone\n        else if (nums[mid] == 1) mid++;                     // 1: already in place\n        else                     swap(nums, mid, high--);   // 2: send to right zone\n        // Note: mid does NOT increment after swapping with high —\n        // the swapped element hasn't been examined yet!\n    }\n}")),
                ("Pattern 4 — Three Sum (sorted + converging inner pair)", code("java", "// Fix one element, then use converging two-pointer on the rest.\n// Sort first so duplicates are adjacent — easy to skip.\n//\nList<List<Integer>> threeSum(int[] nums) {\n    Arrays.sort(nums);\n    List<List<Integer>> res = new ArrayList<>();\n    for (int i = 0; i < nums.length - 2; i++) {\n        if (i > 0 && nums[i] == nums[i-1]) continue;  // skip duplicate anchor\n        int l = i + 1, r = nums.length - 1;\n        while (l < r) {\n            int sum = nums[i] + nums[l] + nums[r];\n            if      (sum == 0) {\n                res.add(Arrays.asList(nums[i], nums[l++], nums[r--]));\n                while (l < r && nums[l] == nums[l-1]) l++;  // skip duplicates\n                while (l < r && nums[r] == nums[r+1]) r--;  // skip duplicates\n            }\n            else if (sum < 0) l++;\n            else              r--;\n        }\n    }\n    return res;\n}")),
                ("Pattern 5 — Merging sorted intervals", code("java", "// Sort by start. Walk with one pointer, merging overlapping intervals.\n//\n// [1,3],[2,6],[8,10],[15,18]\n//  └──merge──┘ → [1,6]\n//              [8,10] no overlap → keep\n//                     [15,18] no overlap → keep\n//\nint[][] merge(int[][] intervals) {\n    Arrays.sort(intervals, Comparator.comparingInt(a -> a[0]));\n    List<int[]> merged = new ArrayList<>();\n    for (int[] cur : intervals) {\n        if (merged.isEmpty() || merged.get(merged.size()-1)[1] < cur[0])\n            merged.add(cur);   // no overlap — add as new interval\n        else\n            merged.get(merged.size()-1)[1] = Math.max(merged.get(merged.size()-1)[1], cur[1]);\n    }\n    return merged.toArray(new int[0][]);\n}")),
            ],
            [
                "Using converging two-pointer on an UNSORTED array — the sorted invariant is what makes the decision (advance l or retreat r) correct",
                "Dutch National Flag: incrementing mid after swapping with high — the incoming element from high is unseen and could be anything",
                "Three Sum: forgetting to skip duplicate anchor values at index i — produces duplicate triplets",
                "Two Sum: the classic two-pointer only works for finding ONE pair; for ALL pairs use a loop with duplicate-skipping",
                "Palindrome check: off-by-one — loop must be l < r not l <= r (single middle character is always a palindrome)",
            ],
            [
                "Sorting: converging two-pointer and interval merging require sorted input",
                "Arrays: all patterns operate in-place with O(1) extra space",
                "Sliding Window: sliding window IS two-pointer (same-direction) but with window state tracking",
                "Linked Lists: fast/slow pointer on a linked list detects cycles and finds the middle",
            ],
        ),
        [
            mcq("djtp", 1, "Converging two-pointer on a sorted array works because:", ["The array is small", "Sorted order lets you decide which pointer to move based on whether the current sum is too large or too small", "It uses binary search internally", "Only works for pairs summing to 0"], 1, "If sum < target, moving l right increases the sum. If sum > target, moving r left decreases it. Without sorted order this logic breaks.", ["converging"]),
            mcq("djtp", 2, "Two Sum (sorted array) two-pointer time complexity:", ["O(n²)", "O(n log n)", "O(n)", "O(1)"], 2, "l and r each move at most n times total. Two pointers, single pass.", ["complexity"]),
            code_output("djtp", 3, "Two Sum on sorted [1,2,3,4,6], target=6. Pair:", "// l=0(1) r=4(6): sum=7 > 6 → r--\n// l=0(1) r=3(4): sum=5 < 6 → l++\n// l=1(2) r=3(4): sum=6 == 6 → found", ["[0,4]", "[1,3]", "[2,3]", "[0,3]"], 1, "Indices 1 and 3 hold values 2 and 4 which sum to 6.", ["converging", "tracing"]),
            mcq("djtp", 4, "Same-direction slow/fast pointers: slow marks:", ["The last examined element", "The boundary of the 'processed and valid' region — where the next accepted element should go", "The middle of the array", "The pivot"], 1, "Slow is the 'write cursor'. Fast is the 'read cursor' scanning for elements worth keeping.", ["same-direction"]),
            code_output("djtp", 5, "Remove duplicates from [1,1,2,3,3]. New length:", "// slow=0\n// fast scans: 1(dup skip), 2(write→slow=1), 3(write→slow=2), 3(dup skip)\n// slow+1 = 3", ["2", "3", "4", "5"], 1, "Unique elements: 1,2,3 — length 3.", ["same-direction", "tracing"]),
            mcq("djtp", 6, "Dutch National Flag algorithm maintains how many 'zones'?", ["2", "3", "4", "1"], 1, "Zone 1: confirmed 0s [0..low-1]. Zone 2: confirmed 1s [low..mid-1]. Zone 3: unknown [mid..high]. Zone 4: confirmed 2s [high+1..n-1].", ["dutch-flag"]),
            mcq("djtp", 7, "Dutch Flag: after swap(nums, mid, high--), mid is NOT incremented because:", ["It is an off-by-one error", "The element swapped from high is unseen — it could be 0, 1, or 2 and must be examined next", "high-- already advances the pointer", "It causes an infinite loop otherwise"], 1, "You just received an unknown element at mid from the right zone — you haven't processed it yet.", ["dutch-flag"]),
            code_output("djtp", 8, "Dutch Flag on [2,0,1]. Final array:", "// mid=0,low=0,high=2\n// nums[0]=2 → swap(0,high=2) → [1,0,2] high=1\n// nums[0]=1 → mid++ → [1,0,2] mid=1\n// nums[1]=0 → swap(low=0,mid=1) → [0,1,2] low=1,mid=2\n// mid>high → done", ["[0,1,2]", "[2,1,0]", "[1,0,2]", "[0,2,1]"], 0, "Result is sorted [0,1,2].", ["dutch-flag", "tracing"]),
            mcq("djtp", 9, "Palindrome check using two pointers:", ["O(n) time O(n) space — copy reverse", "O(n) time O(1) space — converging l and r", "O(n²) time", "O(log n) time"], 1, "l starts at 0, r at n-1. Compare and move inward — O(n) single pass, no extra array.", ["palindrome"]),
            mcq("djtp", 10, "Three Sum requires sorting first because:", ["The result must be sorted", "Sorting allows duplicate skipping and enables the inner converging two-pointer", "Three-way comparison needs order", "It speeds up the O(n) part"], 1, "Sorted array lets you skip duplicate anchors (i) and duplicate pairs (l,r) cleanly to avoid repeat triplets.", ["three-sum"]),
            mcq("djtp", 11, "Three Sum time complexity after sorting:", ["O(n)", "O(n log n)", "O(n²)", "O(n³)"], 2, "Outer loop O(n) × inner two-pointer O(n) = O(n²). Sorting is O(n log n) — dominated by O(n²).", ["complexity"]),
            mcq("djtp", 12, "Interval merging: you sort by interval start because:", ["End time is irrelevant", "Intervals that could overlap are adjacent after sorting — single forward scan suffices", "It produces the output in order", "Binary search requires it"], 1, "Sorting ensures the next interval either overlaps the current one (starts ≤ current end) or is definitively separate.", ["intervals"]),
            mcq("djtp", 13, "Two intervals [a,b] and [c,d] overlap when:", ["a < c", "c <= b  (new interval starts before or when current interval ends)", "a == c", "b < c"], 1, "If c > b the intervals are disjoint. If c <= b they overlap and should merge to [a, max(b,d)].", ["intervals"]),
            code_output("djtp", 14, "Merge [[1,3],[2,6],[8,10],[15,18]]. Count of merged intervals:", "// [1,3]+[2,6]→[1,6]  [8,10]  [15,18]\n// 3 merged intervals", ["2", "3", "4", "1"], 1, "[1,6], [8,10], [15,18] — three non-overlapping merged intervals.", ["intervals", "tracing"]),
            mcq("djtp", 15, "Container With Most Water uses converging pointers because:", ["It needs the maximum", "Moving the shorter side inward is the only direction that can increase area — moving the taller side can only decrease it", "The array is sorted", "It is always O(log n)"], 1, "Area = min(height[l], height[r]) × (r-l). The width shrinks by 1 each step, so you must try to increase the height by moving the shorter side.", ["applications"]),
            code_output("djtp", 16, "Container With Most Water on heights [1,8,6,2,5,4,8,3,7]. Max area:", "// Best: l=1(h=8), r=8(h=7) → min(8,7)×7=49\n// vs l=0,r=8: min(1,7)×8=8", ["49", "56", "48", "36"], 0, "Indices 1 and 8 with heights 8 and 7: area = 7 × 7 = 49.", ["applications", "tracing"]),
            mcq("djtp", 17, "Move Zeroes in-place (keep relative order of non-zeroes) uses:", ["Sorting", "Same-direction two-pointer: slow writes non-zeroes, fast scans", "Converging pointers", "Stack"], 1, "slow pointer marks next write position; fast pointer finds non-zero elements to move there.", ["same-direction"]),
            multi("djtp", 18, "Which problems require the array to be SORTED before applying two pointers?", ["Two Sum (pair target)", "Three Sum (all triplets)", "Remove duplicates (dedup sorted array)", "Dutch National Flag (sort 0/1/2)"], [0, 1], "Remove duplicates already receives a sorted array (problem guarantee). Dutch Flag sorts via the algorithm itself — no pre-sort needed. Two Sum and Three Sum need intentional sorting.", ["prerequisites"]),
            mcq("djtp", 19, "Trapping Rain Water optimal solution:", ["O(n) two-pointer — l and r converge, tracking max heights from each side", "O(n) prefix/suffix max arrays", "O(n log n) sort then scan", "Both A and B are O(n) — two-pointer uses O(1) space vs O(n)"], 3, "Prefix/suffix approach O(n) space. Two-pointer achieves same in O(1) space by processing the shorter column first.", ["applications"]),
            mcq("djtp", 20, "Two pointers fail (give wrong answer) on an unsorted array for two-sum because:", ["They are too slow", "Without sorted order, you cannot determine which pointer to move — a small left value paired with a small right value could match, but moving either pointer might skip the answer", "Negative numbers break it", "Arrays must always be sorted in Java"], 1, "The 'move l right to increase sum, move r left to decrease sum' logic only holds when the array is monotonically non-decreasing.", ["insight"]),
        ],
        cards("djtp", [
            ("Converging pointers", "Start l=0, r=n-1 on SORTED array. Move l right if sum too small, r left if too large. O(n)."),
            ("Same-direction pointers", "slow = write cursor (valid region boundary). fast = read cursor (scanner). O(n)."),
            ("Dutch National Flag", "3 zones: 0s|1s|unknown|2s. mid scans unknown. Don't increment mid after swap with high."),
            ("Three Sum", "Sort first. Fix i, then converge l and r. Skip duplicates at i, l, and r."),
            ("Interval merging", "Sort by start. Merge if next.start <= current.end. Extend end to max of both ends."),
            ("Palindrome check", "l=0, r=n-1. Compare chars, move both inward. O(n) time O(1) space."),
            ("Container With Most Water", "Move the SHORTER side inward — only way to potentially increase area."),
            ("Key requirement", "Converging pattern REQUIRES sorted array. Same-direction works on unsorted too."),
        ], "two-pointers"),
        project(
            "Write TwoPointersLab.java with:\n1. twoSum(int[] sorted, int target) → int[]  (converging, sorted input)\n2. removeDuplicates(int[] nums) → int  (in-place, sorted)\n3. sortColors(int[] nums)  (Dutch National Flag, in-place)\n4. threeSum(int[] nums) → List<List<Integer>>  (all unique triplets)\n5. merge(int[][] intervals) → int[][]  (sorted merged intervals)\n6. maxArea(int[] height) → int  (container with most water)\nInclude main() tests: all zeros, all same, no valid pair, single interval, already merged.",
            ["twoSum returns {-1,-1} when no pair found, not an exception", "removeDuplicates handles single-element array returning 1", "sortColors: mid NOT incremented after swap with high", "threeSum skips duplicate i values AND duplicate l/r values after finding a triplet", "merge handles single interval and already-sorted non-overlapping intervals", "maxArea handles arrays of length 2"],
            ["sortColors: while(mid <= high) is the loop condition — not mid < high.", "threeSum: after adding a triplet, advance both l++ and r-- then skip while duplicates.", "merge: the overlap condition is intervals[i][0] <= last[1] — not strictly less than."],
        ),
    ))


add_more_topics()

# A singular linked-list file was requested in one place, but this project already
# uses dsa-java-linked-lists consistently. Keep the canonical plural id to avoid
# duplicate topics and broken prereqs/progress records.

ORDER_AND_PREREQS = {t["id"]: (t["order"], t["prereqs"]) for t in TOPICS}


def normalize_existing_metadata(path: Path, generated: dict[str, Any]) -> bool:
    data = json.loads(path.read_text())
    changed = False
    for key in ("unit", "order", "summary", "prereqs"):
        if data.get(key) != generated[key]:
            data[key] = generated[key]
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n")
    return changed


def validate_topic(data: dict[str, Any]) -> None:
    required = {"id", "unit", "order", "title", "summary", "prereqs", "guide", "questions", "flashcards", "project"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{data.get('id', '<unknown>')} missing keys: {sorted(missing)}")
    if data["unit"] != 9:
        raise ValueError(f"{data['id']} must be unit 9")
    for q in data["questions"]:
        if "id" not in q or "type" not in q or "explanation" not in q or "tags" not in q:
            raise ValueError(f"Invalid question in {data['id']}: {q}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true", help="Regenerate all DSA topic files, including existing ones")
    args = parser.parse_args()

    TOPICS_DIR.mkdir(parents=True, exist_ok=True)
    created = updated = skipped = 0

    for data in TOPICS:
        validate_topic(data)
        path = TOPICS_DIR / f"{data['id']}.json"

        # Safety check: preserve hand-crafted topics with 20+ questions
        if path.exists():
            existing = json.loads(path.read_text())
            if len(existing.get('questions', [])) >= 20:
                print(f"✓ Skipping {path.name} (20+ questions, hand-crafted)")
                skipped += 1
                continue

        if path.exists() and not args.overwrite:
            if normalize_existing_metadata(path, data):
                updated += 1
                print(f"Updated metadata {path.name}")
            else:
                skipped += 1
                print(f"Skipped {path.name} (exists)")
            continue
        path.write_text(json.dumps(data, indent=2) + "\n")
        if path.exists() and args.overwrite:
            updated += 1
            print(f"Wrote {path.name}")
        else:
            created += 1
            print(f"Created {path.name}")

    print(f"Done: {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()

