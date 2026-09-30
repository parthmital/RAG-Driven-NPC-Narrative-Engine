import { useState } from "react";
import { DoorOpen } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useLocations } from "@/hooks/useLocations";
import { splitPlaceName, toTitleCase } from "@/lib/format";
import { SectionLabel } from "@/components/ui/EmptyState";

/** Where the player stands and the ways out. */
export function PlaceSection() {
	const name = useGameStore((s) => s.currentLocationName);
	const description = useGameStore((s) => s.currentLocationDescription);
	const exits = useGameStore((s) => s.connectedLocations);
	const turn = useGameStore((s) => s.turn);
	const isProcessing = useGameStore((s) => s.isProcessing);
	const movePlayer = useGameStore((s) => s.movePlayer);
	const { locations, isLoading } = useLocations();
	const [travellingTo, setTravellingTo] = useState<string | null>(null);

	const { area, place } = splitPlaceName(name || "Somewhere unknown");
	const exitName = (id: string) => {
		const found = locations.find((l) => l.id === id);
		if (found) return splitPlaceName(found.name).place;
		// Until the real names arrive, hold the space instead of a guessed name.
		if (isLoading) {
			return (
				<>
					<span
						aria-hidden
						className="block h-4 w-32 animate-pulse rounded bg-raised"
					/>
					<span className="sr-only">{toTitleCase(id)}</span>
				</>
			);
		}
		return toTitleCase(id);
	};

	const travel = async (id: string) => {
		setTravellingTo(id);
		try {
			await movePlayer(id);
		} catch {
			// The store reports travel failures.
		} finally {
			setTravellingTo(null);
		}
	};

	return (
		<section aria-labelledby="place-heading" className="flex flex-col gap-4">
			<div>
				<p className="text-caption text-faint">
					{area ?? "Location"} · Turn {turn}
				</p>
				<h2 id="place-heading" className="text-headline">
					{place}
				</h2>
			</div>
			{description && (
				<p className="font-read text-body leading-relaxed text-muted">
					{description}
				</p>
			)}
			{exits.length > 0 && (
				<div className="flex flex-col gap-2">
					<SectionLabel>Exits</SectionLabel>
					<ul className="flex flex-col">
						{exits.map((id) => (
							<li key={id}>
								<button
									type="button"
									onClick={() => travel(id)}
									disabled={isProcessing || travellingTo !== null}
									aria-busy={travellingTo === id || undefined}
									className="group flex min-h-11 w-full items-center gap-3 rounded-md px-2 text-left text-body text-text transition-colors duration-150 hover:bg-raised active:bg-raised/70 disabled:cursor-not-allowed disabled:opacity-50"
								>
									<DoorOpen
										aria-hidden
										className="size-4 shrink-0 text-faint transition-colors group-hover:text-gilt"
									/>
									<span className="flex-1">{exitName(id)}</span>
									<span className="text-label text-faint group-hover:text-gilt">
										{travellingTo === id ? "Travelling…" : "Go"}
									</span>
								</button>
							</li>
						))}
					</ul>
				</div>
			)}
		</section>
	);
}
