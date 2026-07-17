import { Select } from "@pit-wall-insight/ui";

import { isConstructorId, useConstructorTheme } from "../themes/index.js";

const DEFAULT_OPTION_VALUE = "default";

/**
 * "Team" is one of the documented selectors (docs/assets/09_COMPONENT_STYLING.md
 * — "Selectors": Team, Driver, Circuit, Season, Session — "All selectors
 * should follow identical interaction patterns"), so this reuses the same
 * Select primitive as every other selector rather than a bespoke control.
 *
 * Holds no color values itself — selecting an option only calls
 * `setConstructor`, which flips `data-constructor` on <html>; the actual
 * theme colors live entirely in CSS (see packages/config/tailwind).
 */
export interface ConstructorSwitcherProps {
  /** Use in compact contexts like the header toolbar (label stays accessible, just visually hidden). */
  hideLabel?: boolean;
}

export function ConstructorSwitcher({ hideLabel = false }: ConstructorSwitcherProps) {
  const { constructorId, constructors, setConstructor } = useConstructorTheme();

  return (
    <Select
      label="Constructor"
      hideLabel={hideLabel}
      placeholder="Default"
      value={constructorId ?? DEFAULT_OPTION_VALUE}
      onValueChange={(value) => {
        setConstructor(isConstructorId(value) ? value : null);
      }}
      options={[
        { value: DEFAULT_OPTION_VALUE, label: "Default" },
        ...constructors.map((constructor) => ({
          value: constructor.id,
          label: constructor.name,
        })),
      ]}
    />
  );
}
