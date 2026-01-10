// ---------------- Blockly ----------------
const workspace = Blockly.inject("blocklyDiv", {
  toolbox: document.getElementById("toolbox"),
});

// Custom blocks
Blockly.Blocks["trade_call"] = {
  init: function () {
    this.appendDummyInput().appendField("CALL Trade");
    this.setNextStatement(true);
    this.setColour(120);
  },
};

Blockly.Blocks["trade_put"] = {
  init: function () {
    this.appendDummyInput().appendField("PUT Trade");
    this.setNextStatement(true);
    this.setColour(0);
  },
};

// Code generator
Blockly.JavaScript["trade_call"] = () => "CALL\n";
Blockly.JavaScript["trade_put"] = () => "PUT\n";

// ---------------- Bot Control ----------------
function runBot() {
  const code = Blockly.JavaScript.workspaceToCode(workspace);
  fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ strategy: code }),
  });
}

function stopBot() {
  fetch("/stop");
}

// ---------------- Live Tick ----------------
setInterval(() => {
  fetch("/tick")
    .then(res => res.json())
    .then(data => {
      document.getElementById("tick").innerText = data.price ?? "---";
    });
}, 1000);
// -------- SAVE STRATEGY ----------
function saveStrategy() {
  const json = Blockly.serialization.workspaces.save(workspace);
  const blob = new Blob([JSON.stringify(json)], { type: "application/json" });

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "strategy.dbot.json";
  a.click();
}

// -------- LOAD STRATEGY ----------
function loadStrategy(event) {
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = () => {
    const json = JSON.parse(reader.result);
    workspace.clear();
    Blockly.serialization.workspaces.load(json, workspace);
  };

  reader.readAsText(file);
}
