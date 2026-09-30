import { useEffect, useState } from "react";
import { apiClient, type LocationInfo } from "@/services/api";
import { useGameStore } from "@/stores/gameStore";

// Last list per session, so remounting screens show real names immediately
// while the refetch runs, instead of flashing placeholders.
let cache: { sessionId: string; locations: LocationInfo[] } | null = null;

/** Every location in the world, refetched after moves, turns, and take or drop. */
export function useLocations() {
	const sessionId = useGameStore((s) => s.sessionId);
	const currentLocation = useGameStore((s) => s.currentLocation);
	const turn = useGameStore((s) => s.turn);
	const carried = useGameStore((s) => s.inventory.length);
	const cached = cache?.sessionId === sessionId ? cache.locations : null;
	const [locations, setLocations] = useState<LocationInfo[]>(cached ?? []);
	const [isLoading, setIsLoading] = useState(cached === null);
	const [failed, setFailed] = useState(false);

	useEffect(() => {
		if (!sessionId) return;
		let cancelled = false;
		setFailed(false);
		apiClient
			.listLocations(sessionId)
			.then((list) => {
				cache = { sessionId, locations: list };
				if (!cancelled) setLocations(list);
			})
			.catch((error) => {
				console.error("[useLocations] Failed to list locations:", error);
				if (!cancelled) setFailed(true);
			})
			.finally(() => !cancelled && setIsLoading(false));
		return () => {
			cancelled = true;
		};
	}, [sessionId, currentLocation, turn, carried]);

	return { locations, isLoading, failed };
}
