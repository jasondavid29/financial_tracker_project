document.addEventListener("DOMContentLoaded", function () {
    const chartDataScript = document.getElementById("chart-data");
    const expenseSourcesScript = document.getElementById("expense-sources");

    let chartData = { labels: [], amounts: [] };
    let expenseData = [];

    try {
        if (chartDataScript && chartDataScript.textContent.trim()) {
            chartData = JSON.parse(chartDataScript.textContent.trim());
        }
    } catch (e) {
        console.error("Failed to parse chart data:", e);
    }

    try {
        if (expenseSourcesScript && expenseSourcesScript.textContent.trim()) {
            expenseData = JSON.parse(expenseSourcesScript.textContent.trim());
        }
    } catch (e) {
        console.error("Failed to parse expense data:", e);
    }

    // Line Chart
    const ctx = document.getElementById("expenseLineChart").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: chartData.labels,
            datasets: [{
                label: "Daily Expense (₹)",
                data: chartData.amounts,
                borderColor: "#f44336",
                backgroundColor: "rgba(244, 67, 54, 0.1)",
                tension: 0.3,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Table population
    const tbody = document.getElementById("expenseSourcesBody");
    expenseData.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${item.date}</td><td>${item.category}</td><td>₹${item.amount}</td>`;
        tbody.appendChild(row);
    });
});
