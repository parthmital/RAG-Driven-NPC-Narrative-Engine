import { useEffect, useRef } from "react";
import { AlertTriangle, Info, TrendingDown, TrendingUp } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { NARRATOR_ID } from "@/config/constants";
import { cn } from "@/lib/utils";
import type { DialogueMessage } from "@/types/game";

/** Grid shared by entries: speaker gutter, then the line itself. */
const ROW =
	"grid gap-x-6 gap-y-1 sm:grid-cols-[7.5rem_minmax(0,1fr)] animate-in";

function Speaker({ name, tone }: { name?: string; tone: string }) {
	return (
		<span
			className={cn(
				"pt-1 font-ui text-label font-semibold sm:text-right",
				tone,
			)}
		>
			{name}
		</span>
	);
}

function TrustChange({ value }: { value: number }) {
	const up = value > 0;
	const Icon = up ? TrendingUp : TrendingDown;
	return (
		<span
			className={cn(
				"mt-2 inline-flex items-center gap-1.5 text-label",
				up ? "text-arcane" : "text-ember",
			)}
		>
			<Icon aria-hidden className="size-4" />
			Trust {up ? "+" : ""}
			{value}
		</span>
	);
}

function Entry({ msg }: { msg: DialogueMessage }) {
	if (msg.type === "system") {
		const isError = Boolean(msg.isError);
		const Icon = isError ? AlertTriangle : Info;
		return (
			<li className={ROW}>
				<span aria-hidden />
				<p
					className={cn(
						"flex items-start gap-2 text-label",
						isError ? "text-ember" : "text-muted",
					)}
				>
					<Icon aria-hidden className="mt-0.5 size-4 shrink-0" />
					{msg.content}
				</p>
			</li>
		);
	}

	if (msg.type === "narration") {
		return (
			<li className={ROW}>
				<span aria-hidden />
				<p className="whitespace-pre-line font-read text-read italic text-text/80">
					{msg.content}
				</p>
			</li>
		);
	}

	const isPlayer = msg.type === "player";
	return (
		<li className={ROW}>
			<Speaker
				name={isPlayer ? "You" : msg.speaker}
				tone={isPlayer ? "text-gilt" : "text-arcane"}
			/>
			<div>
				<p
					className={cn(
						"whitespace-pre-line font-read text-read",
						isPlayer ? "text-gilt/90" : "text-text",
					)}
				>
					{msg.content}
				</p>
				{msg.trustChange ? <TrustChange value={msg.trustChange} /> : null}
			</div>
		</li>
	);
}

function Thinking() {
	const addresseeId = useUIStore((s) => s.addresseeId);
	const npcs = useGameStore((s) => s.npcs);
	const name =
		addresseeId === NARRATOR_ID
			? "The narrator"
			: (npcs[addresseeId]?.name ?? "Someone");
	return (
		<li className={ROW} aria-live="polite">
			<span aria-hidden />
			<p className="flex items-center gap-2 text-label text-muted">
				<span aria-hidden className="flex gap-1">
					{[0, 1, 2].map((i) => (
						<span
							key={i}
							className="animate-thinking size-1.5 rounded-full bg-arcane"
							style={{ animationDelay: `${i * 160}ms` }}
						/>
					))}
				</span>
				{name} is considering your words
			</p>
		</li>
	);
}

/** The conversation, set like a play script. */
export function DialoguePanel() {
	const dialogueHistory = useGameStore((s) => s.dialogueHistory);
	const isProcessing = useGameStore((s) => s.isProcessing);
	const scrollRef = useRef<HTMLDivElement>(null);
	const hasScrolled = useRef(false);

	// Slash commands are instructions to the engine, not part of the story.
	const visible = dialogueHistory.filter(
		(msg) => !(msg.type === "player" && msg.content.startsWith("/")),
	);

	// Scroll only this panel: jump on first render, glide for new lines.
	useEffect(() => {
		const el = scrollRef.current;
		if (!el) return;
		el.scrollTo({
			top: el.scrollHeight,
			behavior: hasScrolled.current ? "smooth" : "auto",
		});
		hasScrolled.current = true;
	}, [visible.length, isProcessing]);

	return (
		<div ref={scrollRef} className="scroll-area min-h-0 flex-1">
			<ol
				aria-label="Conversation"
				className="mx-auto flex max-w-3xl flex-col gap-7 px-4 py-8 sm:px-8"
			>
				{visible.map((msg) => (
					<Entry key={msg.id} msg={msg} />
				))}
				{isProcessing && <Thinking />}
			</ol>
		</div>
	);
}
