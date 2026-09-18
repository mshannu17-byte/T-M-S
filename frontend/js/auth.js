// =========================================================
// CARELINE TELEMEDICINE SYSTEM
// Authentication JavaScript
// =========================================================


// =========================================================
// GLOBAL USER DATA
// =========================================================

let currentUser = null;


// =========================================================
// PAGE SECTION CONTROL
// =========================================================

function hideAllSections() {

    const sections = document.querySelectorAll(
        ".page-section, .dashboard-section"
    );

    sections.forEach(function (section) {
        section.classList.remove("active-section");
    });
}


function showHome() {

    hideAllSections();

    document
        .getElementById("home-section")
        .classList.add("active-section");

    updateNavigation(false);
}


function showLogin() {

    hideAllSections();

    document
        .getElementById("login-section")
        .classList.add("active-section");

    updateNavigation(false);
}


function showRegistration() {

    hideAllSections();

    document
        .getElementById("registration-section")
        .classList.add("active-section");

    updateNavigation(false);

    showRegistrationForm("patient");
}


function showForgotPassword() {

    hideAllSections();

    document
        .getElementById("forgot-password-section")
        .classList.add("active-section");

    updateNavigation(false);
}


// =========================================================
// REGISTRATION FORM SWITCHING
// =========================================================

function showRegistrationForm(type) {

    const patientForm =
        document.getElementById(
            "patient-registration-form"
        );

    const doctorForm =
        document.getElementById(
            "doctor-registration-form"
        );

    const patientTab =
        document.getElementById(
            "patient-registration-tab"
        );

    const doctorTab =
        document.getElementById(
            "doctor-registration-tab"
        );


    if (type === "patient") {

        patientForm.classList.remove("hidden");
        doctorForm.classList.add("hidden");

        patientTab.classList.add("active-tab");
        doctorTab.classList.remove("active-tab");

    } else {

        patientForm.classList.add("hidden");
        doctorForm.classList.remove("hidden");

        patientTab.classList.remove("active-tab");
        doctorTab.classList.add("active-tab");
    }
}


// =========================================================
// MESSAGE DISPLAY
// =========================================================

function showMessage(elementId, message, type) {

    const element =
        document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = message;

    element.className = "message " + type;
}


function clearMessage(elementId) {

    const element =
        document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.textContent = "";
    element.className = "message";
}


// =========================================================
// NAVIGATION
// =========================================================

function updateNavigation(isLoggedIn) {

    const navigation =
        document.getElementById(
            "main-navigation"
        );

    if (!navigation) {
        return;
    }


    if (isLoggedIn) {

        navigation.innerHTML = "";

    } else {

        navigation.innerHTML = `
            <button type="button" onclick="showHome()">
                Home
            </button>

            <button type="button" onclick="showLogin()">
                Login
            </button>

            <button type="button" onclick="showRegistration()">
                Register
            </button>
        `;
    }
}


// =========================================================
// LOGIN
// =========================================================

async function loginUser(event) {

    event.preventDefault();

    clearMessage("login-message");


    const email =
        document.getElementById(
            "login-email"
        ).value.trim();

    const password =
        document.getElementById(
            "login-password"
        ).value;


    if (!email || !password) {

        showMessage(
            "login-message",
            "Please enter your email and password.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/auth/login",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            showMessage(
                "login-message",
                data.message ||
                    "Login failed. Please check your details.",
                "error"
            );

            return;
        }


        currentUser = data.user;


        localStorage.setItem(
            "careline_user",
            JSON.stringify(currentUser)
        );


        document.getElementById(
            "login-form"
        ).reset();


        showDashboard(currentUser);

    } catch (error) {

        console.error(
            "Login error:",
            error
        );

        showMessage(
            "login-message",
            "Unable to connect to the CareLine server.",
            "error"
        );
    }
}


// =========================================================
// SHOW CORRECT DASHBOARD
// =========================================================

