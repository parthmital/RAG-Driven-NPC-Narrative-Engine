import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Tooltip } from "@/components/ui/Tooltip";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	/** Accessible name, also shown as the tooltip. */
	label: string;
	icon: ReactNode;
	tooltipSide?: "top" | "bottom" | "left";
}

/** Square 44px icon button with a custom tooltip. */
export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
	function IconButton(
		{
			label,
			icon,
			tooltipSide = "bottom",
			className,
			type = "button",
			...props
		},
		ref,
	) {
		return (
			<Tooltip label={label} side={tooltipSide}>
				<button
					ref={ref}
					type={type}
					aria-label={label}
					className={cn(
						"inline-flex size-11 shrink-0 items-center justify-center rounded-md text-muted press hover:bg-raised hover:text-text active:bg-raised/70 disabled:cursor-not-allowed disabled:opacity-40",
						className,
					)}
					{...props}
				>
					{icon}
				</button>
			</Tooltip>
		);
	},
);
