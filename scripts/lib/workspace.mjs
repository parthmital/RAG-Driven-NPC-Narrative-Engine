// Repository-local environment, runtime discovery, and idempotent first-run setup.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(
	path.dirname(fileURLToPath(import.meta.url)),
	"../..",
);
export const BACKEND = path.join(ROOT, "Backend");
export const FRONTEND = path.join(ROOT, "Frontend");
export const CACHE = path.join(ROOT, ".cache");
export const IS_WINDOWS = process.platform === "win32";
export const VENV_PYTHON = path.join(
	ROOT,
	".venv",
	IS_WINDOWS ? "Scripts/python.exe" : "bin/python",
);

const STAMP = path.join(CACHE, "setup-stamp.json");
const REQUIREMENTS = path.join(BACKEND, "requirements-dev.txt");

// Status lines are tagged with the running script: [dev] or [check].
const TAG = `[${path.basename(process.argv[1] ?? "dev", ".mjs")}]`;
const COLOR = process.stdout.isTTY && !process.env.NO_COLOR && !process.env.CI;
const paint = (code, text) => (COLOR ? `\x1b[${code}m${text}\x1b[0m` : text);

export const log = (msg) => console.log(`${paint(2, TAG)} ${msg}`);
export const ok = (msg) => log(`${paint(32, "✓")} ${msg}`);
export const warn = (msg) => log(`${paint(33, "!")} ${msg}`);
export const fail = (msg) =>
	console.error(`${paint(2, TAG)} ${paint(31, "✗")} ${msg}`);

export class SetupError extends Error {}

/** Point every tool cache inside the repository and set local URL defaults. */
export function repoEnv() {
	const hf = path.join(CACHE, "huggingface");
	const env = {
		...process.env,
		npm_config_cache: path.join(CACHE, "npm"),
		PIP_CACHE_DIR: path.join(CACHE, "pip"),
		PIP_DISABLE_PIP_VERSION_CHECK: "1",
		PIP_REQUIRE_VIRTUALENV: "true",
		HF_HOME: hf,
		HUGGINGFACE_HUB_CACHE: path.join(hf, "hub"),
		SENTENCE_TRANSFORMERS_HOME: path.join(hf, "sentence-transformers"),
		TORCH_HOME: path.join(CACHE, "torch"),
		XDG_CACHE_HOME: CACHE,
		PYTHONPYCACHEPREFIX: path.join(CACHE, "pycache"),
		PYTHONIOENCODING: "utf-8",
		PYTHONUNBUFFERED: "1",
		TQDM_DISABLE: "1",
	};
	delete env.TRANSFORMERS_CACHE;
	env.FRONTEND_URL ||= "http://localhost:8080";
	env.CORS_ORIGINS ||= env.FRONTEND_URL;
	env.VITE_API_URL ||= "http://localhost:8000";
	env.VITE_DEV_HOST ||= "localhost";
	return env;
}

/**
 * Run a command to completion and throw on failure. `quiet` captures the
 * output and prints it only when the command fails.
 */
export function run(
	file,
	args,
	{ cwd = ROOT, env = repoEnv(), what, quiet = false, shell = false } = {},
) {
	const result = spawnSync(file, args, {
		cwd,
		env,
		shell,
		stdio: quiet ? "pipe" : "inherit",
		encoding: "utf-8",
		maxBuffer: 64 * 1024 * 1024,
	});
	if (result.error) throw new SetupError(`${what}: ${result.error.message}`);
	if (result.status !== 0) {
		if (quiet) process.stderr.write(`${result.stdout}${result.stderr}`);
		throw new SetupError(`${what} failed (exit code ${result.status}).`);
	}
}

/** npm invocation that works from `npm run` and from a bare `node` call. */
export function npm(args, options = {}) {
	const npmCli = process.env.npm_execpath;
	if (npmCli && npmCli.endsWith(".js")) {
		return run(process.execPath, [npmCli, ...args], options);
	}
	return run(IS_WINDOWS ? "npm.cmd" : "npm", args, {
		what: "npm",
		...options,
		shell: IS_WINDOWS,
	});
}

