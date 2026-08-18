document.addEventListener("DOMContentLoaded", () => {

    loadTransactions();
    loadSummary();

    const form = document.getElementById("transaction-form");

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const description =
            document.getElementById("description").value;

        const amount =
            document.getElementById("amount").value;

        const type =
            document.getElementById("type").value;


        const response = await fetch("/api/transactions", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                description: description,
                amount: amount,
                type: type
            })

        });


        const result = await response.json();


        if (!response.ok) {

            alert(result.error);

            return;
        }


        form.reset();

        await loadTransactions();

        await loadSummary();

    });

});


async function loadTransactions() {

    const response =
        await fetch("/api/transactions");

    const transactions =
        await response.json();


    const transactionList =
        document.getElementById("transaction-list");


    transactionList.innerHTML = "";


    transactions.forEach(transaction => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${transaction.description}
            </td>

            <td>
                ₹${Number(transaction.amount).toFixed(2)}
            </td>

            <td>
                ${transaction.type}
            </td>

            <td>

                <button
                    class="delete-button"
                    onclick="deleteTransaction(${transaction.id})">

                    Delete

                </button>

            </td>

        `;


        transactionList.appendChild(row);

    });

}


async function loadSummary() {

    const response =
        await fetch("/api/summary");


    const summary =
        await response.json();


    document.getElementById("total-income").textContent =
        `₹${Number(summary.total_income).toFixed(2)}`;


    document.getElementById("total-expense").textContent =
        `₹${Number(summary.total_expense).toFixed(2)}`;


    document.getElementById("balance").textContent =
        `₹${Number(summary.balance).toFixed(2)}`;

}


async function deleteTransaction(id) {

    const confirmed =
        confirm("Delete this transaction?");


    if (!confirmed) {
        return;
    }


    const response =
        await fetch(`/api/transactions/${id}`, {

            method: "DELETE"

        });


    if (response.ok) {

        await loadTransactions();

        await loadSummary();

    }

}