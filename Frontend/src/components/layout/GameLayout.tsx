import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Menu } from "lucide-react";
import { GameNavigation } from "@/components/layout/GameNavigation";
import { PauseMenu } from "@/components/game/PauseMenu";
import { IconButton } from "@/components/ui/IconButton";
import { Tooltip } from "@/components/ui/Tooltip";
import { useGameStore } from "@/stores/gameStore";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";

function ConnectionStatus() {
	const isConnected = useGameStore((s) => s.isConnected);
	const label = isConnected ? "Live updates on" : "Live updates reconnecting";
	return (
		<Tooltip label={label}>
			<span
				tabIndex={0}
				role="status"
				aria-label={label}
				className="inline-flex size-11 items-center justify-center rounded-md"
			>
				<span
					aria-hidden
					className={cn(
						"size-2 rounded-full",
						isConnected ? "bg-arcane" : "animate-thinking bg-ember",
					)}
				/>
			</span>
		</Tooltip>
	);
}

export function GameLayout() {
	const sessionId = useGameStore((s) => s.sessionId);
	const playerName = useGameStore((s) => s.playerName);
	const openModal = useUIStore((s) => s.openModal);
	const { pathname } = useLocation();

	if (!sessionId) {
		return <Navigate to="/" replace />;
	}

	return (
		<div className="flex h-dvh flex-col bg-ground">
			<header className="flex h-14 shrink-0 items-center gap-4 border-b bg-surface px-2 sm:px-4">
				<div className="flex min-w-0 items-center gap-2 pl-2">
					<img src="/favicon.png" alt="" className="size-7" />
					<span className="hidden font-display text-title lg:inline">
						The Obsidian Flask
					</span>
				</div>
				<GameNavigation variant="top" />
				<div className="ml-auto flex items-center gap-1">
					{playerName && (
						<span className="hidden max-w-40 truncate pr-2 text-label text-muted sm:inline">
							{playerName}
						</span>
					)}
					<ConnectionStatus />
					<IconButton
						label="Menu"
						icon={<Menu aria-hidden className="size-5" />}
						onClick={() => openModal("pause")}
						tooltipSide="left"
					/>
				</div>
			</header>
			<main className="min-h-0 flex-1">
				<div key={pathname} className="h-full animate-fade">
					<Outlet />
				</div>
			</main>
			<GameNavigation variant="bottom" />
			<PauseMenu />
		</div>
	);
}
