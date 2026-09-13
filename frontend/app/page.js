"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PHASES = [
  "RECEIVED",
  "REPOSITORY_ANALYSIS",
  "ISSUE_DIAGNOSIS",
  "PLANNING",
  "IMPLEMENTATION",
  "TESTING",
  "FAILURE_ANALYSIS",
  "ADAPTATION",
  "RETRY",
  "VERIFICATION",
  "FINAL_RESULT",
];

const LABELS = {
  RECEIVED: "Received",
  REPOSITORY_ANALYSIS: "Repository Analysis",
  ISSUE_DIAGNOSIS: "Issue Diagnosis",
  PLANNING: "Planning",
  IMPLEMENTATION: "Implementation",
  TESTING: "Testing",
  FAILURE_ANALYSIS: "Failure Analysis",
  ADAPTATION: "Adaptation",
  RETRY: "Retry",
  VERIFICATION: "Verification",
  FINAL_RESULT: "Final Result",
};

function safeText(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function statusForPhase(phase, active, index) {
  if (index < active) return "done";
  if (index === active) return "active";
  return "waiting";
}

export default function Home() {
  const [repo, setRepo] = useState("");
  const [branch, setBranch] = useState("");
  const [issue, setIssue] = useState(""); 
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function start() {
    setLoading(true);
    setJob(null);
    setError("");

    try {
      const response = await fetch(`${API}/api/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repo,
          issue,
          branch: branch.trim() || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      setJob({ job_id: data.job_id });
    } catch (err) {
      setError(err.message || "Unable to start PatchLoop.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!job?.job_id) return;

    let stopped = false;

    async function poll() {
      try {
        const response = await fetch(
          `${API}/api/run/${job.job_id}`
        );

        if (!response.ok) {
          throw new Error(`Status error: ${response.status}`);
        }

        const data = await response.json();

        if (!stopped) {
          setJob(data);
        }

        if (
          ["resolved", "unresolved", "failed"].includes(
            data.final_status
          )
        ) {
          clearInterval(timer);
        }
      } catch (err) {
        if (!stopped) {
          setError(err.message || "Failed to get agent status.");
        }
      }
    }

    poll();

    const timer = setInterval(poll, 1000);

    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, [job?.job_id]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">PatchLoop</div>
            <div className="brand-sub">
              Autonomous Software Maintenance
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot live" />
          AGENT READY
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">ADAPTIVE REPAIR ENGINE</div>

          <h1>
            Software that <span>learns from failure.</span>
          </h1>

          <p>
            PatchLoop investigates bugs, writes a fix, tests it,
            analyzes failures and adapts until the repair is verified.
          </p>
        </div>

        <div className="hero-visual">
          <div className="orb orb-one" />
          <div className="orb orb-two" />
          <div className="orbit-line" />
          <div className="core">
            <div className="core-dot" />
          </div>
        </div>
      </section>

      <section className="input-card">
        <div className="card-heading">
          <div>
            <div className="section-label">NEW REPAIR JOB</div>
            <h2>Give the agent something to fix</h2>
          </div>

          <div className="attempt-limit">MAX 3 ATTEMPTS</div>
        </div>

        <div className="form-grid">

          <div className="field">
            <label>GITHUB REPOSITORY</label>
            <input
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="https://github.com/owner/repository"
            />
          </div>
          
          <div className="field">
            <label>BRANCH <span>(OPTIONAL)</span></label>
            <input
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
            />
          </div>

          <div className="field">
            <label>ISSUE</label>
            <input
              value={issue}
              onChange={(e) => setIssue(e.target.value)}
              placeholder="#17 or describe the bug..."
            />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="run-button"
          onClick={start}
          disabled={loading || !repo || !issue}
        >
          {loading ? (
            <>
              <span className="button-spinner" />
              INITIALIZING AGENT
            </>
          ) : (
            <>
              RUN PATCHLOOP
              <span>→</span>
            </>
          )}
        </button>
      </section>

      {job && <Dashboard job={job} />}
    </main>
  );
}

function Dashboard({ job }) {
  const activeIndex = Math.max(
    PHASES.indexOf(job.phase),
    0
  );

  const attempts = job.attempt_history || [];

  const isFinished = [
    "resolved",
    "unresolved",
    "failed",
  ].includes(job.final_status);

  return (
    <section className="dashboard">
      <div className="dashboard-top">
        <div>
          <div className="section-label">LIVE AGENT SESSION</div>
          <h2>Repair in progress</h2>
        </div>

        <div
          className={`session-status ${
            isFinished ? job.final_status : "running"
          }`}
        >
          <span className="status-dot" />
          {isFinished
            ? job.final_status.toUpperCase()
            : "PROCESSING"}
        </div>
      </div>

      <section className="process-card">
        <div className="process-header">
          <div>
            <div className="section-label">REPAIR PIPELINE</div>
            <div className="process-title">
              {LABELS[job.phase] || "Processing"}
            </div>
          </div>

          <div className="attempt-indicator">
            ATTEMPT{" "}
            <strong>{job.attempt_number || 1}</strong>
            <span>/ 3</span>
          </div>
        </div>

        <div className="timeline">
          {PHASES.map((phase, index) => {
            const state = statusForPhase(
              phase,
              activeIndex,
              index
            );

            return (
              <div
                className={`timeline-item ${state}`}
                key={phase}
              >
                <div className="timeline-node">
                  {state === "done" ? (
                    "✓"
                  ) : state === "active" ? (
                    <span className="pulse-node" />
                  ) : (
                    <span className="small-node" />
                  )}
                </div>

                <div className="timeline-text">
                  {LABELS[phase]}
                </div>

                {index !== PHASES.length - 1 && (
                  <div
                    className={`timeline-line ${
                      index < activeIndex ? "filled" : ""
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </section>

      <div className="content-grid">
        <section className="attempts-card">
          <div className="card-heading">
            <div>
              <div className="section-label">
                ADAPTIVE LOOP
              </div>
              <h2>Attempts</h2>
            </div>

            <div className="attempt-count">
              {attempts.length} / 3
            </div>
          </div>

          {attempts.length === 0 ? (
            <div className="waiting">
              <span className="loading-dots">
                <i />
                <i />
                <i />
              </span>
              Agent is preparing the first attempt...
            </div>
          ) : (
            attempts.map((attempt) => (
              <Attempt key={attempt.number} attempt={attempt} />
            ))
          )}
        </section>

        <section className="activity-card">
          <div className="card-heading">
            <div>
              <div className="section-label">
                EVENT STREAM
              </div>
              <h2>Agent activity</h2>
            </div>
          </div>

          <div className="event-list">
            {(job.logs || [])
              .slice()
              .reverse()
              .slice(0, 12)
              .map((event, index) => (
                <div className="event" key={index}>
                  <div className="event-dot" />

                  <div className="event-body">
                    <div className="event-phase">
                      {safeText(event.phase)}
                    </div>

                    <div className="event-message">
                      {safeText(event.message)}
                    </div>
                  </div>
                </div>
              ))}

            {(!job.logs || job.logs.length === 0) && (
              <div className="waiting">
                Waiting for events...
              </div>
            )}
          </div>
        </section>
      </div>

      <section className="result-card">
        <div className="result-heading">
          <div>
            <div className="section-label">VERIFICATION</div>
            <h2>Final outcome</h2>
          </div>

          <ResultBadge status={job.final_status} />
        </div>

        {job.final_status === "resolved" && (
          <div className="success-result">
            <div className="success-icon">✓</div>

            <div>
              <strong>Repair verified successfully</strong>
              <p>
                PatchLoop adapted to the failure and the final
                test suite passed verification.
              </p>
            </div>
          </div>
        )}

        {job.final_status &&
          job.final_status !== "resolved" && (
            <div className="failure-result">
              <div className="failure-icon">!</div>
              <div>
                <strong>Repair was not verified</strong>
                <p>
                  The agent reached its current execution limit
                  without a verified resolution.
                </p>
              </div>
            </div>
          )}

        <pre>
          {JSON.stringify(
            job.final_evidence || {},
            null,
            2
          )}
        </pre>
      </section>
    </section>
  );
}

function Attempt({ attempt }) {
  const passed = !!attempt.test_result?.passed;
  const hasTests = !!attempt.test_result;
  const hasFailure = !!attempt.failure_analysis;
  const hasAdaptation = !!attempt.adaptation_strategy;

  return (
    <div className={`attempt ${passed ? "passed" : ""}`}>
      <div className="attempt-header">
        <div className="attempt-title">
          <span className="attempt-number">
            {attempt.number}
          </span>

          <div>
            <div className="attempt-label">ATTEMPT</div>
            <strong>
              {passed ? "Repair verified" : "Repair attempt"}
            </strong>
          </div>
        </div>

        {hasTests && (
          <div
            className={`attempt-result ${
              passed ? "pass" : "fail"
            }`}
          >
            <span>{passed ? "✓" : "×"}</span>
            {passed ? "PASS" : "FAIL"}
          </div>
        )}
      </div>

      {attempt.hypothesis && (
        <Info
          label="HYPOTHESIS"
          value={attempt.hypothesis}
        />
      )}

      {attempt.actions?.length > 0 && (
        <Info
          label="ACTIONS"
          value={attempt.actions
            .map((action) => safeText(action))
            .join("  →  ")}
        />
      )}

      {hasTests && (
        <div className="test-box">
          <div className="test-header">
            <span>TEST EVIDENCE</span>

            <strong
              className={passed ? "green" : "red"}
            >
              EXIT {attempt.test_result.exit_code}
            </strong>
          </div>

          <pre>
            {safeText(
              attempt.test_result.stdout ||
              attempt.test_result.stderr ||
              "No test output."
            )}
          </pre>
        </div>
      )}

      {hasFailure && (
        <div className="reason-box red-box">
          <div className="reason-title">
            <span>01</span>
            FAILURE ANALYSIS
          </div>

          <p>{safeText(attempt.failure_analysis)}</p>
        </div>
      )}

      {hasAdaptation && (
        <div className="reason-box yellow-box">
          <div className="reason-title">
            <span>02</span>
            ADAPTATION
          </div>

          <p>{safeText(attempt.adaptation_strategy)}</p>
        </div>
      )}
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="info">
      <div>{label}</div>
      <p>{safeText(value)}</p>
    </div>
  );
}

function ResultBadge({ status }) {
  if (!status) {
    return (
      <div className="result-badge running">
        <span className="loading-dots">
          <i />
          <i />
          <i />
        </span>
        RUNNING
      </div>
    );
  }

  return (
    <div className={`result-badge ${status}`}>
      <span className="status-dot" />
      {status.toUpperCase()}
    </div>
  );
}