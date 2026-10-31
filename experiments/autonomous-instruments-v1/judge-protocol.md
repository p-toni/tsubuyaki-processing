# Judge protocol — JUDGE-1

You are one judge on a panel. You review pairs of short generative animations
and say which one is the better finished study. Work only from the files in this
package. Do not open the repository's experiment archives, decisions, grades, or
any `sealed` directory, and do not read other judges' files.

## Evidence

`items.json` lists the items in the order to judge them. Each item has two
animations, **A** and **B**. Each animation has:

- `contact`: sixteen stills in reading order, evenly spaced across about eleven
  seconds of a twelve-second animation on a 400 × 400 canvas;
- `motion` (if present): the same sixteen moments, showing where the image
  changes over the next tenth of a second. Brighter means more movement.

## Question

Which animation is the better finished study of a mathematical organic form?
Weigh coherence of the form, material and density, composition and framing, and
how the motion develops over time. Answer `A`, `B`, or `equal`. Use `equal` only
when you cannot name a difference that matters.

Judge each item on its own. File names, item order and ids carry no information.
Some pairs may look nearly identical; still give your best answer.

## Output

Write one JSON object per line to `judgments/<your-judge-id>.jsonl`:

```json
{"id": "3f2a9c01b7de", "choice": "A", "confidence": 2, "reason": "B's points are sparse and the fold is hard to read"}
```

- `choice`: `A`, `B` or `equal`;
- `confidence`: 1 (guess), 2 (leaning), 3 (clear);
- `reason`: one short sentence naming the deciding difference.

Commit your file before anyone opens the sealed key. Do not revise a judgment
after committing it.
