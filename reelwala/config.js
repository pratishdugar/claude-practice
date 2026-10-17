// Reelwala configuration.
//
// Leave GEMINI_API_KEY as the placeholder to run in DEMO MODE: every AI step is
// simulated on your device, so the whole flow (ideas, plan, voice-over, export) works
// without a key.
//
// To switch on real AI, EITHER:
//   1. paste your key in the app under Settings (stored only in that browser), OR
//   2. put it here — only for a copy you run privately. Never commit a real key
//      to a public repo or deploy it to GitHub Pages: anyone could read it.
//
// Free key: https://aistudio.google.com/apikey
window.REELWALA_CONFIG = {
  GEMINI_API_KEY: "YOUR_GEMINI_API_KEY",
  TEXT_MODEL: "gemini-2.5-flash",
  TTS_MODEL: "gemini-2.5-flash-preview-tts"
};
