document.addEventListener("DOMContentLoaded", () => {
    const toggleEntryDateFields = () => {
        const selected = document.querySelector('input[name="zeitpunkt"]:checked');
        const customFields = document.querySelector("[data-custom-date-fields]");
        if (!selected || !customFields) return;

        const showCustom = selected.value === "eigen";
        customFields.hidden = !showCustom;
        customFields.querySelectorAll("input").forEach((input) => {
            input.required = showCustom;
            input.disabled = !showCustom;
        });
    };

    document.querySelectorAll('input[name="zeitpunkt"]').forEach((input) => {
        input.addEventListener("change", toggleEntryDateFields);
    });
    toggleEntryDateFields();

    const periodSelect = document.querySelector("[data-period-select]");
    const periodPanels = document.querySelectorAll("[data-period-panel]");
    const togglePeriodFields = () => {
        if (!periodSelect) return;
        periodPanels.forEach((panel) => {
            const visible = panel.dataset.periodPanel === periodSelect.value;
            panel.hidden = !visible;
            panel.querySelectorAll("input").forEach((input) => {
                input.disabled = !visible;
                input.required = visible;
            });
        });
    };
    if (periodSelect) {
        periodSelect.addEventListener("change", togglePeriodFields);
        togglePeriodFields();
    }

    document.querySelectorAll("[data-confirm]").forEach((element) => {
        element.addEventListener("click", (event) => {
            if (!window.confirm(element.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });
});

// Bearbeitungsfenster auf der Kategorienseite öffnen und schließen.
document.querySelectorAll("[data-dialog-id]").forEach((button) => {
    button.addEventListener("click", () => {
        const dialog = document.getElementById(button.dataset.dialogId);
        if (dialog) dialog.showModal();
    });
});

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => {
        const dialog = button.closest("dialog");
        if (dialog) dialog.close();
    });
});

document.querySelectorAll("dialog.edit-dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
        const box = dialog.getBoundingClientRect();
        const outside = event.clientX < box.left || event.clientX > box.right ||
            event.clientY < box.top || event.clientY > box.bottom;
        if (outside) dialog.close();
    });
});
