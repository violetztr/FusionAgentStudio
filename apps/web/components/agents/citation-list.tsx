type Citation = {
  title?: unknown;
  excerpt?: unknown;
  score?: unknown;
  chunk_index?: unknown;
};

export function CitationList({ citations }: { citations: Array<Record<string, unknown>> }) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="citation-list">
      {citations.map((citation, index) => (
        <CitationItem citation={citation} index={index} key={`${citation.chunk_id ?? index}`} />
      ))}
    </div>
  );
}

function CitationItem({ citation, index }: { citation: Citation; index: number }) {
  const title = typeof citation.title === "string" ? citation.title : `Source ${index + 1}`;
  const excerpt = typeof citation.excerpt === "string" ? citation.excerpt : "";
  const score = typeof citation.score === "number" ? citation.score.toFixed(2) : "n/a";
  const chunkIndex = typeof citation.chunk_index === "number" ? citation.chunk_index : index;

  return (
    <div className="citation">
      <div className="row-title">{title}</div>
      <div className="row-meta">
        chunk {chunkIndex} · score {score}
      </div>
      {excerpt ? <div className="row-meta">{excerpt}</div> : null}
    </div>
  );
}
