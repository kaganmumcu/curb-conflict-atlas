# Scene Annotation Guide

This guide defines the human-reviewed layer planned for the next release. It is intentionally separate from the synopsis heuristics used in version 1.

## Unit of analysis

One row represents one distinct social conflict within an episode. A new row begins when the disputed rule, main target, or setting changes materially.

## Required fields

| Field | Definition |
| --- | --- |
| `episode_code` | Canonical episode key such as `S08E03` |
| `scene_id` | Stable within-episode identifier such as `S08E03-C01` |
| `rule_category` | One category from `data/rule_taxonomy.csv` |
| `rule_description` | Short natural-language description of the disputed norm |
| `initiator` | Character who first turns the issue into an explicit dispute |
| `target` | Main person or group challenged by the initiator |
| `escalation_steps` | Count of material increases in stakes, from 0 upward |
| `larry_position` | `right`, `wrong`, `technically_right_socially_wrong`, `mixed`, or `not_applicable` |
| `larry_vindicated` | `yes`, `no`, `partial`, or `not_applicable` |
| `callback_present` | `yes` when the conflict or its consequence returns later in the episode |
| `source_url` | Link used by the annotator to verify the scene |
| `annotator_notes` | Brief rationale; do not paste long copyrighted dialogue |

## Consistency rules

1. Annotate what happens on screen, not what a character claims happened.
2. Use `technically_right_socially_wrong` only when the rule claim is defensible but the response violates a separate social norm.
3. Count an escalation only when stakes, audience, consequence, or hostility materially increases.
4. A callback must occur after the original conflict has apparently ended.
5. Do not copy full dialogue or complete scene transcripts into the dataset.

## Quality plan

- Double-annotate a pilot sample of 10 episodes.
- Reconcile disagreements and revise definitions before scaling.
- Report agreement for categorical fields and absolute differences for `escalation_steps`.
- Keep raw annotations separate from adjudicated labels.

