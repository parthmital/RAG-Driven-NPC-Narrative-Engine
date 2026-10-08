import type { Config } from "tailwindcss";

// Palette roles (values live in src/index.css):
//   lapis night surfaces, sandstone lines, sand text, gilt = the player and
//   primary actions, arcane (turquoise tile) = NPC voices and trust,
//   ember (pomegranate) = danger, distrust, and errors.
const token = (name: string) => `hsl(var(--${name}) / <alpha-value>)`;

export default {
	content: ["./index.html", "./src/**/*.{ts,tsx}"],
	// Hover styles would otherwise stick after a tap on touch screens.
	future: { hoverOnlyWhenSupported: true },
	theme: {
		extend: {
			// Mouse and trackpad: compact controls. Touch keeps 44px targets.
			screens: { fine: { raw: "(pointer: fine)" } },
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
				display: ['"El Messiri"', "Georgia", "serif"],
				read: ["Literata", "Georgia", "serif"],
				ui: ['"Instrument Sans"', "system-ui", "sans-serif"],
			},
			fontSize: {
				caption: ["0.75rem", { lineHeight: "1rem" }],
				label: ["0.8125rem", { lineHeight: "1.125rem" }],
				body: ["0.875rem", { lineHeight: "1.375rem" }],
				read: ["1rem", { lineHeight: "1.625rem" }],
				title: ["1.25rem", { lineHeight: "1.625rem" }],
				headline: ["1.75rem", { lineHeight: "2.125rem" }],
				hero: ["2.75rem", { lineHeight: "1.1" }],
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
