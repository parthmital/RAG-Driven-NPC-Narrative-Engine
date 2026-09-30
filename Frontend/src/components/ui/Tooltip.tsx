import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const SIDES = {
	top: "bottom-full left-1/2 mb-2 -translate-x-1/2",
	bottom: "top-full left-1/2 mt-2 -translate-x-1/2",
	left: "right-full top-1/2 mr-2 -translate-y-1/2",
};

/**
 * Visual label shown on hover and keyboard focus. The wrapped control must
 * carry its own accessible name; the tooltip is hidden from assistive tech.
 */
export function Tooltip({
	label,
	side = "bottom",
	children,
}: {
	label: string;
	side?: keyof typeof SIDES;
	children: ReactNode;
}) {
	return (
		<span className="group/tip relative inline-flex">
			{children}
			<span
				aria-hidden
				className={cn(
					"pointer-events-none absolute z-50 whitespace-nowrap rounded-md border bg-raised px-2 py-1 text-caption text-text opacity-0 shadow-lg shadow-black/40 transition-opacity delay-0 duration-150 group-hover/tip:opacity-100 group-hover/tip:delay-300 group-has-[:focus-visible]/tip:opacity-100",
					SIDES[side],
				)}
			>
				{label}
			</span>
		</span>
	);
}
