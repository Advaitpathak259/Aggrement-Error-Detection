import { useState } from "react";
import axios from "axios";
import "./App.css";

export default function App() {
  const [sentence, setSentence] = useState("");
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!sentence.trim()) return;

    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:8000/predict", {
        sentence,
      });
      setTokens(res.data.tokens || []);
    } catch (error) {
      console.error(error);
      alert("Backend not reachable.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSentence("");
    setTokens([]);
  };

  return (
    <div className="app">
      <div className="card">
        <div className="topbar">
          <div>
            <h1>Agreement Error Detector</h1>
            <p>Type a sentence and highlight agreement errors.</p>
          </div>
          <span className="badge">Local AI</span>
        </div>

        <textarea
          rows="6"
          value={sentence}
          onChange={(e) => setSentence(e.target.value)}
          placeholder="Example: The boys plays cricket."
        />

        <div className="actions">
          <button className="primary" onClick={handleCheck} disabled={loading}>
            {loading ? "Checking..." : "Check Sentence"}
          </button>
          <button className="secondary" onClick={handleClear} disabled={loading}>
            Clear
          </button>
        </div>

        <div className="result">
          <h2>Result</h2>
          <div className="output-box">
            {tokens.length === 0 ? (
              <span className="placeholder">No result yet.</span>
            ) : (
              tokens.map((item, idx) => (
                <span
                  key={idx}
                  className={item.label === "AGR_ERR" ? "token error" : "token"}
                >
                  {item.token}
                </span>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}