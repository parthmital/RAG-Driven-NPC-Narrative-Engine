import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft, FolderOpen, Loader2 } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { useSavedSessions } from "@/hooks/useSavedSessions";
import { errorMessage } from "@/stores/mappers";
import { formatRelativeTime, splitPlaceName } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

/** Saved games, newest first. Reachable from the title screen and the game menu. */
export default function SessionPage() {
	const navigate = useNavigate();
	const loadGame = useGameStore((s) => s.loadGame);
	const inGame = useGameStore((s) => Boolean(s.sessionId));
	const { saves, isLoading, failed } = useSavedSessions();
	const [loadingId, setLoadingId] = useState<string | null>(null);

	const load = async (id: string) => {
		setLoadingId(id);
		try {
			await loadGame(id);
			navigate("/game");
		} catch (error) {
			toast.error("Couldn't load that save", {
				description: errorMessage(error, "The save may be damaged."),
			});
			setLoadingId(null);
		}
	};

	return (
		<main className="scroll-area h-dvh animate-fade bg-ground">
			<div className="mx-auto flex max-w-3xl flex-col gap-8 px-5 py-8 sm:py-14">
				<div className="flex flex-col gap-4">
					<Button
						variant="ghost"
						icon={<ArrowLeft aria-hidden className="size-4" />}
						onClick={() => navigate(inGame ? "/game" : "/")}
						className="-ml-3 self-start"
					>
						{inGame ? "Back to the game" : "Title screen"}
					</Button>
					<h1 className="text-headline">Load game</h1>
				</div>

				{isLoading ? (
					<p className="flex items-center gap-2 text-muted">
						<Loader2 aria-hidden className="size-4 animate-spin" /> Reading
						saved games
					</p>
				) : failed ? (
					<EmptyState
						icon={<FolderOpen aria-hidden />}
						title="Saves unavailable"
					>
						The game server didn't return your saved games. Check that it is
						running, then reopen this page.
					</EmptyState>
				) : saves.length === 0 ? (
					<EmptyState
						icon={<FolderOpen aria-hidden />}
						title="No saved games"
						action={
							<Button variant="primary" onClick={() => navigate("/new-game")}>
								Start a new game
							</Button>
						}
					>
						Games save automatically after every turn.
					</EmptyState>
				) : (
					<ul className="flex flex-col">
						{saves.map((save) => (
							<li
								key={save.session_id}
								className="flex flex-wrap items-center gap-x-6 gap-y-3 border-t py-5"
							>
								<div className="min-w-0 flex-1">
									<p className="flex items-center gap-3">
										<span className="font-display text-title">
											{save.player_name}
										</span>
										<span
											className={cn(
												"rounded-full px-2 text-caption",
												save.is_auto
													? "bg-raised text-muted"
													: "bg-gilt/15 text-gilt",
											)}
										>
											{save.is_auto ? "Autosave" : "Saved"}
										</span>
									</p>
									<p className="text-label text-muted">
										{splitPlaceName(save.location_name).place} · turn{" "}
										{save.turn} · {formatRelativeTime(save.created_at)}
									</p>
								</div>
								<Button
									onClick={() => load(save.session_id)}
									loading={loadingId === save.session_id}
									disabled={loadingId !== null}
									aria-label={`Load ${save.player_name}, turn ${save.turn}`}
								>
									Load
								</Button>
							</li>
						))}
					</ul>
				)}
			</div>
		</main>
	);
}
