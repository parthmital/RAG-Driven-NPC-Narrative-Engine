import { create } from "zustand";
import { NARRATOR_ID } from "@/config/constants";

type ModalId = "pause" | "scene";

interface UIState {
	activeModal: ModalId | null;
	openModal: (id: ModalId) => void;
	closeModal: () => void;

	/** Who the player is speaking to: an NPC id, or "narrator". */
	addresseeId: string;
	setAddressee: (id: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
	activeModal: null,
	openModal: (id) => set({ activeModal: id }),
	closeModal: () => set({ activeModal: null }),

	addresseeId: NARRATOR_ID,
	setAddressee: (id) => set({ addresseeId: id }),
}));
