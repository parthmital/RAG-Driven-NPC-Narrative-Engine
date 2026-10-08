# Design

The design system and UI decisions of The Obsidian Flask frontend (`Frontend/`). Keep this file in sync with the code it describes: tokens in [Frontend/src/index.css](Frontend/src/index.css) and [Frontend/tailwind.config.ts](Frontend/tailwind.config.ts), primitives in [Frontend/src/components/ui/](Frontend/src/components/ui/), and screens in [Frontend/src/pages/](Frontend/src/pages/). Module boundaries are in [ARCHITECTURE.md](ARCHITECTURE.md); screenshots are in the [README](README.md#screenshots).

## Brief

| Item             | Decision                                                                                                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Subject          | A dark fantasy text adventure set in a tavern district, where NPCs talk through an LLM and remember the player, styled as a Persian palace at night after Prince of Persia |
| Audience         | One player at a time, on phone, tablet, or desktop, with keyboard, mouse, or touch                                                                                         |
| Primary task     | Read the conversation and say the next thing to the right person                                                                                                           |
| Secondary tasks  | Move between rooms, take and drop objects, check who trusts you, review the journal, save and load                                                                         |
| Screens          | Boot gate, Title, New game, Scene, Map, People, Journal, Load game, Not found, plus the Menu dialog and the Scene sheet                                                    |
| Success criteria | The player always knows who is speaking, who they are addressing, where they are, and what changed; no screen scrolls the page or hides text at any width                  |

The first screen after boot is the title screen, because the player must choose to continue, start, or load. Every screen inside a game opens straight onto the tool, with no landing content.

## Palette

Colours are HSL CSS variables on `:root` in `index.css`, exposed to Tailwind by role through `token()` in `tailwind.config.ts`, so every class supports alpha (`bg-gilt/10`). There is one theme, dark (`color-scheme: dark`, `theme-color #0c0f18`).

| Token      | HSL           | Role                                                                                                           |
| ---------- | ------------- | -------------------------------------------------------------------------------------------------------------- |
| `ground`   | `224 34% 7%`  | Page background (lapis night), modal backdrop (`ground/80`)                                                    |
| `surface`  | `223 30% 10%` | Header, tab bar, side panels, dialogs, the arch niche                                                          |
| `raised`   | `222 26% 14%` | Inputs, hover and selected rows, tooltips, toasts, empty meter track                                           |
| `line`     | `34 20% 22%`  | Every border (set globally on `*`), scrollbar thumb; sandstone, so borders read as carved trim                 |
| `text`     | `38 40% 88%`  | Body text, warm desert sand                                                                                    |
| `muted`    | `35 18% 67%`  | Secondary text, inactive nav and controls                                                                      |
| `faint`    | `33 11% 52%`  | Hints, captions, placeholders, idle icons                                                                      |
| `gilt`     | `41 74% 58%`  | The player: their lines, primary actions, focus ring, caret, selection, selected tabs, the game title          |
| `gilt-ink` | `224 40% 8%`  | Text on gilt fills                                                                                             |
| `arcane`   | `173 46% 56%` | Turquoise tilework. NPCs: speaker names, the addressed person, positive trust, live connection, slash commands |
| `ember`    | `354 66% 62%` | Pomegranate. Danger, distrust, errors, invalid fields, reconnecting                                            |

Rules:

- Three accents only, each with one meaning: gilt is you, arcane is them, ember is trouble. Never use an accent for decoration.
- Surfaces step up in lightness (`ground` 6%, `surface` 9%, `raised` 13%) instead of using shadows; shadows appear only on floating layers (dialogs, tooltips, toasts).
- Surfaces carry a lapis hue (222 to 224); lines and text carry a warm sandstone hue (33 to 38): night-blue halls trimmed in carved stone and gold. The token name `arcane` is kept from the earlier violet theme to avoid churn; its colour is now turquoise.

## Type

Three families, loaded from Google Fonts in `index.html` with `display=swap` and explicit fallbacks:

| Family          | Class          | Weights              | Use                                                      |
| --------------- | -------------- | -------------------- | -------------------------------------------------------- |
| El Messiri      | `font-display` | 500, 600             | `h1` to `h3`, place names, NPC names, empty-state titles |
| Literata        | `font-read`    | 400, 600, 400 italic | Dialogue, narration (italic), descriptions, the composer |
| Instrument Sans | `font-ui`      | 400, 500, 600        | Body default, controls, labels, captions                 |

Scale (`fontSize` in `tailwind.config.ts`):

| Step       | Size / line height | Use                                                  |
| ---------- | ------------------ | ---------------------------------------------------- |
| `caption`  | 12px / 16px        | Metadata, tab bar labels, counts, tooltips           |
| `label`    | 13px / 18px        | Buttons, field labels, section labels, speaker names |
| `body`     | 14px / 22px        | Default text and inputs                              |
| `read`     | 16px / 26px        | Dialogue and narration                               |
| `title`    | 20px / 26px        | Dialog titles, NPC names, background cards           |
| `headline` | 28px / 34px        | Page titles, the current place                       |
| `hero`     | 44px / 1.1         | Title screen only, from `sm` up                      |

Body text is never below 14px, and reading text is 16px with a 1.625 line height. The scale was cut one step from an earlier 16px base, which made every screen feel zoomed in. Font size never scales with viewport width; only the title screen steps from `headline` to `hero` at `sm`, and in-game page titles stay at `headline`. Long reading text is capped at `max-w-read` (68ch) or `max-w-3xl`. Numbers that change (trust, counts, age) use `tabular-nums`.

## Spacing and layout

- Spacing uses Tailwind's 4px scale. Common rhythm: `gap-2` inside controls, `gap-3` to `gap-4` inside a section, `gap-5` between transcript entries, `gap-6` between sections. Panel padding is `p-4`; page gutters are `px-4` to `px-5` on phones and `px-8` from `sm`.
- The document never scrolls (`html`, `body` are `overflow: hidden`). Every screen is `h-dvh` or fills the game shell, and scrolls inside elements with the `.scroll-area` utility, which is `position: relative` so screen-reader text and tooltips cannot stretch the page. New scrolling panels must use `.scroll-area`, not `overflow-y-auto`.
- Fixed tracks keep text from reflowing unpredictably:

| Region                    | Size                               |
| ------------------------- | ---------------------------------- |
| Game header               | `h-14`, `h-12` on fine pointers    |
| Conversation column       | `max-w-3xl`, centred               |
| Speaker gutter            | `6.5rem`, right-aligned, from `sm` |
| Scene side panel          | `340px`, from `xl`                 |
| Scene sheet               | `min(26rem, 100%)`, below `xl`     |
| Master list (Map, People) | `20rem`, from `lg`                 |
| Dialog                    | `max-w-sm`                         |
| Toast                     | `min(22rem, 100vw - 2rem)`         |

- The bottom tab bar pads by `env(safe-area-inset-bottom)` and the viewport uses `viewport-fit=cover`, so it clears phone home indicators.

## Breakpoints

Tailwind defaults. Each breakpoint changes structure, not just spacing:

| Breakpoint    | What changes                                                                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| below `sm`    | Single column everywhere; speaker name sits above its line; headings at `headline`                                                                                                   |
| `sm` (640px)  | Speaker gutter appears beside each line; the title screen steps to `hero`; wider page gutters; name and age share a row; background cards go two-up; player name shows in the header |
| `md` (768px)  | Game navigation moves from the bottom tab bar to inline tabs in the header                                                                                                           |
| `lg` (1024px) | Map and People show list and detail side by side; title screen splits into art and actions; full title shows in the header                                                           |
| `xl` (1280px) | The Scene panel docks beside the conversation instead of opening as a sheet                                                                                                          |

`fine` (custom screen, `(pointer: fine)`): mouse and trackpad devices get 36px controls (`fine:min-h-9`, `fine:size-9`) and a 48px header; touch devices keep 44px targets.

Target range: 320px wide to wide desktop, with no horizontal scroll, including at 200% zoom.

## Components

### Primitives (`components/ui/`)

| Component      | Purpose                                                      | Variants and states                                                                                                                                                                                          |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Button`       | Every text button                                            | `primary` (gilt fill), `secondary` (bordered, default), `ghost`, `danger`; hover, active, focus-visible, disabled, `loading` (spinner replaces icon, `aria-busy`), `block`; 44px high, 36px on fine pointers |
| `IconButton`   | Icon-only actions                                            | 44px square, 36px on fine pointers; its `label` is both the accessible name and the tooltip; hover, active, disabled                                                                                         |
| `Tooltip`      | Visual label for icon controls                               | Shows on hover after 300ms and immediately on keyboard focus; `top`, `bottom`, `left`; hidden from assistive tech                                                                                            |
| `Modal`        | Dialogs and side sheets                                      | `center` (fade and rise) or `right` (slide-in sheet); backdrop, focus trap, Escape and outside-click close, focus return, `data-autofocus`                                                                   |
| `ChoiceGroup`  | Single choice from a small set, replacing radios and selects | `pills` (short labels) or `cards` (label plus description); roving focus, arrow keys, selected, invalid, disabled                                                                                            |
| `Field`        | Label, hint, control, and inline error                       | Error renders with an icon and `role="alert"`; `inputClass` styles text inputs (hover, focus, invalid, disabled)                                                                                             |
| `Stepper`      | Numeric entry (age)                                          | Text input with numeric keyboard plus decrement and increment buttons; arrow keys step; buttons disable at bounds                                                                                            |
| `EmptyState`   | What is missing and what to do                               | Icon, title, explanation, optional action                                                                                                                                                                    |
| `ArchFrame`    | Pointed Persian arch niche framing the emblem                | Title screen and boot gate; gilt outer arch on a `surface` fill, inner hairline, plinth line; the SVG is `aria-hidden`                                                                                       |
| `SectionLabel` | Panel section heading                                        | Optional count pill                                                                                                                                                                                          |
| `Toaster`      | Transient feedback (sonner, unstyled and themed)             | `success` (gilt icon), `info` (arcane), `error` (ember border); bottom right                                                                                                                                 |

### Layout (`components/layout/`)

| Component        | Purpose                                                                                                                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BootGate`       | Holds the app until the backend is ready, with the emblem in an `ArchFrame` on the girih ground; explains slow starts after 8 s and a stopped server after 90 s                                       |
| `GameLayout`     | Girih-textured header with a `gilt/20` rule (logo, gilt title, inline tabs, player name, connection dot, menu), routed content, tab bar, Menu dialog; redirects to the title screen without a session |
| `GameNavigation` | Scene, Map, People, Journal; inline tabs from `md`, a four-item tab bar below                                                                                                                         |
| `MasterDetail`   | List and detail side by side from `lg`; below, one at a time with a back button. `ListRow` marks the selected row with a gilt left rule                                                               |

### Game (`components/game/`)

| Component          | Purpose                                                                                                                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `DialoguePanel`    | The transcript as an ordered list: player lines (gilt), NPC lines (arcane name), italic narration, system notes and errors, trust changes, and a "considering your words" indicator                                                        |
| `PlayerInputDock`  | "Speak to" choice of narrator or present NPCs, an auto-growing textarea, and a gilt Send button; Enter sends, Shift+Enter breaks a line, Up and Down recall earlier lines; a leading `/` switches the field to arcane UI type for commands |
| `TrustScale`       | Trust from -100 to 100 as a bar growing from a centre notch, arcane towards trust and ember towards distrust, with relationship thresholds notched in (gilt once unlocked); `role="meter"`                                                 |
| `PauseMenu`        | Resume, Save game, Load game, Title screen; opens with the Menu button or Escape                                                                                                                                                           |
| `scene/`           | `ScenePanel` in the order a player acts: `PlaceSection` (area, turn, place, description, exits with Go), `PeopleSection` (mood, trust, Speak), `ObjectsSection`, `PlayerSection` (purse, standing, carrying)                               |
| `emotionStyles.ts` | The single table of NPC mood labels and colours                                                                                                                                                                                            |

Cards are used only for repeated items (people in the room, background choices) and for dialogs. Cards are never nested and sections are never wrapped in floating cards.

### State coverage

| State         | How it is shown                                                                                                                                                   |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hover         | One step lighter surface (`raised`) or border `faint`; only on hover-capable devices (`hoverOnlyWhenSupported`)                                                   |
| Focus-visible | 2px gilt outline, 2px offset, on every focusable element; inputs switch their border to gilt                                                                      |
| Active        | `.press` scales to 0.97 instantly; fills darken a step                                                                                                            |
| Selected      | Gilt border and `gilt/10` fill (choices), gilt left rule (list rows), `gilt/10` fill and gilt text (top tabs), gilt text (tab bar), arcane border (addressed NPC) |
| Disabled      | 40% to 60% opacity and `not-allowed` cursor; Send turns `raised` with a `faint` icon                                                                              |
| Loading       | Spinner inside the button; "Travelling..." on an exit; skeleton bars for exit names; three pulsing arcane dots while an NPC replies                               |
| Invalid       | Ember border and inline ember error after the first submit; focus moves to the first invalid field                                                                |
| Success       | Gilt toast                                                                                                                                                        |
| Empty         | `EmptyState` on Journal, People, Map, and Load game, saying what is missing and what to do                                                                        |
| Connection    | Arcane dot when live, pulsing ember dot while reconnecting                                                                                                        |

## Icons

One set: Lucide (`lucide-react`), outline style, `size-4` inline and `size-5` in icon buttons and the tab bar, always `aria-hidden` beside a visible or `aria-label` name.

| Meaning      | Icons                                                                                                                                           |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Navigation   | `ScrollText` (Scene), `Map`, `Users` (People), `BookOpen` (Journal), `ArrowLeft`, `Menu`, `PanelRight`                                          |
| Game actions | `DoorOpen` (exits), `Footprints`, `MapPin`, `MessageCircle` (speak), `Hand` (take), `ArrowDownToLine` (drop), `Coins` (purse), `SendHorizontal` |
| Session      | `Play`, `Plus`, `Save`, `FolderOpen`, `LogOut`                                                                                                  |
| Feedback     | `Loader2`, `AlertCircle`, `AlertTriangle`, `Info`, `Compass` (not found), `TrendingUp`, `TrendingDown`, `X`, `Minus`                            |

No emoji. The only decorative graphics are the `ArchFrame` outline and the `.girih` lattice texture. The only image asset is the flask emblem (`public/favicon.png`, also used at title size), with `public/og.png` for link previews.

## Motion

| Utility or setting  | Spec                                                                                                 | Use                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `.girih`            | static 48px eight-pointed star lattice, gilt stroke at 6% opacity                                    | Texture on the header, tab bar, title screen, and boot gate; never behind reading text |
| `.press`            | colour, border, opacity, transform over 150ms, `cubic-bezier(0.22, 1, 0.36, 1)`; scale 0.97 on press | Compact controls                                                                       |
| `.animate-fade`     | opacity in over 200ms                                                                                | Route changes, new room in the Scene panel, new detail in Master-Detail                |
| `.animate-in`       | rise 6px and fade over 220ms, same easing                                                            | New transcript lines                                                                   |
| `.animate-thinking` | 1.2s opacity pulse                                                                                   | NPC reply indicator, reconnecting dot                                                  |
| `Modal`             | backdrop 180ms; panel 220ms with the same easing                                                     | Dialog rise, sheet slide                                                               |
| `TrustScale`        | 500ms ease-out on the bar                                                                            | Trust changes                                                                          |
| Transcript scroll   | jump on first render, smooth for new lines, inside the panel only                                    | Conversation                                                                           |

Motion only clarifies state or arrival. `prefers-reduced-motion` reduces every CSS animation and transition to 0.01ms, and `MotionConfig reducedMotion="user"` does the same for Framer Motion.

## No browser-native UI

| Native element                                                  | Replacement                                              |
| --------------------------------------------------------------- | -------------------------------------------------------- |
| `alert`, `confirm`                                              | `Modal` and sonner toasts                                |
| `<select>`, radios                                              | `ChoiceGroup`                                            |
| `type="number"` spinner                                         | `Stepper` (text input with `inputMode="numeric"`)        |
| `title` tooltips                                                | `Tooltip`                                                |
| Validation bubbles                                              | `noValidate` on the form, `Field` inline errors          |
| `<dialog>`                                                      | `Modal` with its own backdrop, animation, and focus trap |
| `<meter>`, `<progress>`                                         | `TrustScale` and the standing scale, with `role="meter"` |
| Focus ring, selection, caret, placeholder, autofill, scrollbars | Styled in the base layer of `index.css`                  |

Real `<input>` and `<textarea>` elements remain for typing, fully restyled. An audit of [`Frontend/src`](Frontend/src) on 8 October 2026 found no `alert(`, `confirm(`, `prompt(`, `<select`, `<datalist`, `<details`, `<dialog`, `<progress`, `<meter`, native picker input types, or `title=` attributes on elements, and the only form uses `noValidate`.

## Copy and terminology

Write from the player's side, in the voice of the setting, but name controls by what they do.

| Concept                  | Term used                                                      | Not                       |
| ------------------------ | -------------------------------------------------------------- | ------------------------- |
| The four game views      | Scene, Map, People, Journal                                    | Chat, World, NPCs         |
| Choosing whom to address | Speak to, Speak, Speaking                                      | Select NPC, Switch        |
| Leaving a room           | Exits, Go, Travelling...                                       | Move, Navigate            |
| Inventory                | Carrying; actions Take and Drop                                | Inventory, Pick up        |
| Money and alignment      | Purse, Standing (Corrupt to Virtuous)                          | Currency, Moral alignment |
| Occupation               | Background                                                     | Occupation, Class         |
| Session actions          | New game, Continue, Resume, Save game, Load game, Title screen | Submit, Exit              |
| Starting                 | Who walks in?, Begin the story, Opening the door...            | Create character          |
| Waiting                  | Waking the storyteller; _Name_ is considering your words       | Loading...                |

Errors and empty states say what happened and what to do next, for example "Couldn't save. The game server did not respond. Try again." and "Saved games couldn't be read. New game still works." Field errors are instructions: "Give your character a name.", "Choose a background." Slash commands typed by the player are hidden from the transcript, because they instruct the engine and are not part of the story.

## Signature

A Persian palace at night, after Prince of Persia: lapis surfaces, sandstone trim, saffron gold, turquoise tile, and the emblem set in a pointed arch niche over a faint girih lattice. Ornament stays at the frame (header, tab bar, title screens) so it never competes with the story.

The conversation is set like a play script: a right-aligned speaker gutter, gilt for the player, arcane for NPCs, and italic Literata narration without a speaker. It matches the backend's output contract, which keeps narration and speech in separate fields, and it answers the primary question (who said what) at a glance. Everything else stays quiet so the transcript carries the screen.

## Decisions

| Decision                                                                  | Reason                                                                                                                                                 |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| One dark theme only                                                       | The setting is a palace district at night; a light theme would fight the emblem and the colour roles                                                   |
| Persian palette and ornament, kept to the frame                           | Gives the Prince of Persia feel the premise asks for without decorating the transcript, which must stay easy to read                                   |
| Smaller type scale, 36px controls on fine pointers                        | The 16px base and 44px controls made desktop feel zoomed in; touch keeps 44px targets                                                                  |
| Colour encodes who, not decoration (gilt you, arcane them, ember trouble) | The player must tell their lines, NPC lines, and problems apart without reading names                                                                  |
| Three type families with fixed roles                                      | A display face with Arabic-inspired Latin for places and people, a reading serif for the story, and a sans for controls keep story and interface apart |
| The page never scrolls; panels do                                         | Keeps the header, composer, and tab bar fixed on phones, and stops tooltips or hidden text from stretching the page                                    |
| Scene panel docks at `xl`, sheet below                                    | Below 1280px a docked 340px panel would squeeze the transcript under its reading width                                                                 |
| Bottom tab bar below `md`                                                 | Thumb reach on phones; the four views are peers                                                                                                        |
| `ChoiceGroup` for addressee, gender, and background                       | Few, visible options are faster than a dropdown and behave the same in every browser                                                                   |
| `Stepper` for age instead of a number input                               | Native spinners differ by browser and are too small to tap                                                                                             |
| Trust as a centred bar with notches                                       | Trust is signed; growing from neutral shows direction and the distance to the next threshold at once                                                   |
| Errors appear after the first submit and clear as fixed                   | No red fields before the player has tried; immediate feedback afterwards                                                                               |
| Failed turns restore the player's text                                    | A server error must not cost the player what they typed                                                                                                |
| Hover styles only on hover-capable devices                                | Prevents sticky hover after a tap on touch screens                                                                                                     |
| 44px minimum touch targets                                                | On touch, every button, row, choice, and icon button meets it (`min-h-11`, `size-11`)                                                                  |

## Verification

Checked on 8 October 2026 against the source and in Chrome at 1440x900 (fine pointer) and 390x844 (touch): title, Scene, Map, People, Journal, and the Menu dialog render with no clipped text or horizontal scroll. The screenshots in [docs/screenshots/](docs/screenshots/) show this restyle.
