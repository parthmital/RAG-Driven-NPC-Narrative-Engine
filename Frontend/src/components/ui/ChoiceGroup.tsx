import { useRef } from "react";
import { cn } from "@/lib/utils";

export interface Choice {
	value: string;
	label: string;
	description?: string;
}

interface ChoiceGroupProps {
	/** Accessible name of the group. */
	label: string;
	choices: Choice[];
	value: string | null;
	onChange: (value: string) => void;
	/** "pills" for short options in a row, "cards" for options with descriptions. */
	variant?: "pills" | "cards";
	disabled?: boolean;
	invalid?: boolean;
	className?: string;
}

/** Custom radio group with roving focus and arrow-key selection. */
export function ChoiceGroup({
	label,
	choices,
	value,
	onChange,
	variant = "pills",
	disabled = false,
	invalid = false,
	className,
}: ChoiceGroupProps) {
	const refs = useRef<(HTMLButtonElement | null)[]>([]);
	const selectedIndex = choices.findIndex((c) => c.value === value);
	const focusIndex = selectedIndex === -1 ? 0 : selectedIndex;

	const move = (from: number, step: number) => {
		const next = (from + step + choices.length) % choices.length;
		onChange(choices[next].value);
		refs.current[next]?.focus();
	};

	const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
		if (event.key === "ArrowRight" || event.key === "ArrowDown") {
			event.preventDefault();
			move(index, 1);
		} else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
			event.preventDefault();
			move(index, -1);
		}
	};

	return (
		<div className={className}>
			<div
				role="radiogroup"
				aria-label={label}
				aria-invalid={invalid || undefined}
				className={cn(
					variant === "pills"
						? "flex flex-wrap gap-2"
						: "grid gap-3 sm:grid-cols-2",
				)}
			>
				{choices.map((choice, index) => {
					const checked = choice.value === value;
					return (
						<button
							key={choice.value}
							ref={(el) => (refs.current[index] = el)}
							type="button"
							role="radio"
							aria-checked={checked}
							tabIndex={index === focusIndex ? 0 : -1}
							disabled={disabled}
							onClick={() => onChange(choice.value)}
							onKeyDown={(e) => handleKeyDown(e, index)}
							className={cn(
								"press rounded-md border text-left disabled:cursor-not-allowed disabled:opacity-50",
								variant === "pills"
									? "min-h-11 fine:min-h-9 whitespace-nowrap px-4 text-label font-medium"
									: "flex min-h-24 flex-col gap-1 p-4",
								checked
									? "border-gilt bg-gilt/10 text-text"
									: cn(
											"bg-raised/30 text-muted hover:border-faint hover:text-text",
											invalid && "border-ember/60",
										),
							)}
						>
							{variant === "cards" ? (
								<>
									<span className="flex items-center justify-between gap-3">
										<span className="font-display text-title">
											{choice.label}
										</span>
										<span
											aria-hidden
											className={cn(
												"size-4 shrink-0 rounded-full border-2 transition-colors",
												checked
													? "border-gilt bg-gilt shadow-[inset_0_0_0_3px_hsl(var(--surface))]"
													: "border-faint",
											)}
										/>
									</span>
									{choice.description && (
										<span className="text-label text-muted">
											{choice.description}
										</span>
									)}
								</>
							) : (
								choice.label
							)}
						</button>
					);
				})}
			</div>
		</div>
	);
}
