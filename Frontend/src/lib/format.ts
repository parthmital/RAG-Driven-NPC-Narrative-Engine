/** Convert snake_case IDs to Title Case display names */
export function toTitleCase(s: string): string {
	return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Split "The Obsidian Flask - Shadowed Cellar" into its building and room.
 * Names without a separator are a place of their own.
 */
export function splitPlaceName(name: string): { area?: string; place: string } {
	const [area, ...rest] = name.split(" - ");
	return rest.length ? { area, place: rest.join(" - ") } : { place: name };
}

const RELATIVE_UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
	["year", 31536000],
	["month", 2592000],
	["week", 604800],
	["day", 86400],
	["hour", 3600],
	["minute", 60],
];

/** "3 hours ago" style label for a Unix timestamp in seconds. */
export function formatRelativeTime(epochSeconds: number, now = Date.now()) {
	const diff = epochSeconds - now / 1000;
	const format = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
	for (const [unit, seconds] of RELATIVE_UNITS) {
		if (Math.abs(diff) >= seconds) {
			return format.format(Math.round(diff / seconds), unit);
		}
	}
	return "just now";
}
