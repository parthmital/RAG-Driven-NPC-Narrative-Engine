import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<Variant, string> = {
	primary:
		"bg-gilt text-gilt-ink hover:bg-gilt/90 active:bg-gilt/80 disabled:bg-gilt/30 disabled:text-gilt-ink/70",
	secondary:
		"border border-line bg-raised/40 text-text hover:border-faint hover:bg-raised active:bg-raised/70",
	ghost: "text-muted hover:bg-raised hover:text-text active:bg-raised/70",
	danger:
		"border border-line text-muted hover:border-ember/60 hover:text-ember active:bg-ember/10",
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: Variant;
	icon?: ReactNode;
	loading?: boolean;
	block?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
	function Button(
		{
			variant = "secondary",
			icon,
			loading = false,
			block = false,
			disabled,
			className,
			children,
			type = "button",
			...props
		},
		ref,
	) {
		return (
			<button
				ref={ref}
				type={type}
				disabled={disabled || loading}
				aria-busy={loading || undefined}
				className={cn(
					"inline-flex min-h-11 select-none items-center justify-center gap-2 rounded-md px-4 text-label font-medium press disabled:cursor-not-allowed disabled:opacity-60",
					VARIANTS[variant],
					block && "w-full",
					className,
				)}
				{...props}
			>
				{loading ? (
					<Loader2 aria-hidden className="size-4 animate-spin" />
				) : (
					icon
				)}
				{children}
			</button>
		);
	},
);
