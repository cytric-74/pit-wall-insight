import { Features, Hero, Statistics } from "@pit-wall-insight/ui";

import { FEATURES } from "../constants/features.js";
import { STATISTICS } from "../constants/statistics.js";

/**
 * Only the Hero, Features, and Statistics sections — no standings, race
 * lists, or other Mission Control content yet (out of scope for this task).
 */
export function MissionControlPage() {
  return (
    <>
      <Hero
        eyebrow="Mission Control"
        title="Every lap. Every decision. Understood."
        description="Formula One telemetry, strategy, and race intelligence in one engineering-grade analytics platform."
        stats={[
          { label: "Seasons", value: "75" },
          { label: "Drivers", value: "20" },
          { label: "Constructors", value: "10" },
          { label: "Circuits", value: "24" },
        ]}
        actions={[
          { label: "Explore season", href: "/season", variant: "primary" },
          { label: "View telemetry", href: "/telemetry", variant: "secondary" },
        ]}
      />
      <Features
        eyebrow="Capabilities"
        title="One platform, every angle of the weekend."
        description="Each area is a dedicated analytics instrument, not another chart bolted onto a dashboard."
        features={FEATURES}
      />
      <Statistics
        eyebrow="This season"
        title="The numbers behind the season."
        description="A snapshot of what's been tracked so far."
        stats={STATISTICS}
      />
    </>
  );
}
