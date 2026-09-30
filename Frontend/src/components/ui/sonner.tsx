import { Toaster as Sonner } from "sonner";

export function Toaster() {
	return (
		<Sonner
			theme="dark"
			position="bottom-right"
			toastOptions={{
				unstyled: true,
				classNames: {
					toast:
						"flex w-[min(22rem,calc(100vw-2rem))] items-start gap-3 rounded-lg border bg-raised p-4 font-ui text-body text-text shadow-xl shadow-black/50",
					title: "font-medium",
					description: "mt-0.5 text-label text-muted",
					success: "[&_[data-icon]]:text-gilt",
					info: "[&_[data-icon]]:text-arcane",
					error: "border-ember/40 [&_[data-icon]]:text-ember",
				},
			}}
		/>
	);
}
