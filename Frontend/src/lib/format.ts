/** Convert snake_case IDs to Title Case display names */
export function toTitleCase(s: string): string {
	return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
