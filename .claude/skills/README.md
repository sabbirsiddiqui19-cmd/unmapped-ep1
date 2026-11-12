# The Unmapped Page — এপিসোড পাইপলাইন

প্রতিটা এপিসোড এই ক্রমে চলে। প্রতিটা ধাপের শেষে Claude Code থামে, আপনি দেখে অনুমতি দিলে পরের ধাপ শুরু হয়।

| ধাপ | কী হয় | কে করে | ফাইল কোথায় যায় |
|---|---|---|---|
| ১. টপিক বাছাই | `/topic-research` লিখলেই Part A নিজে নিজে চলে: ডেটা সংগ্রহ (Chrome দিয়ে Studio Trends ও Google Trends সহ), সেরা ৩টা টপিকের সোর্স যাচাই, স্কোর, তারপর একটা টপিক বেছে দেয় | Claude Code | `episodes/_candidates/<তারিখ>/` |
| ২. আপনার সিদ্ধান্ত | রিপোর্টে লেখা থাকবে "এই টপিকে আগাবেন স্যার: …"; "আগাও" লিখলে Part B শুরু হবে | আপনি | — |
| ৩. গবেষণা | `topic-research` Part B: সোর্স, claim ledger, জায়গার নাম, ছবির লাইসেন্স | Claude Code | `episodes/EPn/research/` |
| ৪. স্ক্রিপ্ট | শুধু ledger-এর VERIFIED/CONTESTED তথ্য দিয়ে লেখা; `check_claims.py` আর `fact-auditor` subagent দিয়ে অডিট | Claude Code | `episodes/EPn/script/` |
| ৫. ভয়েস | TTS দিয়ে `vo.wav` বানিয়ে `episodes/EPn/audio/`-এ রাখা | আপনি | — |
| ৬. বিল্ড ও QA | টাইমস্ট্যাম্প, SRT, Remotion রেন্ডার, `BUILD_REPORT.md` | Claude Code | `episodes/EPn/` |
| ৭. আপলোড কিট | `upload-kit`: টাইটেল/থাম্বনেইল A-B-C, ডেসক্রিপশন, ট্যাগ, সেটিং শিট, চেক | Claude Code | `episodes/EPn/upload_kit/` |
| ৮. আপলোড | YouTube Studio-তে কপি-পেস্ট, 🟡 সিদ্ধান্তগুলো | আপনি | — |
| ৯. ফিডব্যাক | পাবলিশের ২৮ দিন পর পরের `/topic-research` চালানোর সময় Claude Code নিজেই Studio থেকে geography, traffic source আর search terms নামিয়ে সারাংশ বানায় (Part C) | Claude Code | `episodes/EPn/feedback/` |

## ফোন থেকে চালানো (Claude অ্যাপের Code অংশ, cloud session)

1. **Environment বানানো:** ফোনের ব্রাউজারে claude.ai/code খুলুন। মেসেজ বক্সের নিচের environment selector থেকে **New environment** বেছে নিন।
   - **Network access:** **Full** দিন। গবেষণার জন্য Wikipedia, Library of Congress, Internet Archive আর নানা জার্নালের সাইটে ঢুকতে হয়, যেগুলো ডিফল্ট তালিকায় নেই।
   - **Environment variables:** লিখুন `YT_API_KEY=আপনার-key`।
2. **Session শুরু:** Claude অ্যাপের Code অংশে নতুন session খুলে repo `unmapped-ep1` আর ওই environment বেছে নিন। Claude-এর কোনো Project-এর ভেতরে session খুলবেন না, কারণ Project-এর ভেতরের session repo-র skill লোড করে না।
3. **চালানো:** `/topic-research` লিখুন।
4. **সীমা:** ফোনে Chrome-এর সংযোগ নেই। তাই Studio Trends, Google Trends আর Studio থেকে আগের এপিসোডের ফিডব্যাক সংগ্রহ হবে না, রিপোর্টে "যা সংগ্রহ করা যায়নি" অংশে সেটা লেখা থাকবে। YouTube API, কমেন্ট, Reddit আর Wikipedia থেকে ডেটা ঠিকই আসবে।

## কম্পিউটার থেকে চালানো: একবারের সেটআপ

