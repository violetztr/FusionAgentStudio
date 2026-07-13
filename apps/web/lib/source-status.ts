export type SourceStatusTone = "amber" | "teal" | "green" | "red" | "neutral";

export function getSourceStatusMeta(status: string): { label: string; tone: SourceStatusTone } {
  const normalized = status.toLowerCase();
  if (normalized === "pending") {
    return { label: "Pending", tone: "amber" };
  }
  if (normalized === "processing") {
    return { label: "Processing", tone: "teal" };
  }
  if (normalized === "indexed") {
    return { label: "Indexed", tone: "green" };
  }
  if (normalized === "failed") {
    return { label: "Failed", tone: "red" };
  }
  return { label: toTitleCase(status), tone: "neutral" };
}

function toTitleCase(value: string) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1).toLowerCase() : "Unknown";
}
