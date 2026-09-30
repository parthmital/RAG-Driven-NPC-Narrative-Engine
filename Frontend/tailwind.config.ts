import type { Config } from "tailwindcss";

// Palette roles (values live in src/index.css):
//   obsidian surfaces, vellum text, gilt = the player and primary actions,
//   arcane = NPC voices and trust, ember = danger, distrust, and errors.
const token = (name: string) => `hsl(var(--${name}) / <alpha-value>)`;

export default {
	content: ["./index.html", "./src/**/*.{ts,tsx}"],
	// Hover styles would otherwise stick after a tap on touch screens.
	future: { hoverOnlyWhenSupported: true },
	theme: {
		extend: {
			colors: {
				ground: token("ground"),
				surface: token("surface"),
				raised: token("raised"),
				line: token("line"),
				text: token("text"),
				muted: token("muted"),
				faint: token("faint"),
				gilt: { DEFAULT: token("gilt"), ink: token("gilt-ink") },
				arcane: token("arcane"),
				ember: token("ember"),
			},
			fontFamily: {
				display: ['"Cormorant Garamond"', "Georgia", "serif"],
				read: ["Literata", "Georgia", "serif"],
				ui: ['"Instrument Sans"', "system-ui", "sans-serif"],
			},
			fontSize: {
				caption: ["0.8125rem", { lineHeight: "1.25rem" }],
				label: ["0.875rem", { lineHeight: "1.25rem" }],
				body: ["1rem", { lineHeight: "1.5rem" }],
				read: ["1.125rem", { lineHeight: "1.85rem" }],
				title: ["1.625rem", { lineHeight: "2rem" }],
				headline: ["2.25rem", { lineHeight: "2.5rem" }],
				hero: ["3.5rem", { lineHeight: "1" }],
			},
			maxWidth: {
				read: "68ch",
			},
			transitionTimingFunction: {
				out: "cubic-bezier(0.22, 1, 0.36, 1)",
			},
		},
	},
} satisfies Config;
