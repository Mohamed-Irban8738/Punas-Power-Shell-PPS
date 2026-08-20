import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [lines, setLines] = useState([
    {
      text: "Punas Power Shell v1.0.0",
      type: "normal",
    },
    {
      text: "Type 'help' for available commands.",
      type: "normal",
    },
    {
      text: "",
      type: "normal",
    },
  ]);

  const [command, setCommand] = useState("");
  const [prompt, setPrompt] = useState("psh> ");
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState("/");
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [commands, setCommands] = useState([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [connectionError, setConnectionError] = useState(false);

  const inputRef = useRef(null);
  const terminalRef = useRef(null);
  const abortControllerRef = useRef(null);
  const draftCommandRef = useRef("");

  // ==========================================
  // FOCUS TERMINAL
  // ==========================================

  const focusTerminal = () => {
    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  };

  // ==========================================
  // INITIAL LOAD
  // ==========================================

  useEffect(() => {
    loadFiles();
    loadHistory();
    loadCommands();

    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  // ==========================================
  // FOCUS WHEN RETURNING TO TAB
  // ==========================================

  useEffect(() => {
    const handleWindowFocus = () => {
      if (!isExecuting) {
        inputRef.current?.focus();
      }
    };

    window.addEventListener("focus", handleWindowFocus);

    return () => {
      window.removeEventListener(
        "focus",
        handleWindowFocus
      );
    };
  }, [isExecuting]);

  // ==========================================
  // ADD TERMINAL LINE
  // ==========================================

  const addLine = (text, type = "normal") => {
    setLines((prev) => [
      ...prev,
      {
        text,
        type,
      },
    ]);
  };

  // ==========================================
  // LOAD FILES
  // ==========================================

  const loadFiles = async () => {
    try {
      const response = await fetch(
        `${API}/api/files`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(
          data.error || "Failed to load files"
        );
      }

      setFiles(data.items);
      setCurrentPath(data.path);
      setConnectionError(false);

    } catch (error) {
      console.error(
        "Failed to load files:",
        error
      );

      setConnectionError(true);
    }
  };

  // ==========================================
  // LOAD HISTORY
  // ==========================================

  const loadHistory = async () => {
    try {
      const response = await fetch(
        `${API}/api/history`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      const commandList = (data.history || [])
        .map((entry) => entry.command)
        .filter(Boolean);

      setHistory(commandList);

    } catch (error) {
      console.error(
        "Failed to load history:",
        error
      );
    }
  };

  // ==========================================
  // LOAD COMMANDS
  // ==========================================

  const loadCommands = async () => {
    try {
      const response = await fetch(
        `${API}/api/commands`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      setCommands(data.commands || []);

    } catch (error) {
      console.error(
        "Failed to load commands:",
        error
      );
    }
  };

  // ==========================================
  // AUTO SCROLL
  // ==========================================

  useEffect(() => {
    terminalRef.current?.scrollTo(
      0,
      terminalRef.current.scrollHeight
    );
  }, [lines]);

  // ==========================================
  // EXECUTE COMMAND
  // ==========================================

  const executeCommand = async () => {
    const cmd = command.trim();

    if (!cmd || isExecuting) {
      return;
    }

    // ========================================
    // CLEAR TERMINAL
    // ========================================

    if (cmd.toLowerCase() === "clear") {
      setLines([]);
      setCommand("");
      setHistoryIndex(-1);
      draftCommandRef.current = "";

      setTimeout(() => {
        inputRef.current?.focus();
      }, 0);

      return;
    }

    // ========================================
    // NORMAL COMMAND
    // ========================================

    addLine(
      `${prompt}${cmd}`,
      "command"
    );

    setCommand("");
    setHistoryIndex(-1);
    draftCommandRef.current = "";

    setIsExecuting(true);
    setConnectionError(false);

    const controller =
      new AbortController();

    abortControllerRef.current =
      controller;

    try {
      const response = await fetch(
        `${API}/api/execute`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            command: cmd,
          }),

          signal: controller.signal,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned HTTP ${response.status}`
        );
      }

      const data =
        await response.json();

      // ======================================
      // COMMAND FAILED
      // ======================================

      if (!data.success) {

        if (data.output) {
          data.output
            .split("\n")
            .forEach((line) => {
              if (line.trim()) {
                addLine(
                  line,
                  "error"
                );
              }
            });
        }

        if (
          !data.error &&
          !data.output
        ) {
          addLine(
            "Command failed.",
            "error"
          );
        }

      }

      // ======================================
      // COMMAND SUCCESS
      // ======================================

      else if (data.output) {

        data.output
          .split("\n")
          .forEach((line) => {
            addLine(
              line,
              "normal"
            );
          });
      }

      // ======================================
      // UPDATE PROMPT
      // ======================================

      if (data.prompt) {
        setPrompt(data.prompt);
      }

      setConnectionError(false);

      // Refresh filesystem/history
      await loadFiles();
      await loadHistory();

    } catch (error) {

      // ======================================
      // CTRL + C
      // ======================================

      if (
        error.name ===
        "AbortError"
      ) {

        addLine(
          "^C",
          "error"
        );

      }

      // ======================================
      // CONNECTION ERROR
      // ======================================

      else {

        console.error(error);

        addLine(
          "PPS connection error: Unable to reach the backend.",
          "error"
        );

        addLine(
          "Make sure FastAPI is running on port 8000.",
          "error"
        );

        setConnectionError(true);
      }

    } finally {

      setIsExecuting(false);

      abortControllerRef.current =
        null;

      setTimeout(() => {
        inputRef.current?.focus();
      }, 0);
    }
  };

  // ==========================================
  // CLEAR TERMINAL
  // ==========================================

  const clearTerminal = () => {
    setLines([]);
    setCommand("");
    setHistoryIndex(-1);
    draftCommandRef.current = "";

    focusTerminal();
  };

  // ==========================================
  // GO BACK
  // ==========================================

  const goBack = async () => {

    if (isExecuting) {
      return;
    }

    setIsExecuting(true);

    try {

      const response =
        await fetch(
          `${API}/api/execute`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              command: "cd ..",
            }),
          }
        );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data =
        await response.json();

      addLine(
        `${prompt}cd ..`,
        "command"
      );

      if (data.output) {
        data.output
          .split("\n")
          .forEach((line) => {
            addLine(
              line,
              "normal"
            );
          });
      }

      if (data.prompt) {
        setPrompt(data.prompt);
      }

      await loadFiles();
      await loadHistory();

    } catch (error) {

      addLine(
        "Failed to navigate to parent directory.",
        "error"
      );

    } finally {

      setIsExecuting(false);

      focusTerminal();
    }
  };

  // ==========================================
  // REFRESH FILES
  // ==========================================

  const refreshFiles = async () => {
    await loadFiles();

    focusTerminal();
  };

  // ==========================================
  // OPEN DIRECTORY
  // ==========================================

  const openDirectory = async (
    name
  ) => {

    if (isExecuting) {
      return;
    }

    const cmd = `cd ${name}`;

    addLine(
      `${prompt}${cmd}`,
      "command"
    );

    setIsExecuting(true);

    try {

      const response =
        await fetch(
          `${API}/api/execute`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              command: cmd,
            }),
          }
        );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data =
        await response.json();

      if (!data.success) {

        if (data.output) {
          data.output
            .split("\n")
            .forEach((line) => {
              if (line.trim()) {
                addLine(
                  line,
                  "error"
                );
              }
            });
        }

      } else if (data.output) {

        data.output
          .split("\n")
          .forEach((line) => {
            addLine(
              line,
              "normal"
            );
          });
      }

      if (data.prompt) {
        setPrompt(data.prompt);
      }

      await loadFiles();
      await loadHistory();

    } catch (error) {

      addLine(
        `Unable to open directory '${name}'.`,
        "error"
      );

    } finally {

      setIsExecuting(false);

      focusTerminal();
    }
  };

  // ==========================================
  // TAB AUTOCOMPLETE
  // ==========================================

  const handleAutocomplete = () => {

    const value =
      command.trim();

    if (!value) {
      return;
    }

    // Only autocomplete command name
    if (value.includes(" ")) {
      return;
    }

    const matches =
      commands.filter(
        (cmd) =>
          cmd
            .toLowerCase()
            .startsWith(
              value.toLowerCase()
            )
      );

    // One match
    if (matches.length === 1) {

      setCommand(
        `${matches[0]} `
      );

      focusTerminal();

      return;
    }

    // Multiple matches
    if (matches.length > 1) {

      addLine(
        matches.join("    "),
        "suggestion"
      );

      focusTerminal();
    }
  };

  // ==========================================
  // KEYBOARD HANDLER
  // ==========================================

  const handleKeyDown = (
    event
  ) => {

    // ========================================
    // ENTER
    // ========================================

    if (
      event.key === "Enter"
    ) {

      event.preventDefault();

      executeCommand();

      return;
    }

    // ========================================
    // TAB
    // ========================================

    if (
      event.key === "Tab"
    ) {

      event.preventDefault();

      handleAutocomplete();

      return;
    }

    // ========================================
    // CTRL + L
    // ========================================

    if (
      event.ctrlKey &&
      event.key.toLowerCase() === "l"
    ) {

      event.preventDefault();

      clearTerminal();

      return;
    }

    // ========================================
    // CTRL + C
    // ========================================

    if (
      event.ctrlKey &&
      event.key.toLowerCase() === "c"
    ) {

      event.preventDefault();

      if (isExecuting) {

        abortControllerRef
          .current
          ?.abort();

      } else {

        setCommand("");

        addLine(
          "^C",
          "error"
        );
      }

      focusTerminal();

      return;
    }

    // ========================================
    // ARROW UP
    // ========================================

    if (
      event.key === "ArrowUp"
    ) {

      event.preventDefault();

      if (
        history.length === 0
      ) {
        return;
      }

      if (
        historyIndex === -1
      ) {

        draftCommandRef.current =
          command;
      }

      const nextIndex =
        historyIndex === -1
          ? history.length - 1
          : Math.max(
              0,
              historyIndex - 1
            );

      setHistoryIndex(
        nextIndex
      );

      setCommand(
        history[nextIndex]
      );

      return;
    }

    // ========================================
    // ARROW DOWN
    // ========================================

    if (
      event.key === "ArrowDown"
    ) {

      event.preventDefault();

      if (
        historyIndex === -1
      ) {
        return;
      }

      if (
        historyIndex ===
        history.length - 1
      ) {

        setHistoryIndex(-1);

        setCommand(
          draftCommandRef.current
        );

        return;
      }

      const nextIndex =
        historyIndex + 1;

      setHistoryIndex(
        nextIndex
      );

      setCommand(
        history[nextIndex]
      );
    }
  };

  // ==========================================
  // RENDER
  // ==========================================

  return (
    <div className="app">

      <div className="terminal-window">

        {/* HEADER */}

        <div className="terminal-header">

          <div className="traffic-lights">

            <span className="red"></span>
            <span className="yellow"></span>
            <span className="green"></span>

          </div>

          <div className="title">
            Punas Power Shell
          </div>

          <div className="version">
            v1.0.0
          </div>

        </div>

        {/* MAIN */}

        <div className="main-content">

          {/* FILE EXPLORER */}

          <aside className="file-explorer">

            <div className="explorer-header">
              FILE EXPLORER
            </div>

            <div className="explorer-toolbar">

              <button
                onClick={goBack}
                title="Back"
                disabled={isExecuting}
              >
                ←
              </button>

              <button
                onClick={refreshFiles}
                title="Refresh"
                disabled={isExecuting}
              >
                ⟳
              </button>

              <div className="current-path">
                {currentPath}
              </div>

            </div>

            <div className="file-list">

              {files.map(
                (item) => (

                  <div
                    key={item.name}
                    className="file-item"

                    onDoubleClick={() =>
                      item.type === "dir"
                        ? openDirectory(
                            item.name
                          )
                        : null
                    }
                  >

                    <span className="file-icon">
                      {item.type === "dir"
                        ? "📁"
                        : "📄"}
                    </span>

                    <span>
                      {item.name}
                    </span>

                  </div>

                )
              )}

            </div>

          </aside>

          {/* TERMINAL */}

          <main
            className="terminal-body"
            ref={terminalRef}
            onMouseDown={(event) => {

              if (
                event.target.tagName !==
                "INPUT"
              ) {

                event.preventDefault();

                focusTerminal();
              }

            }}
          >

            {lines.map(
              (line, index) => (

                <div
                  className={`terminal-line ${line.type}`}
                  key={index}
                >
                  {line.text}
                </div>

              )
            )}

            {/* EXECUTION INDICATOR */}

            {isExecuting && (

              <div className="execution-indicator">

                <span className="spinner"></span>

                Executing...

              </div>

            )}

            {/* INPUT */}

            <div className="input-line">

              <span className="prompt">
                {prompt}
              </span>

              <input
                ref={inputRef}
                value={command}

                onChange={(event) => {

                  setCommand(
                    event.target.value
                  );

                  setHistoryIndex(-1);

                }}

                onKeyDown={
                  handleKeyDown
                }

                autoFocus

                autoComplete="off"

                spellCheck="false"

                disabled={
                  isExecuting
                }
              />

            </div>

            {/* CONNECTION STATUS */}

            {connectionError && (

              <div className="connection-status">
                ● Backend disconnected
              </div>

            )}

          </main>

        </div>

      </div>

    </div>
  );
}

export default App;