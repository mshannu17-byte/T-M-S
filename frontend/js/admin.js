// ==========================================
// CareLine - Admin Module
// ==========================================

async function loadAdminDashboard() {
    if (!currentUser || currentUser.role !== "admin") {
        return;
    }

    await loadPendingDoctors();
    await loadAllDoctors();
    await loadAllPatients();
    await loadAllAppointments();
}


// ==========================================
// Load Pending Doctor Requests
// ==========================================

async function loadPendingDoctors() {
    const container =
        document.getElementById("pending-doctors-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Loading doctor requests...
        </div>
    `;

    try {
        const response = await fetch(
            "/api/admin/doctors/pending"
        );

        const data = await response.json();

        if (!data.success) {
            container.innerHTML = `
                <div class="message error">
                    ${escapeHtml(data.message)}
                </div>
            `;
            return;
        }

        const doctors = data.doctors || [];

        if (doctors.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No pending requests</h3>
                    <p>There are no doctor registration requests waiting for approval.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = doctors.map((doctor) => `
            <div class="data-card">

                <div class="data-card-header">
                    <div>
                        <h3>
                            ${escapeHtml(
                                doctor.full_name || "Doctor"
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                doctor.email || ""
                            )}
                        </p>
                    </div>

                    <span class="status-badge pending">
                        Pending
                    </span>
                </div>

                <div class="data-grid">

                    <div>
                        <strong>Phone</strong>
                        <span>
                            ${escapeHtml(
                                doctor.phone || "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Specialization</strong>
                        <span>
                            ${escapeHtml(
                                doctor.specialization ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Qualification</strong>
                        <span>
                            ${escapeHtml(
                                doctor.qualification ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Experience</strong>
                        <span>
                            ${escapeHtml(
                                doctor.experience ||
                                "0"
                            )} years
                        </span>
                    </div>

                    <div>
                        <strong>License Number</strong>
                        <span>
                            ${escapeHtml(
                                doctor.license_number ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Consultation Fee</strong>
                        <span>
                            ₹${escapeHtml(
                                doctor.consultation_fee ||
                                "0"
                            )}
                        </span>
                    </div>

                </div>

                <div class="action-buttons">

                    <button
                        class="btn btn-success"
                        onclick="approveDoctor(${doctor.doctor_id})"
                    >
                        Approve
                    </button>

                    <button
                        class="btn btn-danger"
                        onclick="rejectDoctor(${doctor.doctor_id})"
                    >
                        Reject
                    </button>

                </div>

            </div>
        `).join("");

    } catch (error) {
        console.error(
            "Pending doctors error:",
            error
        );

        container.innerHTML = `
            <div class="message error">
                Unable to load doctor requests.
            </div>
        `;
    }
}


// ==========================================
// Approve Doctor
// ==========================================

async function approveDoctor(doctorId) {

    if (!doctorId) {
        return;
    }

    const confirmed = confirm(
        "Are you sure you want to approve this doctor?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/api/admin/doctors/${doctorId}/approve`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        const data = await response.json();

        if (data.success) {

            showMessage(
                "adminMessage",
                "Doctor approved successfully.",
                "success"
            );

            await loadPendingDoctors();
            await loadAllDoctors();

        } else {

            showMessage(
                "adminMessage",
                data.message ||
                "Unable to approve doctor.",
                "error"
            );
        }

    } catch (error) {

        console.error(
            "Approve doctor error:",
            error
        );

        showMessage(
            "adminMessage",
            "Something went wrong while approving the doctor.",
            "error"
        );
    }
}


// ==========================================
// Reject Doctor
// ==========================================

async function rejectDoctor(doctorId) {

    if (!doctorId) {
        return;
    }

    const confirmed = confirm(
        "Are you sure you want to reject this doctor?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/api/admin/doctors/${doctorId}/reject`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        const data = await response.json();

        if (data.success) {

            showMessage(
                "adminMessage",
                "Doctor rejected successfully.",
                "success"
            );

            await loadPendingDoctors();
            await loadAllDoctors();

        } else {

            showMessage(
                "adminMessage",
                data.message ||
                "Unable to reject doctor.",
                "error"
            );
        }

    } catch (error) {

        console.error(
            "Reject doctor error:",
            error
        );

        showMessage(
            "adminMessage",
            "Something went wrong while rejecting the doctor.",
            "error"
        );
    }
}


// ==========================================
// Load All Doctors
// ==========================================

async function loadAllDoctors() {

    const container =
        document.getElementById("admin-doctors-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Loading doctors...
        </div>
    `;

    try {

        const response = await fetch(
            "/api/admin/doctors"
        );

        const data = await response.json();

        if (!data.success) {
            container.innerHTML = `
                <div class="message error">
                    ${escapeHtml(data.message)}
                </div>
            `;
            return;
        }

        const doctors = data.doctors || [];

        if (doctors.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No doctors found</h3>
                </div>
            `;
            return;
        }

        container.innerHTML = doctors.map((doctor) => {

            const status =
                doctor.status || "inactive";

            let actionButton = "";

            if (status === "active") {

                actionButton = `
                    <button
                        class="btn btn-danger"
                        onclick="deleteDoctor(${doctor.id})"
                    >
                        Deactivate
                    </button>
                `;

            } else {

                actionButton = `
                    <button
                        class="btn btn-success"
                        onclick="reactivateDoctor(${doctor.id})"
                    >
                        Reactivate
                    </button>
                `;
            }

            return `
                <div class="data-card">

                    <div class="data-card-header">

                        <div>
                            <h3>
                                ${escapeHtml(
                                    doctor.full_name ||
                                    "Doctor"
                                )}
                            </h3>

                            <p>
                                ${escapeHtml(
                                    doctor.email || ""
                                )}
                            </p>
                        </div>

                        ${getStatusBadge(status)}

                    </div>

                    <div class="data-grid">

                        <div>
                            <strong>Specialization</strong>
                            <span>
                                ${escapeHtml(
                                    doctor.specialization ||
                                    "Not provided"
                                )}
                            </span>
                        </div>

                        <div>
                            <strong>Qualification</strong>
                            <span>
                                ${escapeHtml(
                                    doctor.qualification ||
                                    "Not provided"
                                )}
                            </span>
                        </div>

                        <div>
                            <strong>Experience</strong>
                            <span>
                                ${escapeHtml(
                                    doctor.experience ||
                                    "0"
                                )} years
                            </span>
                        </div>

                        <div>
                            <strong>License</strong>
                            <span>
                                ${escapeHtml(
                                    doctor.license_number ||
                                    "Not provided"
                                )}
                            </span>
                        </div>

                        <div>
                            <strong>Consultation Fee</strong>
                            <span>
                                ₹${escapeHtml(
                                    doctor.consultation_fee ||
                                    "0"
                                )}
                            </span>
                        </div>

                    </div>

                    <div class="action-buttons">
                        ${actionButton}
                    </div>

                </div>
            `;
        }).join("");

    } catch (error) {

        console.error(
            "All doctors error:",
            error
        );

        container.innerHTML = `
            <div class="message error">
                Unable to load doctors.
            </div>
        `;
    }
}


// ==========================================
// Deactivate Doctor
// ==========================================

async function deleteDoctor(doctorId) {

    if (!doctorId) {
        return;
    }

    const confirmed = confirm(
        "This will deactivate the doctor account. Continue?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/api/admin/doctors/${doctorId}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (data.success) {

            showMessage(
                "adminMessage",
                "Doctor deactivated successfully.",
                "success"
            );

            await loadAllDoctors();

        } else {

            showMessage(
                "adminMessage",
                data.message ||
                "Unable to deactivate doctor.",
                "error"
            );
        }

    } catch (error) {

        console.error(
            "Deactivate doctor error:",
            error
        );

        showMessage(
            "adminMessage",
            "Something went wrong while deactivating the doctor.",
            "error"
        );
    }
}


// ==========================================
// Reactivate Doctor
// ==========================================

async function reactivateDoctor(doctorId) {

    if (!doctorId) {
        return;
    }

    const confirmed = confirm(
        "Do you want to reactivate this doctor?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/api/admin/doctors/${doctorId}/reactivate`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        );

        const data = await response.json();

        if (data.success) {

            showMessage(
                "adminMessage",
                "Doctor reactivated successfully.",
                "success"
            );

            await loadAllDoctors();

        } else {

            showMessage(
                "adminMessage",
                data.message ||
                "Unable to reactivate doctor.",
                "error"
            );
        }

    } catch (error) {

        console.error(
            "Reactivate doctor error:",
            error
        );

        showMessage(
            "adminMessage",
            "Something went wrong while reactivating the doctor.",
            "error"
        );
    }
}


// ==========================================
// Load All Patients
// ==========================================

async function loadAllPatients() {

    const container =
        document.getElementById("admin-patients-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Loading patients...
        </div>
    `;

    try {

        const response = await fetch(
            "/api/admin/patients"
        );

        const data = await response.json();

        if (!data.success) {
            container.innerHTML = `
                <div class="message error">
                    ${escapeHtml(data.message)}
                </div>
            `;
            return;
        }

        const patients = data.patients || [];

        if (patients.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No patients found</h3>
                </div>
            `;
            return;
        }

        container.innerHTML = patients.map((patient) => `
            <div class="data-card">

                <div class="data-card-header">

                    <div>
                        <h3>
                            ${escapeHtml(
                                patient.full_name ||
                                "Patient"
                            )}
                        </h3>

                        <p>
                            ${escapeHtml(
                                patient.email || ""
                            )}
                        </p>
                    </div>

                    ${getStatusBadge(
                        patient.status || "active"
                    )}

                </div>

                <div class="data-grid">

                    <div>
                        <strong>Phone</strong>
                        <span>
                            ${escapeHtml(
                                patient.phone ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Gender</strong>
                        <span>
                            ${escapeHtml(
                                patient.gender ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Blood Group</strong>
                        <span>
                            ${escapeHtml(
                                patient.blood_group ||
                                "Not provided"
                            )}
                        </span>
                    </div>

                    <div>
                        <strong>Date of Birth</strong>
                        <span>
                            ${formatDate(
                                patient.date_of_birth
                            )}
                        </span>
                    </div>

                </div>

            </div>
        `).join("");

    } catch (error) {

        console.error(
            "Patients error:",
            error
        );

        container.innerHTML = `
            <div class="message error">
                Unable to load patients.
            </div>
        `;
    }
}


// ==========================================
// Load All Appointments
// ==========================================

async function loadAllAppointments() {

    const container =
        document.getElementById("admin-appointments-list");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            Loading appointments...
        </div>
    `;

    try {

        const response = await fetch(
            "/api/admin/appointments"
        );

        const data = await response.json();

        if (!data.success) {
            container.innerHTML = `
                <div class="message error">
                    ${escapeHtml(data.message)}
                </div>
            `;
            return;
        }

        const appointments =
            data.appointments || [];

        if (appointments.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No appointments found</h3>
                </div>
            `;
            return;
        }

        container.innerHTML = appointments.map(
            (appointment) => `
                <div class="data-card">

                    <div class="data-card-header">

                        <div>
                            <h3>
                                ${escapeHtml(
                                    appointment.patient_name ||
                                    "Patient"
                                )}
                            </h3>

                            <p>
                                Doctor:
                                ${escapeHtml(
                                    appointment.doctor_name ||
                                    "Doctor"
                                )}
                            </p>
                        </div>

                        ${getStatusBadge(
                            appointment.status ||
                            "pending"
                        )}

                    </div>

                    <div class="data-grid">

                        <div>
                            <strong>Date</strong>
                            <span>
                                ${formatDate(
                                    appointment.appointment_date
                                )}
                            </span>
                        </div>

                        <div>
                            <strong>Time</strong>
                            <span>
                                ${formatTime(
                                    appointment.appointment_time
                                )}
                            </span>
                        </div>

                        <div>
                            <strong>Reason</strong>
                            <span>
                                ${escapeHtml(
                                    appointment.reason ||
                                    "Not provided"
                                )}
                            </span>
                        </div>

                    </div>

                </div>
            `
        ).join("");

    } catch (error) {

        console.error(
            "Appointments error:",
            error
        );

        container.innerHTML = `
            <div class="message error">
                Unable to load appointments.
            </div>
        `;
    }
}


// ==========================================
// Initialize Admin Dashboard
// ==========================================

async function initializeAdminDashboard() {

    if (!currentUser || currentUser.role !== "admin") {
        return;
    }

    await loadAdminDashboard();
}


// ==========================================
// Event Listener
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    () => {
        if (
            typeof currentUser !== "undefined" &&
            currentUser &&
            currentUser.role === "admin"
        ) {
            initializeAdminDashboard();
        }
    }
);