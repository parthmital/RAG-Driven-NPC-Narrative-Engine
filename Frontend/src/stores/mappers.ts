import type {
	ActionResponse,
	GameStateResponse,
	NPCInfo,
} from "@/contracts/api";
import type {
	Clue,
	DialogueMessage,
	EmotionalState,
	JournalEntry,
	MessageType,
	NPC,
	RelationshipTier,
} from "@/types/game";

export interface InventoryItem {
	id: string;
	name: string;
	description: string;
	properties?: Record<string, unknown>;
}

/** Convert backend NPCInfo to frontend NPC type */
export function toFrontendNPC(info: NPCInfo): NPC {
	return {
		id: info.id,
		name: info.name,
		title: info.title,
		description: info.description,
		personality: info.personality,
		trust: info.trust,
		maxTrust: info.max_trust,
		trustThresholds: info.trust_thresholds,
		emotionalState: info.emotional_state as EmotionalState,
		hiddenSecrets: 0,
		revealedSecrets: 0,
		allegiances: [],
		relationshipTier: info.relationship_tier as RelationshipTier,
		suspicion: info.suspicion,
		emotionalLabel: info.emotional_label,
		trustPercent: info.trust_percent,
		locationId: info.location_id,
	};
}

export function systemMessage(content: string, id = `${Date.now()}`) {
	return {
		id,
		type: "system" as const,
		content,
		timestamp: Date.now(),
	} satisfies DialogueMessage;
}

export function errorMessage(error: unknown, fallback: string): string {
	return error instanceof Error ? error.message : fallback;
}

/** Narration and NPC dialogue bubbles for one non-command action result. */
export function toDialogueMessages(result: ActionResponse): DialogueMessage[] {
	const narration = (result.narration || "").trim();
	const dialogue = (result.npc_dialogue || "").trim();
	const now = Date.now();

	if (result.npc_id === "narrator") {
		const combined =
			narration && dialogue
				? `${narration}\n\n${dialogue}`
				: narration || dialogue;
		return combined
			? [
					{
						id: `nar-npc-${now}`,
						type: "narration",
						speaker: "Narrator",
						content: combined,
						timestamp: now,
					},
				]
			: [];
	}

	const messages: DialogueMessage[] = [];
	if (narration) {
		messages.push({
			id: `nar-path-${now}`,
			type: "narration",
			speaker: "Narrator",
			content: narration,
			timestamp: now,
		});
	}
	if (dialogue) {
		messages.push({
			id: `npc-path-${now + 1}`,
			type: "npc",
			speaker: result.npc_name,
			content: dialogue,
			timestamp: now + 1,
			trustChange: result.trust_change || undefined,
		});
	}
	return messages;
}

export function toInventory(
	inventory: NonNullable<GameStateResponse["player"]>["inventory"],
): InventoryItem[] {
	return inventory.map((o) => ({
		id: o.id,
		name: o.name,
		description: o.description,
		properties: o.properties as Record<string, unknown> | undefined,
	}));
}

export function toJournal(
	journal: GameStateResponse["journal"],
): JournalEntry[] {
	return (journal || []).map((j) => ({
		id: j.id,
		timestamp: j.timestamp,
		content: j.content,
		tags: j.tags || [],
	}));
}

export function toClues(clues: GameStateResponse["clues"]): Clue[] {
	return (clues || []).map((c) => ({
		id: c.id,
		title: c.title,
		description: c.description,
		linkedClues: c.linked_clues,
		npcId: c.npc_id,
		tension: c.tension,
		discovered: c.discovered,
	}));
}

export function toDialogueHistory(
	history: NonNullable<GameStateResponse["dialogue_history"]>,
): DialogueMessage[] {
	return history.map((m) => ({
		id: m.id,
		type: m.type as MessageType,
		speaker: m.speaker,
		content: m.content,
		timestamp: m.timestamp,
		trustChange: m.trustChange,
	}));
}
