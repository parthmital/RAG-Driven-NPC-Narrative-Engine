// Full local validation: `npm run check` from the repository root.
import path from "node:path";
import {
	BACKEND,
	FRONTEND,
	ROOT,
	SetupError,
	VENV_PYTHON,
	ensureSetup,
	log,
	npm,
	run,
} from "./lib/workspace.mjs";

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
				{ what: "Clone detection" },
			),
	],
	[
		"Backend format",
		() =>
			run(VENV_PYTHON, ["-m", "black", "--check", "--quiet", "."], {
				cwd: BACKEND,
				what: "black",
			}),
	],
	[
		"Backend tests",
		() =>
			run(VENV_PYTHON, ["-m", "unittest", "discover", "-s", "tests"], {
				cwd: BACKEND,
				what: "Backend tests",
			}),
	],
	...["format:check", "typecheck", "lint", "test", "build"].map((script) => [
		`Frontend ${script}`,
		() =>
			npm(["run", "--silent", script], {
				cwd: FRONTEND,
				what: `Frontend ${script}`,
			}),
	]),
];

try {
	ensureSetup();
	for (const [name, step] of steps) {
		log(`${name}...`);
		step();
	}
	log("All checks passed.");
} catch (error) {
	if (!(error instanceof SetupError)) throw error;
	console.error(`[check] ${error.message}`);
	process.exit(1);
}
