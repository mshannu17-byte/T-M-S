// =========================================================
// CARELINE TELEMEDICINE SYSTEM
// Patient Module JavaScript
// =========================================================


// =========================================================
// LOAD PATIENT PROFILE
// =========================================================

async function loadPatientProfile() {

    if (!currentUser) {
        return;
    }

    try {

        const response = await fetch(
            `/api/patient/profile/${currentUser.id}`
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error(
                data.message || "Unable to load patient profile."
            );
            return;
        }

        return data.profile;

    } catch (error) {

        console.error(
            "Patient profile error:",
            error
        );
    }
}


// =========================================================
// LOAD DOCTORS
// =========================================================

async function loadDoctors() {

    if (!currentUser || currentUser.role !== "patient") {
        return;
    }

    showPatientArea("patient-doctors-area");

    const doctorsList =
        document.getElementById("doctors-list");

    doctorsList.innerHTML = `
        <div class="data-card">
            Loading doctors...
        </div>
    `;


    const searchInput =
        document.getElementById("doctor-search");

    const specialization =
        searchInput
            ? searchInput.value.trim()
            : "";


    try {

        let url = "/api/patient/doctors";

        if (specialization) {

            url +=
                "?specialization=" +
                encodeURIComponent(
                    specialization
                );
        }


        const response =
            await fetch(url);

        const data =
            await response.json();


        if (!response.ok || !data.success) {

            doctorsList.innerHTML = `
                <div class="data-card">
                    ${escapeHtml(
                        data.message ||
                        "Unable to load doctors."
                    )}
                </div>
            `;

            return;
        }


        if (!data.doctors || data.doctors.length === 0) {

            doctorsList.innerHTML = `
                <div class="data-card">
                    No approved doctors found.
                </div>
            `;

            return;
        }


        doctorsList.innerHTML =
            data.doctors
                .map(function (doctor) {

                    return `
                        <div class="doctor-card">

                            <h4>
                                Dr. ${escapeHtml(
                                    doctor.full_name
                                )}
                            </h4>

                            <p>
                                <strong>
                                    Specialization:
                                </strong>
                                ${escapeHtml(
                                    doctor.specialization ||
                                    "Not specified"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Qualification:
                                </strong>
                                ${escapeHtml(
                                    doctor.qualification ||
                                    "Not specified"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Experience:
                                </strong>
                                ${escapeHtml(
                                    String(
                                        doctor.experience ?? 0
                                    )
                                )}
                                years
                            </p>

                            <p>
                                <strong>
                                    Consultation Fee:
                                </strong>
                                ₹${escapeHtml(
                                    String(
                                        doctor.consultation_fee ?? 0
                                    )
                                )}
                            </p>

                            <p>
                                ${escapeHtml(
                                    doctor.about ||
                                    "No description available."
                                )}
                            </p>

                            <div class="action-buttons">

                                <button
                                    type="button"
                                    class="action-button action-primary"
                                    onclick="openAppointmentModal(
                                        ${doctor.doctor_id},
                                        '${escapeJs(
                                            doctor.full_name
                                        )}'
                                    )"
                                >
                                    Book Appointment
                                </button>

                            </div>

                        </div>
                    `;
                })
                .join("");


    } catch (error) {

        console.error(
            "Load doctors error:",
            error
        );

        doctorsList.innerHTML = `
            <div class="data-card">
                Unable to connect to the CareLine server.
            </div>
        `;
    }
}


// =========================================================
// APPOINTMENT MODAL
// =========================================================

function openAppointmentModal(
    doctorId,
    doctorName
) {

    document.getElementById(
        "selected-doctor-id"
    ).value = doctorId;


    document.getElementById(
        "selected-doctor-name"
    ).textContent =
        "Selected Doctor: Dr. " +
        doctorName;


    document.getElementById(
        "appointment-date"
    ).value = "";


    document.getElementById(
        "appointment-time"
    ).value = "";


    document.getElementById(
        "appointment-reason"
    ).value = "";


    clearMessage(
        "appointment-message"
    );


    document
        .getElementById("appointment-modal")
        .classList.remove("hidden");
}


function closeAppointmentModal() {

    document
        .getElementById("appointment-modal")
        .classList.add("hidden");
}


// =========================================================
// BOOK APPOINTMENT
// =========================================================

