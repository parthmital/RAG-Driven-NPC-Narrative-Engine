import { cn } from "@/lib/utils";
import type { TrustThreshold } from "@/types/game";

const MIN = -100;
const MAX = 100;
const toPercent = (value: number) =>
	((Math.min(MAX, Math.max(MIN, value)) - MIN) / (MAX - MIN)) * 100;

/**
 * Trust as a scale that grows out from neutral: violet towards trust,
 * ember towards distrust, with relationship thresholds notched in.
 */
export function TrustScale({
	name,
	trust,
	thresholds = [],
	showLabels = false,
}: {
	name: string;
	trust: number;
	thresholds?: TrustThreshold[];
	showLabels?: boolean;
}) {
	const position = toPercent(trust);
	const positive = trust >= 0;

	// The compact scale sits inside list-row buttons, so it must be phrasing content.
	const Root = showLabels ? "div" : "span";
	return (
		<Root className="block">
			<span
				role="meter"
				aria-label={`${name}'s trust in you`}
				aria-valuemin={MIN}
				aria-valuemax={MAX}
				aria-valuenow={trust}
				aria-valuetext={`${trust > 0 ? "+" : ""}${trust}`}
				className="relative block h-2 rounded-full bg-raised"
			>
				<span
					className={cn(
						"absolute inset-y-0 rounded-full transition-all duration-500 ease-out",
						positive ? "bg-arcane" : "bg-ember",
					)}
					style={
						positive
							? { left: "50%", width: `${position - 50}%` }
							: { left: `${position}%`, width: `${50 - position}%` }
					}
				/>
				<span
					aria-hidden
					className="absolute -top-1 left-1/2 h-4 w-px -translate-x-1/2 bg-faint"
				/>
				{thresholds.map((t) => (
					<span
						key={t.value}
						aria-hidden
						className={cn(
							"absolute top-0 h-2 w-0.5 -translate-x-1/2",
							t.unlocked ? "bg-gilt" : "bg-ground",
						)}
						style={{ left: `${toPercent(t.value)}%` }}
					/>
				))}
			</span>
			{showLabels && thresholds.length > 0 && (
				<ul className="relative mt-2 h-10 text-caption">
					{thresholds.map((t) => (
						<li
							key={t.value}
							className={cn(
								"absolute -translate-x-1/2 whitespace-nowrap text-center",
								t.unlocked ? "text-gilt" : "text-faint",
							)}
							style={{ left: `${toPercent(t.value)}%` }}
						>
							<span className="block">{t.label}</span>
							<span className="block tabular-nums">
								{t.value > 0 ? "+" : ""}
								{t.value}
							</span>
						</li>
					))}
				</ul>
			)}
		</Root>
	);
}
