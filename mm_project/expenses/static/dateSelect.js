function fillYearSelect(elementID) {
    const yearSelect = document.getElementById(elementID);
    const currentYear = new Date().getFullYear();
    const startYear = currentYear - 10; // Adjust for how many years in the past you want
    const endYear = currentYear + 10; // Adjust for how many years in the future you want

    for (let year = startYear; year <= endYear; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (year === currentYear) {
            option.selected = true; // Set current year as default
        }
        yearSelect.appendChild(option);
    }
}

function fillMonthSelect(elementID) {
    const monthSelect = document.getElementById(elementID);
    const currentMonth = new Date().getMonth() + 1; // Months are 0-indexed in JS

// Fill the month dropdown
    const monthNames = [
        "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October",
        "November", "December"
    ];

    monthNames.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index + 1; // Value should match the month number (1-12)
        option.textContent = month;
        if (index + 1 === currentMonth) {
            option.selected = true; // Select the current month
        }
        monthSelect.appendChild(option);
    });
}