async function bookAppointment() {

    if (!currentUser) {

        showMessage(
            "appointment-message",
            "Please login first.",
            "error"
        );

        return;
    }


    const doctorId =
        document.getElementById(
            "selected-doctor-id"
        ).value;


    const appointmentDate =
        document.getElementById(
            "appointment-date"
        ).value;


    const appointmentTime =
        document.getElementById(
            "appointment-time"
        ).value;


    const reason =
        document.getElementById(
            "appointment-reason"
        ).value.trim();


    if (
        !doctorId ||
        !appointmentDate ||
        !appointmentTime
    ) {

        showMessage(
            "appointment-message",
            "Please select the date and time.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/patient/appointments",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    user_id:
                        currentUser.id,

                    doctor_id:
                        Number(doctorId),

                    appointment_date:
                        appointmentDate,

                    appointment_time:
                        appointmentTime,

                    reason:
                        reason
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            showMessage(
                "appointment-message",
                data.message ||
                    "Unable to book appointment.",
                "error"
            );

            return;
        }


        showMessage(
            "appointment-message",
            "Appointment booked successfully.",
            "success"
        );


        setTimeout(function () {

            closeAppointmentModal();

            loadPatientAppointments();

        }, 1200);


    } catch (error) {

        console.error(
            "Book appointment error:",
            error
        );

        showMessage(
            "appointment-message",
            "Unable to connect to the CareLine server.",
            "error"
        );
    }
}


// =========================================================
// LOAD PATIENT APPOINTMENTS
// =========================================================

async function loadPatientAppointments() {

    if (!currentUser) {
        return;
    }

    showPatientArea(
        "patient-appointments-area"
    );


    const list =
        document.getElementById(
            "patient-appointments-list"
        );


    list.innerHTML = `
        <div class="data-card">
            Loading appointments...
        </div>
    `;


    try {

        const response = await fetch(
            `/api/patient/appointments/${currentUser.id}`
        );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            list.innerHTML = `
                <div class="data-card">
                    ${escapeHtml(
                        data.message ||
                        "Unable to load appointments."
                    )}
                </div>
            `;

            return;
        }


        if (
            !data.appointments ||
            data.appointments.length === 0
        ) {

            list.innerHTML = `
                <div class="data-card">
                    You do not have any appointments yet.
                </div>
            `;

            return;
        }


        list.innerHTML =
            data.appointments
                .map(function (appointment) {

                    return `
                        <div class="data-card">

                            <h4>
                                Dr. ${escapeHtml(
                                    appointment.doctor_name ||
                                    "Doctor"
                                )}
                            </h4>

                            <p>
                                <strong>
                                    Specialization:
                                </strong>
                                ${escapeHtml(
                                    appointment.specialization ||
                                    "Not specified"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Date:
                                </strong>
                                ${escapeHtml(
                                    formatDate(
                                        appointment.appointment_date
                                    )
                                )}
                            </p>

                            <p>
                                <strong>
                                    Time:
                                </strong>
                                ${escapeHtml(
                                    formatTime(
                                        appointment.appointment_time
                                    )
                                )}
                            </p>

                            <p>
                                <strong>
                                    Reason:
                                </strong>
                                ${escapeHtml(
                                    appointment.reason ||
                                    "Not provided"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Status:
                                </strong>

                                ${getStatusBadge(
                                    appointment.status
                                )}
                            </p>

                            ${
                                appointment.status ===
                                "accepted"
                                ? `
                                    <div class="action-buttons">

                                        ${
                                            appointment.meeting_link
                                            ? `
                                                <a
                                                    href="${escapeAttribute(
                                                        appointment.meeting_link
                                                    )}"
                                                    target="_blank"
                                                    class="action-button action-success"
                                                >
                                                    Join Consultation
                                                </a>
                                            `
                                            : ""
                                        }

                                        <button
                                            type="button"
                                            class="action-button action-danger"
                                            onclick="cancelAppointment(
                                                ${appointment.id}
                                            )"
                                        >
                                            Cancel Appointment
                                        </button>

                                    </div>
                                `
                                : ""
                            }

                            ${
                                appointment.status ===
                                "pending"
                                ? `
                                    <div class="action-buttons">

                                        <button
                                            type="button"
                                            class="action-button action-danger"
                                            onclick="cancelAppointment(
                                                ${appointment.id}
                                            )"
                                        >
                                            Cancel Appointment
                                        </button>

                                    </div>
                                `
                                : ""
                            }

                        </div>
                    `;
                })
                .join("");


    } catch (error) {

        console.error(
            "Load patient appointments error:",
            error
        );

        list.innerHTML = `
            <div class="data-card">
                Unable to connect to the CareLine server.
            </div>
        `;
    }
}


// =========================================================
// CANCEL APPOINTMENT
// =========================================================

