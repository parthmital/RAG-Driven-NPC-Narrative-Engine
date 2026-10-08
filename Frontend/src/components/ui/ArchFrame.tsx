import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/** A pointed Persian arch, like a palace niche, framing the emblem. */
export function ArchFrame({
	children,
	className,
}: {
	children: ReactNode;
	className?: string;
}) {
	return (
		<div className={cn("relative aspect-[5/7]", className)}>
			<svg
				aria-hidden
				viewBox="0 0 100 140"
				preserveAspectRatio="none"
				fill="none"
				className="absolute inset-0 size-full"
			>
				<path
					d="M3 140V60C3 36 30 22 50 2C70 22 97 36 97 60V140"
					vectorEffect="non-scaling-stroke"
					className="fill-surface stroke-gilt/50"
				/>
				<path
					d="M9 140V62C9 41 33 28 50 11C67 28 91 41 91 62V140"
					vectorEffect="non-scaling-stroke"
					className="stroke-gilt/20"
				/>
				<path
					d="M0 139.5H100"
					vectorEffect="non-scaling-stroke"
					className="stroke-gilt/50"
				/>
			</svg>
			<div className="relative flex size-full items-end justify-center px-[16%] pb-[14%]">
				{children}
			</div>
		</div>
	);
}
