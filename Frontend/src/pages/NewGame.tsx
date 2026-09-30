import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useGameStore } from "@/stores/gameStore";
import { PLAYER_AGE } from "@/config/constants";
import { errorMessage } from "@/stores/mappers";
import { Button } from "@/components/ui/Button";
import { ChoiceGroup } from "@/components/ui/ChoiceGroup";
import { Field, inputClass } from "@/components/ui/Field";
import { Stepper } from "@/components/ui/Stepper";

type Errors = Partial<Record<"name" | "age" | "gender" | "occupation", string>>;

function validate(
	name: string,
	age: string,
	gender: string,
	occupation: string,
) {
	const errors: Errors = {};
	const years = Number.parseInt(age, 10);
	if (!name.trim()) errors.name = "Give your character a name.";
	if (Number.isNaN(years) || years < PLAYER_AGE.MIN || years > PLAYER_AGE.MAX) {
		errors.age = `Age must be between ${PLAYER_AGE.MIN} and ${PLAYER_AGE.MAX}.`;
	}
	if (!gender) errors.gender = "Choose one.";
	if (!occupation) errors.occupation = "Choose a background.";
	return errors;
}

export default function NewGame() {
	const navigate = useNavigate();
	const createSession = useGameStore((s) => s.createSession);
	const metadata = useGameStore((s) => s.metadata);
	const [name, setName] = useState("");
	const [age, setAge] = useState("30");
	const [gender, setGender] = useState("");
	const [occupation, setOccupation] = useState("");
	const [submitted, setSubmitted] = useState(false);
	const [isCreating, setIsCreating] = useState(false);
	const [serverError, setServerError] = useState<string | null>(null);

	// Errors appear after the first submit and clear as the player fixes them.
	const liveErrors: Errors = submitted
		? validate(name, age, gender, occupation)
		: {};

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		setSubmitted(true);
		if (Object.keys(validate(name, age, gender, occupation)).length) {
			// Move focus to the first field that needs attention once errors render.
			requestAnimationFrame(() => {
				const invalid = document.querySelector<HTMLElement>(
					'[aria-invalid="true"]',
				);
				(
					invalid?.querySelector<HTMLElement>('[role="radio"]') ?? invalid
				)?.focus();
			});
			return;
		}

		setIsCreating(true);
		setServerError(null);
		try {
			await createSession({
				name: name.trim(),
				gender,
				age: Number.parseInt(age, 10),
				occupation,
			});
			navigate("/game");
		} catch (error) {
			setServerError(
				errorMessage(error, "The game server did not respond. Try again."),
			);
			setIsCreating(false);
		}
	};

	if (!metadata) {
		return (
			<main className="flex h-dvh items-center justify-center gap-2 bg-ground text-muted">
				<Loader2 aria-hidden className="size-4 animate-spin" />
				Loading character options
			</main>
		);
	}

	const genders = (metadata.character_options?.genders ?? []).map((g) => ({
		value: g,
		label: g,
	}));
	const occupations = (metadata.character_options?.occupations ?? []).map(
		(o) => ({ value: o.name, label: o.name, description: o.desc }),
	);

	return (
		<main className="scroll-area h-dvh animate-fade bg-ground">
			<form
				noValidate
				onSubmit={handleSubmit}
				className="mx-auto flex max-w-2xl flex-col gap-10 px-5 py-8 sm:py-14"
			>
				<div className="flex flex-col gap-4">
					<Button
						variant="ghost"
						icon={<ArrowLeft aria-hidden className="size-4" />}
						onClick={() => navigate("/")}
						className="-ml-3 self-start"
					>
						Title screen
					</Button>
					<h1 className="text-headline sm:text-hero">Who walks in?</h1>
					<p className="text-body text-muted sm:text-read">
						The people of the tavern judge you by what they see. Your background
						shapes how they speak to you.
					</p>
				</div>

				<div className="grid gap-8 sm:grid-cols-[minmax(0,1fr)_auto]">
					<Field id="name" label="Name" error={liveErrors.name}>
						<input
							id="name"
							type="text"
							autoComplete="off"
							maxLength={40}
							value={name}
							onChange={(e) => setName(e.target.value)}
							placeholder="Mara Voss"
							disabled={isCreating}
							aria-invalid={Boolean(liveErrors.name) || undefined}
							aria-describedby={liveErrors.name ? "name-error" : undefined}
							className={inputClass}
						/>
					</Field>
					<Field id="age" label="Age" error={liveErrors.age}>
						<Stepper
							id="age"
							value={age}
							onChange={setAge}
							min={PLAYER_AGE.MIN}
							max={PLAYER_AGE.MAX}
							unit="age"
							invalid={Boolean(liveErrors.age)}
							disabled={isCreating}
						/>
					</Field>
				</div>

				<Field label="Gender" error={liveErrors.gender}>
					<ChoiceGroup
						label="Gender"
						choices={genders}
						value={gender}
						onChange={setGender}
						invalid={Boolean(liveErrors.gender)}
						disabled={isCreating}
					/>
				</Field>

				<Field label="Background" error={liveErrors.occupation}>
					<ChoiceGroup
						label="Background"
						variant="cards"
						choices={occupations}
						value={occupation}
						onChange={setOccupation}
						invalid={Boolean(liveErrors.occupation)}
						disabled={isCreating}
					/>
				</Field>

				<div className="flex flex-col gap-3 border-t pt-6">
					{serverError && (
						<p role="alert" className="text-label text-ember">
							Couldn't start the game: {serverError}
						</p>
					)}
					<Button
						type="submit"
						variant="primary"
						loading={isCreating}
						className="sm:self-end sm:px-8"
					>
						{isCreating ? "Opening the door…" : "Begin the story"}
					</Button>
				</div>
			</form>
		</main>
	);
}
