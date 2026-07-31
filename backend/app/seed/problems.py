# ruff: noqa: E501
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem, TestCase

LANGUAGE_STARTERS = {
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  // Read the input in the format shown in the sample cases.\n  return 0;\n}\n",
    "java": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    // Read the input in the format shown in the sample cases.\n  }\n}\n",
}


CPP_STARTERS = {
    "array_target": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> nums(n);\n  for (int i = 0; i < n; i++) cin >> nums[i];\n  int target;\n  cin >> target;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "array_only": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> nums(n);\n  for (int i = 0; i < n; i++) cin >> nums[i];\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "prices": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> prices(n);\n  for (int i = 0; i < n; i++) cin >> prices[i];\n  // TODO: compute and print max profit.\n  return 0;\n}\n",
    "string": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  string s;\n  cin >> s;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "two_strings": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  string s, t;\n  cin >> s >> t;\n  // TODO: print true or false.\n  return 0;\n}\n",
    "intervals": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<pair<int, int>> intervals(n);\n  for (int i = 0; i < n; i++) cin >> intervals[i].first >> intervals[i].second;\n  // TODO: merge and print intervals.\n  return 0;\n}\n",
    "grid_chars": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int rows, cols;\n  cin >> rows >> cols;\n  vector<string> grid(rows);\n  for (int r = 0; r < rows; r++) cin >> grid[r];\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "single_int": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "words": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<string> words(n);\n  for (int i = 0; i < n; i++) cin >> words[i];\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "values": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<string> values(n);\n  for (int i = 0; i < n; i++) cin >> values[i];\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "cycle": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n, pos;\n  cin >> n >> pos;\n  // TODO: build or reason about the list and print true or false.\n  return 0;\n}\n",
    "ops": '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<vector<string>> ops(n);\n  for (int i = 0; i < n; i++) {\n    string op;\n    cin >> op;\n    ops[i].push_back(op);\n    if (op == "push") {\n      string value;\n      cin >> value;\n      ops[i].push_back(value);\n    }\n  }\n  // TODO: process stack operations and print query results.\n  return 0;\n}\n',
    "array_k": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> nums(n);\n  for (int i = 0; i < n; i++) cin >> nums[i];\n  int k;\n  cin >> k;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "coins": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> coins(n);\n  for (int i = 0; i < n; i++) cin >> coins[i];\n  int amount;\n  cin >> amount;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "word_break": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  string s;\n  cin >> s;\n  int m;\n  cin >> m;\n  vector<string> words(m);\n  for (int i = 0; i < m; i++) cin >> words[i];\n  // TODO: print true or false.\n  return 0;\n}\n",
    "edges": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n, m;\n  cin >> n >> m;\n  vector<pair<int, int>> edges(m);\n  for (int i = 0; i < m; i++) cin >> edges[i].first >> edges[i].second;\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "grid_ints": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int rows, cols;\n  cin >> rows >> cols;\n  vector<vector<int>> grid(rows, vector<int>(cols));\n  for (int r = 0; r < rows; r++) {\n    for (int c = 0; c < cols; c++) cin >> grid[r][c];\n  }\n  // TODO: compute and print the answer.\n  return 0;\n}\n",
    "adj": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  string line;\n  getline(cin, line);\n  vector<vector<int>> adj(n);\n  for (int i = 0; i < n; i++) {\n    getline(cin, line);\n    stringstream ss(line);\n    int neighbor;\n    while (ss >> neighbor) adj[i].push_back(neighbor);\n  }\n  // TODO: clone/process graph and print adjacency list.\n  return 0;\n}\n",
    "two_arrays": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  int n;\n  cin >> n;\n  vector<int> a(n);\n  for (int i = 0; i < n; i++) cin >> a[i];\n  int m;\n  cin >> m;\n  vector<int> b(m);\n  for (int i = 0; i < m; i++) cin >> b[i];\n  // TODO: compute and print the median.\n  return 0;\n}\n",
}


