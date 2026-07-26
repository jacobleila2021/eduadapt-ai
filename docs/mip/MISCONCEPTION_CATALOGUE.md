# Mathematics Misconception Catalogue

Pattern-based library in `engines/mathematics_intelligence/misconceptions.py`.  
Detection annotates lessons for tutoring; it does **not** invent new curriculum statements.

| ID | Label | Domain |
|----|-------|--------|
| `math.frac_larger_denominator` | Larger denominator ⇒ larger fraction | arithmetic |
| `math.negative_smaller_absolute` | Larger absolute value ⇒ greater negative | number_systems |
| `math.place_value_digit` | Digit treated without place value | arithmetic |
| `math.algebra_sign_distribution` | Sign errors distributing negatives | algebra |
| `math.equation_balance_oneside` | Operation on one side only | algebra |
| `math.order_operations` | Left-to-right ignoring BODMAS/PEMDAS | arithmetic |
| `math.ratio_vs_fraction` | Ratio conflated with fraction | arithmetic |
| `math.area_vs_perimeter` | Area/perimeter confusion | geometry |
| `math.function_vertical` | Function interpretation / vertical-line | algebra |

Each hit returns:

- `misconception_id`, `label`, `domain`
- `matched_patterns`
- `correction_strategy` (pedagogical guidance)
- `related_concepts` (for linking to ULI concepts when present)
- `confidence`, `provenance`

Extend the catalogue by appending entries to `MATH_MISCONCEPTIONS` with regex patterns that match **learner language or lesson discussion of the error**, not by inventing new syllabus topics.
