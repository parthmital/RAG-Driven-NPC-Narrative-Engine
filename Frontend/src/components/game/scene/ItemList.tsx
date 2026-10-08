import { useState, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import type { InventoryItem } from "@/stores/mappers";

/** Objects with one action each: take from the room or drop from the pack. */
export function ItemList({
	items,
	actionLabel,
	actionIcon,
	onAction,
	disabled,
}: {
	items: InventoryItem[];
	actionLabel: string;
	actionIcon: ReactNode;
	onAction: (id: string) => Promise<void>;
	disabled?: boolean;
}) {
	const [busyId, setBusyId] = useState<string | null>(null);

	const run = async (id: string) => {
		setBusyId(id);
		try {
			await onAction(id);
		} catch {
			// The store reports the failure.
		} finally {
			setBusyId(null);
		}
	};

	return (
		<ul className="flex flex-col divide-y">
			{items.map((item) => (
				<li
					key={item.id}
					className="flex animate-in items-start gap-3 py-3 first:pt-0"
				>
					<div className="min-w-0 flex-1">
						<p className="text-body font-medium text-text">{item.name}</p>
						<p className="line-clamp-2 text-label text-muted">
							{item.description}
						</p>
					</div>
					<button
						type="button"
						onClick={() => run(item.id)}
						disabled={disabled || busyId !== null}
						aria-label={`${actionLabel} ${item.name}`}
						className="inline-flex min-h-11 fine:min-h-9 shrink-0 items-center gap-2 press rounded-md border px-3 text-label font-medium text-muted hover:border-faint hover:text-text disabled:opacity-50"
					>
						{busyId === item.id ? (
							<Loader2 aria-hidden className="size-4 animate-spin" />
						) : (
							actionIcon
						)}
						{actionLabel}
					</button>
				</li>
			))}
		</ul>
	);
}
