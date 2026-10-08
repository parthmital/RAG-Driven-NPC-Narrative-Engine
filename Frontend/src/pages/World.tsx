import { useState } from "react";
import { Footprints, Hand, Loader2, MapPin } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useLocations } from "@/hooks/useLocations";
import { splitPlaceName } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { EmptyState, SectionLabel } from "@/components/ui/EmptyState";
import { ListRow, MasterDetail } from "@/components/layout/MasterDetail";
import { ItemList } from "@/components/game/scene/ItemList";
import { emotionOf } from "@/components/game/emotionStyles";
import type { LocationInfo } from "@/services/api";

function PlaceDetail({
	place,
	onSelect,
	nameOf,
}: {
	place: LocationInfo;
	onSelect: (id: string) => void;
	nameOf: (id: string) => string;
}) {
	const currentLocation = useGameStore((s) => s.currentLocation);
	const connected = useGameStore((s) => s.connectedLocations);
	const movePlayer = useGameStore((s) => s.movePlayer);
	const pickupObject = useGameStore((s) => s.pickupObject);
	const isProcessing = useGameStore((s) => s.isProcessing);
	const [isTravelling, setIsTravelling] = useState(false);

	const isHere = place.id === currentLocation;
	const isAdjacent = connected.includes(place.id);
	const { area, place: title } = splitPlaceName(place.name);

	const travel = async () => {
		setIsTravelling(true);
		try {
			await movePlayer(place.id);
		} catch {
			// The store reports travel failures.
		} finally {
			setIsTravelling(false);
		}
	};

	return (
		<>
			<header className="flex flex-col gap-3">
				{area && <p className="text-label text-faint">{area}</p>}
				<h1 className="text-headline">{title}</h1>
				{isHere ? (
					<p className="flex items-center gap-2 text-label text-gilt">
						<MapPin aria-hidden className="size-4" /> You are here
					</p>
				) : isAdjacent ? (
					<Button
						variant="primary"
						loading={isTravelling}
						disabled={isProcessing}
						icon={<Footprints aria-hidden className="size-4" />}
						onClick={travel}
						className="self-start"
					>
						Travel here
					</Button>
				) : (
					<p className="text-label text-muted">
						Not reachable from where you stand. Travel through a neighbouring
						place.
					</p>
				)}
			</header>

			<p className="font-read text-read text-text/85">{place.description}</p>

			<div className="flex flex-col gap-3">
				<SectionLabel count={place.npcs_present.length}>People</SectionLabel>
				{place.npcs_present.length === 0 ? (
					<p className="text-body text-muted">No one of note.</p>
				) : (
					<ul className="flex flex-col gap-1">
						{place.npcs_present.map((npc) => (
							<li key={npc.id} className="flex items-baseline gap-2">
								<span className="font-display text-title text-arcane">
									{npc.name}
								</span>
								<span
									className={cn(
										"text-label",
										emotionOf(npc.emotional_state).color,
									)}
								>
									{emotionOf(npc.emotional_state).label}
								</span>
							</li>
						))}
					</ul>
				)}
			</div>

			{place.objects_here.length > 0 && (
				<div className="flex flex-col gap-3">
					<SectionLabel count={place.objects_here.length}>Objects</SectionLabel>
					{isHere ? (
						<ItemList
							items={place.objects_here}
							actionLabel="Take"
							actionIcon={<Hand aria-hidden className="size-4" />}
							onAction={pickupObject}
							disabled={isProcessing}
						/>
					) : (
						<ul className="flex flex-col gap-3">
							{place.objects_here.map((obj) => (
								<li key={obj.id}>
									<p className="text-body font-medium">{obj.name}</p>
									<p className="text-label text-muted">{obj.description}</p>
								</li>
							))}
						</ul>
					)}
				</div>
			)}

			<div className="flex flex-col gap-3">
				<SectionLabel>Leads to</SectionLabel>
				<div className="flex flex-wrap gap-2">
					{place.connected_to.map((id) => (
						<Button key={id} onClick={() => onSelect(id)}>
							{nameOf(id)}
						</Button>
					))}
				</div>
			</div>
		</>
	);
}

export default function WorldPage() {
	const currentLocation = useGameStore((s) => s.currentLocation);
	const connected = useGameStore((s) => s.connectedLocations);
	const { locations, isLoading, failed } = useLocations();
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [detailOpen, setDetailOpen] = useState(false);

	const selected =
		locations.find((l) => l.id === (selectedId ?? currentLocation)) ?? null;
	const nameOf = (id: string) =>
		splitPlaceName(locations.find((l) => l.id === id)?.name ?? id).place;
	const select = (id: string) => {
		setSelectedId(id);
		setDetailOpen(true);
	};

	if (isLoading) {
		return (
			<div className="flex h-full items-center justify-center gap-2 text-muted">
				<Loader2 aria-hidden className="size-4 animate-spin" /> Loading the map
			</div>
		);
	}
	if (failed) {
		return (
			<EmptyState icon={<MapPin aria-hidden />} title="The map didn't load">
				The game server didn't return the list of places. Return to the scene
				and try again.
			</EmptyState>
		);
	}

	return (
		<MasterDetail
			listLabel="All places"
			detailKey={selected?.id}
			detailOpen={detailOpen}
			onBack={() => setDetailOpen(false)}
			list={
				<ul>
					{locations.map((loc) => {
						const { area, place } = splitPlaceName(loc.name);
						const isHere = loc.id === currentLocation;
						return (
							<ListRow
								key={loc.id}
								selected={selected?.id === loc.id}
								onSelect={() => select(loc.id)}
							>
								<span className="text-caption text-faint">
									{area ?? "Outside"}
								</span>
								<span className="flex items-center gap-2 font-display text-title">
									{place}
									{isHere && (
										<MapPin aria-hidden className="size-4 text-gilt" />
									)}
								</span>
								<span className="text-label text-muted">
									{isHere
										? "You are here"
										: connected.includes(loc.id)
											? "Next door"
											: "Further away"}
									{loc.npcs_present.length > 0 &&
										` · ${loc.npcs_present.map((n) => n.name).join(", ")}`}
								</span>
							</ListRow>
						);
					})}
				</ul>
			}
			detail={
				selected && (
					<PlaceDetail place={selected} onSelect={select} nameOf={nameOf} />
				)
			}
		/>
	);
}