function showDashboard(user) {

    hideAllSections();

    updateNavigation(true);


    if (user.role === "patient") {

        document
            .getElementById("patient-dashboard")
            .classList.add("active-section");


        const welcome =
            document.getElementById(
                "patient-welcome"
            );

        if (welcome) {

            welcome.textContent =
                "Welcome, " +
                user.full_name +
                "!";
        }


        hidePatientAreas();


    } else if (user.role === "doctor") {

        document
            .getElementById("doctor-dashboard")
            .classList.add("active-section");


        const welcome =
            document.getElementById(
                "doctor-welcome"
            );

        if (welcome) {

            welcome.textContent =
                "Welcome, Dr. " +
                user.full_name +
                "!";
        }


        hideDoctorAreas();


    } else if (user.role === "admin") {

        document
            .getElementById("admin-dashboard")
            .classList.add("active-section");

    } else {

        showHome();
    }
}


// =========================================================
// PATIENT AREA CONTROL
// =========================================================

function hidePatientAreas() {

    const areas = [
        "patient-doctors-area",
        "patient-appointments-area",
        "patient-records-area",
        "patient-consultations-area",
        "patient-chat-area"
    ];


    areas.forEach(function (id) {

        const area =
            document.getElementById(id);

        if (area) {
            area.classList.add("hidden");
        }
    });
}


function showPatientArea(id) {

    hidePatientAreas();

    const area =
        document.getElementById(id);

    if (area) {
        area.classList.remove("hidden");
    }
}


// =========================================================
// DOCTOR AREA CONTROL
// =========================================================

function hideDoctorAreas() {

    const areas = [
        "doctor-appointments-area",
        "doctor-profile-area",
        "doctor-patient-area"
    ];


    areas.forEach(function (id) {

        const area =
            document.getElementById(id);

        if (area) {
            area.classList.add("hidden");
        }
    });
}


function showDoctorArea(id) {

    hideDoctorAreas();

    const area =
        document.getElementById(id);

    if (area) {
        area.classList.remove("hidden");
    }
}


// =========================================================
// LOGOUT
// =========================================================

function logout() {

    currentUser = null;

    localStorage.removeItem(
        "careline_user"
    );


    hideAllSections();

    document
        .getElementById("home-section")
        .classList.add("active-section");


    updateNavigation(false);
}


// =========================================================
// FORGOT PASSWORD
// =========================================================

async function requestPasswordReset(event) {

    event.preventDefault();

    clearMessage("forgot-message");


    const email =
        document.getElementById(
            "forgot-email"
        ).value.trim();


    if (!email) {

        showMessage(
            "forgot-message",
            "Please enter your email address.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/auth/forgot-password",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    email: email
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            showMessage(
                "forgot-message",
                data.message ||
                    "Password reset request failed.",
                "error"
            );

            return;
        }


        showMessage(
            "forgot-message",
            data.message ||
                "Password reset request submitted successfully.",
            "success"
        );


        document.getElementById(
            "forgot-password-form"
        ).reset();


    } catch (error) {

        console.error(
            "Forgot password error:",
            error
        );

        showMessage(
            "forgot-message",
            "Unable to connect to the CareLine server.",
            "error"
        );
    }
}


// =========================================================
// PATIENT REGISTRATION
// =========================================================

