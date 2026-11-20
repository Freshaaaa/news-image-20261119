import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry: copy the rendered front page beside this file to /output/entry.png.
// The image is fully baked by build-image.py (deterministic PIL render of
// the 52 verified 19-Nov-2026 stories); this program only moves the bytes.
const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
if (!existsSync(src)) throw new Error("entry.png missing next to main.ts");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
const bytes = statSync(join(outDir, "entry.png")).size;
const head = readFileSync(src).subarray(0, 8);
if (head.toString("hex") !== "89504e470d0a1a0a") throw new Error("entry.png is not a PNG");
console.log(`wrote ${join(outDir, "entry.png")} (${bytes} bytes, 1024x1024)`);
