// Research paper build: `npm run paper` from the repository root.
// Compiles the manuscript docs/paper/main.tex, its supplementary material
// supplementary.tex, and their variants (anonymised copies, separate title
// page, copy without the reference list) with Tectonic, then fails if a TeX or
// BibTeX log reports a problem that affects correctness.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import {
	CACHE,
	IS_WINDOWS,
	ROOT,
	SetupError,
	fail,
	ok,
	repoEnv,
	run,
} from "./lib/workspace.mjs";

const PAPER = path.join(ROOT, "docs", "paper");
const BUNDLED = path.join(ROOT, "docs", "tectonic.exe");
// Each wrapper defines one switch and inputs main.tex or supplementary.tex.
// The manuscript and its supplement read each other's .aux (xr-hyper), so
// each pair builds manuscript, supplement, manuscript, and only the last build
// of a document is checked. The title page stops before the bibliography, so
// it has no BibTeX log.
const BUILDS = [
	{ name: "main", check: false },
	{ name: "supplementary" },
	{ name: "main" },
	{ name: "main-anonymised", check: false },
	{ name: "supplementary-anonymised" },
	{ name: "main-anonymised" },
	{ name: "main-title-page", bibtex: false },
	{ name: "main-no-references" },
];

// Log patterns that mean a wrong or incomplete PDF, not cosmetic chatter.
const PROBLEMS = [
	/^! .*/,
	/Overfull \\[hv]box.*/,
	/Citation `[^']+' .*undefined.*/,
	/Reference `[^']+' .*undefined.*/,
	/There were undefined references.*/,
	/multiply defined.*/,
	/Rerun to get .*/,
	/Missing character: .*/,
	/Float too large.*/,
];

/** docs/tectonic.exe on Windows; elsewhere $TECTONIC or `tectonic` on PATH. */
function findTectonic() {
	const candidates = [
		process.env.TECTONIC,
		IS_WINDOWS ? BUNDLED : undefined,
		"tectonic",
	].filter(Boolean);
	for (const file of candidates) {
		const probe = spawnSync(file, ["--version"], { encoding: "utf-8" });
		if (probe.status === 0) return file;
	}
	throw new SetupError(
		IS_WINDOWS
			? `Tectonic not found: expected ${path.relative(ROOT, BUNDLED)}.`
			: "Tectonic not found: install it on PATH or set TECTONIC to its path.",
	);
}

function logProblems(file, patterns) {
	if (!fs.existsSync(file)) return [`${path.basename(file)} was not written`];
	const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/);
	return lines.filter((line) => patterns.some((re) => re.test(line)));
}

try {
	const startedAt = Date.now();
	const tectonic = findTectonic();
	const problems = [];
	for (const { name, bibtex = true, check = true } of BUILDS) {
		const logs = [`${name}.log`, ...(bibtex ? [`${name}.blg`] : [])];
		for (const log of logs) fs.rmSync(path.join(PAPER, log), { force: true });
		// A fixed rerun count: Tectonic 0.15's automatic .bbl change check
		// otherwise loops to its six-pass limit after the document has converged.
		// Intermediates are kept so the other document can read this .aux.
		run(
			tectonic,
			["--keep-logs", "--keep-intermediates", "--reruns", "3", `${name}.tex`],
			{
				cwd: PAPER,
				env: { ...repoEnv(), TECTONIC_CACHE_DIR: path.join(CACHE, "tectonic") },
				what: `Tectonic (${name}.tex)`,
				quiet: true,
			},
		);
		if (!check) continue;
		problems.push(
			...logProblems(path.join(PAPER, `${name}.log`), PROBLEMS),
			...(bibtex
				? logProblems(path.join(PAPER, `${name}.blg`), [
						/^Warning--.*/,
						/error/i,
					])
				: []),
		);
	}
	if (problems.length) {
		throw new SetupError(
			`Paper built with ${problems.length} problem(s):\n  ${problems.join("\n  ")}`,
		);
	}
	const seconds = ((Date.now() - startedAt) / 1000).toFixed(1);
	ok(
		`Built ${new Set(BUILDS.map((b) => b.name)).size} PDFs in ${path.relative(ROOT, PAPER)} in ${seconds}s with clean logs`,
	);
} catch (error) {
	if (!(error instanceof SetupError)) throw error;
	fail(error.message);
	process.exit(1);
}
