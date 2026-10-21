---
type: llm
---

The review reports as a finding that `item_count` stores state derivable from `lines`, and proposes computing it from the lines instead, such as a property returning the sum of line quantities, as a snippet or outline. The finding names what that removes: the counter updates in `add`, `remove` and `set_quantity` and the session field, or the stale count for carts saved to the session before this change, which load with `item_count` 0. Its severity is Medium or higher. A fix that keeps the stored field and only recomputes it in `load_cart` does not pass.