1. **YouTube API key:** Google Cloud Console-এ একটা প্রজেক্ট খুলে **YouTube Data API v3** চালু করুন, তারপর একটা API key বানান (ফ্রি)। Repo-র root-এ `.env` ফাইলে লিখুন `YT_API_KEY=...`, আর `.gitignore`-এ `.env` যোগ করুন।
2. **Chrome:**
   - Chrome-এ **Claude in Chrome** extension বসিয়ে সেই একই Claude অ্যাকাউন্টে লগইন করুন।
   - Claude Code-এ `/chrome` চালিয়ে **Enabled by default** বেছে নিন। Project-এর settings ফাইল নিজে থেকে Chrome চালু করতে পারে না, তাই এটা আপনাকেই একবার করতে হবে।
   - Extension-এর site permission-এ `studio.youtube.com`, `trends.google.com` আর `www.reddit.com`-কে অনুমতি দিন, যাতে প্রতিবার জিজ্ঞেস না করে।
   - Chrome-এ YouTube আর Google-এ আগে থেকে লগইন করা থাকতে হবে।
3. **Python:** Python 3 আর `pip install pillow` লাগবে। `ffprobe` (ffmpeg-এর অংশ) আগে থেকেই আছে।
4. **Permission:** প্রথমবার repo খুললে Claude Code একটা "trust" প্রশ্ন দেখাবে। সেটায় হ্যাঁ দিলে `.claude/settings.json`-এর অনুমতিগুলো চালু হয়। তখন স্ক্রিপ্ট, ওয়েব সার্চ আর Chrome-এর কাজে Claude Code বারবার অনুমতি চাইবে না। `.env` ফাইল Claude পড়তে পারবে না; শুধু স্ক্রিপ্ট key ব্যবহার করে।

## ব্যবহার

- `/topic-research` লিখুন। কোনো বিষয়ের মধ্যে টপিক চাইলে সাথে লিখে দিন, যেমন `/topic-research phantom islands`।
- মাঝে আপনাকে কিছু জিজ্ঞেস করবে না। শুধু Chrome-এ লগইন পেজ বা CAPTCHA এলে থামবে; সেটা আপনি সামলালে আবার চলবে।
- শেষে একটা ছোট রিপোর্ট দেবে: "এই টপিকে আগাবেন স্যার: …", সাথে স্কোর, কারণ, ঝুঁকি আর দ্বিতীয় পছন্দ।
- কোনো টুল কাজ না করলে (Chrome সংযোগ নেই, কোটা শেষ) সেই অংশ বাদ দিয়ে কাজ চালিয়ে যাবে। রিপোর্টে "যা সংগ্রহ করা যায়নি" অংশে সেটা লেখা থাকবে।

## ফ্রি সীমা

- YouTube search দিনে ১০০ বার।
- অন্য সব YouTube কল মিলিয়ে দিনে ১০,০০০ ইউনিট।
- Library of Congress API মিনিটে ২০টা অনুরোধ।

বিস্তারিত দেখুন `topic-research/SOURCES.md`-এ।

নিয়ম বদলাতে চাইলে `MASTER_PROMPT_topic_research.md` সম্পাদনা করে Claude Code-এ দিন।

## পরে যোগ করার আইডিয়া

এগুলো এখনো বানানো হয়নি।

- **ভয়েস স্কিল:** স্ক্রিপ্ট থেকে লোকাল TTS দিয়ে ভয়েস বানাবে, তারপর faster-whisper দিয়ে প্রতিটা শব্দের সময় মিলিয়ে SRT তৈরি করবে।
- **বিল্ড QA-তে "slideshow risk" চেক:** OpenMontage-এর ধারণা থেকে নেওয়া। দেখবে কতক্ষণ ধরে শুধু স্থির ছবি চলছে, ক্যামেরা নড়াচড়া করছে কিনা, আর দৃশ্য কত ঘন ঘন বদলাচ্ছে। YouTube-এর inauthentic content নীতি ধারাবর্ণনা বা শিক্ষামূলক মূল্য কম থাকা স্লাইডশোকে monetization-এর বাইরে রাখে, তাই এটা আগেই ধরা দরকার।

