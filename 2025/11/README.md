# November 2025 Ponder This Challenge
The [November challenge](https://research.ibm.com/haifa/ponderthis/challenges/November2025.html) involves extracting substrings from recursively generated strings.

## Challenges

The main challenge defines a recursively generated sequence of strings $s_0, s_1, s_2, \ldots$, with $s_0$ = 'CAT'. String $s_n$ is derived from string $s_{n-1}$ by the following substitution rules:

- G -> T
- T -> CA
- C -> TG
- A -> C

The challenge asks for the substring $s_n[n..(n+1000)]$ for $n = 10^{100}$.

The bonus challenge asks for the substring $t_n[n..(n+1000)]$ for $n = 10^{100}$ where $t_0$ = 'RABBITS' and string $t_n$ is derived from string $t_{n-1}$ with the substitution rules:

- G -> T
- T -> CA
- C -> BR
- A -> I
- R -> B
- B -> IS
- I -> TG
- S -> C

## Solution

The solution is implemented in Python

Usage:

```console
    $ python nov2025.py
```

The script will compute and output the answers to both challenges.

## Discussion

Iterating over $0 \le n \le 10^{100}$ for $s_{n}$ or $t_{n}$ would not be feasible in reasonable time, nor would it be practical to store the intermediate strings or portions thereof.  Fortunately, the behavior of the strings for both the main and bonus challenges reveal patterns that can be used to infer the challenge answers.

The equations below deal with string terms like $a_{n}$. For these terms, $+$ denotes concatenation and string length is denoted as $\lvert a_{n} \rvert$.

### Main challenge

Take string $s_{n}$ as a sequence of string segments based on the starting string $s_{0}$ = 'CAT'

$$s_n = a_{n} + b_{n} + c_{n}$$

where $a_{0}$ = 'C', $b_{0}$ = 'A' and $c_{0}$ = 'T'. 

The iterations of $s$ can be thought of as performing substitutions on each segment independently. After examining these segments for small $n$, some recurrence relations between segments can be observed as they evolve according to the substitution rules. Note that any observed recurrences could be used to solve this problem. As long as they are verified to hold true over several iterations, the recurrences are a consequence of the substitution rules and will necessarily continue to hold true for all further $n$. For this solution, the following recurrence relations for $n \ge 2$ are used.

$$a_{n} = a_{n-2} + b_{n-2} + c_{n-2}$$
$$b_{n} = a_{n-1}$$
$$c_{n} = a_{n-1} + b_{n-1}$$

Importantly, this means that the $a$ term of a given $s_n$ will appear at the beginnning of every subsequent second string. In fact the entirety of $s_n$ will appear at the beginning of every subsequent second string, although this solution doesn't explicitly make use of that relation.

A list of string segments can be constructed for low $n$ using the substitution rules and stored in a lookup table. Using the recurrence relations, the lengths of subsequent string segments can be determined arithmetically without having to construct the full strings directly.

$$\lvert a_{n} \rvert = \lvert a_{n-2} \rvert + \lvert b_{n-2} \rvert + \lvert c_{n-2} \rvert$$
$$\lvert b_{n} \rvert = \lvert a_{n-1} \rvert$$
$$\lvert c_{n} \rvert = \lvert a_{n-1} \rvert + \lvert b_{n-1} \rvert$$

The segment lengths expand rapidly as $n$ increases, and an iteration can be quickly found where the length of the $a$ term exceeds the ending index of the answer substring: $\lvert a_{480} \rvert \approx 2.41 \times 10^{100} > 10^{100} + 1000$. Since $a_n$ will appear at the beginnning of every second subsequent string, and since $480 \equiv 10^{100} \pmod 2$, this means that $s_{10^{100}}$ must also begin with $a_{480}$. Therefore the answer substring is found entirely within this segment.

Using the recurrence relations for the segments of $s_{n}$, it is then possible to produce repeated symbolic expansions of $a_{480}$ into segments of lower $n$. Keeping track of string lengths and starting and stopping indexes of the challenge answer substring, any terms of the expansion that do not overlap the intended substring can be discarded and eventually the expansion reaches a level where all the terms have previously been directly calculated as actual strings in the lookup table. The challenge answer can then be constructed from these terms.

### Bonus challenge

Similar to the main challenge, $t_n$ can be divided into segments based on the starting string $t_{0}$ = 'RABBITS'

$$t_n = a_{n} + b_{n} + c_{n} + c_{n} + d_{n} + e_{n} + f_{n}$$

where $a_{0}$ = 'R', $b_{0}$ = 'A', $c_{0}$ = 'B', $d_{0}$ = 'I', $e_{0}$ = 'T', $f_{0}$ = 'S'. Note that term $c$ appears twice. Both copies will evolve identically with the substitution rules, which means calculations only need to be performed for one of them.

Recurrence relations between these terms can be observed as with the main challenge, such as the following for $n \ge 2$.

$$a_{n} = c_{n-1}$$
$$b_{n} = d_{n-1}$$
$$c_{n} = d_{n-1} + f_{n-1}$$
$$d_{n} = e_{n-1} + e_{n-2}$$
$$e_{n} = a_{n-1} + a_{n-2} + b_{n-1}$$
$$f_{n} = a_{n-1} + a_{n-2}$$

Via substitution, $a_{n}$ and $b_{n}$ can be written entirely in terms of each other for $n \ge 6$.

$$a_{n} = a_{n-4} + a_{n-5} + b_{n-4} + a_{n-5} + a_{n-6} + b_{n-5} + a_{n-3} + a_{n-4}$$

$$b_{n} = a_{n-3} + a_{n-4} + b_{n-3} + a_{n-4} + a_{n-5} + b_{n-4}$$

This shows that the $a$ term of a given $t_{n}$ will always be reproduced at the beginning of every subsequent fourth string.

As with the main challenge, an initial set of actual string segments for low $n$ can be computed and stored in a lookup table. Lengths of subsequent segments can be calculated based on the recurrences until $n = 480$ is reached with $\lvert a_{480} \rvert  \approx 1.49 \times 10^{100} > 10^{100} + 1000$. Since $480 \equiv 10^{100} \pmod 4$, it follows that $a_{480}$ will appear at the beginning of $t_{10^{100}}$, and so a similar recursive expansion of terms can be performed until the answer substring can be constructed from segments that have been directly computed.