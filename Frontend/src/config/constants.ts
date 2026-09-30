/**
 * Global application constants — central repository for all tunables.
 */

export const API_BASE_URL = "/api/game";

export const WS_CONFIG = {
	RECONNECT_MAX_ATTEMPTS: 5,
	HEARTBEAT_INTERVAL_MS: 30000,
	RECONNECT_BASE_DELAY_MS: 1000,
	RECONNECT_MAX_DELAY_MS: 30000,
};

export const GAME_CONSTANTS = {
	INITIAL_MORAL_ALIGNMENT: 50,
};

/** Speaker id the backend uses for the narrator. */
export const NARRATOR_ID = "narrator";

export const PLAYER_AGE = { MIN: 18, MAX: 120 };
