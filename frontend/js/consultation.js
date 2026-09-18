async function leaveConsultation() {
    const params = new URLSearchParams(window.location.search);
    const appointmentId = params.get("appointment_id");
    const savedUser = localStorage.getItem("careline_user");

    if (!appointmentId || !savedUser) {
        window.location.href = "/";
        return;
    }

    const user = JSON.parse(savedUser);
    let endpoint;
    let payload;

    if (user.role === "doctor") {
        endpoint = "/api/doctor/consultations/complete";
        payload = {
            user_id: user.id,
            appointment_id: Number(appointmentId),
            symptoms: "",
            diagnosis: "",
            prescription: "",
            doctor_notes: ""
        };
    } else {
        endpoint = `/api/patient/appointments/${appointmentId}/complete`;
        payload = { user_id: user.id };
    }

    try {
        const response = await fetch(endpoint, {
            method: user.role === "doctor" ? "POST" : "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            document.getElementById("consultationMessage").textContent =
                data.message || "Unable to complete consultation.";
            return;
        }

        window.location.href = "/";
    } catch (error) {
        console.error("Leave consultation error:", error);
        document.getElementById("consultationMessage").textContent =
            "Unable to connect to the CareLine server.";
    }
}