function findSystemPython() {
	const candidates = IS_WINDOWS
		? [
				["py", ["-3"]],
				["python", []],
				["python3", []],
			]
		: [
				["python3", []],
				["python", []],
			];
	for (const [file, prefix] of candidates) {
		const probe = spawnSync(
			file,
			[...prefix, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
			{ encoding: "utf-8" },
		);
		const version = probe.status === 0 ? probe.stdout.trim() : "";
		const [major, minor] = version.split(".").map(Number);
		if (major === 3 && minor >= 10) return { file, prefix, version };
	}
	throw new SetupError(
		"Python 3.10 or newer is required on PATH (python, python3, or the py launcher).",
	);
}

export function assertNodeVersion() {
	const [major, minor] = process.versions.node.split(".").map(Number);
	const supported =
		(major === 20 && minor >= 19) ||
		(major === 22 && minor >= 12) ||
		major >= 23;
	if (!supported) {
		throw new SetupError(
			`Node ${process.versions.node} is too old; Frontend needs ^20.19.0 or >=22.12.0.`,
		);
	}
}

function hashFiles(files) {
	const hash = createHash("sha256");
	for (const file of files)
		hash.update(fs.existsSync(file) ? fs.readFileSync(file) : "");
	return hash.digest("hex");
}

function readStamp() {
	try {
		return JSON.parse(fs.readFileSync(STAMP, "utf-8"));
	} catch {
		return {};
	}
}

function pythonHealthy() {
	if (!fs.existsSync(VENV_PYTHON)) return false;
	const probe = spawnSync(
		VENV_PYTHON,
		["-c", "import fastapi, uvicorn, faiss"],
		{
			stdio: "ignore",
			env: repoEnv(),
		},
	);
	return probe.status === 0;
}

/**
 * Install Node deps, the .venv, and .env on first run; later runs skip each
 * part unless its lockfile changed or its environment is broken.
 */
export function ensureSetup() {
	assertNodeVersion();
	fs.mkdirSync(CACHE, { recursive: true });
	const stamp = readStamp();
	const env = repoEnv();

	const nodeLocks = [
		path.join(ROOT, "package-lock.json"),
		path.join(FRONTEND, "package-lock.json"),
	];
	const nodeHash = hashFiles(nodeLocks);
	const nodeHealthy =
		fs.existsSync(path.join(ROOT, "node_modules")) &&
		fs.existsSync(path.join(FRONTEND, "node_modules/vite"));
	const upToDate = [];
	if (stamp.node !== nodeHash || !nodeHealthy) {
		log("Installing Node dependencies...");
		const quiet = ["--no-audit", "--no-fund", "--loglevel=error"];
		npm(["ci", ...quiet], { cwd: ROOT, env, what: "Root npm install" });
		npm(["ci", ...quiet], { cwd: FRONTEND, env, what: "Frontend npm install" });
		stamp.node = nodeHash;
	} else {
		upToDate.push("Node");
	}

	const pyFiles = [REQUIREMENTS, path.join(BACKEND, "requirements.txt")];
	const pyHash = hashFiles(pyFiles);
	if (stamp.python !== pyHash || !pythonHealthy()) {
		if (!fs.existsSync(VENV_PYTHON)) {
			const python = findSystemPython();
			log(`Creating .venv with Python ${python.version}...`);
			run(
				python.file,
				[...python.prefix, "-m", "venv", path.join(ROOT, ".venv")],
				{ env, what: "Creating .venv", quiet: true },
			);
		}
		log(
			"Installing backend requirements into .venv (first run downloads PyTorch)...",
		);
		run(VENV_PYTHON, ["-m", "pip", "install", "--quiet", "-r", REQUIREMENTS], {
			cwd: BACKEND,
			env,
			what: "Backend pip install",
		});
		stamp.python = pyHash;
	} else {
		upToDate.push("Python");
	}
	if (upToDate.length) ok(`${upToDate.join(" and ")} dependencies up to date`);

	const dotenv = path.join(BACKEND, ".env");
	if (!fs.existsSync(dotenv)) {
		fs.copyFileSync(path.join(BACKEND, ".env.example"), dotenv);
		ok("Created Backend/.env from .env.example");
	}
	if (
		/GROQ_API_KEY=(your_groq_api_key_here)?\s*$/m.test(
			fs.readFileSync(dotenv, "utf-8"),
		)
	) {
		warn("GROQ_API_KEY is not set in Backend/.env; NPC replies will fail");
	}

	fs.writeFileSync(STAMP, JSON.stringify(stamp, null, 2));
}
