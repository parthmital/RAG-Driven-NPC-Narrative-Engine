// Single local launcher: `npm run dev` from the repository root.
//
// Sets up everything on first run, then starts each long-running service in
// its own titled terminal window (Windows) or with prefixed output (elsewhere).
// Ctrl+C here stops every process tree and window.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import {
	BACKEND,
	CACHE,
	FRONTEND,
	IS_WINDOWS,
	SetupError,
	VENV_PYTHON,
	ensureSetup,
	log,
	repoEnv,
} from "./lib/workspace.mjs";

const SERVICES = {
	backend: {
		title: "Obsidian Flask Backend",
		cwd: BACKEND,
		command: VENV_PYTHON,
		args: ["-u", "server.py"],
		port: 8000,
		readyUrl: "http://127.0.0.1:8000/health",
		isReady: async (res) => res.ok && (await res.json()).ready === true,
	},
	frontend: {
		title: "Obsidian Flask Frontend",
		cwd: FRONTEND,
		command: process.execPath,
		args: [path.join(FRONTEND, "node_modules/vite/bin/vite.js")],
		port: 8080,
		readyUrl: "http://localhost:8080",
		isReady: async (res) => res.status < 500,
	},
};
const APP_URL = SERVICES.frontend.readyUrl;
const READY_TIMEOUT_MS = 10 * 60 * 1000;
// Per-launcher directory where service supervisors report exits.
const RUN_DIR = path.join(
	CACHE,
	"dev",
	process.argv[2] === "--service" ? process.argv[4] : String(process.pid),
);
const exitFile = (name) => path.join(RUN_DIR, `${name}.exit`);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Service mode: runs inside a spawned window and supervises one service.
if (process.argv[2] === "--service") {
	const name = process.argv[3];
	const service = SERVICES[name];
	const child = spawn(service.command, service.args, {
		cwd: service.cwd,
		env: repoEnv(),
		stdio: "inherit",
	});
	child.on("exit", (code) => {
		fs.writeFileSync(exitFile(name), String(code ?? 1));
		console.error(
			`\n${service.title} exited with code ${code}. The main terminal will close this window.`,
		);
		setInterval(() => {}, 1 << 30);
	});
} else {
	await main();
}

function accepts(host, port) {
	return new Promise((resolve) => {
		const socket = net.connect({ host, port });
		const done = (open) => {
			socket.destroy();
			resolve(open);
		};
		socket.setTimeout(1000);
		socket.once("connect", () => done(true));
		socket.once("error", () => done(false));
		socket.once("timeout", () => done(false));
	});
}

/** A port is busy if anything accepts on IPv4 or IPv6 loopback. */
async function portBusy(port) {
	const results = await Promise.all([
		accepts("127.0.0.1", port),
		accepts("::1", port),
	]);
	return results.some(Boolean);
}

function killTree(pid) {
	if (!pid) return;
	if (IS_WINDOWS) {
		spawnSync("taskkill", ["/pid", String(pid), "/T", "/F"], {
			stdio: "ignore",
		});
	} else {
		try {
			process.kill(-pid, "SIGTERM");
		} catch {
			// already gone
		}
	}
}

function startInWindow(name, service) {
	const script = path.join(import.meta.dirname, "dev.mjs");
	const inner = `title ${service.title}&& "${process.execPath}" "${script}" --service ${name} ${process.pid}`;
	return spawn("cmd.exe", ["/d", "/s", "/c", `"${inner}"`], {
		cwd: service.cwd,
		env: repoEnv(),
		detached: true,
		stdio: "ignore",
		windowsVerbatimArguments: true,
	});
}

