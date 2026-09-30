import type { ReactNode } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

/**
 * List beside detail on wide screens. Below lg only one shows at a time:
 * the list until something is opened, then the detail with a back button.
 */
export function MasterDetail({
	listLabel,
	list,
	detail,
	detailKey,
	detailOpen,
	onBack,
}: {
	listLabel: string;
	list: ReactNode;
	detail: ReactNode;
	/** Identity of the shown detail; a new one fades in scrolled to the top. */
	detailKey?: string;
	/** Whether the detail is showing on narrow screens. */
	detailOpen: boolean;
	onBack: () => void;
}) {
	return (
		<div className="grid h-full min-h-0 lg:grid-cols-[22rem_minmax(0,1fr)]">
			<nav
				aria-label={listLabel}
				className={cn(
					"min-h-0 scroll-area border-r bg-surface",
					detailOpen && "hidden lg:block",
				)}
			>
				{list}
			</nav>
			<section
				key={detailKey}
				className={cn("min-h-0 scroll-area", !detailOpen && "hidden lg:block")}
			>
				<div className="mx-auto flex max-w-3xl animate-fade flex-col gap-8 px-5 py-6 sm:px-10 sm:py-10">
					<Button
						variant="ghost"
						icon={<ArrowLeft aria-hidden className="size-4" />}
						onClick={onBack}
						className="-ml-3 self-start lg:hidden"
					>
						{listLabel}
					</Button>
					{detail}
				</div>
			</section>
		</div>
	);
}

/** One selectable row in a MasterDetail list. */
export function ListRow({
	selected,
	onSelect,
	children,
}: {
	selected: boolean;
	onSelect: () => void;
	children: ReactNode;
}) {
	return (
		<li>
			<button
				type="button"
				aria-current={selected || undefined}
				onClick={onSelect}
				className={cn(
					"flex w-full flex-col gap-1 border-b border-l-2 px-5 py-4 text-left transition-colors duration-150",
					selected
						? "border-l-gilt bg-raised"
						: "border-l-transparent hover:bg-raised/50 active:bg-raised",
				)}
			>
				{children}
			</button>
		</li>
	);
}
