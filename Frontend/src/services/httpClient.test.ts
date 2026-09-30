import { afterEach, describe, expect, it, vi } from "vitest";
import { APIClient, APIError } from "./httpClient";

function mockJsonResponse(
	body: unknown,
	init: { ok?: boolean; status?: number; statusText?: string } = {},
) {
	return {
		ok: init.ok ?? true,
		status: init.status ?? 200,
		statusText: init.statusText ?? "OK",
		json: vi.fn().mockResolvedValue(body),
	} as unknown as Response;
}

describe("APIClient", () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("serialises session creation requests", async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			mockJsonResponse({
				session_id: "session-1",
				player_name: "Ada",
				turn: 0,
				active_npc_id: null,
				current_location_id: "tavern_common",
				created_at: 1,
			}),
		);
		vi.stubGlobal("fetch", fetchMock);

		const client = new APIClient("/api/game");
		await expect(
			client.createSession({
				name: "Ada",
				gender: "Female",
				age: 31,
				occupation: "Scholar",
			}),
		).resolves.toMatchObject({ session_id: "session-1" });

		expect(fetchMock).toHaveBeenCalledWith(
			"/api/game/session",
			expect.objectContaining({
				method: "POST",
				body: JSON.stringify({
					name: "Ada",
					gender: "Female",
					age: 31,
					occupation: "Scholar",
					reset: false,
				}),
			}),
		);
	});

	it("normalises FastAPI validation errors", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(
				mockJsonResponse(
					{
						detail: [
							{
								loc: ["body", "age"],
								msg: "Input should be greater than or equal to 18",
							},
						],
					},
					{ ok: false, status: 422, statusText: "Unprocessable Entity" },
				),
			),
		);

		const client = new APIClient("/api/game");
		await expect(
			client.createSession({
				name: "Ada",
				gender: "Female",
				age: 17,
				occupation: "Scholar",
			}),
		).rejects.toMatchObject({
			status: 422,
			message: "age: Input should be greater than or equal to 18",
		});
	});

	it("polls backend readiness defensively", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(mockJsonResponse({ ready: true })),
		);

		const client = new APIClient("/api/game");
		await expect(client.pollReady()).resolves.toBe(true);
	});

	it("treats failed readiness fetches as not ready", async () => {
		vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

		const client = new APIClient("/api/game");
		await expect(client.pollReady()).resolves.toBe(false);
	});
});
