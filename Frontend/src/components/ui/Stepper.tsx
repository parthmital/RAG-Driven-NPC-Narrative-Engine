import { Minus, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { inputClass } from "@/components/ui/Field";

/** Numeric entry as a text field with decrement and increment buttons. */
export function Stepper({
	id,
	value,
	onChange,
	min,
	max,
	unit,
	invalid,
	disabled,
}: {
	id: string;
	value: string;
	onChange: (value: string) => void;
	min: number;
	max: number;
	unit: string;
	invalid?: boolean;
	disabled?: boolean;
}) {
	const number = Number.parseInt(value, 10);
	const step = (delta: number) => {
		const base = Number.isNaN(number) ? min : number;
		onChange(String(Math.min(max, Math.max(min, base + delta))));
	};
	const buttonClass =
		"inline-flex size-11 fine:size-9 shrink-0 items-center justify-center press rounded-md border bg-raised/40 text-muted hover:border-faint hover:text-text active:bg-raised disabled:opacity-40";

	return (
		<div className="flex items-center gap-2">
			<button
				type="button"
				aria-label={`Decrease ${unit}`}
				className={buttonClass}
				disabled={disabled || number <= min}
				onClick={() => step(-1)}
			>
				<Minus aria-hidden className="size-4" />
			</button>
			<input
				id={id}
				type="text"
				inputMode="numeric"
				pattern="[0-9]*"
				autoComplete="off"
				value={value}
				disabled={disabled}
				aria-invalid={invalid || undefined}
				aria-describedby={invalid ? `${id}-error` : undefined}
				onChange={(e) =>
					onChange(e.target.value.replace(/\D/g, "").slice(0, 3))
				}
				onKeyDown={(e) => {
					if (e.key === "ArrowUp" || e.key === "ArrowDown") {
						e.preventDefault();
						step(e.key === "ArrowUp" ? 1 : -1);
					}
				}}
				className={cn(inputClass, "w-20 text-center tabular-nums")}
			/>
			<button
				type="button"
				aria-label={`Increase ${unit}`}
				className={buttonClass}
				disabled={disabled || number >= max}
				onClick={() => step(1)}
			>
				<Plus aria-hidden className="size-4" />
			</button>
		</div>
	);
}
