"""End-to-end test for Reelwala in demo mode (no API key needed).

Walks the whole flow a creator would: create a project from a template, change its
voice-over language, generate ideas, turn an idea into a reel, upload a photo and a
video, build the AI plan, generate the voice-over, preview, and export a video file.

Run:
    pip install playwright
    python -m playwright install chromium
    python reelwala/tests/e2e_test.py
"""
import asyncio
import pathlib
import sys

from playwright.async_api import async_playwright

APP = (pathlib.Path(__file__).resolve().parent.parent / "index.html").as_uri() + "?demo=1"
OUT = pathlib.Path(__file__).resolve().parent / "artifacts"

# Builds a test photo and a 3-second test video inside the page, then hands both to the
# real file input so the app's own upload handler runs.
MAKE_MEDIA = """async ([sel, copies]) => {
  const c = document.createElement('canvas'); c.width = 1080; c.height = 1350; const x = c.getContext('2d');
  const g = x.createLinearGradient(0, 0, 1080, 1350); g.addColorStop(0, '#2a6'); g.addColorStop(1, '#126');
  x.fillStyle = g; x.fillRect(0, 0, 1080, 1350); x.fillStyle = '#fff'; x.font = '120px sans-serif'; x.fillText('PHOTO', 300, 700);
  const photo = await new Promise(r => c.toBlob(r, 'image/jpeg'));
  const v = document.createElement('canvas'); v.width = 640; v.height = 360; const y = v.getContext('2d');
  const rec = new MediaRecorder(v.captureStream(30), {mimeType: 'video/webm'}); const chunks = [];
  rec.ondataavailable = e => chunks.push(e.data); rec.start();
  let f = 0;
  await new Promise(res => { const iv = setInterval(() => {
    y.fillStyle = 'hsl(' + (f * 4) + ',70%,50%)'; y.fillRect(0, 0, 640, 360);
    y.fillStyle = '#000'; y.font = '60px sans-serif'; y.fillText('CLIP ' + f, 200, 200);
    if (++f > 90) { clearInterval(iv); res(); } }, 33); });
  rec.stop(); await new Promise(r => rec.onstop = r);
  const dt = new DataTransfer();
  for (let i = 0; i < copies; i++) {
    const t = Date.now() - (copies - i) * 86400000;
    dt.items.add(new File([photo], 'photo' + i + '.jpg', {type: 'image/jpeg', lastModified: t}));
    dt.items.add(new File(chunks, 'clip' + i + '.webm', {type: 'video/webm', lastModified: t + 3600000}));
  }
  const input = document.querySelector(sel); input.files = dt.files;
  input.dispatchEvent(new Event('change', {bubbles: true}));
}"""


def step(msg):
    print("  -", msg, flush=True)


