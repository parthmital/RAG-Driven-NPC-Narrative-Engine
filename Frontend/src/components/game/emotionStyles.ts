export const EMOTION_STYLES: Record<string, { label: string; color: string }> =
	{
		neutral: { label: "Composed", color: "text-muted" },
		suspicious: { label: "Suspicious", color: "text-ember" },
		fearful: { label: "Fearful", color: "text-arcane" },
		angry: { label: "Angry", color: "text-ember" },
		melancholic: { label: "Melancholic", color: "text-muted" },
		guarded: { label: "Guarded", color: "text-muted" },
		trusting: { label: "Trusting", color: "text-gilt" },
		desperate: { label: "Desperate", color: "text-ember" },
		hostile: { label: "Hostile", color: "text-ember" },
		playful: { label: "Playful", color: "text-gilt" },
	};

export function emotionOf(state: string) {
	return EMOTION_STYLES[state] ?? EMOTION_STYLES.neutral;
}
