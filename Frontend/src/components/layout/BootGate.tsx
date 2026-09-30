import { useEffect, useState, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { apiClient } from "@/services/api";

const POLL_MS = 1000;
const SLOW_AFTER_S = 8;
const STUCK_AFTER_S = 90;

/** Holds the app until the backend reports ready, explaining long waits. */
export function BootGate({ children }: { children: ReactNode }) {
	const [ready, setReady] = useState(false);
	const [seconds, setSeconds] = useState(0);

	useEffect(() => {
		let timer: ReturnType<typeof setTimeout>;
		let stopped = false;
		const startedAt = Date.now();
		const poll = async () => {
			if (await apiClient.pollReady()) return setReady(true);
			if (stopped) return;
			setSeconds(Math.round((Date.now() - startedAt) / 1000));
			timer = setTimeout(poll, POLL_MS);
		};
		void poll();
		return () => {
			stopped = true;
			clearTimeout(timer);
		};
	}, []);

	if (ready) return <>{children}</>;

	return (
		<main className="flex h-dvh flex-col items-center justify-center gap-6 bg-ground px-6 text-center">
			<img src="/favicon.png" alt="" className="size-20" />
			<div className="flex flex-col items-center gap-2" role="status">
				<h1 className="text-headline">The Obsidian Flask</h1>
				<p className="flex items-center gap-2 text-body text-muted">
					<Loader2 aria-hidden className="size-4 animate-spin" />
					Waking the storyteller
				</p>
			</div>
			{seconds >= SLOW_AFTER_S && (
				<p className="max-w-md text-label text-faint">
					{seconds >= STUCK_AFTER_S
						? "Still waiting for the game server. If it isn't running, start it with npm run dev from the project folder; this page continues on its own."
						: "The first start loads the language model into memory, which can take a minute."}
				</p>
			)}
		</main>
	);
}
