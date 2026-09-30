import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/** Says what is missing and, when possible, what to do next. */
export function EmptyState({
	icon,
	title,
	children,
	action,
	className,
}: {
	icon: ReactNode;
	title: string;
	children?: ReactNode;
	action?: ReactNode;
	className?: string;
}) {
	return (
		<div
			className={cn(
				"flex flex-col items-center justify-center gap-3 px-6 py-12 text-center",
				className,
			)}
		>
			<span className="text-faint [&>svg]:size-7">{icon}</span>
			<p className="font-display text-title">{title}</p>
			{children && <p className="max-w-sm text-body text-muted">{children}</p>}
			{action && <div className="mt-2">{action}</div>}
		</div>
	);
}

/** Small heading for a panel section. */
export function SectionLabel({
	id,
	children,
	count,
}: {
	id?: string;
	children: ReactNode;
	count?: number;
}) {
	return (
		<h3
			id={id}
			className="flex items-center gap-2 font-ui text-label font-semibold text-muted"
		>
			{children}
			{count !== undefined && (
				<span className="rounded-full bg-raised px-2 text-caption tabular-nums text-faint">
					{count}
				</span>
			)}
		</h3>
	);
}