JAVA_STARTERS = {
    "array_target": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] nums = new int[n];\n    for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n    int target = sc.nextInt();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "array_only": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] nums = new int[n];\n    for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "prices": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] prices = new int[n];\n    for (int i = 0; i < n; i++) prices[i] = sc.nextInt();\n    // TODO: compute and print max profit.\n  }\n}\n",
    "string": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    String s = sc.next();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "two_strings": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    String s = sc.next();\n    String t = sc.next();\n    // TODO: print true or false.\n  }\n}\n",
    "intervals": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[][] intervals = new int[n][2];\n    for (int i = 0; i < n; i++) {\n      intervals[i][0] = sc.nextInt();\n      intervals[i][1] = sc.nextInt();\n    }\n    // TODO: merge and print intervals.\n  }\n}\n",
    "grid_chars": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int rows = sc.nextInt();\n    int cols = sc.nextInt();\n    char[][] grid = new char[rows][cols];\n    for (int r = 0; r < rows; r++) grid[r] = sc.next().toCharArray();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "single_int": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "words": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    String[] words = new String[n];\n    for (int i = 0; i < n; i++) words[i] = sc.next();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "values": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    String[] values = new String[n];\n    for (int i = 0; i < n; i++) values[i] = sc.next();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "cycle": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int pos = sc.nextInt();\n    // TODO: build or reason about the list and print true or false.\n  }\n}\n",
    "ops": 'import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    List<String[]> ops = new ArrayList<>();\n    for (int i = 0; i < n; i++) {\n      String op = sc.next();\n      if (op.equals("push")) ops.add(new String[] {op, sc.next()});\n      else ops.add(new String[] {op});\n    }\n    // TODO: process stack operations and print query results.\n  }\n}\n',
    "array_k": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] nums = new int[n];\n    for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n    int k = sc.nextInt();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "coins": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] coins = new int[n];\n    for (int i = 0; i < n; i++) coins[i] = sc.nextInt();\n    int amount = sc.nextInt();\n    // TODO: compute and print the answer.\n  }\n}\n",
    "word_break": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    String s = sc.next();\n    int m = sc.nextInt();\n    String[] words = new String[m];\n    for (int i = 0; i < m; i++) words[i] = sc.next();\n    // TODO: print true or false.\n  }\n}\n",
    "edges": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int m = sc.nextInt();\n    int[][] edges = new int[m][2];\n    for (int i = 0; i < m; i++) {\n      edges[i][0] = sc.nextInt();\n      edges[i][1] = sc.nextInt();\n    }\n    // TODO: compute and print the answer.\n  }\n}\n",
    "grid_ints": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int rows = sc.nextInt();\n    int cols = sc.nextInt();\n    int[][] grid = new int[rows][cols];\n    for (int r = 0; r < rows; r++) {\n      for (int c = 0; c < cols; c++) grid[r][c] = sc.nextInt();\n    }\n    // TODO: compute and print the answer.\n  }\n}\n",
    "adj": 'import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = Integer.parseInt(sc.nextLine().trim());\n    List<List<Integer>> adj = new ArrayList<>();\n    for (int i = 0; i < n; i++) {\n      List<Integer> neighbors = new ArrayList<>();\n      if (sc.hasNextLine()) {\n        String line = sc.nextLine().trim();\n        if (!line.isEmpty()) {\n          for (String token : line.split("\\\\s+")) neighbors.add(Integer.parseInt(token));\n        }\n      }\n      adj.add(neighbors);\n    }\n    // TODO: clone/process graph and print adjacency list.\n  }\n}\n',
    "two_arrays": "import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    int n = sc.nextInt();\n    int[] a = new int[n];\n    for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n    int m = sc.nextInt();\n    int[] b = new int[m];\n    for (int i = 0; i < m; i++) b[i] = sc.nextInt();\n    // TODO: compute and print the median.\n  }\n}\n",
}


STARTER_KIND_BY_SLUG = {
    "two-sum": "array_target",
    "valid-parentheses": "string",
    "maximum-subarray": "array_only",
    "binary-search": "array_target",
    "merge-intervals": "intervals",
    "number-of-islands": "grid_chars",
    "climbing-stairs": "single_int",
    "longest-substring-without-repeating": "string",
    "contains-duplicate": "array_only",
    "best-time-to-buy-and-sell-stock": "prices",
    "valid-anagram": "two_strings",
    "product-of-array-except-self": "array_only",
    "top-k-frequent-elements": "array_k",
    "group-anagrams": "words",
    "palindrome-number": "single_int",
    "reverse-linked-list": "values",
    "middle-of-linked-list": "values",
    "linked-list-cycle": "cycle",
    "min-stack": "ops",
    "daily-temperatures": "array_only",
    "kth-largest-element": "array_k",
    "search-in-rotated-sorted-array": "array_target",
    "find-minimum-in-rotated-sorted-array": "array_only",
    "coin-change": "coins",
    "longest-increasing-subsequence": "array_only",
    "word-break": "word_break",
    "course-schedule": "edges",
    "rotting-oranges": "grid_ints",
    "clone-graph": "adj",
    "trapping-rain-water": "array_only",
    "median-of-two-sorted-arrays": "two_arrays",
}