async function cancelAppointment(
    appointmentId
) {

    if (
        !confirm(
            "Are you sure you want to cancel this appointment?"
        )
    ) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/patient/appointments/${appointmentId}/cancel`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        user_id: currentUser.id
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            alert(
                data.message ||
                "Unable to cancel appointment."
            );

            return;
        }


        alert(
            "Appointment cancelled successfully."
        );


        loadPatientAppointments();


    } catch (error) {

        console.error(
            "Cancel appointment error:",
            error
        );

        alert(
            "Unable to connect to the CareLine server."
        );
    }
}


// =========================================================
// LOAD MEDICAL RECORDS
// =========================================================

async function loadPatientRecords() {

    if (!currentUser) {
        return;
    }

    showPatientArea(
        "patient-records-area"
    );


    const list =
        document.getElementById(
            "patient-records-list"
        );


    list.innerHTML = `
        <div class="data-card">
            Loading medical records...
        </div>
    `;


    try {

        const response =
            await fetch(
                `/api/patient/records/${currentUser.id}`
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            list.innerHTML = `
                <div class="data-card">
                    ${escapeHtml(
                        data.message ||
                        "Unable to load medical records."
                    )}
                </div>
            `;

            return;
        }


        if (
            !data.records ||
            data.records.length === 0
        ) {

            list.innerHTML = `
                <div class="data-card">
                    No medical records are available.
                </div>
            `;

            return;
        }


        list.innerHTML =
            data.records
                .map(function (record) {

                    return `
                        <div class="data-card">

                            <h4>
                                ${escapeHtml(
                                    record.title ||
                                    "Medical Record"
                                )}
                            </h4>

                            <p>
                                <strong>
                                    Type:
                                </strong>
                                ${escapeHtml(
                                    record.record_type ||
                                    "General"
                                )}
                            </p>

                            <p>
                                ${escapeHtml(
                                    record.description ||
                                    "No description available."
                                )}
                            </p>

                            <p>
                                <strong>
                                    Date:
                                </strong>
                                ${escapeHtml(
                                    formatDateTime(
                                        record.created_at
                                    )
                                )}
                            </p>

                        </div>
                    `;
                })
                .join("");


    } catch (error) {

        console.error(
            "Medical records error:",
            error
        );

        list.innerHTML = `
            <div class="data-card">
                Unable to connect to the CareLine server.
            </div>
        `;
    }
}


// =========================================================
// LOAD CONSULTATION HISTORY
// =========================================================

async function loadPatientConsultations() {

    if (!currentUser) {
        return;
    }

    showPatientArea(
        "patient-consultations-area"
    );


    const list =
        document.getElementById(
            "patient-consultations-list"
        );


    list.innerHTML = `
        <div class="data-card">
            Loading consultation history...
        </div>
    `;


    try {

        const response =
            await fetch(
                `/api/patient/consultations/${currentUser.id}`
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            list.innerHTML = `
                <div class="data-card">
                    ${escapeHtml(
                        data.message ||
                        "Unable to load consultation history."
                    )}
                </div>
            `;

            return;
        }


        if (
            !data.consultations ||
            data.consultations.length === 0
        ) {

            list.innerHTML = `
                <div class="data-card">
                    No completed consultations found.
                </div>
            `;

            return;
        }


        list.innerHTML =
            data.consultations
                .map(function (consultation) {

                    return `
                        <div class="data-card">

                            <h4>
                                Consultation with Dr.
                                ${escapeHtml(
                                    consultation.doctor_name ||
                                    "Doctor"
                                )}
                            </h4>

                            <p>
                                <strong>
                                    Date:
                                </strong>
                                ${escapeHtml(
                                    formatDateTime(
                                        consultation.consultation_date
                                    )
                                )}
                            </p>

                            <p>
                                <strong>
                                    Symptoms:
                                </strong>
                                ${escapeHtml(
                                    consultation.symptoms ||
                                    "Not recorded"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Diagnosis:
                                </strong>
                                ${escapeHtml(
                                    consultation.diagnosis ||
                                    "Not recorded"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Prescription:
                                </strong>
                                ${escapeHtml(
                                    consultation.prescription ||
                                    "Not recorded"
                                )}
                            </p>

                            <p>
                                <strong>
                                    Doctor Notes:
                                </strong>
                                ${escapeHtml(
                                    consultation.doctor_notes ||
                                    "No additional notes."
                                )}
                            </p>

                        </div>
                    `;
                })
                .join("");


    } catch (error) {

        console.error(
            "Consultation history error:",
            error
        );

        list.innerHTML = `
            <div class="data-card">
                Unable to connect to the CareLine server.
            </div>
        `;
    }
}


// =========================================================
// SHOW PATIENT CHAT
// =========================================================

function showPatientChat() {

    showPatientArea(
        "patient-chat-area"
    );

    loadChatHistory();
}


// =========================================================
// LOAD CHAT HISTORY
// =========================================================

async function loadChatHistory() {

    if (!currentUser) {
        return;
    }


    const chatBox =
        document.getElementById(
            "chat-messages"
        );


    if (!chatBox) {
        return;
    }


    chatBox.innerHTML = `
        <div class="chat-message chat-bot">
            Hello! I'm the CareLine health assistant.
            How can I help you with a general health question?
        </div>
    `;


    try {

        const response =
            await fetch(
                `/api/patient/chat/${currentUser.id}`
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {
            return;
        }


        if (
            data.messages &&
            data.messages.length > 0
        ) {

            chatBox.innerHTML = "";


            data.messages.forEach(
                function (message) {

                    addChatMessage(
                        message.sender,
                        message.message
                    );
                }
            );
        }


        chatBox.scrollTop =
            chatBox.scrollHeight;


    } catch (error) {

        console.error(
            "Chat history error:",
            error
        );
    }
}


// =========================================================
// SEND CHAT MESSAGE
// =========================================================

async function sendChatMessage() {

    if (!currentUser) {
        return;
    }


    const input =
        document.getElementById(
            "chat-input"
        );


    const message =
        input.value.trim();


    if (!message) {
        return;
    }


    addChatMessage(
        "user",
        message
    );


    input.value = "";


    try {

        const response =
            await fetch(
                "/api/patient/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        user_id:
                            currentUser.id,

                        message:
                            message
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            addChatMessage(
                "bot",
                data.message ||
                    "Sorry, I could not process your message."
            );

            return;
        }


        addChatMessage(
            "bot",
            data.reply ||
                "Please consult a qualified doctor for medical advice."
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        addChatMessage(
            "bot",
            "Unable to connect to the CareLine server."
        );
    }
}


// =========================================================
// ADD CHAT MESSAGE
// =========================================================

function addChatMessage(
    sender,
    message
) {

    const chatBox =
        document.getElementById(
            "chat-messages"
        );


    if (!chatBox) {
        return;
    }


    const messageElement =
        document.createElement("div");


    messageElement.classList.add(
        "chat-message"
    );


    if (sender === "user") {

        messageElement.classList.add(
            "chat-user"
        );

    } else {

        messageElement.classList.add(
            "chat-bot"
        );
    }


    messageElement.textContent =
        message;


    chatBox.appendChild(
        messageElement
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// =========================================================
// STATUS BADGE
// =========================================================

function getStatusBadge(status) {

    const safeStatus =
        status || "unknown";


    return `
        <span class="status-badge status-${escapeAttribute(
            safeStatus
        )}">
            ${escapeHtml(
                safeStatus
            )}
        </span>
    `;
}


// =========================================================
// DATE FORMATTING
// =========================================================

function formatDate(value) {

    if (!value) {
        return "Not available";
    }


    try {

        const date =
            new Date(value);


        if (isNaN(date.getTime())) {
            return String(value);
        }


        return date.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );

    } catch (error) {

        return String(value);
    }
}


// =========================================================
// TIME FORMATTING
// =========================================================

function formatTime(value) {

    if (!value) {
        return "Not available";
    }


    const valueString =
        String(value);


    const parts =
        valueString.split(":");


    if (parts.length < 2) {
        return valueString;
    }


    let hour =
        parseInt(parts[0], 10);

    const minute =
        parts[1];


    if (isNaN(hour)) {
        return valueString;
    }


    const period =
        hour >= 12
            ? "PM"
            : "AM";


    hour =
        hour % 12 || 12;


    return `${hour}:${minute} ${period}`;
}


// =========================================================
// DATE AND TIME FORMATTING
// =========================================================

function formatDateTime(value) {

    if (!value) {
        return "Not available";
    }


    try {

        const date =
            new Date(value);


        if (isNaN(date.getTime())) {
            return String(value);
        }


        return date.toLocaleString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );

    } catch (error) {

        return String(value);
    }
}


// =========================================================
// BASIC HTML SAFETY
// =========================================================

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================================================
// JAVASCRIPT STRING SAFETY
// =========================================================

function escapeJs(value) {

    if (value === null ||
        value === undefined) {

        return "";
    }


    return String(value)
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\r/g, "")
        .replace(/\n/g, "\\n");
}


// =========================================================
// ATTRIBUTE SAFETY
// =========================================================

function escapeAttribute(value) {

    return escapeHtml(value);
}