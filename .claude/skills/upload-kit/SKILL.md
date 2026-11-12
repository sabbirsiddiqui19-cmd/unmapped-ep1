---
name: upload-kit
description: Build and validate the YouTube upload kit for a finished The Unmapped Page episode (search research, title and thumbnail variants, description with chapters, tags, captions, pinned comment, settings sheet, promo). Use after the final render passes QA and before anything goes to YouTube.
---

# Upload kit for a finished episode

Run this after `BUILD_REPORT.md` for the episode exists and its QA passed. The kit is everything the owner needs to fill YouTube Studio by copy and paste, with no guessing at upload time.

`PUBLISH = NO` applies here as everywhere: never upload, schedule, publish, or change any channel or video setting. Finished episodes and their kits are read-only; build the new kit in its own folder.

The limits and policies this skill relies on are in `REFERENCE.md` next to this file, with sources and the date they were checked. If that date is more than 3 months old, re-check the listed help pages before building and update `REFERENCE.md` first.

## Inputs to read before writing anything

- The final mp4 for the episode. Get the exact duration with `ffprobe`; every timing in the kit comes from this file, never from script estimates.
- The voice-synced SRT used in the render.
- The final narration script.
- The research folder `episodes/EPn/research/` made by the `topic-research` skill. It holds `demand.md`, the `yt/` and `trends/` folders, `sources.csv`, `claims.csv` and `assets.csv`. Facts, sources and asset licenses come from these files only.
- Every earlier kit under `episodes/EP*/upload_kit/` (or the older `*Publish_Kit*` folders). They are used for the variety check, for end-screen and card targets, and for the playlist name.
- `REFERENCE.md` in this folder.

## Output

Write to `episodes/EPn/upload_kit/`:

| File | Content | Language |
|---|---|---|
| `00_START_HERE.md` | File table, where each one goes in Studio, open warnings | Bengali |
| `00_THUMBNAIL_A.jpg`, `_B.jpg`, `_C.jpg` | Main thumbnail plus two test variants | — |
| `01_TITLE.txt` | Title to set at upload (same as variant A) | English |
| `01_TITLE_VARIANTS.txt` | Three titles, one per line, A first | English |
| `02_DESCRIPTION.txt` | Full description | English |
| `03_TAGS.txt` | Comma-separated tags | English |
| `04_PINNED_COMMENT.txt` | Comment to post and pin after publishing | English |
| `05_CAPTIONS_English.srt` | Voice-synced captions | English |
| `06_UPLOAD_SETTINGS.md` | Every Studio setting in Studio order | Bengali |
| `07_CREDITS_AND_LICENSES.md` | Proof of rights for every third-party asset | Bengali + English credit lines |
| `08_BUILD_REPORT.md` | Copy of the episode's build report | as is |
| `09_SEO_RESEARCH.md` | Search and competitor research behind the title, tags and description | Bengali |
| `10_PROMO.md` | Short cut-down plan and a community post draft | Bengali notes, English copy |
| `11_CHECK_REPORT.txt` | Output of `check_kit.py` | — |

Owner-facing notes are in Bengali; anything viewers see is in English.

## Step 1. Search and audience research → `09_SEO_RESEARCH.md`

The demand research was already done by the `topic-research` skill. Reuse it and do not repeat it.

1. Read `episodes/EPn/research/demand.md`, the `yt/summary.md` and `yt/requests.md` it points to, and `trends/summary.md` if one exists.
2. If the final script's angle differs from the researched terms, run one extra check, using 2 to 4 `search.list` calls from the 100-per-day search bucket:

   ```
   python3 .claude/skills/topic-research/scripts/yt_demand.py --terms "<title phrase>" --regions US GB --out episodes/EPn/research/yt_title/
   ```
3. In `09_SEO_RESEARCH.md`, write:
   - the words US and UK viewers use for this subject, taken from the top results and from Trends
   - which angles the existing videos already cover
   - what this episode shows that they do not
4. Pick one primary phrase (what a curious person would type), two to four secondary phrases, and any alternate spellings or common misspellings of names (for EP3 these would be things like "Poyas" or "McGregor").
5. Give each choice a figure from those files, with its region. Never write a demand number without its source file.
6. Never copy a competitor's title wording or thumbnail layout.