PROBLEMS = [
    {
        "slug": "two-sum",
        "title": "Two Sum",
        "difficulty": "easy",
        "tags": ["array", "hash-map"],
        "description": "Given an array of integers and a target, return indices of two numbers that add up to the target.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n# print two indices\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main(){\n  return 0;\n}\n",
            "java": "import java.util.*;\npublic class Main { public static void main(String[] args) { } }\n",
        },
        "test_cases": [("4\n2 7 11 15\n9\n", "0 1\n"), ("3\n3 2 4\n6\n", "1 2\n")],
    },
    {
        "slug": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "easy",
        "tags": ["stack", "string"],
        "description": "Given a string containing brackets, determine whether every opening bracket is closed in the correct order.",
        "starter_code": {
            "python": "n = int(input())\ns = input().strip()\n# print true or false\n"
        },
        "test_cases": [("6\n()[]{}\n", "true\n"), ("2\n(]\n", "false\n")],
    },
    {
        "slug": "maximum-subarray",
        "title": "Maximum Subarray",
        "difficulty": "medium",
        "tags": ["array", "dynamic-programming"],
        "description": "Find the maximum possible sum of a non-empty contiguous subarray.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print maximum subarray sum\n"
        },
        "test_cases": [("9\n-2 1 -3 4 -1 2 1 -5 4\n", "6\n"), ("5\n5 4 -1 7 8\n", "23\n")],
    },
    {
        "slug": "binary-search",
        "title": "Binary Search",
        "difficulty": "easy",
        "tags": ["array", "binary-search"],
        "description": "Given a sorted array and a target, return the target index or -1 if it is absent.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n# print index\n"
        },
        "test_cases": [("6\n-1 0 3 5 9 12\n9\n", "4\n"), ("6\n-1 0 3 5 9 12\n2\n", "-1\n")],
    },
    {
        "slug": "merge-intervals",
        "title": "Merge Intervals",
        "difficulty": "medium",
        "tags": ["array", "sorting"],
        "description": "Merge all overlapping intervals and print the merged intervals in ascending order.",
        "starter_code": {
            "python": "n = int(input())\nintervals = [tuple(map(int, input().split())) for _ in range(n)]\n"
        },
        "test_cases": [
            ("4\n1 3\n2 6\n8 10\n15 18\n", "1 6\n8 10\n15 18\n"),
            ("4\n1 4\n4 5\n6 8\n7 9\n", "1 5\n6 9\n"),
        ],
    },
    {
        "slug": "number-of-islands",
        "title": "Number of Islands",
        "difficulty": "medium",
        "tags": ["graph", "dfs", "bfs"],
        "description": "Count connected groups of 1s in a grid where connections are horizontal or vertical.",
        "starter_code": {
            "python": "rows, cols = map(int, input().split())\ngrid = [input().strip() for _ in range(rows)]\n"
        },
        "test_cases": [
            ("4 5\n11110\n11010\n11000\n00000\n", "1\n"),
            ("4 5\n11000\n11000\n00100\n00011\n", "3\n"),
        ],
    },
    {
        "slug": "climbing-stairs",
        "title": "Climbing Stairs",
        "difficulty": "easy",
        "tags": ["dynamic-programming", "math"],
        "description": "Count how many distinct ways there are to climb n stairs when each move is 1 or 2 steps.",
        "starter_code": {"python": "n = int(input())\n# print number of ways\n"},
        "test_cases": [("2\n", "2\n"), ("5\n", "8\n")],
    },
    {
        "slug": "longest-substring-without-repeating",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "medium",
        "tags": ["string", "sliding-window", "hash-set"],
        "description": "Find the length of the longest substring with no repeated characters.",
        "starter_code": {"python": "n = int(input())\ns = input().strip()\n# print max length\n"},
        "test_cases": [("8\nabcabcbb\n", "3\n"), ("5\nbbbbb\n", "1\n")],
    },
    {
        "slug": "contains-duplicate",
        "title": "Contains Duplicate",
        "difficulty": "easy",
        "tags": ["array", "hash-set"],
        "description": "Determine whether any value appears at least twice in the array.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print true or false\n"
        },
        "test_cases": [("4\n1 2 3 1\n", "true\n"), ("4\n1 2 3 4\n", "false\n")],
    },
    {
        "slug": "best-time-to-buy-and-sell-stock",
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "easy",
        "tags": ["array", "greedy"],
        "description": "Given daily prices, find the maximum profit from one buy followed by one sell.",
        "starter_code": {
            "python": "n = int(input())\nprices = list(map(int, input().split()))\n# print max profit\n"
        },
        "test_cases": [("6\n7 1 5 3 6 4\n", "5\n"), ("5\n7 6 4 3 1\n", "0\n")],
    },
    {
        "slug": "valid-anagram",
        "title": "Valid Anagram",
        "difficulty": "easy",
        "tags": ["string", "hash-map", "sorting"],
        "description": "Check whether two strings contain the same characters with the same counts.",
        "starter_code": {
            "python": "n = int(input())\ns = input().strip()\nt = input().strip()\n# print true or false\n"
        },
        "test_cases": [("7\nanagram\nnagaram\n", "true\n"), ("3\nrat\ncar\n", "false\n")],
    },
    {
        "slug": "product-of-array-except-self",
        "title": "Product of Array Except Self",
        "difficulty": "medium",
        "tags": ["array", "prefix-product"],
        "description": "For each index, print the product of all other elements without using division.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print products\n"
        },
        "test_cases": [("4\n1 2 3 4\n", "24 12 8 6\n"), ("5\n-1 1 0 -3 3\n", "0 0 9 0 0\n")],
    },
    {
        "slug": "top-k-frequent-elements",
        "title": "Top K Frequent Elements",
        "difficulty": "medium",
        "tags": ["array", "hash-map", "heap"],
        "description": "Print the k values that occur most often, ordered by decreasing frequency then value.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\nk = int(input())\n"
        },
        "test_cases": [("6\n1 1 1 2 2 3\n2\n", "1 2\n"), ("1\n1\n1\n", "1\n")],
    },
    {
        "slug": "group-anagrams",
        "title": "Group Anagrams",
        "difficulty": "medium",
        "tags": ["string", "hash-map", "sorting"],
        "description": "Group words that are anagrams and print each group on its own line.",
        "starter_code": {
            "python": "n = int(input())\nwords = input().split()\n# print grouped words\n"
        },
        "test_cases": [
            ("6\neat tea tan ate nat bat\n", "ate eat tea\nnat tan\nbat\n"),
            ("4\nabc bca cab dog\n", "abc bca cab\ndog\n"),
        ],
    },
    {
        "slug": "palindrome-number",
        "title": "Palindrome Number",
        "difficulty": "easy",
        "tags": ["math", "two-pointers"],
        "description": "Determine whether an integer reads the same forward and backward.",
        "starter_code": {"python": "x = int(input())\n# print true or false\n"},
        "test_cases": [("121\n", "true\n"), ("-121\n", "false\n")],
    },
    {
        "slug": "reverse-linked-list",
        "title": "Reverse Linked List",
        "difficulty": "easy",
        "tags": ["linked-list", "iteration"],
        "description": "Reverse the values of a singly linked list represented as space-separated input.",
        "starter_code": {
            "python": "n = int(input())\nvalues = input().split()\n# print reversed values\n"
        },
        "test_cases": [("5\n1 2 3 4 5\n", "5 4 3 2 1\n"), ("2\n1 2\n", "2 1\n")],
    },
    {
        "slug": "middle-of-linked-list",
        "title": "Middle of the Linked List",
        "difficulty": "easy",
        "tags": ["linked-list", "two-pointers"],
        "description": "Print the middle value of a linked list; for even length, print the second middle.",
        "starter_code": {
            "python": "n = int(input())\nvalues = input().split()\n# print middle value\n"
        },
        "test_cases": [("5\n1 2 3 4 5\n", "3\n"), ("6\n1 2 3 4 5 6\n", "4\n")],
    },
    {
        "slug": "linked-list-cycle",
        "title": "Linked List Cycle",
        "difficulty": "easy",
        "tags": ["linked-list", "two-pointers"],
        "description": "Given n and a zero-based cycle position, determine whether the linked list has a cycle.",
        "starter_code": {"python": "n = int(input())\npos = int(input())\n# print true or false\n"},
        "test_cases": [("4\n1\n", "true\n"), ("1\n-1\n", "false\n")],
    },
    {
        "slug": "min-stack",
        "title": "Min Stack",
        "difficulty": "medium",
        "tags": ["stack", "design"],
        "description": "Process stack operations push, pop, top, and getMin while returning minimum values in O(1).",
        "starter_code": {"python": "n = int(input())\nops = [input().split() for _ in range(n)]\n"},
        "test_cases": [
            ("5\npush -2\npush 0\npush -3\ngetMin\npop\n", "-3\n"),
            ("7\npush 2\npush 1\ngetMin\npop\ntop\ngetMin\npop\n", "1\n2\n2\n"),
        ],
    },
    {
        "slug": "daily-temperatures",
        "title": "Daily Temperatures",
        "difficulty": "medium",
        "tags": ["stack", "monotonic-stack"],
        "description": "For each day, print how many days to wait for a warmer temperature, or 0.",
        "starter_code": {
            "python": "n = int(input())\ntemps = list(map(int, input().split()))\n# print waits\n"
        },
        "test_cases": [
            ("8\n73 74 75 71 69 72 76 73\n", "1 1 4 2 1 1 0 0\n"),
            ("4\n30 40 50 60\n", "1 1 1 0\n"),
        ],
    },
    {
        "slug": "kth-largest-element",
        "title": "Kth Largest Element",
        "difficulty": "medium",
        "tags": ["array", "heap", "quickselect"],
        "description": "Print the kth largest value in an unsorted array.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\nk = int(input())\n"
        },
        "test_cases": [("6\n3 2 1 5 6 4\n2\n", "5\n"), ("9\n3 2 3 1 2 4 5 5 6\n4\n", "4\n")],
    },
    {
        "slug": "search-in-rotated-sorted-array",
        "title": "Search in Rotated Sorted Array",
        "difficulty": "medium",
        "tags": ["array", "binary-search"],
        "description": "Find a target in a rotated sorted array and print its index, or -1.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\n"
        },
        "test_cases": [("7\n4 5 6 7 0 1 2\n0\n", "4\n"), ("7\n4 5 6 7 0 1 2\n3\n", "-1\n")],
    },
    {
        "slug": "find-minimum-in-rotated-sorted-array",
        "title": "Find Minimum in Rotated Sorted Array",
        "difficulty": "medium",
        "tags": ["array", "binary-search"],
        "description": "Print the minimum value in a rotated sorted array with unique values.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print minimum\n"
        },
        "test_cases": [("5\n3 4 5 1 2\n", "1\n"), ("7\n4 5 6 7 0 1 2\n", "0\n")],
    },
    {
        "slug": "coin-change",
        "title": "Coin Change",
        "difficulty": "medium",
        "tags": ["dynamic-programming", "bfs"],
        "description": "Given coin denominations and an amount, print the fewest coins needed or -1.",
        "starter_code": {
            "python": "n = int(input())\ncoins = list(map(int, input().split()))\namount = int(input())\n"
        },
        "test_cases": [("3\n1 2 5\n11\n", "3\n"), ("1\n2\n3\n", "-1\n")],
    },
    {
        "slug": "longest-increasing-subsequence",
        "title": "Longest Increasing Subsequence",
        "difficulty": "medium",
        "tags": ["dynamic-programming", "binary-search"],
        "description": "Print the length of the longest strictly increasing subsequence.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print length\n"
        },
        "test_cases": [("8\n10 9 2 5 3 7 101 18\n", "4\n"), ("6\n0 1 0 3 2 3\n", "4\n")],
    },
    {
        "slug": "word-break",
        "title": "Word Break",
        "difficulty": "medium",
        "tags": ["dynamic-programming", "trie", "string"],
        "description": "Given a string and dictionary words, decide whether the string can be segmented into dictionary words.",
        "starter_code": {
            "python": "n = int(input())\ns = input().strip()\nm = int(input())\nwords = input().split()\n"
        },
        "test_cases": [
            ("8\nleetcode\n2\nleet code\n", "true\n"),
            ("9\ncatsandog\n5\ncats dog sand and cat\n", "false\n"),
        ],
    },
    {
        "slug": "course-schedule",
        "title": "Course Schedule",
        "difficulty": "medium",
        "tags": ["graph", "topological-sort"],
        "description": "Given prerequisites, determine whether all courses can be finished.",
        "starter_code": {
            "python": "n, m = map(int, input().split())\nedges = [tuple(map(int, input().split())) for _ in range(m)]\n"
        },
        "test_cases": [("2 1\n1 0\n", "true\n"), ("2 2\n1 0\n0 1\n", "false\n")],
    },
    {
        "slug": "rotting-oranges",
        "title": "Rotting Oranges",
        "difficulty": "medium",
        "tags": ["graph", "bfs", "grid"],
        "description": "Find how many minutes are needed until no fresh orange remains, or print -1.",
        "starter_code": {
            "python": "r, c = map(int, input().split())\ngrid = [list(map(int, input().split())) for _ in range(r)]\n"
        },
        "test_cases": [
            ("3 3\n2 1 1\n1 1 0\n0 1 1\n", "4\n"),
            ("3 3\n2 1 1\n0 1 1\n1 0 1\n", "-1\n"),
        ],
    },
    {
        "slug": "clone-graph",
        "title": "Clone Graph",
        "difficulty": "medium",
        "tags": ["graph", "dfs", "bfs"],
        "description": "Given an adjacency list for an undirected graph, print the adjacency list of its clone.",
        "starter_code": {"python": "n = int(input())\nadj = [input().split() for _ in range(n)]\n"},
        "test_cases": [("2\n2\n1\n", "2\n1\n"), ("3\n2 3\n1 3\n1 2\n", "2 3\n1 3\n1 2\n")],
    },
    {
        "slug": "trapping-rain-water",
        "title": "Trapping Rain Water",
        "difficulty": "hard",
        "tags": ["array", "two-pointers", "prefix"],
        "description": "Given bar heights, print how much water can be trapped after raining.",
        "starter_code": {
            "python": "n = int(input())\nheight = list(map(int, input().split()))\n# print trapped water\n"
        },
        "test_cases": [("12\n0 1 0 2 1 0 1 3 2 1 2 1\n", "6\n"), ("6\n4 2 0 3 2 5\n", "9\n")],
    },
    {
        "slug": "median-of-two-sorted-arrays",
        "title": "Median of Two Sorted Arrays",
        "difficulty": "hard",
        "tags": ["array", "binary-search", "leetcode"],
        "description": "Given two sorted arrays, print the median of the combined values.",
        "starter_code": {
            "python": "n = int(input())\na = list(map(int, input().split()))\nm = int(input())\nb = list(map(int, input().split()))\n"
        },
        "test_cases": [("2\n1 3\n1\n2\n", "2\n"), ("2\n1 2\n2\n3 4\n", "2.5\n")],
    },
    {
        "slug": "watermelon",
        "title": "Watermelon (Codeforces 4A)",
        "difficulty": "easy",
        "tags": ["math", "codeforces"],
        "description": "Pete and Billy bought a watermelon of weight w kilos. They want to divide it into two parts, each weighing an even number of kilos (> 0). Print YES if they can divide it, otherwise print NO.",
        "starter_code": {"python": "w = int(input())\n# print YES or NO\n"},
        "test_cases": [("8\n", "YES\n"), ("5\n", "NO\n"), ("2\n", "NO\n")],
    },
    {
        "slug": "way-too-long-words",
        "title": "Way Too Long Words (Codeforces 71A)",
        "difficulty": "easy",
        "tags": ["string", "codeforces"],
        "description": "If a word's length is strictly greater than 10 characters, replace it with an abbreviation: first character, count of characters between first and last, and last character. Words with length <= 10 remain unchanged.",
        "starter_code": {
            "python": "n = int(input())\nfor _ in range(n):\n    w = input().strip()\n"
        },
        "test_cases": [
            (
                "4\nword\nlocalization\ninternationalization\npneumonoultramicroscopicsilicovolcanoconiosis\n",
                "word\nl10n\ni18n\np43s\n",
            ),
            ("1\napple\n", "apple\n"),
        ],
    },
    {
        "slug": "theatre-square",
        "title": "Theatre Square (Codeforces 1A)",
        "difficulty": "easy",
        "tags": ["math", "codeforces"],
        "description": "Theatre Square has a rectangular shape of n x m meters. Pave the Square with flagstones of size a x a. Find the minimum number of flagstones needed.",
        "starter_code": {
            "python": "n, m, a = map(int, input().split())\n# print minimum flagstones needed\n"
        },
        "test_cases": [("6 6 4\n", "4\n"), ("1 1 1\n", "1\n")],
    },
    {
        "slug": "three-sum",
        "title": "3Sum (LeetCode 15)",
        "difficulty": "medium",
        "tags": ["array", "two-pointers", "leetcode"],
        "description": "Given an integer array nums, return all unique triplets [nums[i], nums[j], nums[k]] such that nums[i] + nums[j] + nums[k] == 0. Print each triplet on a new line.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print unique triplets\n"
        },
        "test_cases": [("6\n-1 0 1 2 -1 -4\n", "-1 -1 2\n-1 0 1\n"), ("3\n0 1 1\n", "")],
    },
    {
        "slug": "container-with-most-water",
        "title": "Container With Most Water (LeetCode 11)",
        "difficulty": "medium",
        "tags": ["array", "two-pointers", "greedy", "leetcode"],
        "description": "Given an integer array height representing n vertical lines, find two lines that together with the x-axis form a container holding the most water. Print the maximum area.",
        "starter_code": {
            "python": "n = int(input())\nheight = list(map(int, input().split()))\n# print max area\n"
        },
        "test_cases": [("9\n1 8 6 2 5 4 8 3 7\n", "49\n"), ("2\n1 1\n", "1\n")],
    },
    {
        "slug": "subarray-sum-equals-k",
        "title": "Subarray Sum Equals K (LeetCode 560)",
        "difficulty": "medium",
        "tags": ["array", "prefix-sum", "hash-map", "leetcode"],
        "description": "Given an array of integers nums and an integer k, return the total number of contiguous subarrays whose sum equals to k.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\nk = int(input())\n# print count\n"
        },
        "test_cases": [("3\n1 1 1\n2\n", "2\n"), ("3\n1 2 3\n3\n", "2\n")],
    },
    {
        "slug": "next-permutation",
        "title": "Next Permutation (LeetCode 31)",
        "difficulty": "medium",
        "tags": ["array", "two-pointers", "leetcode"],
        "description": "Find the lexicographically next greater permutation of numbers. If not possible, rearrange in ascending order.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\n# print next permutation\n"
        },
        "test_cases": [
            ("3\n1 2 3\n", "1 3 2\n"),
            ("3\n3 2 1\n", "1 2 3\n"),
            ("3\n1 1 5\n", "1 5 1\n"),
        ],
    },
    {
        "slug": "word-search",
        "title": "Word Search (LeetCode 79)",
        "difficulty": "medium",
        "tags": ["matrix", "backtracking", "dfs", "leetcode"],
        "description": "Given an m x n grid of characters and a string word, return true if word exists in the grid constructed from horizontally or vertically adjacent cells.",
        "starter_code": {
            "python": "r, c = map(int, input().split())\ngrid = [input().strip() for _ in range(r)]\nword = input().strip()\n# print true or false\n"
        },
        "test_cases": [
            ("3 4\nABCE\nSFCS\nADEE\nABCCED\n", "true\n"),
            ("3 4\nABCE\nSFCS\nADEE\nABCB\n", "false\n"),
        ],
    },
    {
        "slug": "edit-distance",
        "title": "Edit Distance (LeetCode 72)",
        "difficulty": "hard",
        "tags": ["string", "dynamic-programming", "leetcode"],
        "description": "Given two strings word1 and word2, return the minimum number of operations (insert, delete, replace) required to convert word1 to word2.",
        "starter_code": {
            "python": "word1 = input().strip()\nword2 = input().strip()\n# print min operations\n"
        },
        "test_cases": [("horse\nros\n", "3\n"), ("intention\nexecution\n", "5\n")],
    },
    {
        "slug": "sliding-window-maximum",
        "title": "Sliding Window Maximum (LeetCode 239)",
        "difficulty": "hard",
        "tags": ["array", "sliding-window", "deque", "leetcode"],
        "description": "Given an array of integers nums and a sliding window of size k moving from left to right, print the max value in the window at each position.",
        "starter_code": {
            "python": "n = int(input())\nnums = list(map(int, input().split()))\nk = int(input())\n# print max values\n"
        },
        "test_cases": [("8\n1 3 -1 -3 5 3 6 7\n3\n", "3 3 5 5 6 7\n"), ("1\n1\n1\n", "1\n")],
    },
    {
        "slug": "minimum-window-substring",
        "title": "Minimum Window Substring (LeetCode 76)",
        "difficulty": "hard",
        "tags": ["string", "sliding-window", "hash-map", "leetcode"],
        "description": "Given strings s and t, return the minimum window substring of s such that every character in t is included in the window.",
        "starter_code": {
            "python": "s = input().strip()\nt = input().strip()\n# print minimum window substring\n"
        },
        "test_cases": [("ADOBECODEBANC\nABC\n", "BANC\n"), ("a\na\n", "a\n")],
    },
    {
        "slug": "beautiful-matrix",
        "title": "Beautiful Matrix (Codeforces 263A)",
        "difficulty": "easy",
        "tags": ["matrix", "implementation", "codeforces"],
        "description": "Given a 5x5 matrix consisting of 24 zeroes and a single 1, find the minimum number of moves to move the number 1 to the center of the matrix (row 3, col 3).",
        "starter_code": {
            "python": "grid = [list(map(int, input().split())) for _ in range(5)]\n# print min moves\n"
        },
        "test_cases": [
            ("0 0 0 0 0\n0 0 0 0 0\n0 1 0 0 0\n0 0 0 0 0\n0 0 0 0 0\n", "1\n"),
            ("0 0 0 0 0\n0 0 0 0 1\n0 0 0 0 0\n0 0 0 0 0\n0 0 0 0 0\n", "3\n"),
        ],
    },
    {
        "slug": "domino-piling",
        "title": "Domino Piling (Codeforces 50A)",
        "difficulty": "easy",
        "tags": ["math", "greedy", "codeforces"],
        "description": "Given a rectangular board of M x N squares, find the maximum number of 2 x 1 dominoes that can be placed on the board.",
        "starter_code": {"python": "m, n = map(int, input().split())\n# print max dominoes\n"},
        "test_cases": [("2 4\n", "4\n"), ("3 3\n", "4\n")],
    },
    {
        "slug": "kth-smallest-in-bst",
        "title": "Kth Smallest Element in a BST (LeetCode 230)",
        "difficulty": "medium",
        "tags": ["tree", "binary-search-tree", "dfs", "leetcode"],
        "description": "Given a binary search tree represented as an array (level-order traversal where -1 denotes null) and an integer k, return the kth smallest value (1-indexed).",
        "starter_code": {
            "python": "n = int(input())\nvals = list(map(int, input().split()))\nk = int(input())\n"
        },
        "test_cases": [("6\n3 1 4 -1 2 -1\n1\n", "1\n"), ("7\n5 3 6 2 4 -1 -1\n3\n", "4\n")],
    },
    {
        "slug": "bitwise-and-range",
        "title": "Bitwise AND of Numbers Range (LeetCode 201)",
        "difficulty": "medium",
        "tags": ["bit-manipulation", "leetcode"],
        "description": "Given two integers left and right representing the range [left, right], return the bitwise AND of all numbers in this range, inclusive.",
        "starter_code": {
            "python": "left, right = map(int, input().split())\n# print bitwise AND\n"
        },
        "test_cases": [("5 7\n", "4\n"), ("0 0\n", "0\n"), ("1 2147483647\n", "0\n")],
    },
    {
        "slug": "word-ladder",
        "title": "Word Ladder (LeetCode 127)",
        "difficulty": "hard",
        "tags": ["graph", "bfs", "string", "leetcode"],
        "description": "Return the number of words in the shortest transformation sequence from beginWord to endWord changing 1 letter at a time through wordList, or 0 if impossible.",
        "starter_code": {
            "python": "begin = input().strip()\nend = input().strip()\nn = int(input())\nword_list = input().split()\n"
        },
        "test_cases": [
            ("hit\ncog\n6\nhot dot dog lot log cog\n", "5\n"),
            ("hit\ncog\n5\nhot dot dog lot log\n", "0\n"),
        ],
    },
]


