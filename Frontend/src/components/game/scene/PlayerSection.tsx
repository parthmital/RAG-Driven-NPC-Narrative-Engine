import { ArrowDownToLine, Coins } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { SectionLabel } from "@/components/ui/EmptyState";
import { ItemList } from "@/components/game/scene/ItemList";

function standing(alignment: number) {
	if (alignment > 70) return { label: "Virtuous", color: "text-gilt" };
	if (alignment > 40) return { label: "Uncommitted", color: "text-muted" };
	return { label: "Corrupt", color: "text-ember" };
}

/** The player's purse, moral standing, and pack. */
export function PlayerSection() {
	const playerName = useGameStore((s) => s.playerName);
	const currency = useGameStore((s) => s.currency);
	const alignment = useGameStore((s) => s.moralAlignment);
	const inventory = useGameStore((s) => s.inventory);
	const dropObject = useGameStore((s) => s.dropObject);
	const isProcessing = useGameStore((s) => s.isProcessing);
	const { label, color } = standing(alignment);

	return (
		<section aria-labelledby="player-heading" className="flex flex-col gap-4">
			<SectionLabel id="player-heading">{playerName ?? "You"}</SectionLabel>
			<dl className="grid grid-cols-2 gap-4">
				<div>
					<dt className="text-caption text-faint">Purse</dt>
					<dd className="flex items-center gap-1.5 font-display text-title text-gilt">
						<Coins aria-hidden className="size-4" />
						<span className="lining-nums tabular-nums">{currency}</span>
						<span className="sr-only">coins</span>
					</dd>
				</div>
				<div>
					<dt className="text-caption text-faint">Standing</dt>
					<dd className={`font-display text-title ${color}`}>{label}</dd>
				</div>
			</dl>
			<div
				role="meter"
				aria-label="Moral standing, corrupt to virtuous"
				aria-valuemin={0}
				aria-valuemax={100}
				aria-valuenow={alignment}
				className="relative h-2 rounded-full bg-raised"
			>
				<span
					className="absolute top-1/2 size-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface bg-text transition-all duration-500"
					style={{ left: `${alignment}%` }}
				/>
			</div>
			<div className="flex justify-between text-caption text-faint">
				<span>Corrupt</span>
				<span>Virtuous</span>
			</div>

			<div className="flex flex-col gap-3">
				<SectionLabel count={inventory.length}>Carrying</SectionLabel>
				{inventory.length === 0 ? (
					<p className="text-body text-muted">
						Nothing yet. Take objects you find in a room.
					</p>
				) : (
					<ItemList
						items={inventory}
						actionLabel="Drop"
						actionIcon={<ArrowDownToLine aria-hidden className="size-4" />}
						onAction={dropObject}
						disabled={isProcessing}
					/>
				)}
			</div>
		</section>
	);
}
