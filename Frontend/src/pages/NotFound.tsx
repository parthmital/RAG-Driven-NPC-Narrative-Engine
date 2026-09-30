import { useNavigate } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

export default function NotFound() {
	const navigate = useNavigate();
	return (
		<main className="flex h-dvh animate-fade items-center justify-center bg-ground">
			<EmptyState
				icon={<Compass aria-hidden />}
				title="The trail goes cold"
				action={
					<Button variant="primary" onClick={() => navigate("/")}>
						Title screen
					</Button>
				}
			>
				There is no page at this address.
			</EmptyState>
		</main>
	);
}
