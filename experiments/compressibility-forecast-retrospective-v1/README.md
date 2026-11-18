# Mechanical compression after visual selection

Once a readable p5 sketch has been selected on its motion, this optional command produces a complete compact draft, hashtag included. Count it as an attempt when the brief limits attempts. Run the existing character checker on the draft and compare its behavior with the selected sketch before delivery.

From this directory, this example makes a 234-weighted-character draft of Fronds from the pilot's selected sketch. The pilot originally delivered its own 212-weighted-character version.

```sh
source_file=../autonomous-discovery-pilot-v1/B02/v2.js
output_dir=$(mktemp -d)
node mechanical-post.mjs "$source_file" > "$output_dir/post.txt" &&
  node ../../scripts/check-length.mjs "$output_dir/post.txt" &&
  node ../compact-preflight-v1/audit-source.mjs "$source_file" "$output_dir/post.txt" "$output_dir/audit.json"
```

The command uses the token rewrites contributed in PR #143 for arithmetic sketches in p5 global mode. It shortens numeric literals and local names, drops declarations, and compiles the draft before printing it. Removing declarations can change scope and behavior. Code that relies on automatic semicolon insertion can fail to compress. The checker reports the exact length of this draft. Further hand edits can still save characters. [Original implementation](https://github.com/p-toni/tsubuyaki-processing/blob/6927be1156a198971f0ef05e63339aa07b762d50/experiments/compressibility-forecast-retrospective-v1/forecast-length.mjs)

## What the archive shows

Across the pilot, rendered-feedback, and compact-preflight studies, 18 distinct readable sources received compact attempts. **Eight fit both 280-character limits after mechanical compression alone.** All 18 drafts matched their readable sources at every indexed point and stroke over 720 frames. These measurements apply to those sketches. Artistic quality and success on a fresh brief still require direct observation. The original per-attempt records also include manual compression and failed attempts. [Source paths, weighted counts, and SHA-256 hashes](october-posts.tsv) · [Original retrospective data](https://github.com/p-toni/tsubuyaki-processing/blob/6927be1156a198971f0ef05e63339aa07b762d50/experiments/compressibility-forecast-retrospective-v1/results.json)

One in-budget draft, F06, recycles points across a 400-pixel screen. The compact-preflight auditor reports that crossing as a jump. The original F06 protocol measures displacement across the wrap. Its auditor recorded 2,744 crossings, a maximum step of 1.34 pixels, and a pass. The two versions agreed point for point under both measurements. [F06 protocol](../feedback-value-v1/protocol.md)

Pleated lantern illustrates the cost of rejecting a sketch on this count. Its mechanical draft reached 306 weighted characters. The manually compressed post fit at 280 with every rendered frame intact. [Pleated lantern](../pleated-lantern-v1/README.md)

Run `node --test test.mjs` here to regenerate all 18 posts from the readable sources, compare their bytes with the archived hashes, and count them with the repository checker. The tests also reproduce the lantern's first attempt.
