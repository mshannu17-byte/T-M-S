async function loadDoctorAppointments() {
	if (!currentUser || currentUser.role !== "doctor") {
		return;
	}

	showDoctorArea("doctor-appointments-area");

	const list = document.getElementById("doctor-appointments-list");
	list.innerHTML = `<div class="data-card">Loading appointments...</div>`;

	try {
		const response = await fetch(
			`/api/doctor/appointments/${currentUser.id}`
		);
		const data = await response.json();

		if (!response.ok || !data.success) {
			list.innerHTML = `
				<div class="data-card">
					${escapeHtml(data.message || "Unable to load appointments.")}
				</div>
			`;
			return;
		}

		const appointments = data.appointments || [];

		if (appointments.length === 0) {
			list.innerHTML = `
				<div class="data-card">No appointment requests found.</div>
			`;
			return;
		}

		list.innerHTML = appointments.map(function (appointment) {
			const actions = appointment.status === "pending"
				? `
					<div class="action-buttons">
						<button
							type="button"
							class="action-button action-success"
							onclick="acceptDoctorAppointment(${appointment.id})"
						>
							Accept
						</button>
						<button
							type="button"
							class="action-button action-danger"
							onclick="rejectDoctorAppointment(${appointment.id})"
						>
							Reject
						</button>
					</div>
				`
				: appointment.meeting_link
					? `<a class="action-button action-primary" href="${escapeAttribute(appointment.meeting_link)}">Open Consultation</a>`
					: "";

			return `
				<div class="data-card">
					<h4>${escapeHtml(appointment.patient_name || "Patient")}</h4>
					<p><strong>Email:</strong> ${escapeHtml(appointment.patient_email || "Not provided")}</p>
					<p><strong>Phone:</strong> ${escapeHtml(appointment.patient_phone || "Not provided")}</p>
					<p><strong>Date:</strong> ${escapeHtml(formatDate(appointment.appointment_date))}</p>
					<p><strong>Time:</strong> ${escapeHtml(formatTime(appointment.appointment_time))}</p>
					<p><strong>Reason:</strong> ${escapeHtml(appointment.reason || "Not provided")}</p>
					<p><strong>Status:</strong> ${getStatusBadge(appointment.status)}</p>
					${actions}
				</div>
			`;
		}).join("");
	} catch (error) {
		console.error("Doctor appointments error:", error);
		list.innerHTML = `
			<div class="data-card">Unable to connect to the CareLine server.</div>
		`;
	}
}


async function updateDoctorAppointment(appointmentId, action) {
	if (!currentUser || !appointmentId) {
		return;
	}

	try {
		const response = await fetch(
			`/api/doctor/appointments/${appointmentId}/${action}`,
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
		const data = await response.json();

		if (!response.ok || !data.success) {
			alert(data.message || "Unable to update appointment.");
			return;
		}

		await loadDoctorAppointments();
	} catch (error) {
		console.error("Doctor appointment update error:", error);
		alert("Unable to connect to the CareLine server.");
	}
}


function acceptDoctorAppointment(appointmentId) {
	updateDoctorAppointment(appointmentId, "accept");
}


function rejectDoctorAppointment(appointmentId) {
	updateDoctorAppointment(appointmentId, "reject");
}
