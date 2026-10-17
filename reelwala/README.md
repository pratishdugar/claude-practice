# Reelwala

A free, AI-powered Instagram Reel and Story maker that runs entirely in the browser.

Upload your clips and photos, type a few lines about what happened, and Reelwala:

1. watches frames from every clip and picks the best moments,
2. writes on-screen captions and a voice-over script in your project's language and tone,
3. generates the voice-over (30 AI voices) or lets you record or upload your own,
4. cuts everything to vertical 9:16 with word-by-word captions, a hook title, music and an end card,
5. exports an MP4 you can share straight to Instagram, plus a ready post caption and hashtags.

There is no server and no build step. Video editing happens on your device; only small preview frames and text go to the AI.

## Features

| Area | What you get |
|---|---|
| **Projects** | One per series. Saves format (Reel/Story, 15–90 s), pacing, story structure, tone, "always remember" rules, voice-over, caption look, transitions, handle and end card, so every reel stays consistent. Templates: Sports challenge, Travel diary, Food review, Day in my life, Blank. |
| **Ideas** | 5 ideas at a time that follow the project's structure, each with a hook, story beats, shot list, draft voice-over and post caption. Star, delete, or tap **Make this reel**. |
| **Create** | Upload media → story (with **Expand with AI**) → AI edit plan you can change scene by scene → voice-over → music → preview with Instagram safe zones → export. |
| **Voice-over** | AI voice (Gemini TTS, 30 voices, 18 languages incl. Hindi and Hinglish, delivery style, pace), record your own voice, upload audio, or none. Scene lengths auto-fit the narration. |
| **Backup** | Export/import projects and ideas as JSON. |

## Run it

Open `index.html` in Chrome (desktop or Android) or Safari (iPhone). That's it.

Without a key it runs in **demo mode**: ideas, plans and stories are simulated and the voice-over is a placeholder tone, so you can try the full flow end to end.

## Turn on real AI (free)

1. Get a free key at <https://aistudio.google.com/apikey>.
2. In the app, open **Settings**, paste the key and tap **Save and test**. The key is stored only in that browser.

Alternatively, for a private copy only, put the key in `config.js` (`GEMINI_API_KEY`). Don't commit a real key to this public repo or deploy it to Pages — anyone could read it.

`config.js` also sets the default models (`gemini-2.5-flash` for planning, `gemini-2.5-flash-preview-tts` for voice). If Google renames or limits a model, **Settings → Save and test** lists the models your key can use and picks working ones.

## Use it on your phone

Option A — GitHub Pages (recommended):

1. In this repo, go to **Settings → Pages** and set **Source** to **GitHub Actions**.
2. Go to **Actions → Reelwala → Run workflow**, tick **deploy**, and run it.
3. Open the URL it prints (`https://pratishdugar.github.io/claude-practice/`) on your phone and add your key in Settings.

Option B — drag `index.html` and `config.js` onto <https://app.netlify.com/drop> for an instant free link.

## Tests

`tests/e2e_test.py` drives the whole app in a headless browser in demo mode: create a project, change its language, generate ideas, use an idea, upload a photo and a video, build the plan, generate and fit the voice-over, preview, export a video, and reload to check everything was saved.

```bash
pip install playwright
python -m playwright install chromium
python reelwala/tests/e2e_test.py
```

The exported test reel and a preview screenshot land in `tests/artifacts/` (git-ignored). The same test runs in GitHub Actions on every push that touches `reelwala/`.

## Files

```
reelwala/
  index.html        the whole app (UI, renderer, AI calls, storage)
  config.js         API key placeholder and default models
  tests/e2e_test.py end-to-end test
.github/workflows/reelwala.yml   CI test + optional Pages deploy
```

## Limits worth knowing

- **Free tier limits**: Gemini's free tier is rate-limited. If you see "Free limit reached", wait a minute or pick another model in Settings.
- **Free tier data use**: Google may use free-tier requests to improve its products. Don't upload private footage.
- **No generated footage**: the AI edits what you upload; it doesn't create new video.
- **Export is real time**: a 45-second reel takes about 45 seconds. Keep the screen on.
- **Format**: Chrome and Safari export H.264 MP4, which Instagram accepts. Browsers without H.264 recording fall back to another format and the app warns you.
- **Music rights**: use tracks you're allowed to use, or add music inside Instagram after uploading.
- Projects and ideas live in the browser's storage (IndexedDB). Use **Settings → Export backup** to move them between devices.