function startPrefixed(name, service) {
	const child = spawn(service.command, service.args, {
		cwd: service.cwd,
		env: repoEnv(),
		detached: true,
		stdio: ["ignore", "pipe", "pipe"],
	});
	const tag = `[${name}]`.padEnd(11);
	for (const stream of [child.stdout, child.stderr]) {
		let buffer = "";
		stream.on("data", (chunk) => {
			buffer += chunk;
			const lines = buffer.split(/\r?\n/);
			buffer = lines.pop();
			for (const line of lines) console.log(`${tag}${line}`);
		});
	}
	child.on("exit", (code) =>
		fs.writeFileSync(exitFile(name), String(code ?? 1)),
	);
	return child;
}

async function probe(service) {
	try {
		const res = await fetch(service.readyUrl, {
			signal: AbortSignal.timeout(2000),
		});
		return await service.isReady(res);
	} catch {
		return false;
	}
}

function crashed() {
	for (const name of Object.keys(SERVICES)) {
		if (fs.existsSync(exitFile(name))) {
			return `${SERVICES[name].title} exited with code ${fs.readFileSync(exitFile(name), "utf-8")}.`;
		}
	}
	return null;
}

function openBrowser(url) {
	if (process.env.CI) return;
	const [file, args] = IS_WINDOWS
		? ["cmd.exe", ["/c", "start", "", url]]
		: process.platform === "darwin"
			? ["open", [url]]
			: ["xdg-open", [url]];
	spawn(file, args, { stdio: "ignore", detached: true }).unref();
}

async function main() {
	const children = [];
	let stopping = false;
	const stop = (code) => {
		if (stopping) return;
		stopping = true;
		log("Stopping services...");
		for (const child of children) killTree(child.pid);
		fs.rmSync(RUN_DIR, { recursive: true, force: true });
		process.exit(code);
	};
	process.on("SIGINT", () => stop(0));
	process.on("SIGTERM", () => stop(0));
	process.on("SIGHUP", () => stop(0));

	try {
		ensureSetup();
		for (const service of Object.values(SERVICES)) {
			if (await portBusy(service.port)) {
				throw new SetupError(
					`Port ${service.port} is busy. Stop whatever is using it (maybe an earlier run) and retry.`,
				);
			}
		}
	} catch (error) {
		if (!(error instanceof SetupError)) throw error;
		console.error(`[dev] ${error.message}`);
		process.exit(1);
	}

	fs.rmSync(RUN_DIR, { recursive: true, force: true });
	fs.mkdirSync(RUN_DIR, { recursive: true });
	for (const [name, service] of Object.entries(SERVICES)) {
		const child = IS_WINDOWS
			? startInWindow(name, service)
			: startPrefixed(name, service);
		children.push(child);
		log(`Started ${name}${IS_WINDOWS ? " in its own window" : ""}.`);
	}

	const ready = new Set();
	const startedAt = Date.now();
	let lastStatus = 0;
	while (ready.size < children.length) {
		const failure = crashed();
		if (failure) {
			console.error(`[dev] ${failure} Check its window or output above.`);
			return stop(1);
		}
		if (Date.now() - startedAt > READY_TIMEOUT_MS) {
			console.error("[dev] Services were not ready within 10 minutes.");
			return stop(1);
		}
		for (const [name, service] of Object.entries(SERVICES)) {
			if (!ready.has(name) && (await probe(service))) {
				ready.add(name);
				log(
					`${name} ready at ${service.readyUrl.replace("127.0.0.1", "localhost")}`,
				);
			}
		}
		if (Date.now() - lastStatus > 10000 && ready.size < children.length) {
			const waiting = Object.keys(SERVICES).filter((n) => !ready.has(n));
			log(
				`Waiting for ${waiting.join(" and ")} (the backend loads the embedding model first)...`,
			);
			lastStatus = Date.now();
		}
		await sleep(1000);
	}

	log(`All services ready: ${APP_URL}`);
	openBrowser(APP_URL);
	log("Press Ctrl+C to stop everything.");

	while (!stopping) {
		const failure = crashed();
		if (failure) {
			console.error(`[dev] ${failure}`);
			return stop(1);
		}
		await sleep(1000);
	}
}
