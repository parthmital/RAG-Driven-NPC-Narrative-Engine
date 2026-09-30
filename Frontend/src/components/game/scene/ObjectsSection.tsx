import { Hand } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { SectionLabel } from "@/components/ui/EmptyState";
import { ItemList } from "@/components/game/scene/ItemList";

/** Things lying in the room that the player can take. */
export function ObjectsSection() {
	const objects = useGameStore((s) => s.objectsHere);
	const pickupObject = useGameStore((s) => s.pickupObject);
	const isProcessing = useGameStore((s) => s.isProcessing);

	if (objects.length === 0) return null;
	return (
		<section className="flex flex-col gap-3">
			<SectionLabel count={objects.length}>In this room</SectionLabel>
			<ItemList
				items={objects}
				actionLabel="Take"
				actionIcon={<Hand aria-hidden className="size-4" />}
				onAction={pickupObject}
				disabled={isProcessing}
			/>
		</section>
	);
}
