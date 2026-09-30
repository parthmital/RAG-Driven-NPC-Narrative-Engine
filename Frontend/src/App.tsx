import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { MotionConfig } from "framer-motion";
import { Toaster } from "@/components/ui/sonner";
import { BootGate } from "@/components/layout/BootGate";
import { GameLayout } from "@/components/layout/GameLayout";
import { useGameStore } from "@/stores/gameStore";
import MainMenu from "@/pages/MainMenu";
import NewGame from "@/pages/NewGame";
import ScenePage from "@/pages/Index";
import WorldPage from "@/pages/World";
import NpcsPage from "@/pages/Npcs";
import JournalPage from "@/pages/Journal";
import SessionPage from "@/pages/Session";
import NotFound from "@/pages/NotFound";

const App = () => {
	const fetchMetadata = useGameStore((state) => state.fetchMetadata);

	useEffect(() => {
		fetchMetadata();
	}, [fetchMetadata]);

	return (
		<MotionConfig reducedMotion="user">
			<Toaster />
			<BootGate>
				<BrowserRouter>
					<Routes>
						<Route path="/" element={<MainMenu />} />
						<Route path="/new-game" element={<NewGame />} />
						<Route path="/session" element={<SessionPage />} />
						<Route element={<GameLayout />}>
							<Route path="/game" element={<ScenePage />} />
							<Route path="/world" element={<WorldPage />} />
							<Route path="/npcs" element={<NpcsPage />} />
							<Route path="/journal" element={<JournalPage />} />
						</Route>
						<Route path="*" element={<NotFound />} />
					</Routes>
				</BrowserRouter>
			</BootGate>
		</MotionConfig>
	);
};

export default App;
