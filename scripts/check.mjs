// Full local validation: `npm run check` from the repository root.
// Each step's output is shown only when that step fails.
import path from "node:path";
import {
	BACKEND,
	FRONTEND,
	ROOT,
	SetupError,
	VENV_PYTHON,
	ensureSetup,
	fail,
	npm,
	ok,
	run,
} from "./lib/workspace.mjs";

const quiet = true;
const steps = [
	[
		"Clone detection",
		() =>
			run(
				process.execPath,
				[
					path.join(ROOT, "node_modules/jscpd/bin/jscpd"),
					...["--min-tokens", "50", "--threshold", "1", "--silent"],
					...[
						"--ignore",
						"**/node_modules/**,**/__pycache__/**,**/components/ui/**,**/*.json",
					],
					"Backend",
					"Frontend/src",
					"scripts",
				],
				{ what: "Clone detection", quiet },
			),
	],
	[
		"Backend format",
		() =>
			run(VENV_PYTHON, ["-m", "black", "--check", "--quiet", "."], {
				cwd: BACKEND,
				what: "black",
				quiet,
			}),
	],
	[
		"Backend tests",
		() =>
			run(VENV_PYTHON, ["-m", "unittest", "discover", "-s", "tests"], {
				cwd: BACKEND,
				what: "Backend tests",
				quiet,
			}),
	],
	...["format:check", "typecheck", "lint", "test", "build"].map((script) => [
		`Frontend ${script}`,
		() =>
			npm(["run", "--silent", script], {
				cwd: FRONTEND,
				what: `Frontend ${script}`,
				quiet,
			}),
	]),
];

const seconds = (since) => `${((Date.now() - since) / 1000).toFixed(1)}s`;

try {
	ensureSetup();
	const startedAt = Date.now();
	for (const [name, step] of steps) {
		const stepStartedAt = Date.now();
		step();
		ok(`${name.padEnd(22)} ${seconds(stepStartedAt)}`);
	}
	ok(`All ${steps.length} checks passed in ${seconds(startedAt)}`);
} catch (error) {
	if (!(error instanceof SetupError)) throw error;
	fail(error.message);
	process.exit(1);
}
