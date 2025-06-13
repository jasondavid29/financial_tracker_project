let allTransactions = [];

document.addEventListener("DOMContentLoaded", function () {
    fetchTransactions();

    // Category/Monthly Pie Charts
    const categoryLabelsEl = document.getElementById("category-labels");
    const categoryValuesEl = document.getElementById("category-values");
    const monthLabelsEl = document.getElementById("month-labels");
    const monthValuesEl = document.getElementById("month-values");

    if (categoryLabelsEl && categoryValuesEl && monthLabelsEl && monthValuesEl) {
        const categoryLabels = JSON.parse(categoryLabelsEl.textContent);
        const categoryValues = JSON.parse(categoryValuesEl.textContent);
        const monthLabels = JSON.parse(monthLabelsEl.textContent);
        const monthValues = JSON.parse(monthValuesEl.textContent);

        new Chart(document.getElementById("categoryPieChart"), {
            type: "pie",
            data: {
                labels: categoryLabels,
                datasets: [{
                    label: "Expenses by Category",
                    data: categoryValues,
                    backgroundColor: [
                        "#FF6384", "#36A2EB", "#FFCE56", "#81C784", "#BA68C8", "#4DD0E1"
                    ]
                }]
            }
        });

        new Chart(document.getElementById("monthlyPieChart"), {
            type: "pie",
            data: {
                labels: monthLabels,
                datasets: [{
                    label: "Expenses by Month",
                    data: monthValues,
                    backgroundColor: [
                        "#FF6384", "#36A2EB", "#FFCE56", "#81C784", "#BA68C8", "#4DD0E1"
                    ]
                }]
            }
        });
    }

    // Form submission - Add
    document.getElementById("transactionForm").addEventListener("submit", function (event) {
        event.preventDefault();

        let formData = {
            type: document.getElementById("type").value,
            category: document.getElementById("category").value,
            amount: parseFloat(document.getElementById("amount").value)
        };

        let csrftoken = getCookie("csrftoken");
        if (!csrftoken) {
            alert("Error: CSRF token not found.");
            return;
        }

        fetch("/transactions/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Server Error: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            alert("Transaction added successfully!");
            document.getElementById("transactionForm").reset();
            fetchTransactions();
        })
        .catch(error => {
            alert("Error: " + error.message);
            console.error("Error:", error);
        });
    });

    document.querySelectorAll(".category-btn").forEach(button => {
        button.addEventListener("click", () => {
            const category = button.getAttribute("data-category");
            const filtered = category === "all" ? allTransactions : allTransactions.filter(t => t.category.toLowerCase() === category.toLowerCase());
            renderTransactions(filtered);
        });
    });

    // Form submission - Update
    document.getElementById("editTransactionForm").addEventListener("submit", function (e) {
        e.preventDefault();

        const id = document.getElementById("edit-id").value;
        const formData = {
            type: document.getElementById("edit-type").value,
            category: document.getElementById("edit-category").value,
            amount: parseFloat(document.getElementById("edit-amount").value)
        };

        const csrftoken = getCookie("csrftoken");

        fetch(`/transactions/update/${id}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Update failed: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            alert("Transaction updated successfully!");
            closeEditModal();
            fetchTransactions();
        })
        .catch(error => {
            alert("Error updating transaction: " + error.message);
            console.error(error);
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function fetchTransactions() {
    fetch("/transactions/history/")
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Failed to fetch transactions: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            allTransactions = data;
            renderTransactions(data);
        })
        .catch(error => console.error("Error fetching transactions:", error));
}

function renderTransactions(transactions) {
    const transactionList = document.getElementById("transaction-list");
    transactionList.innerHTML = "";

    if (transactions.length === 0) {
        transactionList.innerHTML = "<tr><td colspan='5'>No transactions available.</td></tr>";
        updateTotalDisplay(0, 0);
        updatePieChart([]);
        return;
    }

    let incomeTotal = 0;
    let expenseTotal = 0;

    transactions.forEach(transaction => {
        const amount = parseFloat(transaction.amount) || 0;
        transaction.type.toLowerCase() === "income" ? incomeTotal += amount : expenseTotal += amount;

        const dateFormatted = transaction.created_at ? new Date(transaction.created_at).toLocaleString() : "N/A";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${transaction.type}</td>
            <td>${transaction.category}</td>
            <td>${transaction.amount}</td>
            <td>${dateFormatted}</td>
            <td>
                <button class="edit-btn" data-id="${transaction.id}">✏️</button>
                <button class="delete-btn" data-id="${transaction.id}">🗑️</button>
            </td>
        `;
        transactionList.appendChild(row);

        // Edit button
        const editBtn = row.querySelector(".edit-btn");
        editBtn.addEventListener("click", (e) => openEditModal(transaction.id, e));

        // Delete button
        const deleteBtn = row.querySelector(".delete-btn");
        deleteBtn.addEventListener("click", () => deleteTransaction(transaction.id));
    });

    updateTotalDisplay(incomeTotal, expenseTotal);
    updatePieChart(transactions);
}

function updateTotalDisplay(income, expense) {
    document.getElementById("total-income").textContent = income.toFixed(2);
    document.getElementById("total-expense").textContent = expense.toFixed(2);
    document.getElementById("total-savings").textContent = (income - expense).toFixed(2);
}

let myPieChart = null;

function updatePieChart(transactions) {
    let incomeTotal = 0;
    let expenseTotal = 0;

    transactions.forEach(transaction => {
        const amount = parseFloat(transaction.amount) || 0;
        transaction.type.toLowerCase() === "income" ? incomeTotal += amount : expenseTotal += amount;
    });

    const ctx = document.getElementById("transactionChart").getContext("2d");

    if (myPieChart) myPieChart.destroy();

    myPieChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["Income", "Expense"],
            datasets: [{
                data: [incomeTotal, expenseTotal],
                backgroundColor: ["#28a745", "#dc3545"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function openEditModal(id, event) {
    const transaction = allTransactions.find(t => t.id === id);
    if (!transaction) return;

    const modal = document.getElementById("transaction-modal");

    document.getElementById("edit-id").value = transaction.id;
    document.getElementById("edit-type").value = transaction.type;
    document.getElementById("edit-category").value = transaction.category;
    document.getElementById("edit-amount").value = transaction.amount;

    const iconRect = event.target.getBoundingClientRect();
    const scrollTop = window.scrollY;
    const scrollLeft = window.scrollX;

    modal.style.position = "absolute";
    modal.style.top = `${iconRect.top + scrollTop}px`;
    modal.style.left = `${iconRect.left + scrollLeft + 30}px`;
    modal.style.display = "block";
}

function closeEditModal() {
    document.getElementById("transaction-modal").style.display = "none";
}

function deleteTransaction(id) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    const csrftoken = getCookie("csrftoken");

    fetch(`/transactions/delete/${id}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Failed to delete transaction: ${text}`);
            });
        }
        alert("Transaction deleted successfully!");
        fetchTransactions();
    })
    .catch(error => {
        alert("Error deleting transaction: " + error.message);
        console.error(error);
    });
}
