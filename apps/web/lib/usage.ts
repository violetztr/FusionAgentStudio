export function formatUsage(usage: Record<string, unknown>): string {
  const total = usage.total_tokens;
  if (typeof total === "number") {
    return `${total} tokens`;
  }
  return "No usage recorded";
}
