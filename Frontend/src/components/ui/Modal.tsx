import { useEffect, useId, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { IconButton } from "@/components/ui/IconButton";

const FOCUSABLE =
	'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

interface ModalProps {
	open: boolean;
	onClose: () => void;
	title: string;
	/** "center" for dialogs, "right" for a full-height side sheet. */
	placement?: "center" | "right";
	children: ReactNode;
}

/** Dialog with backdrop, focus trap, Escape and outside-click close, and focus return. */
export function Modal({
	open,
	onClose,
	title,
	placement = "center",
	children,
}: ModalProps) {
	const titleId = useId();
	const panelRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!open) return;
		const previous = document.activeElement as HTMLElement | null;
		const panel = panelRef.current;
		const first =
			panel?.querySelector<HTMLElement>("[data-autofocus]") ??
			panel?.querySelector<HTMLElement>(FOCUSABLE);
		(first ?? panel)?.focus();
		return () => previous?.focus();
	}, [open]);

	const handleKeyDown = (event: React.KeyboardEvent) => {
		if (event.key === "Escape") {
			event.preventDefault();
			onClose();
			return;
		}
		if (event.key !== "Tab" || !panelRef.current) return;
		const items = [
			...panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE),
		];
		if (items.length === 0) return;
		const first = items[0];
		const last = items[items.length - 1];
		if (event.shiftKey && document.activeElement === first) {
			event.preventDefault();
			last.focus();
		} else if (!event.shiftKey && document.activeElement === last) {
			event.preventDefault();
			first.focus();
		}
	};

	const isSheet = placement === "right";

	return createPortal(
		<AnimatePresence>
			{open && (
				<div
					className={cn(
						"fixed inset-0 z-50 flex",
						isSheet ? "justify-end" : "items-center justify-center p-4",
					)}
					onKeyDown={handleKeyDown}
				>
					<motion.div
						aria-hidden
						className="absolute inset-0 bg-ground/80"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						transition={{ duration: 0.18 }}
						onClick={onClose}
					/>
					<motion.div
						ref={panelRef}
						role="dialog"
						aria-modal="true"
						aria-labelledby={titleId}
						tabIndex={-1}
						className={cn(
							"relative flex flex-col border bg-surface shadow-2xl shadow-black/60",
							isSheet
								? "h-full w-[min(26rem,100%)] border-y-0 border-r-0"
								: "max-h-full w-full max-w-sm rounded-xl",
						)}
						initial={isSheet ? { x: "100%" } : { opacity: 0, y: 8 }}
						animate={isSheet ? { x: 0 } : { opacity: 1, y: 0 }}
						exit={isSheet ? { x: "100%" } : { opacity: 0, y: 8 }}
						transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
					>
						<div className="flex items-center justify-between gap-2 border-b py-2 pl-5 pr-2">
							<h2 id={titleId} className="text-title">
								{title}
							</h2>
							<IconButton
								label="Close"
								icon={<X aria-hidden className="size-5" />}
								onClick={onClose}
								tooltipSide="left"
							/>
						</div>
						<div className="min-h-0 flex-1 scroll-area">{children}</div>
					</motion.div>
				</div>
			)}
		</AnimatePresence>,
		document.body,
	);
}
