export function WebSourceForm() {
  return (
    <form className="panel">
      <h2 className="panel-title">Web Source</h2>
      <div className="field-stack">
        <input className="input" name="url" placeholder="https://example.com/guide" type="url" />
        <button className="button" type="button">
          Import URL
        </button>
      </div>
    </form>
  );
}
