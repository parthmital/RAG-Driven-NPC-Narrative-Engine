import { useEffect, useState } from "react";
import { apiClient, type SaveInfo } from "@/services/api";

/** Fetch the saved session list on every mount. */
export function useSavedSessions() {
	const [saves, setSaves] = useState<SaveInfo[]>([]);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		setIsLoading(true);
		apiClient
			.listSessions()
			.then(setSaves)
			.catch(console.error)
			.finally(() => setIsLoading(false));
	}, []);

	return { saves, isLoading };
}
