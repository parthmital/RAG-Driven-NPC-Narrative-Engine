import { create } from "zustand";
import type { DialogueMessage, NPC, JournalEntry, Clue } from "@/types/game";
import {
	apiClient,
	wsService,
	type GameStateResponse,
	type ActionResponse,
	type NPCInfo,
	type WSOutMessage,
	type SaveInfo,
	type GameMetadataResponse,
} from "@/services/api";
import {
	errorMessage,
	systemMessage,
	toClues,
	toDialogueHistory,
	toDialogueMessages,
	toFrontendNPC,
	toInventory,
	toJournal,
	type InventoryItem,
} from "@/stores/mappers";
import { GAME_CONSTANTS } from "@/config/constants";
import { toast } from "sonner";

interface GameState {
	// Session
	sessionId: string | null;
	playerName: string | null;
	isConnected: boolean;

	// App Metadata
	metadata: GameMetadataResponse | null;
	fetchMetadata: () => Promise<void>;

	// Location
	currentLocation: string;
	currentLocationName: string;
	currentLocationDescription: string;
	connectedLocations: string[];

	// Dialogue
	dialogueHistory: DialogueMessage[];
	addMessage: (msg: DialogueMessage) => void;

	// NPCs
	activeNPC: NPC | null;
	npcs: Record<string, NPC>;

	// Journal
	journalEntries: JournalEntry[];

	// Clues
	clues: Clue[];

	// Processing
	isProcessing: boolean;

	// Inventory & Currency
	inventory: InventoryItem[];
	currency: number;

	// Relationships
	relationships: Record<string, Record<string, number>>;

	// Turn
	turn: number;
	moralAlignment: number;

	// ── Backend integration actions ──────────────────────────

	/** Create a new game session on the backend */
	createSession: (metadata: {
		name: string;
		gender: string;
		age: number;
		occupation: string;
	}) => Promise<void>;

	/** Refresh state from the backend */
	refreshState: () => Promise<void>;

	/** Send player input (dialogue or command) to backend */
	sendAction: (content: string, targetNpcId?: string) => Promise<void>;

	/** Directly move player to location */
	movePlayer: (locationId: string) => Promise<void>;

	/** Link two clues logically on the backend */
	linkClues: (id1: string, id2: string) => Promise<void>;

	/** Switch active NPC via backend */
	switchNPC: (npcId: string) => Promise<void>;

	/** Trigger manual save on backend */
	saveGame: () => Promise<boolean>;

	/** Load an existing session */
	loadGame: (sessionId: string) => Promise<void>;

	/** Get list of saved sessions */
	listSavedSessions: () => Promise<SaveInfo[]>;

	/** Disconnect and clean up */
	disconnect: () => void;

	/** Connect WebSocket to session */
	connectWebSocket: () => void;

	/** Pick up an object from current location */
	pickupObject: (objectId: string) => Promise<void>;

	/** Drop an object from inventory */
	dropObject: (objectId: string) => Promise<void>;
}

