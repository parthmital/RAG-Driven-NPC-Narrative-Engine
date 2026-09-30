import { useEffect, useState } from "react";
import { apiClient, type SaveInfo } from "@/services/api";

/** Fetch the saved session list on every mount. */
export function useSavedSessions() {
	const [saves, setSaves] = useState<SaveInfo[]>([]);
	const [isLoading, setIsLoading] = useState(true);
	const [failed, setFailed] = useState(false);

	useEffect(() => {
		setIsLoading(true);
		apiClient
			.listSessions()
			.then(setSaves)
			.catch((error) => {
				console.error("[useSavedSessions] Failed to list saves:", error);
				setFailed(true);
			})
			.finally(() => setIsLoading(false));
	}, []);

	return { saves, isLoading, failed };
}
