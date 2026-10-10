
import CytoscapeComponent from "react-cytoscapejs";
import type { Investigation } from "./types";

type GraphProps = {
  data: Investigation;
};

export default function Graph({ data }: GraphProps) {
  const elements = [
    ...data.nodes.map((node) => ({
      data: {
        id: node.id,
        label: node.label,
      },
    })),
    ...data.edges.map((edge) => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
      },
    })),
  ];

  return (
    <div className="h-96 w-full overflow-hidden rounded-xl border border-slate-700 bg-slate-950">
      {elements.length > 0 ? (
        <CytoscapeComponent
          elements={elements}
          layout={{
            name: "breadthfirst",
            directed: true,
            padding: 24,
          }}
          stylesheet={[
            {
              selector: "node",
              style: {
                label: "data(label)",
                color: "#e2e8f0",
                "background-color": "#0891b2",
                "text-wrap": "wrap",
                "text-max-width": 120,
                "font-size": 11,
                width: 36,
                height: 36,
                "text-valign": "bottom",
                "text-margin-y": 7,
              },
            },
            {
              selector: "edge",
              style: {
                label: "data(label)",
                width: 2,
                "line-color": "#64748b",
                "target-arrow-color": "#22d3ee",
                "target-arrow-shape": "triangle",
                "curve-style": "bezier",
                color: "#cbd5e1",
                "font-size": 9,
                "text-background-color": "#0f172a",
                "text-background-opacity": 1,
              },
            },
          ]}
          style={{ width: "100%", height: "100%" }}
        />
      ) : (
        <div className="flex h-full items-center justify-center text-slate-400">
          No transaction paths available to visualize.
        </div>
      )}
    </div>
  );
}
