import { BookOpen } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { EmptyState } from "@/components/ui/EmptyState";

const timeFormat = new Intl.DateTimeFormat(undefined, {
	hour: "2-digit",
	minute: "2-digit",
});

export default function JournalPage() {
	const journalEntries = useGameStore((s) => s.journalEntries);
	const entries = [...journalEntries].sort((a, b) => b.timestamp - a.timestamp);

	return (
		<div className="h-full scroll-area">
			<div className="mx-auto flex max-w-3xl flex-col gap-8 px-5 py-8 sm:px-10 sm:py-12">
				<header className="flex flex-col gap-2">
					<h1 className="text-headline sm:text-hero">Journal</h1>
					<p className="text-body text-muted">
						What you have learned, newest first.
					</p>
				</header>

				{entries.length === 0 ? (
					<EmptyState
						icon={<BookOpen aria-hidden />}
						title="Nothing written yet"
						className="rounded-lg border border-dashed"
					>
						Discoveries from your conversations are recorded here as the story
						unfolds.
					</EmptyState>
				) : (
					<ol className="flex flex-col">
						{entries.map((entry, index) => (
							<li
								key={entry.id || index}
								className="grid gap-x-6 gap-y-1 border-t py-5 sm:grid-cols-[5rem_minmax(0,1fr)]"
							>
								<time
									dateTime={new Date(entry.timestamp).toISOString()}
									className="pt-1 text-label tabular-nums text-faint"
								>
									{timeFormat.format(entry.timestamp)}
								</time>
								<p className="font-read text-read text-text/90">
									{entry.content}
								</p>
							</li>
						))}
					</ol>
				)}
			</div>
		</div>
	);
}
