function saveStrategy() {
    const strategy = {
        market: document.getElementById("market").value,
        condition: document.getElementById("condition").value,
        stake: parseFloat(document.getElementById("stake").value)
    };

    fetch("/api/save-strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(strategy)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").textContent =
            JSON.stringify(data, null, 2);
    });
}
