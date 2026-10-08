import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { SendHorizontal } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { NARRATOR_ID } from "@/config/constants";
import { ChoiceGroup } from "@/components/ui/ChoiceGroup";
import { cn } from "@/lib/utils";

const HISTORY_LIMIT = 50;

/** Who to address and what to say. */
export function PlayerInputDock() {
	const [input, setInput] = useState("");
	const [history, setHistory] = useState<string[]>([]);
	const [historyIndex, setHistoryIndex] = useState(-1);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	const isProcessing = useGameStore((s) => s.isProcessing);
	const sendAction = useGameStore((s) => s.sendAction);
	const npcs = useGameStore((s) => s.npcs);
	const currentLocation = useGameStore((s) => s.currentLocation);
	const addresseeId = useUIStore((s) => s.addresseeId);
	const setAddressee = useUIStore((s) => s.setAddressee);

	const present = Object.values(npcs).filter(
		(npc) => npc.id !== NARRATOR_ID && npc.locationId === currentLocation,
	);
	const addressee = present.find((npc) => npc.id === addresseeId);

	// Someone who has left the room can no longer be addressed.
	useEffect(() => {
		if (addresseeId !== NARRATOR_ID && !addressee) setAddressee(NARRATOR_ID);
	}, [addresseeId, addressee, setAddressee]);

	// Grow with the text up to the CSS max height.
	useLayoutEffect(() => {
		const el = textareaRef.current;
		if (!el) return;
		el.style.height = "auto";
		el.style.height = `${el.scrollHeight}px`;
	}, [input]);

	const send = async () => {
		const text = input.trim();
		if (!text || isProcessing) return;
		setHistory((prev) => [text, ...prev].slice(0, HISTORY_LIMIT));
		setHistoryIndex(-1);
		setInput("");
		try {
			await sendAction(text, addresseeId);
		} catch {
			// The store explains the failure in the transcript; keep the words.
			setInput((current) => current || text);
		}
		textareaRef.current?.focus();
	};

	const recall = (index: number) => {
		setHistoryIndex(index);
		setInput(index === -1 ? "" : history[index]);
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
			e.preventDefault();
			void send();
			return;
		}
		// Browse earlier lines only while not editing a draft.
		const browsing = input === "" || historyIndex !== -1;
		if (e.key === "ArrowUp" && browsing && history.length) {
			e.preventDefault();
			recall(Math.min(historyIndex + 1, history.length - 1));
		} else if (e.key === "ArrowDown" && historyIndex !== -1) {
			e.preventDefault();
			recall(historyIndex - 1);
		}
	};

	const isCommand = input.startsWith("/");
	const choices = [
		{ value: NARRATOR_ID, label: "Narrator" },
		...present.map((npc) => ({ value: npc.id, label: npc.name })),
	];

	return (
		<div className="border-t bg-surface/80 px-4 pb-4 pt-3 sm:px-8">
			<div className="mx-auto flex max-w-3xl flex-col gap-3">
				<div className="flex flex-wrap items-center gap-x-3 gap-y-2">
					<span aria-hidden className="text-label text-muted">
						Speak to
					</span>
					<ChoiceGroup
						label="Speak to"
						choices={choices}
						value={addresseeId}
						onChange={setAddressee}
						disabled={isProcessing}
					/>
				</div>
				<div
					className={cn(
						"flex items-end gap-2 rounded-lg border bg-raised/50 p-1.5 pl-4 transition-colors focus-within:border-gilt",
						isCommand && "focus-within:border-arcane",
					)}
				>
					<label htmlFor="player-input" className="sr-only">
						Your words
					</label>
					<textarea
						id="player-input"
						ref={textareaRef}
						value={input}
						rows={1}
						onChange={(e) => {
							setInput(e.target.value);
							setHistoryIndex(-1);
						}}
						onKeyDown={handleKeyDown}
						placeholder={
							addressee
								? `Say something to ${addressee.name}…`
								: "Say or do something…"
						}
						className={cn(
							"max-h-40 min-h-11 flex-1 resize-none bg-transparent py-2.5 font-read text-read text-text focus-visible:outline-none",
							isCommand && "font-ui text-arcane",
						)}
					/>
					<button
						type="button"
						aria-label="Send"
						onClick={() => void send()}
						disabled={!input.trim() || isProcessing}
						className="inline-flex size-11 fine:size-9 shrink-0 items-center justify-center press rounded-md bg-gilt text-gilt-ink hover:bg-gilt/90 active:bg-gilt/80 disabled:bg-raised disabled:text-faint"
					>
						<SendHorizontal aria-hidden className="size-5" />
					</button>
				</div>
			</div>
		</div>
	);
}