async def run():
    OUT.mkdir(exist_ok=True)
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        page = await browser.new_page(viewport={"width": 400, "height": 860})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(APP)
        await page.wait_for_selector("[data-tpl='0']")

        step("create a project from the Sports challenge template")
        await page.click("[data-tpl='0']")
        await page.wait_for_selector("#setupForm")
        await page.select_option("#f_language", "Hindi")
        await page.fill("#f_handle", "@brolympics")
        await page.wait_for_timeout(700)  # autosave debounce
        assert await page.input_value("#f_structure"), "structure should be filled from the preset"

        step("generate ideas")
        await page.click("[data-go='ideas']")
        await page.click("#ideaBtn")
        await page.wait_for_selector(".idea", timeout=10000)
        n_ideas = await page.locator(".idea").count()
        assert n_ideas == 5, f"expected 5 ideas, got {n_ideas}"

        step("turn the first idea into a reel")
        await page.locator("[data-act='use-idea']").first.click()
        await page.wait_for_selector("#storyIn")
        assert "Using a saved idea" in await page.inner_text("#createBox")
        await page.fill("#storyIn", "Badminton week. Rohan was two points down. He smashed three in a row. He won 21-19. I lost my shoe mid-rally.")

        step("upload a photo and a video")
        await page.evaluate(MAKE_MEDIA, ["#fileIn", 1])
        await page.wait_for_function("document.querySelectorAll('#mediaGrid .mi').length === 2", timeout=15000)

        step("build the edit plan")
        await page.click("[data-act='plan']")
        await page.wait_for_selector("#sceneList .scene", timeout=30000)
        n_scenes = await page.locator("#sceneList .scene").count()
        assert n_scenes >= 2, f"expected at least 2 scenes, got {n_scenes}"
        assert await page.input_value("#hookIn"), "hook should be filled"

        step("generate the voice-over and fit scenes to it")
        await page.click("[data-act='gen-vo']")
        await page.wait_for_selector("#voBody .msg.good", timeout=15000)
        vo = await page.evaluate("S.vo && S.vo.buffer.duration")
        total = await page.evaluate("planTotal()")
        assert vo and vo > 1, "voice-over should have audio"
        assert abs(total - 2.5 - (vo + 0.6)) < 1.0, f"scenes ({total}s) should fit the voice-over ({vo}s)"

        step("preview")
        await page.click("#playBtn")
        await page.wait_for_function("S.renderer && S.renderer.running", timeout=15000)
        await page.wait_for_timeout(1500)
        await page.locator(".screen").first.screenshot(path=str(OUT / "preview.png"))
        await page.click("[data-act='stop']")

        step(f"export the reel (real time, about {total:.0f}s)")
        await page.click("#expBtn")
        await page.wait_for_selector("#expMsg .msg.good", timeout=int((total + 40) * 1000))
        size, kind = await page.evaluate("[S.exportBlob.size, S.exportBlob.type]")
        assert size > 50_000, f"export too small: {size} bytes"
        assert kind in ("video/mp4", "video/webm"), kind
        await page.wait_for_selector("#result video")
        data = await page.evaluate("""async () => { const b = new Uint8Array(await S.exportBlob.arrayBuffer());
            let s = ''; for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000)); return btoa(s); }""")
        import base64
        out_file = OUT / ("reel." + ("mp4" if "mp4" in kind else "webm"))
        out_file.write_bytes(base64.b64decode(data))

        step("projects and ideas survive a reload")
        await page.reload()
        await page.wait_for_selector(".pcard")
        assert await page.locator(".pcard").count() == 1
        await page.click("[data-go='ideas']")
        assert await page.locator(".idea").count() == 5

        step("series: upload a whole trip and plan 3 reels")
        await page.click("[data-go='series']")
        await page.fill("#bName", "Cebu trip")
        await page.fill("#bStory", "Six days in Cebu. Whale sharks at Oslob. Canyoneering at Kawasan. Street food in the city.")
        await page.evaluate(MAKE_MEDIA, ["#bFiles", 3])
        await page.wait_for_function("S.bnew.length === 6", timeout=30000)
        await page.select_option("#bCount", "3")
        await page.select_option("#bFreq", "daily")
        await page.click("#bPlanBtn")
        await page.wait_for_selector(".reel", timeout=60000)
        assert await page.locator(".reel").count() == 3, "expected 3 reels"
        dates = await page.evaluate("curBatch().reels.map(r => r.date)")
        assert len(set(dates)) == 3 and dates == sorted(dates), f"posting dates should be consecutive days: {dates}"

        step("series: download the posting calendar")
        async with page.expect_download() as dl:
            await page.click("[data-act='ics']")
        ics_path = OUT / "posting-plan.ics"
        await (await dl.value).save_as(str(ics_path))
        ics = ics_path.read_text()
        assert ics.count("BEGIN:VEVENT") == 3 and "VALARM" in ics, "calendar should have 3 events with reminders"

        step("series: make all reels in one go")
        await page.click("[data-act='make-all']")
        await page.wait_for_function("Object.keys(S.bOut).length === 3 && !S.queue", timeout=300000)
        assert not await page.evaluate("curBatch().queueErr"), await page.evaluate("curBatch().queueErr")
        statuses = await page.evaluate("curBatch().reels.map(r => r.status)")
        assert statuses == ["made"] * 3, statuses
        sizes = await page.evaluate("Object.values(S.bOut).map(o => o.blob.size)")
        assert all(sz > 50_000 for sz in sizes), sizes
        assert await page.locator(".reel video").count() == 3

        step("series: open part 2 in the editor and mark part 1 posted")
        await page.locator("[data-act='open-reel']").nth(1).click()
        await page.wait_for_selector("#sceneList .scene")
        assert "part 2 of 3" in (await page.inner_text("#createBox")).lower()
        await page.click("[data-act='back-series']")
        await page.click("#posted0")
        await page.wait_for_timeout(300)
        await page.reload()
        await page.click("[data-go='series']")
        await page.click("[data-act='open-batch']")
        statuses = await page.evaluate("curBatch().reels.map(r => r.status)")
        assert statuses == ["posted", "made", "made"], statuses
        assert "aren't loaded on this device" in await page.inner_text("#seriesBox"), "should ask to re-select files after reload"

        await browser.close()
    real_errors = [e for e in errors if "net::" not in e]
    assert not real_errors, f"page errors: {real_errors}"
    print(f"PASS: exported {kind}, {size/1048576:.1f} MB -> {out_file}; series of 3 reels made and scheduled")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