export const useGameStore = create<GameState>((set, get) => ({
	// ... existing state ...
	sessionId: null,
	playerName: null,
	isConnected: false,

	// App Metadata
	metadata: null,
	fetchMetadata: async () => {
		try {
			const md = await apiClient.getMetadata();
			set({ metadata: md });
			if (md.title) {
				document.title = md.title;
			}
			if (md.description) {
				const metaDesc = document.querySelector('meta[name="description"]');
				if (metaDesc) {
					metaDesc.setAttribute("content", md.description);
				}
			}
		} catch (error) {
			console.error("[GameStore] Failed to fetch metadata:", error);
		}
	},

	// Location
	currentLocation: "",
	currentLocationName: "",
	currentLocationDescription: "",
	connectedLocations: [],

	// Dialogue
	dialogueHistory: [],
	addMessage: (msg) =>
		set((s) => ({
			dialogueHistory: [...s.dialogueHistory, msg],
		})),

	// NPCs
	activeNPC: null,
	npcs: {},

	// Journal
	journalEntries: [],

	// Clues
	clues: [],

	// Processing
	isProcessing: false,

	// Inventory & Currency
	inventory: [],
	currency: 100,

	// Relationships
	relationships: {},

	// Turn
	turn: 0,
	moralAlignment: GAME_CONSTANTS.INITIAL_MORAL_ALIGNMENT,

	// ── Backend integration ─────────────────────────────────

	createSession: async (metadata) => {
		try {
			const session = await apiClient.createSession({
				...metadata,
			});
			set({
				sessionId: session.session_id,
				playerName: session.player_name,
				turn: session.turn,
				activeNPC: null,
				dialogueHistory: [],
			});

			// Fetch full state
			await get().refreshState();

			// Connect WebSocket
			get().connectWebSocket();

			// We no longer add hardcoded narration here.
			// The backend should return the initial state/narration if turn=0.
			// Or the user can type /look.
		} catch (error) {
			console.error("[GameStore] Failed to create session:", error);
			throw error;
		}
	},

	refreshState: async () => {
		const { sessionId } = get();
		if (!sessionId) return;

		try {
			const state: GameStateResponse = await apiClient.getGameState(sessionId);

			const updates: Partial<GameState> = {
				turn: state.turn,
				relationships: state.relationships,
			};

			// Location
			if (state.location) {
				updates.currentLocation = state.location.id;
				updates.currentLocationName = state.location.name;
				updates.currentLocationDescription = state.location.description;
				updates.connectedLocations = state.location.connected_to;
			}

			// Active NPC
			updates.activeNPC = state.active_npc
				? toFrontendNPC(state.active_npc)
				: null;

			// Player
			if (state.player) {
				const oldCurrency = get().currency;
				const newCurrency = state.player.currency;

				if (get().sessionId && oldCurrency !== newCurrency && get().turn > 0) {
					const diff = newCurrency - oldCurrency;
					const sign = diff > 0 ? "+" : "";
					const msg = `Currency changed: ${sign}$${diff} (Now $${newCurrency})`;
					toast.info("Wallet Updated", { description: msg });
					get().addMessage(systemMessage(msg, `currency-${Date.now()}`));
				}

				updates.inventory = toInventory(state.player.inventory);
				updates.moralAlignment = state.player.moral_alignment;
				updates.currency = newCurrency;
			}

			// All NPCs in location — accumulate
			if (state.location?.npcs_present) {
				const npcsRecord: Record<string, NPC> = { ...get().npcs };
				for (const npcInfo of state.location.npcs_present) {
					npcsRecord[npcInfo.id] = toFrontendNPC(npcInfo);
				}
				updates.npcs = npcsRecord;
			} else {
				// We don't clear NPCs when moving to a location with no NPCs
			}

			// Journal, clues, and dialogue always sync from backend
			updates.journalEntries = toJournal(state.journal);
			updates.clues = toClues(state.clues);
			if (state.dialogue_history) {
				updates.dialogueHistory = toDialogueHistory(state.dialogue_history);
			}

			set(updates as GameState);
		} catch (error) {
			console.error("[GameStore] Failed to refresh state:", error);
		}
	},

	sendAction: async (content: string, targetNpcId?: string) => {
		const { sessionId } = get();
		if (!sessionId) {
			console.error("[GameStore] No active session");
			return;
		}

		const isCommand = content.startsWith("/");

		// Add player message to history (slash commands are filtered in UI)
		get().addMessage({
			id: Date.now().toString(),
			type: "player",
			content,
			timestamp: Date.now(),
		});

		set({ isProcessing: true });

		try {
			const result: ActionResponse = await apiClient.sendAction(
				sessionId,
				content,
				targetNpcId,
			);

			// Check if it's a command response
			if (isCommand) {
				if (result.error && content.startsWith("/move")) {
					throw new Error(result.npc_dialogue);
				}
				const type = result.npc_id === "narrator" ? "narration" : "system";
				get().addMessage({
					id: (Date.now() + 1).toString(),
					type: type as MessageType,
					speaker: result.npc_name,
					content: result.npc_dialogue,
					timestamp: Date.now(),
				});
			} else {
				toDialogueMessages(result).forEach(get().addMessage);

				// Update turn
				set({ turn: result.turn });

				// Refresh full state (location, NPCs, journal, inventory may have changed)
				await get().refreshState();
			}
		} catch (error) {
			console.error("[GameStore] Action error:", error);
			if (!content.startsWith("/move")) {
				get().addMessage(
					systemMessage(
						`Error: ${errorMessage(error, "Failed to process action")}`,
						(Date.now() + 2).toString(),
					),
				);
			}
			throw error;
		} finally {
			set({ isProcessing: false });
		}
	},

	movePlayer: async (locationId: string) => {
		const { sessionId, refreshState } = get();
		if (!sessionId) return;
		try {
			await apiClient.movePlayer(sessionId, locationId);
			await refreshState();
			const newLocName = get().currentLocationName;
			const msg = `You arrived at ${newLocName || "a new location"}.`;
			toast.success("Moved", {
				description: msg,
			});
			get().addMessage(systemMessage(msg, `move-${Date.now()}`));
		} catch (error) {
			console.error("[GameStore] Failed to move player:", error);
			const errMsg = errorMessage(error, "Cannot travel there.");
			toast.error("Travel Failed", {
				description: errMsg,
			});
			get().addMessage(
				systemMessage(`Travel Failed: ${errMsg}`, `err-${Date.now()}`),
			);
			throw error;
		}
	},

	linkClues: async (id1: string, id2: string) => {
		const { sessionId, refreshState } = get();
		if (!sessionId) return;
		try {
			await apiClient.linkClues(sessionId, id1, id2);
			await refreshState();
		} catch (error) {
			console.error("[GameStore] Failed to link clues:", error);
			throw error;
		}
	},

	switchNPC: async (npcId: string) => {
		const { sessionId } = get();
		if (!sessionId) return;

		try {
			const result = await apiClient.switchNPC(sessionId, npcId);
			const npcInfo = result.npc as NPCInfo;
			const npc = toFrontendNPC(npcInfo);
			set({ activeNPC: npc });

			get().addMessage(systemMessage(`Now talking to: ${npc.name}`));
		} catch (error) {
			console.error("[GameStore] Switch NPC error:", error);
		}
	},

	saveGame: async () => {
		const { sessionId } = get();
		if (!sessionId) return;
		try {
			await apiClient.saveSession(sessionId);
			get().addMessage(
				systemMessage("Game state persisted to secure archive."),
			);
			// Return true so callers know the save succeeded
			return true;
		} catch (error) {
			console.error("[GameStore] Save error:", error);
			return false;
		}
	},

	loadGame: async (sessionId: string) => {
		try {
			const session = await apiClient.loadSession(sessionId);
			set({
				sessionId: session.session_id,
				playerName: session.player_name,
				turn: session.turn,
			});
			await get().refreshState();
			get().connectWebSocket();
		} catch (error) {
			console.error("[GameStore] Load error:", error);
			throw error;
		}
	},

	listSavedSessions: async () => {
		try {
			return await apiClient.listSessions();
		} catch (error) {
			console.error("[GameStore] List saves error:", error);
			return [];
		}
	},

	connectWebSocket: () => {
		const { sessionId } = get();
		if (!sessionId) return;

		wsService.clearListeners();

		// Connection state
		wsService.on("connection", (msg: WSOutMessage) => {
			const status = msg.payload.status as string;
			set({ isConnected: status === "connected" });
		});

		// Real-time NPC responses from other tabs/clients
		wsService.on("npc_response", (_msg: WSOutMessage) => {
			// Responses are already handled in sendAction;
			// this is for multi-client broadcasting only
		});

		// NPC switched (from another client)
		wsService.on("npc_switched", (msg: WSOutMessage) => {
			const npcInfo = msg.payload as unknown as NPCInfo;
			const npc = toFrontendNPC(npcInfo);
			set({ activeNPC: npc });
		});

		wsService.connect(sessionId);
	},

	disconnect: () => {
		wsService.disconnect();
		set({
			sessionId: null,
			isConnected: false,
			dialogueHistory: [],
			activeNPC: null,
			npcs: {},
			turn: 0,
			currency: 100,
		});
	},

	pickupObject: async (objectId: string) => {
		const { sessionId, refreshState, inventory } = get();
		if (!sessionId) return;
		try {
			await apiClient.pickupObject(sessionId, objectId);
			await refreshState();
			// Find newly added item by diffing inventories
			const newInventory = get().inventory;
			const newItem = newInventory.find(
				(i) => !inventory.some((old) => old.id === i.id),
			);
			const itemName = newItem?.name || "an item";
			toast.success("Picked Up", {
				description: `You picked up ${itemName}.`,
			});
			get().addMessage(systemMessage(`Picked up ${itemName}.`));
		} catch (error) {
			console.error("[GameStore] Pickup error:", error);
			toast.error("Pickup Failed", {
				description: errorMessage(error, "Could not pick up item."),
			});
			throw error;
		}
	},

	dropObject: async (objectId: string) => {
		const { sessionId, refreshState, inventory } = get();
		if (!sessionId) return;
		// Find the item name before dropping
		const droppedItem = inventory.find((i) => i.id === objectId);
		const itemName = droppedItem?.name || "an item";
		try {
			await apiClient.dropObject(sessionId, objectId);
			await refreshState();
			toast.success("Dropped", {
				description: `You dropped ${itemName}.`,
			});
			get().addMessage(systemMessage(`Dropped ${itemName}.`));
		} catch (error) {
			console.error("[GameStore] Drop error:", error);
			toast.error("Drop Failed", {
				description: errorMessage(error, "Could not drop item."),
			});
			throw error;
		}
	},
}));
