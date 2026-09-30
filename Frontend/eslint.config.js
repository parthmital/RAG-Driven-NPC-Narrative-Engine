import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
	{ ignores: ["dist"] },
	{
		extends: [js.configs.recommended, ...tseslint.configs.recommended],
		files: ["**/*.{ts,tsx}"],
		languageOptions: {
			ecmaVersion: 2020,
			globals: globals.browser,
		},
		plugins: {
			"react-hooks": reactHooks,
			"react-refresh": reactRefresh,
		},
		rules: {
			...reactHooks.configs.recommended.rules,
			"react-refresh/only-export-components": [
				"warn",
				{ allowConstantExport: true },
			],
			"@typescript-eslint/no-unused-vars": "off",
		},
	},
	// Architecture boundaries: see ARCHITECTURE.md.
	...[
		{
			files: ["src/contracts/**", "src/types/**", "src/config/**"],
			patterns: [
				"react",
				"@/stores/*",
				"@/services/*",
				"@/pages/*",
				"@/components/*",
				"@/hooks/*",
				"@/lib/*",
			],
		},
		{
			files: ["src/services/**"],
			patterns: ["react", "@/stores/*", "@/pages/*", "@/components/*"],
		},
		{
			files: ["src/stores/**"],
			patterns: ["@/pages/*", "@/components/*", "@/hooks/*"],
		},
		{
			files: ["src/components/**", "src/hooks/**", "src/lib/**"],
			patterns: ["@/pages/*"],
		},
	].map(({ files, patterns }) => ({
		files,
		rules: {
			"no-restricted-imports": [
				"error",
				{
					patterns: [
						{
							group: patterns,
							message: "Import breaks the layer rules in ARCHITECTURE.md.",
						},
					],
				},
			],
		},
	})),
);
