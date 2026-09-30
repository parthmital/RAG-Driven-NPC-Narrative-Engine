import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { FolderOpen, Play, Plus } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useSavedSessions } from "@/hooks/useSavedSessions";
import { Button } from "@/components/ui/Button";
import { formatRelativeTime, splitPlaceName } from "@/lib/format";
import { errorMessage } from "@/stores/mappers";

export default function MainMenu() {
	const navigate = useNavigate();
	const sessionId = useGameStore((s) => s.sessionId);
	const playerName = useGameStore((s) => s.playerName);
	const locationName = useGameStore((s) => s.currentLocationName);
	const turn = useGameStore((s) => s.turn);
	const metadata = useGameStore((s) => s.metadata);
	const loadGame = useGameStore((s) => s.loadGame);
	const { saves, isLoading, failed } = useSavedSessions();
	const [isContinuing, setIsContinuing] = useState(false);

	const latest = saves[0];
	const opening = metadata?.initial_narrator_message?.split("\n")[0];

	const continueLatest = async () => {
		setIsContinuing(true);
		try {
			await loadGame(latest.session_id);
			navigate("/game");
		} catch (error) {
			toast.error("Couldn't continue", {
				description: errorMessage(error, "The save could not be loaded."),
			});
			setIsContinuing(false);
		}
	};

	const resume = sessionId
		? {
				label: "Resume",
				detail: `${playerName} · ${splitPlaceName(locationName).place} · turn ${turn}`,
				action: () => navigate("/game"),
			}
		: latest
			? {
					label: "Continue",
					detail: `${latest.player_name} · ${splitPlaceName(latest.location_name).place} · ${formatRelativeTime(latest.created_at)}`,
					action: continueLatest,
				}
			: null;

	return (
		<main className="scroll-area h-dvh animate-fade bg-ground">
			<div className="mx-auto grid min-h-dvh max-w-6xl items-center gap-10 px-6 py-12 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] lg:gap-16">
				<div className="flex justify-center lg:justify-end">
					<img
						src="/favicon.png"
						alt="A black glass flask with gilt edges, a violet constellation glowing inside"
						className="w-40 sm:w-56 lg:w-80"
					/>
				</div>

				<div className="flex max-w-xl flex-col gap-8">
					<div className="flex flex-col gap-4">
						<h1 className="text-headline sm:text-hero">
							{metadata?.title ?? "The Obsidian Flask"}
						</h1>
						<p className="text-body text-muted sm:text-read">
							{metadata?.description ??
								"A dark fantasy text adventure where every character remembers you."}
						</p>
						{opening && (
							<blockquote className="border-l-2 border-gilt/60 pl-4 font-read text-read italic text-text/80">
								{opening}
							</blockquote>
						)}
					</div>

					<div className="flex flex-col gap-3 sm:max-w-sm">
						{resume && (
							<Button
								variant="primary"
								block
								loading={isContinuing}
								icon={<Play aria-hidden className="size-4" />}
								onClick={resume.action}
								className="justify-start py-3 text-left"
							>
								<span className="flex flex-col items-start">
									<span>{resume.label}</span>
									<span className="text-caption font-normal text-gilt-ink/75">
										{resume.detail}
									</span>
								</span>
							</Button>
						)}
						<Button
							variant={resume ? "secondary" : "primary"}
							block
							disabled={isLoading}
							icon={<Plus aria-hidden className="size-4" />}
							onClick={() => navigate("/new-game")}
						>
							New game
						</Button>
						{saves.length > 0 && (
							<Button
								variant="ghost"
								block
								icon={<FolderOpen aria-hidden className="size-4" />}
								onClick={() => navigate("/session")}
							>
								Load game
							</Button>
						)}
						{failed && (
							<p role="alert" className="text-label text-ember">
								Saved games couldn't be read. New game still works.
							</p>
						)}
					</div>
				</div>
			</div>
		</main>
	);
}
