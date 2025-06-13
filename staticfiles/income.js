document.addEventListener("DOMContentLoaded", function () {
    // Safely get and parse chart data
    const chartDataScript = document.getElementById("chart-data");
    const incomeSourcesScript = document.getElementById("income-sources");

    let chartData = { labels: [], amounts: [] };
    let incomeData = [];

    try {
        if (chartDataScript && chartDataScript.textContent.trim()) {
            chartData = JSON.parse(chartDataScript.textContent.trim());
        }
    } catch (e) {
        console.error("Failed to parse chart data:", e);
    }

    try {
        if (incomeSourcesScript && incomeSourcesScript.textContent.trim()) {
            incomeData = JSON.parse(incomeSourcesScript.textContent.trim());
        }
    } catch (e) {
        console.error("Failed to parse income source data:", e);
    }

    // Chart
    const ctx = document.getElementById("incomeBarChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: [{
                label: "Daily Income (₹)",
                data: chartData.amounts,
                backgroundColor: "#4CAF50"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Table
    const tbody = document.getElementById("incomeSourcesBody");
    tbody.innerHTML = "";  // Clear existing rows to avoid duplicates

    incomeData.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${item.date}</td><td>${item.source}</td><td>₹${item.amount}</td>`;
        tbody.appendChild(row);
    });
});
