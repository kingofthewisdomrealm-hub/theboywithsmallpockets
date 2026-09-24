# The Boy With the Small Pockets

A parable about capacity: Joe lives in a village where every pocket holds exactly ten gold coins. A glowing map leads him into the Forest of Too-Much, past the Panic Goblin, to a giant future version of himself, and to a chest that holds only a mirror.

> "It was never about more coins. It was about a bigger you."

Written by the author to see his own ceiling: never more than $8,000 in the bank. Within two months of writing it, he broke that number almost 10x.

## What's here

| Path | What it is |
|---|---|
| `PRODUCTION_PACK.md` | Everything: status, art style lock, 23-scene shot list with image prompts, Author's Note, narration split by scene, Suno voice prompt, editor checklist |
| `scenes/` | One image per scene, named `01_joe_intro.png` … `23_closing_title.png` (see shot list) |
| `audio/` | `narration.mp3` from Suno |

## Pipeline

1. Generate each scene image from `PRODUCTION_PACK.md` §3 (style lock + Joe description in every prompt) and save into `scenes/` with the listed filename.
2. Generate narration in Suno with §6 and save to `audio/narration.mp3`.
3. Hand this folder to the editor. §5 maps audio to images by scene number; §7 is the edit checklist.
