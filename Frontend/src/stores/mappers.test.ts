import { describe, expect, it } from "vitest";
import type { ActionResponse } from "@/contracts/api";
import { toDialogueMessages } from "@/stores/mappers";

const base: ActionResponse = {
	npc_dialogue: "",
	narration: "",
	npc_id: "mara",
	npc_name: "Mara",
	turn: 1,
	trust_change: 0,
	validation_errors: [],
	elapsed_ms: 0,
	events: [],
};

describe("toDialogueMessages", () => {
	it("merges narrator narration and dialogue into one bubble", () => {
		const messages = toDialogueMessages({
			...base,
			npc_id: "narrator",
			narration: " Rain falls. ",
			npc_dialogue: "The door creaks.",
		});
		expect(messages).toHaveLength(1);
		expect(messages[0]).toMatchObject({
			type: "narration",
			speaker: "Narrator",
			content: "Rain falls.\n\nThe door creaks.",
		});
	});

	it("splits NPC results into narration and dialogue bubbles", () => {
		const messages = toDialogueMessages({
			...base,
			narration: "She frowns.",
			npc_dialogue: " Leave. ",
			trust_change: -5,
		});
		expect(messages.map((m) => [m.type, m.content, m.trustChange])).toEqual([
			["narration", "She frowns.", undefined],
			["npc", "Leave.", -5],
		]);
	});

	it("returns nothing for empty text", () => {
		expect(toDialogueMessages(base)).toEqual([]);
	});
});
