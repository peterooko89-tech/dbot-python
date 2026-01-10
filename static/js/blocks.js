function addRSI() {
    const div = document.createElement('div');
    div.innerText = "RSI Block";
    document.getElementById('strategy').appendChild(div);
}

function addEMA() {
    const div = document.createElement('div');
    div.innerText = "EMA Block";
    document.getElementById('strategy').appendChild(div);
}

function runBot() {
    alert("Bot running with selected blocks!");
}
