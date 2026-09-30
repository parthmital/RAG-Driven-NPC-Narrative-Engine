import { MessageCircle } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";
import { SectionLabel } from "@/components/ui/EmptyState";
import { TrustScale } from "@/components/game/TrustScale";
import { emotionOf } from "@/components/game/emotionStyles";

/** People in the room, their mood and trust, and who is being addressed. */
export function PeopleSection() {
	const npcs = useGameStore((s) => s.npcs);
	const currentLocation = useGameStore((s) => s.currentLocation);
	const addresseeId = useUIStore((s) => s.addresseeId);
	const setAddressee = useUIStore((s) => s.setAddressee);
	const closeModal = useUIStore((s) => s.closeModal);

	const present = Object.values(npcs).filter(
		(npc) => npc.locationId === currentLocation,
	);

	return (
		<section aria-labelledby="people-heading" className="flex flex-col gap-3">
			<SectionLabel id="people-heading" count={present.length}>
				People here
			</SectionLabel>
			{present.length === 0 ? (
				<p className="text-body text-muted">No one else is here.</p>
			) : (
				<ul className="flex flex-col gap-2">
					{present.map((npc) => {
						const emotion = emotionOf(npc.emotionalState);
						const addressed = npc.id === addresseeId;
						return (
							<li
								key={npc.id}
								className={cn(
									"flex flex-col gap-3 rounded-lg border p-3 transition-colors",
									addressed ? "border-arcane/50 bg-arcane/5" : "bg-raised/30",
								)}
							>
								<div className="flex items-start justify-between gap-3">
									<div className="min-w-0">
										<p className="font-display text-title text-arcane">
											{npc.name}
										</p>
										<p className="text-label">
											<span className={emotion.color}>{emotion.label}</span>
											<span className="text-faint">
												{" "}
												· {npc.trust > 0 ? "+" : ""}
												{npc.trust} trust
											</span>
										</p>
									</div>
									<button
										type="button"
										aria-pressed={addressed}
										onClick={() => {
											setAddressee(npc.id);
											closeModal();
										}}
										className={cn(
											"press inline-flex min-h-11 shrink-0 items-center gap-2 rounded-md px-3 text-label font-medium",
											addressed
												? "text-arcane"
												: "text-muted hover:bg-raised hover:text-text",
										)}
									>
										<MessageCircle aria-hidden className="size-4" />
										{addressed ? "Speaking" : "Speak"}
									</button>
								</div>
								<TrustScale
									name={npc.name}
									trust={npc.trust}
									thresholds={npc.trustThresholds}
								/>
							</li>
						);
					})}
				</ul>
			)}
		</section>
	);
}
