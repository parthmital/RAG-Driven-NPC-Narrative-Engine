import type { ReactNode } from "react";
import { AlertCircle } from "lucide-react";

/** Visible label, control, and inline error for one form field. */
export function Field({
	id,
	label,
	hint,
	error,
	children,
}: {
	/** id of the labelled control; omit for groups that carry their own aria-label. */
	id?: string;
	label: string;
	hint?: string;
	error?: string;
	children: ReactNode;
}) {
	const Label = id ? "label" : "span";
	return (
		<div className="flex flex-col gap-2">
			<div className="flex items-baseline justify-between gap-4">
				<Label htmlFor={id} className="text-label font-medium text-text">
					{label}
				</Label>
				{hint && <span className="text-caption text-faint">{hint}</span>}
			</div>
			{children}
			{error && (
				<p
					id={id ? `${id}-error` : undefined}
					role="alert"
					className="flex items-center gap-1.5 text-label text-ember"
				>
					<AlertCircle aria-hidden className="size-4 shrink-0" />
					{error}
				</p>
			)}
		</div>
	);
}

export const inputClass =
	"min-h-11 fine:min-h-9 w-full rounded-md border bg-raised/40 px-3 text-body text-text transition-colors duration-150 hover:border-faint focus-visible:border-gilt focus-visible:outline-none aria-[invalid=true]:border-ember/70 disabled:opacity-50";
