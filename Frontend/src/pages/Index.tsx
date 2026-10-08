import { PanelRight } from "lucide-react";
import { DialoguePanel } from "@/components/game/DialoguePanel";
import { PlayerInputDock } from "@/components/game/PlayerInputDock";
import { ScenePanel } from "@/components/game/scene/ScenePanel";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { splitPlaceName } from "@/lib/format";

/** Conversation with the room beside it; the room moves to a sheet below xl. */
export default function ScenePage() {
	const locationName = useGameStore((s) => s.currentLocationName);
	const activeModal = useUIStore((s) => s.activeModal);
	const openModal = useUIStore((s) => s.openModal);
	const closeModal = useUIStore((s) => s.closeModal);

	return (
		<div className="flex h-full min-h-0">
			<div className="flex min-w-0 flex-1 flex-col">
				<div className="flex items-center justify-between gap-3 border-b px-4 py-1.5 xl:hidden">
					<p className="truncate font-display text-title">
						{splitPlaceName(locationName).place}
					</p>
					<Button
						variant="ghost"
						icon={<PanelRight aria-hidden className="size-4" />}
						onClick={() => openModal("scene")}
					>
						Scene
					</Button>
				</div>
				<DialoguePanel />
				<PlayerInputDock />
			</div>
			<aside
				aria-label="Scene"
				className="hidden w-[340px] shrink-0 scroll-area border-l bg-surface xl:block"
			>
				<ScenePanel />
			</aside>
			<Modal
				open={activeModal === "scene"}
				onClose={closeModal}
				title="Scene"
				placement="right"
			>
				<ScenePanel />
			</Modal>
		</div>
	);
}
