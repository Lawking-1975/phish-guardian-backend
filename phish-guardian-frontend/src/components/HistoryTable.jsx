export default function HistoryTable({ history }) {
  if (!history || history.length === 0) return <p>No history yet.</p>;

  return (
    <table className="w-full border-collapse">
      <thead>
        <tr>
          <th className="border px-2 py-1">URL</th>
          <th className="border px-2 py-1">Status</th>
          <th className="border px-2 py-1">Suggestion</th>
        </tr>
      </thead>
      <tbody>
        {history.map((item, index) => (
          <tr key={index}>
            <td className="border px-2 py-1">{item.url}</td>
            <td className="border px-2 py-1">{item.status}</td>
            <td className="border px-2 py-1">
              {item.suggestion?.suggested_url || "-"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
