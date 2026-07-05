document.addEventListener("DOMContentLoaded", function () {
    const scanForm = document.getElementById("scanForm");
    const scanBtn = document.getElementById("scanBtn");
    const folderPathInput = document.getElementById("folderPath");
    const scanProgress = document.getElementById("scanProgress");
    const scanStatus = document.getElementById("scanStatus");

    if (scanForm) {
        scanForm.addEventListener("submit", function (e) {
            const folderPath = folderPathInput.value.trim();

            if (!folderPath) {
                e.preventDefault();
                showValidationError("Please enter a folder path.");
                return;
            }

            if (
                !folderPath.match(/^[a-zA-Z]:\\/) &&
                !folderPath.match(/^[a-zA-Z]:\//) &&
                !folderPath.match(/^\\\\/)
            ) {
                e.preventDefault();
                showValidationError(
                    "Please enter a valid Windows folder path (e.g., C:\\Users\\Pavan\\Downloads)"
                );
                return;
            }

            scanBtn.disabled = true;
            scanBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Scanning...';
            scanProgress.classList.remove("d-none");
            scanStatus.textContent = "Scanning folder: " + folderPath;
        });
    }

    function showValidationError(message) {
        const existingAlert = document.querySelector(".custom-validation-alert");
        if (existingAlert) {
            existingAlert.remove();
        }

        const alertDiv = document.createElement("div");
        alertDiv.className =
            "alert alert-danger alert-dismissible fade show custom-validation-alert mt-3";
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        scanForm.parentNode.insertBefore(alertDiv, scanForm.nextSibling);

        setTimeout(function () {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    const deleteModal = new bootstrap.Modal(
        document.getElementById("deleteModal")
    );
    const confirmDeleteBtn = document.getElementById("confirmDelete");
    const deleteFileName = document.getElementById("deleteFileName");
    const deleteUrl = document.getElementById("deleteUrl");

    let currentDeletePath = null;

    document.addEventListener("click", function (e) {
        const deleteBtn = e.target.closest(".delete-duplicate");
        if (deleteBtn) {
            e.preventDefault();
            currentDeletePath = deleteBtn.getAttribute("data-file-path");
            const fileName = deleteBtn.getAttribute("data-file-name");

            if (deleteFileName) {
                deleteFileName.textContent = fileName;
            }

            deleteModal.show();
        }
    });

    if (confirmDeleteBtn && deleteUrl) {
        confirmDeleteBtn.addEventListener("click", function () {
            if (!currentDeletePath) return;

            confirmDeleteBtn.disabled = true;
            confirmDeleteBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Deleting...';

            fetch(deleteUrl.value, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    file_path: currentDeletePath,
                }),
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.success) {
                        showToast("success", data.message);

                        const rows = document.querySelectorAll(
                            '.delete-duplicate[data-file-path="' +
                                currentDeletePath +
                                '"]'
                        );
                        rows.forEach(function (btn) {
                            const row = btn.closest("tr");
                            if (row) {
                                row.style.transition = "opacity 0.3s ease";
                                row.style.opacity = "0";
                                setTimeout(function () {
                                    row.remove();
                                }, 300);
                            }
                        });
                    } else {
                        showToast("danger", data.message);
                    }
                })
                .catch(function (error) {
                    showToast("danger", "An error occurred while deleting the file.");
                    console.error("Delete error:", error);
                })
                .finally(function () {
                    confirmDeleteBtn.disabled = false;
                    confirmDeleteBtn.innerHTML =
                        '<i class="bi bi-trash me-1"></i>Delete';
                    deleteModal.hide();
                    currentDeletePath = null;
                });
        });
    }

    function showToast(type, message) {
        var iconMap = {
            success: "bi-check-circle-fill",
            danger: "bi-exclamation-triangle-fill",
            warning: "bi-exclamation-circle-fill",
            info: "bi-info-circle-fill",
        };
        var icon = iconMap[type] || "bi-info-circle-fill";

        var toastContainer = document.querySelector(".toast-container");
        if (!toastContainer) {
            toastContainer = document.createElement("div");
            toastContainer.className =
                "toast-container position-fixed bottom-0 end-0 p-3";
            document.body.appendChild(toastContainer);
        }

        var toastId = "toast-" + Date.now();
        var toastHtml =
            '<div id="' +
            toastId +
            '" class="toast align-items-center text-bg-' +
            type +
            ' border-0" role="alert">' +
            '<div class="d-flex">' +
            '<div class="toast-body">' +
            '<i class="bi ' +
            icon +
            ' me-2"></i>' +
            message +
            "</div>" +
            '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
            "</div>" +
            "</div>";

        toastContainer.insertAdjacentHTML("beforeend", toastHtml);

        var toastElement = document.getElementById(toastId);
        var toast = new bootstrap.Toast(toastElement, {
            delay: 4000,
        });
        toast.show();

        toastElement.addEventListener("hidden.bs.toast", function () {
            toastElement.remove();
        });
    }

    if (folderPathInput) {
        folderPathInput.addEventListener("paste", function () {
            setTimeout(function () {
                folderPathInput.value = folderPathInput.value.trim();
            }, 10);
        });
    }

    var tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
});
