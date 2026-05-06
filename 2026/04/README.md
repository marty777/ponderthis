# April 2026 Ponder This Challenge
The [April challenge](https://research.ibm.com/blog/ponder-this-april-2026) involves a difficult-to-read clock.

## Challenges

The challenge describes a 12-hour analog clock with no markings on the dial. The clock has three hands, for hours, minutes and seconds, each of which are of the same length and have no distinguishing features. The hands move continuously rather than in discrete steps.

The time shown on the clock can be deduced using the relative angles between the hands when they are unique to specific moments in time. However, it is not always possible to do this. Some combinations of angles between the hands are produced more than once during a 12-hour period, preventing the displayed time from being deduced.

The main challenge asks for the total number of moments in time that cannot be deduced on the clock in a $43200$ second cycle given $S = 60$ seconds per rotation of the second hand, $M = 60$ rotations of the second hand per rotation of the minute hand, and $H = 12$ rotations of the minute hand per rotation of the hour hand (i.e. how a 12 hour analog clock normally works).

The bonus challenge asks for natural numbers $H,M,S$ where $1 < H \le M \le S$ and $S \cdot M \cdot H = 43200$ such that a clock configured with those ratios of its hands' movements would have the greatest number of moments that cannot be deduced from the position of the clock hands, along with that number of undeducible moments.

## Solution

The solution is implemented in Rust and uses the [Algebraeon library](https://pishleback.github.io/Algebraeon/) for matrix operations with rational terms.

### Usage

```console
$ cargo run --release -- [OPTIONS]
```

or

```console
$ cargo build --release
$ ./target/release/apr2026 [OPTIONS]
```

```console
Options:
  -t, --threads <THREADS>  Set maximum number of worker threads [default: 4]
  -b, --bonus              Calculate bonus challenge solution
  -h, --help               Print help
```

### Examples

Calculate the main challenge answer:

```console
$ cargo build --release
$ ./target/release/apr2026
```

Calculate the bonus challenge answer using 10 worker threads:

```console
$ cargo build --release
$ ./target/release/apr2026 --bonus --threads 10
```

## Discussion

For a given moment $0 \le t < 43200$ measured in seconds, the positions $h,m,s$ of the hour, minute and seconds hands, given as a proportion of a full rotation, can be expressed as fractional parts of $\frac{t}{n}$ with $n$ the number of seconds for a full rotation of the hand. Note that fractional parts of non-negative real numbers can be expanded into expressions involving floored values as $\lbrace x\rbrace = x - \lfloor x\rfloor$.

$$s = \left \lbrace \frac{t}{S} \right \rbrace = \frac{t}{S} - \left \lfloor \frac{t}{S} \right \rfloor$$
$$m = \left \lbrace\frac{t}{MS} \right \rbrace = \frac{t}{MS} - \left\lfloor\frac{t}{MS}\right\rfloor$$
$$h = \left \lbrace \frac{t}{HMS} \right \rbrace = \frac{t}{HMS} - \left\lfloor\frac{t}{HMS}\right\rfloor$$

Because of the lack of reference markings on the dial of the clock, the angles between the hands at a given moment would be indistinguishable from the angles at a different moment during the 12-hour period if the positions of the hands of the two moments were equivalent after a rotation around the face of the clock. If the hand positions of two moments were only equivalent after a reflection and rotation, it would be possible to distinguish between them.

Thus for a given pair of mutually indistinguishable moments $t_1, t_2$, there must be some value $C \not \equiv 0$ such that the positions of the hands of the clock at $t_1$ are equivalent to those at $t_2$, rotated around the face by $C$. Because the clock hands have identical appearances, the relative angles of hands $(s_1, m_1, h_1)$ and $(s_2, m_2, h_2)$  for moments $t_1$ and $t_2$ could be equivalent under rotation between any pairing of hour, minute and second hands, so each of those pairings must be covered. For example, for the pairing $s_1 = m_2 + C, m_1 = h_2 + C, h_1 = s_2 + C$ we would have equations like the following:

$$s_1 = m_2 + C$$
$$\frac{t_1}{S} - \left\lfloor\frac{t_1}{S}\right\rfloor = \frac{t_2}{MS} - \left\lfloor\frac{t_2}{MS}\right\rfloor  + C$$

Expanded to all three equations and rearranged:

$$\frac{t_1}{S} - \frac{t_2}{MS} - C =  \left\lfloor\frac{t_1}{S}\right\rfloor - \left\lfloor\frac{t_2}{MS}\right\rfloor$$
$$\frac{t_1}{MS} - \frac{t_2}{HMS} - C =  \left\lfloor\frac{t_1}{MS}\right\rfloor - \left\lfloor\frac{t_2}{HMS}\right\rfloor$$
$$\frac{t_1}{HMS} - \frac{t_2}{S} - C =  \left\lfloor\frac{t_1}{HMS}\right\rfloor - \left\lfloor\frac{t_2}{S}\right\rfloor$$

This gives three equations with three variables $t_1, t_2, C$. While the floored terms are non-linear over $t_1, t_2$, they are definitionally integers and have finite possible values for $0 \le t_1, t_2 < 43200$. If these terms are replaced with fixed integers, the equations form a linear system which can be used to solve for moments which have undeducible hand angles on the clock. Solving the linear systems over all possible integer values for the floor terms and all pairings of hands allows the total set of undeducible moments to be found. Duplicate moments and solutions where $t_1 \equiv t_2$ should be filtered out of the set.

For the bonus challenge, there are 246 distinct combinations of $H,M,S$ that would produce workable clocks. Iterating over each possible clock is relatively fast, and parallelising the workload allows the undeducible moments of all clocks to be found quickly. The clock with the greatest number of undeducible moments overall gives the challenge answer.
