import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { FolderOpen, LogOut, Play, Save } from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useGameStore } from "@/stores/gameStore";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";

/** Game menu, opened with the menu button or Escape during play. */
export function PauseMenu() {
	const navigate = useNavigate();
	const activeModal = useUIStore((s) => s.activeModal);
	const openModal = useUIStore((s) => s.openModal);
	const closeModal = useUIStore((s) => s.closeModal);
	const saveGame = useGameStore((s) => s.saveGame);
	const [isSaving, setIsSaving] = useState(false);
	const isOpen = activeModal === "pause";

	useEffect(() => {
		const handleKey = (e: KeyboardEvent) => {
			// Open dialogs handle their own Escape and mark it handled.
			if (e.key !== "Escape" || e.defaultPrevented || activeModal) return;
			openModal("pause");
		};
		window.addEventListener("keydown", handleKey);
		return () => window.removeEventListener("keydown", handleKey);
	}, [activeModal, openModal]);

	const save = async () => {
		setIsSaving(true);
		const saved = await saveGame();
		setIsSaving(false);
		if (saved) {
			toast.success("Game saved", {
				description: "You can load it from the title screen.",
			});
			closeModal();
		} else {
			toast.error("Couldn't save", {
				description: "The game server did not respond. Try again.",
			});
		}
	};

	const leaveTo = (path: string) => {
		closeModal();
		navigate(path);
	};

	return (
		<Modal open={isOpen} onClose={closeModal} title="Menu">
			<div className="flex flex-col gap-2 p-5">
				<Button
					variant="primary"
					block
					data-autofocus
					icon={<Play aria-hidden className="size-4" />}
					onClick={closeModal}
				>
					Resume
				</Button>
				<Button
					block
					loading={isSaving}
					icon={<Save aria-hidden className="size-4" />}
					onClick={save}
				>
					Save game
				</Button>
				<Button
					block
					icon={<FolderOpen aria-hidden className="size-4" />}
					onClick={() => leaveTo("/session")}
				>
					Load game
				</Button>
				<Button
					variant="ghost"
					block
					icon={<LogOut aria-hidden className="size-4" />}
					onClick={() => leaveTo("/")}
				>
					Title screen
				</Button>
			</div>
		</Modal>
	);
}