async def seed_problems(db: AsyncSession) -> None:
    existing = await db.execute(select(Problem).options(selectinload(Problem.test_cases)))
    existing_by_slug = {problem.slug: problem for problem in existing.scalars().all()}

    for problem_data in PROBLEMS:
        test_cases = problem_data["test_cases"]
        problem = existing_by_slug.get(problem_data["slug"])

        if problem is None:
            problem = Problem(slug=problem_data["slug"])
            db.add(problem)

        problem.title = problem_data["title"]
        problem.difficulty = problem_data["difficulty"]
        problem.tags = problem_data["tags"]
        problem.description = problem_data["description"]
        starter_kind = STARTER_KIND_BY_SLUG.get(problem_data["slug"])
        starter_code = {
            **LANGUAGE_STARTERS,
            **problem_data["starter_code"],
            "cpp": CPP_STARTERS.get(starter_kind, LANGUAGE_STARTERS["cpp"]),
            "java": JAVA_STARTERS.get(starter_kind, LANGUAGE_STARTERS["java"]),
        }
        problem.starter_code = starter_code
        had_test_cases = bool(problem.test_cases)
        problem.test_cases.clear()
        if had_test_cases:
            await db.flush()

        for position, (stdin, expected_stdout) in enumerate(test_cases, start=1):
            problem.test_cases.append(
                TestCase(
                    position=position,
                    stdin=stdin,
                    expected_stdout=expected_stdout,
                    is_sample=True,
                )
            )

    await db.commit()