## Step 2. Titles → `01_TITLE.txt` and `01_TITLE_VARIANTS.txt`

- Hard limit 100 characters. Aim for 60 or fewer so the whole title shows on phones (this cut-off is approximate and measured by third parties).
- Put the subject's name or the primary phrase early when it reads naturally.
- Promise only what the first minute of the video delivers. Test & Compare picks its winner by watch-time share, and misleading titles break YouTube's metadata policy, so a title that over-promises loses both ways.
- The three variants must test different angles (for example: the mystery, the number, the question). Swapping one word is not a test.
- No hashtags in the title, no all-caps sentences, no `<` or `>`.

## Step 3. Thumbnails → `00_THUMBNAIL_A/B/C.jpg`

- Render each from a Remotion `<Still>` (or from the episode's real hero asset) at 3840×2160, 16:9, saved as JPG. YouTube's help page recommends 3840×2160 with a minimum width of 640.
- File limit is 50 MB from a computer and 2 MB from a phone. If A is over 2 MB, also export `00_THUMBNAIL_A_mobile.jpg` at 1280×720 under 2 MB.
- It must stay readable at small size: one focal object, at most four words of text, strong contrast. Downscale a copy to 320×180, open it with Read, and fix anything that cannot be read.
- B and C change something real (a different focal object, or different text) and are meant to pair with title variants B and C.
- Show only things that appear in the video, and only assets whose license in `07` allows it. No AI-made face of a real person.

## Step 4. Description → `02_DESCRIPTION.txt`

Write the parts in this order:

1. **Opening two lines** (about the first 150 characters, which show before "more"). Restate the title's promise in plain words and include the primary phrase naturally.
2. **Summary**, two to four sentences on what the video covers, using secondary phrases only where they read naturally. Never a keyword list.
3. **One question** for the comments, specific to this episode.
4. **CHAPTERS**, timed from the final mp4:
   - first line `00:00 <title>`
   - at least three chapters, in ascending order
   - every chapter at least 10 seconds long, including the last one measured against the real duration
   - short, descriptive chapter names
5. **SOURCES**, taken from the T1 to T3 rows of `research/sources.csv`, each with its title and URL. Never list a T4 source (such as Wikipedia) as a source.
6. **CREDITS**, one line per row of `research/assets.csv`, using its `credit_line`. CC BY and CC BY-SA assets need the attribution exactly as recorded.

Every fact in the opening, the summary and the pinned comment must come from a VERIFIED or CONTESTED row of `research/claims.csv`.
7. **Production note**, only if the owner chose to add one (for example "Narration: synthetic voice.").
8. **Three hashtags** on the last line. YouTube shows up to three above the title and ignores every hashtag on a video that has more than 60. Never use more than five.

Limits: at most 5,000 bytes of UTF-8, and no `<` or `>` anywhere.

Write the opening, summary and question fresh for every episode. YouTube's inauthentic content policy removes monetization from channels whose videos look templated or mass-produced with little variation. `check_kit.py` compares this prose with earlier kits and warns when it is too similar.

## Step 5. Tags → `03_TAGS.txt`

YouTube's help page says tags play a minimal role in discovery and mainly help when a subject is often misspelled. Keep the list short and useful:

- 5 to 12 tags: the subject's names, alternate spellings and misspellings, the primary phrase, and one series tag (`the unmapped page`).
- The total budget is 500 characters, counted the API way: commas between tags count, and every tag that contains a space costs 2 extra characters. Aim for 400 or fewer.

## Step 6. Pinned comment → `04_PINNED_COMMENT.txt`

One extra fact or source that is not in the video, then one specific question. Keep it under about 500 characters, with no links other than sources.

## Step 7. Captions → `05_CAPTIONS_English.srt`

Copy the voice-synced SRT that the render used. Never use the script-estimated SRT. The checker validates numbering, timing order, overlaps, and that the last cue ends before the video does.

## Step 8. Settings sheet → `06_UPLOAD_SETTINGS.md`

Write it in Bengali and in Studio's order. Mark each item ✅ (copy from a kit file) or 🟡 (owner decides; give a recommendation and the reason).

- **Details:** title, description, thumbnail, playlist, audience, age restriction.
  - For audience, recommend "No, it's not made for kids" for general-audience history. This is a legal call under COPPA, so mark it 🟡.
- **Show more / Attributes:**
  - AI use (apply the rule below)
  - paid promotion
  - tags
  - video language English, caption certification
  - recording date and location
  - license (Standard YouTube License)
  - allow embedding, publish to subscriptions feed
  - category Education
  - comments
- **Video elements:**
  - Subtitles: upload `05` with "With timing".
  - End screen: the video must be at least 25 seconds long, the end screen sits in the last 5 to 20 seconds, and a 16:9 video can have up to four elements. Give the exact start time, calculated from the real duration and the end card's start in the render. Recommend one video (an earlier episode or "best for viewer"), one playlist, and a subscribe element, placed over empty parts of the end card.
  - Cards: optional. If used, give the exact timestamp and the target episode.
- **Checks** and **Visibility:** visibility is owner-only.
- **After publishing:**
  - post and pin `04`
  - set up Test & Compare with titles A/B/C and thumbnails A/B/C, if Studio offers it on this channel
  - post the community post from `10`, about 24 hours later
- **Technical table:** codec, resolution, fps, exact duration and file size from `ffprobe`, and loudness from the build report.

Channel-level settings, such as automatic dubbing (Settings → Channel → Advanced settings), are decided once by the owner. Mention them only if they have not been decided yet.

### Rule for the AI use setting

This rule comes from YouTube's "Disclosing the use of GenAI content" help page (see `REFERENCE.md`).

- **Disclosure required** for realistic content that:
  - makes a real person appear to say or do something they did not
  - alters footage of a real event or place
  - generates a realistic scene that did not happen
  - has AI music as the main focus
- **Not required** for:
  - AI help with the outline, script, title, thumbnail or infographics
  - caption creation
  - clearly non-realistic or animated visuals (maps, doodles, motion graphics)
  - colour and filter effects
  - cloning one's own voice
- A stock TTS voice that does not imitate a real person reading an original script is not on YouTube's "must disclose" list.
- If any shot is a photorealistic AI-generated scene of a real historical person, place or event, recommend **Yes**.
- YouTube states that disclosure alone does not limit a video's audience or its eligibility to earn money, so recommend **Yes** when in doubt.
- In `06`, list each AI-made element of the episode with its reasoning, so the owner can decide quickly.

## Step 9. Credits and build report → `07`, `08`

Build `07` from `research/assets.csv`. It lists every third-party asset: what it is, its source URL, author, license, the date the license was checked, and the credit line used in the description. Any asset that is used in the render but missing from `assets.csv` is a FAIL. Stop and ask the owner about it; never guess a license. Copy `08` from the episode build unchanged.

## Step 10. Promo → `10_PROMO.md`

- A vertical Short cut-down plan: which segment (with timecodes from the final mp4), the opening line, on-screen text, and which long video it points to.
- A community post draft for about 24 hours after publishing: one image idea, two or three lines, and a poll or question.

## Step 11. Start here → `00_START_HERE.md`

Write this in Bengali. It holds a table of every file and where it goes in Studio, then any warnings from the checker that the owner should know about.

## Step 12. Validate

Run:

```
python3 .claude/skills/upload-kit/check_kit.py episodes/EPn/upload_kit \
  --video <final mp4> \
  --previous episodes/EP*/upload_kit \
  --out episodes/EPn/upload_kit/11_CHECK_REPORT.txt
```

Then check every number in the viewer-facing text against the claim ledger:

```
python3 .claude/skills/topic-research/scripts/check_claims.py episodes/EPn/research \
  --text episodes/EPn/upload_kit/01_TITLE_VARIANTS.txt episodes/EPn/upload_kit/02_DESCRIPTION.txt \
         episodes/EPn/upload_kit/04_PINNED_COMMENT.txt \
  >> episodes/EPn/upload_kit/11_CHECK_REPORT.txt
```

Fix every FAIL from either check and run both again until each exits 0. Explain each remaining WARN in `00_START_HERE.md`.

Then stop and report to the owner what the kit holds and which 🟡 decisions are theirs. Do not touch YouTube.
