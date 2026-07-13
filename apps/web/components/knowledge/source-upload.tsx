export function SourceUpload() {
  return (
    <form className="panel">
      <h2 className="panel-title">File Source</h2>
      <div className="field-stack">
        <input className="input" name="file" type="file" />
        <button className="button" type="button">
          Upload
        </button>
      </div>
    </form>
  );
}
