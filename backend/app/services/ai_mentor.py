import json
import re
from pathlib import Path

import httpx

from app.core.config import settings
from app.schemas.mentor import HintRequest, MentorCodeRequest, MentorResponse

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


class AIMentorService:
    @property
    def api_key(self) -> str | None:
        from app.core.config import get_settings

        current_settings = get_settings()
        if current_settings.openai_api_key:
            return current_settings.openai_api_key.get_secret_value()
        return None

    @property
    def model(self) -> str:
        from app.core.config import get_settings

        return get_settings().openai_model

    async def explain(self, payload: MentorCodeRequest) -> MentorResponse:
        return await self._complete("explain", payload, self._local_explanation(payload))

    async def hint(self, payload: HintRequest) -> MentorResponse:
        return await self._complete("hint", payload, self._local_hint(payload))

    async def detect_bugs(self, payload: MentorCodeRequest) -> MentorResponse:
        return await self._complete("detect_bugs", payload, self._local_bug_report(payload))

    async def complexity(self, payload: MentorCodeRequest) -> MentorResponse:
        return await self._complete("complexity", payload, self._local_complexity(payload))

    async def optimize(self, payload: MentorCodeRequest) -> MentorResponse:
        return await self._complete("optimize", payload, self._local_optimization(payload))

    async def _complete(
        self,
        template_name: str,
        payload: MentorCodeRequest,
        fallback: str,
    ) -> MentorResponse:
        api_key = self.api_key
        if not api_key:
            return MentorResponse(result=fallback, source="local")

        prompt = self._render_prompt(template_name, payload)
        try:
            result = await self._call_openai(prompt)
        except (httpx.HTTPError, KeyError, json.JSONDecodeError):
            return MentorResponse(result=fallback, source="local")

        return MentorResponse(result=result.strip() or fallback, source="openai")

    def _render_prompt(self, template_name: str, payload: MentorCodeRequest) -> str:
        template = (PROMPT_DIR / f"{template_name}.md").read_text(encoding="utf-8")
        problem_statement = payload.problem_statement or "No problem statement was provided."
        stdin = payload.stdin or "No stdin was provided."
        stdout = payload.stdout or "No stdout was provided."
        stderr = payload.stderr or "No stderr was provided."
        exit_code = "Not run" if payload.exit_code is None else str(payload.exit_code)
        hint_level = getattr(payload, "hint_level", "")

        replacements = {
            "{language}": str(payload.language),
            "{code}": str(payload.code),
            "{problem_statement}": problem_statement,
            "{stdin}": stdin,
            "{stdout}": stdout,
            "{stderr}": stderr,
            "{exit_code}": exit_code,
            "{hint_level}": str(hint_level),
        }
        rendered = template
        for placeholder, value in replacements.items():
            rendered = rendered.replace(placeholder, value)
        return rendered

    async def _call_openai(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI Coding and Data Structures & Algorithms (DSA) Mentor. "
                        "When given a specific coding problem, directly explain the optimal algorithm, core intuition, "
                        "step-by-step logic, boundary edge cases, and time/space complexity analysis. Avoid generic "
                        "data structure overviews unless explicitly requested."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.25,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        base_url = settings.openai_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                url,
                json=body,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

    def _local_explanation(self, payload: MentorCodeRequest) -> str:
        problem = (payload.problem_statement or "").strip()
        code = payload.code.strip()

        # Check if the user is asking a conceptual question in the Problem Context box or code comment
        concept_explanation = self._get_concept_explanation(problem, payload.language)
        if not concept_explanation:
            todo_match = re.search(r"solve\s+([A-Za-z0-9\s]+)", code, re.IGNORECASE)
            if todo_match:
                concept_explanation = self._get_concept_explanation(
                    todo_match.group(1), payload.language
                )

        if concept_explanation:
            return concept_explanation

        lines = [line for line in code.splitlines() if line.strip()]
        functions = sum(1 for line in lines if line.lstrip().startswith("def "))
        loops = sum(1 for line in lines if any(token in line for token in ("for ", "while ")))
        branches = sum(1 for line in lines if line.lstrip().startswith(("if ", "elif ", "else:")))

        prob_title = "Given Problem"
        if payload.problem_statement:
            prob_title = payload.problem_statement.splitlines()[0].strip()

        observations = self._local_code_observations(payload)
        structure = (
            f"### Problem Context: **{prob_title}**\n\n"
            f"**Code Analysis:**\n"
            f"- Language: `{payload.language}`\n"
            f"- Structure: {len(lines)} lines of code, {functions} function(s), {loops} loop(s), {branches} conditional branch(es)."
        )
        run_context = ""
        if payload.stdout or payload.stderr or payload.exit_code is not None:
            run_context = (
                "\n\n**Latest Execution Run:**\n"
                f"- Exit Code: `{payload.exit_code if payload.exit_code is not None else 'unknown'}`\n"
            )
            if payload.stdout:
                run_context += f"\nstdout: {payload.stdout.strip()}"
            if payload.stderr:
                run_context += f"\nstderr: {payload.stderr.strip()}"

        return f"{structure}\n\n**Overview:**\n{observations}{run_context}"

    def _get_concept_explanation(self, query: str, language: str) -> str | None:
        q = query.lower()
        if not q:
            return None

        # 1. Specific Problem Titles (Highest Priority)
        if any(
            kw in q for kw in ("median", "two sorted arrays", "combined sorted arrays", "log(min")
        ):
            return (
                "### 🔍 Approach: Median of Two Sorted Arrays\n\n"
                "To find the median of two sorted arrays `nums1` (size N) and `nums2` (size M) in **`O(log(min(N,M)))`** time, use **Binary Search on Partitioning**.\n\n"
                "#### 💡 Core Idea:\n"
                "Partition both arrays into Left and Right halves such that every element in the combined Left half is `<= ` every element in the combined Right half.\n\n"
                "#### 📝 Algorithm Steps:\n"
                "1. Ensure `nums1` is the smaller array (if `nums1.size() > nums2.size()`, swap them).\n"
                "2. Perform Binary Search on `nums1` partition index `i` from `low = 0` to `high = N`:\n"
                "   - `i = (low + high) / 2` (elements taken from `nums1` for left half).\n"
                "   - `j = (N + M + 1) / 2 - i` (elements taken from `nums2` for left half).\n"
                "3. Define boundary elements:\n"
                "   - `maxLeft1 = (i == 0) ? -INF : nums1[i-1]`\n"
                "   - `minRight1 = (i == N) ? +INF : nums1[i]`\n"
                "   - `maxLeft2 = (j == 0) ? -INF : nums2[j-1]`\n"
                "   - `minRight2 = (j == M) ? +INF : nums2[j]`\n"
                "4. **Valid Partition Check:** `maxLeft1 <= minRight2` AND `maxLeft2 <= minRight1`:\n"
                "   - If **Odd Total Length**: `median = max(maxLeft1, maxLeft2)`.\n"
                "   - If **Even Total Length**: `median = (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2.0`.\n"
                "5. Adjust search bounds:\n"
                "   - If `maxLeft1 > minRight2`, set `high = i - 1`.\n"
                "   - Else, set `low = i + 1`.\n\n"
                f"#### 💻 Complete {language.upper()} Solution:\n"
                "```cpp\n"
                "#include <vector>\n"
                "#include <algorithm>\n"
                "#include <climits>\n"
                "using namespace std;\n\n"
                "double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {\n"
                "    if (nums1.size() > nums2.size()) return findMedianSortedArrays(nums2, nums1);\n"
                "    int n1 = nums1.size(), n2 = nums2.size();\n"
                "    int low = 0, high = n1;\n"
                "    while (low <= high) {\n"
                "        int i = low + (high - low) / 2;\n"
                "        int j = (n1 + n2 + 1) / 2 - i;\n"
                "        int maxLeft1 = (i == 0) ? INT_MIN : nums1[i - 1];\n"
                "        int minRight1 = (i == n1) ? INT_MAX : nums1[i];\n"
                "        int maxLeft2 = (j == 0) ? INT_MIN : nums2[j - 1];\n"
                "        int minRight2 = (j == n2) ? INT_MAX : nums2[j];\n"
                "        if (maxLeft1 <= minRight2 && maxLeft2 <= minRight1) {\n"
                "            if ((n1 + n2) % 2 == 1) return max(maxLeft1, maxLeft2);\n"
                "            else return (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2.0;\n"
                "        } else if (maxLeft1 > minRight2) high = i - 1;\n"
                "        else low = i + 1;\n"
                "    }\n"
                "    return 0.0;\n"
                "}\n"
                "```\n\n"
                "#### ⏱️ Complexity Analysis:\n"
                "- **Time Complexity:** `O(log(min(N, M)))` — Binary search on smaller array size.\n"
                "- **Space Complexity:** `O(1)` — Constant auxiliary space."
            )

        if "rotated" in q or "rotated sorted array" in q or "search in rotated" in q:
            return (
                "### 🔍 Approach: Search in Rotated Sorted Array\n\n"
                "To solve **Search in Rotated Sorted Array** in `O(log N)` time, use **Modified Binary Search**.\n\n"
                "#### 💡 Core Idea:\n"
                "Even though the array is rotated, **at least one half (left or right) is guaranteed to be strictly sorted** at any iteration!\n\n"
                "#### 📝 Algorithm Steps:\n"
                "1. Initialize `low = 0` and `high = nums.size() - 1`.\n"
                "2. Find `mid = low + (high - low) / 2`.\n"
                "3. If `nums[mid] == target`, return `mid`.\n"
                "4. Check which half is sorted:\n"
                "   - **Left half is sorted (`nums[low] <= nums[mid]`):**\n"
                "     Check if `target` lies within `[nums[low], nums[mid]]`. If yes, set `high = mid - 1`; else set `low = mid + 1`.\n"
                "   - **Right half is sorted (`nums[mid] <= nums[high]`):**\n"
                "     Check if `target` lies within `[nums[mid], nums[high]]`. If yes, set `low = mid + 1`; else set `high = mid - 1`.\n"
                "5. If loop ends without finding target, return `-1`.\n\n"
                f"#### 💻 Complete {language.upper()} Solution:\n"
                "```cpp\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int search(vector<int>& nums, int target) {\n"
                "    int low = 0, high = nums.size() - 1;\n"
                "    while (low <= high) {\n"
                "        int mid = low + (high - low) / 2;\n"
                "        if (nums[mid] == target) return mid;\n"
                "        if (nums[low] <= nums[mid]) {\n"
                "            if (nums[low] <= target && target < nums[mid]) high = mid - 1;\n"
                "            else low = mid + 1;\n"
                "        } else {\n"
                "            if (nums[mid] < target && target <= nums[high]) low = mid + 1;\n"
                "            else high = mid - 1;\n"
                "        }\n"
                "    }\n"
                "    return -1;\n"
                "}\n"
                "```\n\n"
                "#### ⏱️ Complexity Analysis:\n"
                "- **Time Complexity:** `O(log N)`\n"
                "- **Space Complexity:** `O(1)` constant auxiliary space."
            )

        if "two sum" in q:
            return (
                "### 🎯 Two Sum Problem Pattern\n\n"
                "Given an array of integers `nums` and a `target` sum, return the indices of two numbers that add up to `target`.\n\n"
                "#### 💡 Optimal Approach (Hash Map - O(N) Time):\n"
                "- Iterate through `nums` with index `i` and value `num`.\n"
                "- Compute `complement = target - num`.\n"
                "- Check if `complement` exists in your hash map `seen`.\n"
                "  - If yes, return `[seen[complement], i]`.\n"
                "  - If no, store `seen[num] = i` and continue.\n\n"
                "#### ⏱️ Complexity:\n"
                "- **Time Complexity:** `O(N)` — Single pass over array.\n"
                "- **Space Complexity:** `O(N)` — Hash map stores up to N elements."
            )

        if "sliding window" in q:
            return (
                "### 🪟 Sliding Window Pattern\n\n"
                "Used to transform `O(N^2)` brute-force nested loops into `O(N)` linear time for contiguous subarray or substring problems.\n\n"
                "#### 💡 When to Use:\n"
                "- Subarray sum equal to `K`, longest substring without repeating characters, or max values in window size `K`.\n\n"
                "#### 🔄 Mechanism:\n"
                "1. Maintain two pointers `left` and `right` forming a window `[left, right]`.\n"
                "2. Expand `right` to include new elements.\n"
                "3. Shrink `left` when window condition is violated."
            )

        if "binary search" in q:
            return (
                "### 🔍 Binary Search Pattern\n\n"
                "Search algorithm for finding a target value within a **sorted array** by halving the search space at each step.\n\n"
                "#### ⏱️ Complexity:\n"
                "- **Time Complexity:** `O(log N)`\n"
                "- **Space Complexity:** `O(1)` iterative, `O(log N)` recursive call stack."
            )

        if "linked list" in q:
            return (
                "### 🔗 Linked List Data Structure\n\n"
                "A linear collection of data nodes where each node contains a value and a reference pointer (`next`) to the next node.\n\n"
                "#### ⚡ Key Characteristics:\n"
                "- **Insertion/Deletion at Head:** `O(1)` time.\n"
                "- **Access by Index:** `O(N)` time.\n"
                "- **Floyd's Cycle Algorithm:** Fast & Slow pointers to detect loops."
            )

        if "tree" in q or "bst" in q:
            return (
                "### 🌲 Trees & Binary Search Trees (BST)\n\n"
                "A hierarchical structure consisting of nodes with root, left, and right child references.\n\n"
                "#### 💡 BST Property:\n"
                "For every node: `left.val < node.val < right.val`.\n"
                "- Search, Insertion, Deletion: `O(log N)` average, `O(N)` worst-case (skewed tree).\n"
                "- Inorder Traversal of a BST yields values in **strictly sorted order**."
            )

        if "graph" in q or "bfs" in q or "dfs" in q:
            return (
                "### 🕸️ Graph Traversals (BFS & DFS)\n\n"
                "- **BFS (Breadth-First Search):** Uses a **Queue (FIFO)**. Visits nodes level-by-level for **shortest path**.\n"
                "- **DFS (Depth-First Search):** Uses a **Stack / Recursion**. Explores as deep as possible before backtracking."
            )

        if "dp" in q or "dynamic programming" in q:
            return (
                "### 🧩 Dynamic Programming (DP)\n\n"
                "An optimization technique that solves complex problems by breaking them down into **overlapping subproblems** and storing results."
            )

        # 2. Generic Single Word Concepts (Lowest Priority)
        if "array" in q:
            return (
                "### 📚 Understanding Arrays (Data Structures)\n\n"
                "An **Array** is a linear data structure that stores elements of the same data type in **contiguous memory locations**. "
                "Each element is accessed using a zero-based index (`0` to `N-1`).\n\n"
                "#### ⚡ Key Characteristics:\n"
                "- **Random Access:** `O(1)` time to access any element by index (`arr[i]`).\n"
                "- **Contiguous Memory:** Elements are placed sequentially in memory, optimizing CPU cache hits.\n"
                "- **Insertion / Deletion:** `O(N)` time at arbitrary positions (requires shifting elements).\n"
                "- **Search:** `O(N)` for linear search, `O(log N)` for binary search on sorted arrays.\n\n"
                "#### 💡 Common Array Algorithmic Patterns:\n"
                "1. **Two Pointers:** Move `left` and `right` pointers to search pairs or reverse subarrays in `O(N)` time.\n"
                "2. **Sliding Window:** Track a contiguous subarray of fixed or dynamic size for max/min sums or substring conditions.\n"
                "3. **Prefix Sum:** Precompute cumulative sums `prefix[i] = prefix[i-1] + arr[i]` for `O(1)` range sum queries.\n"
                "4. **Kadane's Algorithm:** Find maximum subarray sum in single `O(N)` pass."
            )

        return None

    def _local_code_observations(self, payload: MentorCodeRequest) -> str:
        code = payload.code.strip()
        if not code:
            return "There is no code provided yet."

        if payload.language == "python":
            print_matches = re.findall(r"print\((.*?)\)", code, flags=re.DOTALL)
            if print_matches and len(code.splitlines()) <= 3:
                printed = print_matches[0].strip()
                return f"This Python code sends a value to standard output using `print`. The expression being printed is `{printed}`."
            if "input(" in code:
                return "This Python program reads input using `input()`, processes values line-by-line, and outputs the result."
            if "def " in code:
                return "This Python solution defines a custom helper function. Trace the parameters passed and return values."

        if payload.language == "cpp":
            if "std::cin" in code or re.search(r"\bcin\s*>>", code):
                return "This C++ solution reads formatted input from `cin` and computes the result inside `main`."

        if payload.language == "java":
            if "Scanner" in code or "BufferedReader" in code:
                return "This Java solution reads input using `Scanner`/`BufferedReader` and outputs the calculated solution."

        return f"This `{payload.language}` solution processes input variables and computes the required output."

    def _local_hint(self, payload: HintRequest) -> str:
        problem = (payload.problem_statement or "").strip()
        prob_title = problem.splitlines()[0] if problem else "the problem"
        code = payload.code.strip()
        level = payload.hint_level

        # Detect pattern keywords from problem and code
        is_two_sum = "two sum" in problem.lower() or "target" in problem.lower()
        is_sliding_window = "substring" in problem.lower() or "window" in problem.lower()
        is_two_pointer = (
            "two pointers" in problem.lower()
            or "pair" in problem.lower()
            or "triplet" in problem.lower()
        )
        is_dp = (
            "dp" in problem.lower()
            or "subsequence" in problem.lower()
            or "ways" in problem.lower()
            or "coins" in problem.lower()
        )
        is_tree_graph = (
            "island" in problem.lower() or "tree" in problem.lower() or "graph" in problem.lower()
        )

        if level == 1:
            return (
                f"### 💡 Hint Level 1: Understanding **{prob_title}**\n\n"
                f"- **Goal:** Carefully examine what input data types are given and what exact format is expected for stdout/return.\n"
                f"- **Key Observation:** Identify the constraints. Can the input be empty, negative, or contain duplicate elements?\n"
                f"- **First Step:** Write out a small manual test case on paper and trace the expected output step-by-step before coding."
            )
        elif level == 2:
            if is_two_sum:
                pattern_advice = "Use a **Hash Map / Dictionary** to store numbers you've seen so far. For each number `x`, check if `target - x` is already in the hash map for O(n) time!"
            elif is_sliding_window:
                pattern_advice = "Use the **Sliding Window** technique with two pointers `left` and `right`. Expand `right` to include elements, and shrink `left` when constraints are violated."
            elif is_two_pointer:
                pattern_advice = "Sort the input array first if allowed, then use **Two Pointers** starting from opposite ends (`left = 0`, `right = n - 1`)."
            elif is_dp:
                pattern_advice = "Identify overlapping subproblems and state transitions. Define `dp[i]` as the optimal answer for subproblem of size `i`."
            elif is_tree_graph:
                pattern_advice = "Use **BFS (Queue)** for shortest path / level-order traversal or **DFS (Recursion / Stack)** for exploring deep paths."
            else:
                pattern_advice = "Look at how often you repeat scans over the data. If you have nested loops O(N^2), consider whether a Hash Set, Hash Map, or Sorting can reduce runtime to O(N) or O(N log N)."

            return (
                f"### 💡 Hint Level 2: Algorithmic Pattern Strategy\n\n"
                f"- **Recommended Pattern:** {pattern_advice}\n"
                f"- **Current Code Review:** Your current solution has `{len(code.splitlines())}` line(s) of code. Ensure you avoid unnecessary repeated full-array scans."
            )
        elif level == 3:
            return (
                "### 💡 Hint Level 3: Step-by-Step Logic Guidance\n\n"
                "1. **Initialize State:** Set up your primary data structures (e.g. `visited = set()`, `seen = {}`, or `dp = [...]`).\n"
                "2. **Main Processing Loop:** Iterate through the inputs once. Update your state at each step.\n"
                "3. **Termination Condition:** Ensure your loop or recursion properly terminates and returns/prints the final computed result.\n"
                "4. **Code Template Check:** Verify your code parses all inputs from stdin before performing calculations."
            )
        else:
            return (
                "### 💡 Hint Level 4: Edge Cases & Validation Checklist\n\n"
                "- ⚠️ **Empty / Single Element Input:** Does your code handle `n = 0` or `n = 1` without out-of-bounds errors?\n"
                "- ⚠️ **Negative Values & Zeros:** Test with inputs containing negative numbers or zero.\n"
                "- ⚠️ **Duplicate Values:** Ensure duplicate elements don't cause infinite loops or incorrect counts.\n"
                "- ⚠️ **Large Inputs (Time Limit Exceeded):** Check if your time complexity fits within 1 second (~10^7 operations)."
            )

    def _local_bug_report(self, payload: MentorCodeRequest) -> str:
        issues: list[str] = []
        code = payload.code

        if payload.exit_code not in (None, 0):
            issues.append(
                f"The latest run exited with code {payload.exit_code}. Check stderr first."
            )
        if payload.stderr:
            issues.append(f"Runtime error detected in stderr:\n```\n{payload.stderr.strip()}\n```")
        if "while True" in code and "break" not in code:
            issues.append(
                "A `while True` loop without an explicit `break` condition may cause a Time Limit Exceeded (infinite loop)."
            )
        if code.count("(") != code.count(")"):
            issues.append("Unbalanced parentheses detected `(` vs `)`.")
        if code.count("[") != code.count("]"):
            issues.append("Unbalanced square brackets detected `[` vs `]`.")
        if code.count("{") != code.count("}"):
            issues.append("Unbalanced curly braces detected `{` vs `}`.")
        if not code.strip():
            issues.append("No code submitted yet.")

        if not issues:
            issues.append(
                "No static syntax or unbalanced bracket issues found. Try running edge-case inputs to catch logic bugs."
            )

        return "### 🐛 Bug Detection Report\n\n" + "\n".join(f"- {issue}" for issue in issues)

    def _local_complexity(self, payload: MentorCodeRequest) -> str:
        code = payload.code
        loop_count = sum(
            1 for line in code.splitlines() if any(token in line for token in ("for ", "while "))
        )
        if loop_count == 0:
            time_est = "O(1) constant time (or O(N) depending on built-in library methods)"
        elif loop_count == 1:
            time_est = "O(N) linear time for a single pass over input size N"
        elif loop_count == 2:
            time_est = "O(N^2) quadratic time (nested loops over input size N)"
        else:
            time_est = f"O(N^{loop_count}) polynomial time due to {loop_count} nested loop levels"

        has_map = any(
            kw in code
            for kw in (
                "dict()",
                "set()",
                "HashMap",
                "HashSet",
                "unordered_map",
                "unordered_set",
                "{}",
            )
        )
        space_est = (
            "O(N) linear space (allocating extra map/set/array storage)"
            if has_map
            else "O(1) auxiliary space"
        )

        return (
            f"### ⏱️ Complexity Analysis\n\n"
            f"- **Estimated Time Complexity:** `{time_est}`\n"
            f"- **Estimated Space Complexity:** `{space_est}`\n\n"
            f"> *Tip: To improve O(N^2) to O(N), replace nested lookup loops with a Hash Map or Hash Set.*"
        )

    def _local_optimization(self, payload: MentorCodeRequest) -> str:
        code = payload.code
        suggestions: list[str] = []
        loop_count = sum(
            1 for line in code.splitlines() if any(token in line for token in ("for ", "while "))
        )

        if not code.strip():
            suggestions.append("Write a first working solution before optimizing.")
        if loop_count >= 2:
            suggestions.append(
                "Replace nested loops with a **Hash Map / Dictionary** or **Two Pointers** to reduce complexity from O(N^2) to O(N)."
            )
        if payload.language == "python" and ".count(" in code:
            suggestions.append(
                "`list.count()` inside a loop runs in O(N^2). Precompute frequencies using `collections.Counter`."
            )
        if (
            payload.language == "python"
            and " in " in code
            and "set(" not in code
            and "dict" not in code
        ):
            suggestions.append(
                "Checking membership `x in list` takes O(N). Convert candidate collections to a `set` for O(1) average lookup."
            )
        if "sort(" in code or ".sort" in code:
            suggestions.append(
                "Sorting takes O(N log N). Ensure the sorted order enables Two Pointers or Binary Search."
            )

        suggestions.append(
            "Benchmark execution runtime before and after refactoring bottleneck operations."
        )

        return "Optimization guidance:\n" + "\n".join(f"- {s}" for s in suggestions)


ai_mentor_service = AIMentorService()
