import { NavLink } from "react-router-dom";
import { BookOpen, Map, ScrollText, Users } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
	{ to: "/game", label: "Scene", icon: ScrollText },
	{ to: "/world", label: "Map", icon: Map },
	{ to: "/npcs", label: "People", icon: Users },
	{ to: "/journal", label: "Journal", icon: BookOpen },
];

/** Primary game navigation: inline tabs on wide screens, a tab bar on phones. */
export function GameNavigation({ variant }: { variant: "top" | "bottom" }) {
	const isTop = variant === "top";
	return (
		<nav
			aria-label="Game"
			className={cn(
				isTop
					? "hidden items-center gap-1 md:flex"
					: "grid shrink-0 grid-cols-4 border-t bg-surface px-2 pb-[calc(0.75rem+env(safe-area-inset-bottom))] pt-3 md:hidden",
			)}
		>
			{NAV_ITEMS.map(({ to, label, icon: Icon }) => (
				<NavLink
					key={to}
					to={to}
					className={({ isActive }) =>
						cn(
							"transition-colors duration-150",
							isTop
								? "inline-flex min-h-11 items-center gap-2 rounded-md px-3 text-label font-medium"
								: "flex min-h-12 flex-col items-center justify-center gap-1 rounded-md text-caption font-medium active:bg-raised",
							isActive
								? isTop
									? "bg-raised text-text"
									: "text-gilt"
								: "text-muted hover:text-text",
						)
					}
				>
					<Icon aria-hidden className={isTop ? "size-4" : "size-5"} />
					{label}
				</NavLink>
			))}
		</nav>
	);
}
