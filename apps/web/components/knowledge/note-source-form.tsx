export function NoteSourceForm() {
  return (
    <form className="panel">
      <h2 className="panel-title">Manual Note</h2>
      <div className="field-stack">
        <input className="input" name="title" placeholder="Note title" type="text" />
        <textarea className="textarea" name="content" placeholder="Paste knowledge text" />
        <button className="button" type="button">
          Add Note
        </button>
      </div>
    </form>
  );
}
