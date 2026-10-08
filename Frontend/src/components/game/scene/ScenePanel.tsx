import { useGameStore } from "@/stores/gameStore";
import { PlaceSection } from "@/components/game/scene/PlaceSection";
import { PeopleSection } from "@/components/game/scene/PeopleSection";
import { ObjectsSection } from "@/components/game/scene/ObjectsSection";
import { PlayerSection } from "@/components/game/scene/PlayerSection";

/** Everything about the current room, in the order a player acts on it. */
export function ScenePanel() {
	// A new room fades in rather than swapping in place.
	const location = useGameStore((s) => s.currentLocation);
	return (
		<div key={location} className="flex animate-fade flex-col gap-6 p-4">
			<PlaceSection />
			<PeopleSection />
			<ObjectsSection />
			<div className="border-t pt-6">
				<PlayerSection />
			</div>
		</div>
	);
}
