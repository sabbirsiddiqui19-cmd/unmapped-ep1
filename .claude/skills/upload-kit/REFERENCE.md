# YouTube upload rules used by the upload-kit skill

Checked: 2026-11-12. Re-check these pages when this date is more than 3 months old, and update the numbers here before building a kit.

## Text fields

| Item | Rule | Source |
|---|---|---|
| Title | Up to 100 characters | YouTube Help "Add video info"; YouTube Data API `snippet.title` |
| Description | Up to 5,000 bytes of UTF-8 | YouTube Data API `snippet.description` |
| Angle brackets | `<` and `>` are not allowed in title or description | YouTube Data API videos resource |
| Tags | 500 characters in total; commas count, and a tag with a space is counted as if quoted (+2) | YouTube Data API `snippet.tags[]` |
| Tags weight | Title, thumbnail and description matter more; tags mainly help with commonly misspelled subjects. Excessive tags in the description break spam policy | https://support.google.com/youtube/answer/146402 |
| Hashtags | Up to three can show by the title; more than 60 hashtags on a video and all are ignored; over-tagging can remove a video from search. The older "15" figure is outdated | https://support.google.com/youtube/answer/6390658 |

## YouTube Data API quota

Since the granular quota change announced on 2026-06-01, `search.list` has its own bucket of 100 calls per day, and each call costs 1. Other read methods (`videos.list`, `channels.list`, `playlistItems.list`, `commentThreads.list`) cost 1 unit each from a shared 10,000 units per day. The older rule that a search costs 100 units no longer applies.

Sources: https://developers.google.com/youtube/v3/determine_quota_cost (last updated 2026-11-10) and https://developers.google.com/youtube/data/revision_history

## Chapters

First timestamp `00:00`, at least three timestamps in ascending order, each chapter at least 10 seconds. Manual chapters override automatic chapters. Not available on channels with active strikes or on content that may be inappropriate for some viewers.
Source: https://support.google.com/youtube/answer/9884579

## Thumbnails

- Recommended 3840×2160, minimum width 640, 16:9 for regular videos.
- Formats such as JPG, GIF, PNG.
- File limit 2 MB from a phone, 50 MB from a computer (raised from 2 MB in March 2026).
- A verified account is required. There is a daily custom-thumbnail limit.
- Thumbnails must follow Community Guidelines. Misleading thumbnails break policy.

Source: https://support.google.com/youtube/answer/72431

## Test & Compare

- Up to three titles, three thumbnails, or title-and-thumbnail combinations per video.
- The winner is chosen by watch-time share, not click-through rate.
- Tests usually need one to two weeks.

Source: https://support.google.com/youtube/answer/16391400 and https://support.google.com/youtube/answer/13861714

## End screens

- Last 5 to 20 seconds of the video. The video must be at least 25 seconds long.
- Up to four elements on a 16:9 video.
- Not available on videos set as made for kids.

Source: https://support.google.com/youtube/answer/6388789

## AI use disclosure

The setting is "AI use", under Attributes in the upload flow; it used to be called "Altered content". Disclosure is required for realistic AI content that:

- makes a real person appear to say or do something they didn't
- alters footage of a real event or place
- generates a realistic scene that didn't occur
- creates music that is the main focus

Not required:

- non-realistic or animated content
- minor or aesthetic edits
- AI help with outline, script, thumbnail, title or infographic
- caption creation
- idea generation
- cloning one's own voice

Disclosure alone does not limit audience or monetization. YouTube may label content automatically, for example through its own detection or C2PA metadata. Creators who consistently fail to disclose risk labels being applied, content removal, or YPP suspension.

Source: https://support.google.com/youtube/answer/14328491

## Monetization: inauthentic content

Renamed from "repetitious content" on 2025-07-15. Content that is not allowed to monetize includes:

- mass-produced or repetitive content
- content that looks made from a template with little variation across videos
- content that is easily replicable at scale
- image slideshows or scrolling text with little narrative or educational value

The policy can remove monetization from the whole channel.

Source: https://support.google.com/youtube/answer/1311392

## Audience (made for kids)

Under COPPA, general-audience content (could appeal to everyone, not aimed at children) is set as "not made for kids". Mixed-audience content counts as made for kids. The creator is responsible for the setting, and YouTube may override it in cases of error or abuse.

Source: https://support.google.com/youtube/answer/9528076

## Recommendations

The recommendation system pulls videos for each viewer when they open YouTube. The inputs YouTube names include:

- watch and search history
- subscriptions
- likes and dislikes
- "Not interested" feedback
- satisfaction surveys, which help it measure "satisfaction, not just watch time"

YouTube says no single metric is a good indicator of value on its own.

The practical rules for the kit:

- the title, thumbnail and first description lines make the same promise as the video's first minute
- chapters help viewers navigate
- each episode is written fresh

Sources:

- YouTube Help "How YouTube recommendations work"
- Creator Insider interview with Todd Beaupré, September 2026

## Automatic dubbing

Available to all creators since early 2026, with 27 languages; English videos can be dubbed into about 20 languages. This is a channel-level choice under Settings → Channel → Advanced settings → "Allow automatic dubbing". It can be set to require a manual review of each dub before it is published.
