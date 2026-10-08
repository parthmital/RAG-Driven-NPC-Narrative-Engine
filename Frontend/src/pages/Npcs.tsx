import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageCircle, Users } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { toTitleCase } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { EmptyState, SectionLabel } from "@/components/ui/EmptyState";
import { ListRow, MasterDetail } from "@/components/layout/MasterDetail";
import { TrustScale } from "@/components/game/TrustScale";
import { emotionOf } from "@/components/game/emotionStyles";
import type { NPC } from "@/types/game";

function PersonDetail({ npc }: { npc: NPC }) {
	const navigate = useNavigate();
	const currentLocation = useGameStore((s) => s.currentLocation);
	const setAddressee = useUIStore((s) => s.setAddressee);
	const emotion = emotionOf(npc.emotionalState);
	const isHere = npc.locationId === currentLocation;

	const talk = () => {
		setAddressee(npc.id);
		navigate("/game");
	};

	return (
		<>
			<header className="flex flex-col gap-3">
				<h1 className="text-headline text-arcane">{npc.name}</h1>
				{npc.title && <p className="text-read text-muted">{npc.title}.</p>}
				{isHere ? (
					<Button
						variant="primary"
						icon={<MessageCircle aria-hidden className="size-4" />}
						onClick={talk}
						className="self-start"
					>
						Speak to {npc.name}
					</Button>
				) : (
					<p className="text-label text-muted">
						Last seen at {toTitleCase(npc.locationId ?? "an unknown place")}. Go
						there to speak with them.
					</p>
				)}
			</header>

			<dl className="grid grid-cols-2 gap-6 sm:grid-cols-3">
				<div>
					<dt className="text-caption text-faint">Mood</dt>
					<dd className={`font-display text-title ${emotion.color}`}>
						{emotion.label}
					</dd>
				</div>
				<div>
					<dt className="text-caption text-faint">Relationship</dt>
					<dd className="font-display text-title capitalize">
						{npc.relationshipTier}
					</dd>
				</div>
				<div>
					<dt className="text-caption text-faint">Trust</dt>
					<dd className="font-display text-title lining-nums tabular-nums">
						{npc.trust > 0 ? "+" : ""}
						{npc.trust}
					</dd>
				</div>
			</dl>

			<div className="flex flex-col gap-4">
				<SectionLabel>Trust in you</SectionLabel>
				<TrustScale
					name={npc.name}
					trust={npc.trust}
					thresholds={npc.trustThresholds}
					showLabels
				/>
			</div>

			{npc.description && (
				<div className="flex flex-col gap-3">
					<SectionLabel>What you know</SectionLabel>
					<p className="font-read text-read text-text/85">{npc.description}</p>
				</div>
			)}
		</>
	);
}

export default function NpcsPage() {
	const npcs = useGameStore((s) => s.npcs);
	const currentLocation = useGameStore((s) => s.currentLocation);
	const people = Object.values(npcs);
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [detailOpen, setDetailOpen] = useState(false);
	const selected = people.find((n) => n.id === selectedId) ?? people[0];

	if (people.length === 0) {
		return (
			<EmptyState icon={<Users aria-hidden />} title="No one met yet">
				People you meet on your travels appear here with how they feel about
				you.
			</EmptyState>
		);
	}

	return (
		<MasterDetail
			listLabel="Everyone you've met"
			detailKey={selected?.id}
			detailOpen={detailOpen}
			onBack={() => setDetailOpen(false)}
			list={
				<ul>
					{people.map((npc) => {
						const emotion = emotionOf(npc.emotionalState);
						return (
							<ListRow
								key={npc.id}
								selected={selected?.id === npc.id}
								onSelect={() => {
									setSelectedId(npc.id);
									setDetailOpen(true);
								}}
							>
								<span className="flex items-baseline justify-between gap-3">
									<span className="font-display text-title text-arcane">
										{npc.name}
									</span>
									<span className={`text-label ${emotion.color}`}>
										{emotion.label}
									</span>
								</span>
								<span className="text-label text-muted">
									{npc.locationId === currentLocation
										? "Here with you"
										: toTitleCase(npc.locationId ?? "")}
								</span>
								<span className="mt-2 block">
									<TrustScale
										name={npc.name}
										trust={npc.trust}
										thresholds={npc.trustThresholds}
									/>
								</span>
							</ListRow>
						);
					})}
				</ul>
			}
			detail={selected && <PersonDetail npc={selected} />}
		/>
	);
}