async function registerPatient(event) {

    event.preventDefault();

    clearMessage("registration-message");


    const data = {

        full_name:
            document.getElementById(
                "patient-name"
            ).value.trim(),

        email:
            document.getElementById(
                "patient-email"
            ).value.trim(),

        phone:
            document.getElementById(
                "patient-phone"
            ).value.trim(),

        password:
            document.getElementById(
                "patient-password"
            ).value,

        date_of_birth:
            document.getElementById(
                "patient-dob"
            ).value || null,

        gender:
            document.getElementById(
                "patient-gender"
            ).value || null,

        address:
            document.getElementById(
                "patient-address"
            ).value.trim(),

        blood_group:
            document.getElementById(
                "patient-blood-group"
            ).value || null,

        emergency_contact:
            document.getElementById(
                "patient-emergency"
            ).value.trim()
    };


    if (
        !data.full_name ||
        !data.email ||
        !data.phone ||
        !data.password
    ) {

        showMessage(
            "registration-message",
            "Please fill in all required patient fields.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/auth/register/patient",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        const result =
            await response.json();


        if (!response.ok || !result.success) {

            showMessage(
                "registration-message",
                result.message ||
                    "Patient registration failed.",
                "error"
            );

            return;
        }


        showMessage(
            "registration-message",
            "Patient registration successful. You can now login.",
            "success"
        );


        document
            .getElementById(
                "patient-registration-form"
            )
            .reset();


        setTimeout(function () {

            showLogin();

        }, 1500);


    } catch (error) {

        console.error(
            "Patient registration error:",
            error
        );

        showMessage(
            "registration-message",
            "Unable to connect to the CareLine server.",
            "error"
        );
    }
}


// =========================================================
// DOCTOR REGISTRATION
// =========================================================

async function registerDoctor(event) {

    event.preventDefault();

    clearMessage("registration-message");


    const data = {

        full_name:
            document.getElementById(
                "doctor-name"
            ).value.trim(),

        email:
            document.getElementById(
                "doctor-email"
            ).value.trim(),

        phone:
            document.getElementById(
                "doctor-phone"
            ).value.trim(),

        password:
            document.getElementById(
                "doctor-password"
            ).value,

        specialization:
            document.getElementById(
                "doctor-specialization"
            ).value.trim(),

        qualification:
            document.getElementById(
                "doctor-qualification"
            ).value.trim(),

        experience:
            document.getElementById(
                "doctor-experience"
            ).value || 0,

        license_number:
            document.getElementById(
                "doctor-license"
            ).value.trim(),

        consultation_fee:
            document.getElementById(
                "doctor-fee"
            ).value || 0,

        about:
            document.getElementById(
                "doctor-about"
            ).value.trim()
    };


    if (
        !data.full_name ||
        !data.email ||
        !data.phone ||
        !data.password ||
        !data.specialization ||
        !data.qualification ||
        !data.license_number
    ) {

        showMessage(
            "registration-message",
            "Please fill in all required doctor fields.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/api/auth/register/doctor",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        const result =
            await response.json();


        if (!response.ok || !result.success) {

            showMessage(
                "registration-message",
                result.message ||
                    "Doctor registration failed.",
                "error"
            );

            return;
        }


        showMessage(
            "registration-message",
            "Doctor registration submitted. Please wait for admin approval.",
            "success"
        );


        document
            .getElementById(
                "doctor-registration-form"
            )
            .reset();


    } catch (error) {

        console.error(
            "Doctor registration error:",
            error
        );

        showMessage(
            "registration-message",
            "Unable to connect to the CareLine server.",
            "error"
        );
    }
}


// =========================================================
// RESTORE LOGIN SESSION
// =========================================================

function restoreUserSession() {

    const savedUser =
        localStorage.getItem(
            "careline_user"
        );


    if (!savedUser) {
        return;
    }


    try {

        currentUser =
            JSON.parse(savedUser);


        if (
            currentUser &&
            currentUser.id &&
            currentUser.role
        ) {

            showDashboard(
                currentUser
            );
        }

    } catch (error) {

        console.error(
            "Session restore error:",
            error
        );

        localStorage.removeItem(
            "careline_user"
        );
    }
}


// =========================================================
// EVENT LISTENERS
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const loginForm =
            document.getElementById(
                "login-form"
            );

        if (loginForm) {

            loginForm.addEventListener(
                "submit",
                loginUser
            );
        }


        const patientForm =
            document.getElementById(
                "patient-registration-form"
            );

        if (patientForm) {

            patientForm.addEventListener(
                "submit",
                registerPatient
            );
        }


        const doctorForm =
            document.getElementById(
                "doctor-registration-form"
            );

        if (doctorForm) {

            doctorForm.addEventListener(
                "submit",
                registerDoctor
            );
        }


        const forgotForm =
            document.getElementById(
                "forgot-password-form"
            );

        if (forgotForm) {

            forgotForm.addEventListener(
                "submit",
                requestPasswordReset
            );
        }


        restoreUserSession();
    }
);