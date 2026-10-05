// Research paper build: `npm run paper` from the repository root.
// Compiles docs/paper/main.tex with Tectonic into docs/paper/main.pdf, then
// fails if the TeX or BibTeX logs report a problem that affects correctness.
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
	for (const name of ["main.log", "main.blg"]) {
		fs.rmSync(path.join(PAPER, name), { force: true });
	}
	// A fixed rerun count: Tectonic 0.15's automatic .bbl change check
	// otherwise loops to its six-pass limit after the document has converged.
	run(tectonic, ["--keep-logs", "--reruns", "3", "main.tex"], {
		cwd: PAPER,
		env: { ...repoEnv(), TECTONIC_CACHE_DIR: path.join(CACHE, "tectonic") },
		what: "Tectonic",
		quiet: true,
	});
	const problems = [
		...logProblems(path.join(PAPER, "main.log"), PROBLEMS),
		...logProblems(path.join(PAPER, "main.blg"), [/^Warning--.*/, /error/i]),
	];
	if (problems.length) {
		throw new SetupError(
			`Paper built with ${problems.length} problem(s):\n  ${problems.join("\n  ")}`,
		);
	}
	const seconds = ((Date.now() - startedAt) / 1000).toFixed(1);
	ok(
		`Built ${path.relative(ROOT, path.join(PAPER, "main.pdf"))} in ${seconds}s with a clean log`,
	);
} catch (error) {
	if (!(error instanceof SetupError)) throw error;
	fail(error.message);
	process.exit(1);
}
