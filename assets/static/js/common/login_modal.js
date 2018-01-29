/*
    Handles JS for login modal, including login, sign-up and forgot password
 */
(function() {
    var t = klp.login_modal = {};
    var postLoginCallback = null;
    t.open = function(callback) {
        postLoginCallback = callback;
        klp.openModal = t;
        $('#signupModalTrigger').click();
    };

    t.close = function() {
        //showSignup();
        $('.closeLightBox').click();
        console.log("login modal close called");
    };

    t.afterClose = function() {
        klp.utils.clearForm('signupForm');
        klp.utils.clearForm('loginForm');
        klp.utils.clearForm('forgotPasswordForm');
        klp.utils.clearForm('otpForm');
        postLoginCallback = null;
    };

    t.init = function() {
        $('#signupModalTrigger').rbox({
            'type': 'inline',
            inline: '#loginModalTemplate',
            onopen: initModal,
            onclose: t.afterClose
        });

    };

    function initModal() {
        $('#signupForm').submit(submitSignup);
        $('#signupFormSubmit').click(function(e) {
            e.preventDefault();
            $('#signupForm').submit();
        });

        $('#loginForm').submit(submitLogin);
        $('#loginFormSubmit').click(function(e) {
            e.preventDefault();
            $('#loginForm').submit();
        });

        $('#forgotPasswordForm').submit(submitForgotPassword);
        $('#forgotPasswordFormSubmit').click(function(e) {
            e.preventDefault();
            $('#forgotPasswordForm').submit();
        });

        $('#signupOtpForm').submit(submitSignupOtp);
        $('#signupOtpFormSubmit').click(function(e) {
            e.preventDefault();
            $('#signupOtpForm').submit();
        });

        $('.js-showLogin').click(showLogin);
        $('.js-showSignup').click(showSignup);
        $('.js-showForgotPassword').click(showForgotPassword);

        showLogin();
    }

    function showSignup(e) {
        if (e) {
            e.preventDefault();
        }
        $('#loginContainer').hide();
        $('#forgotPasswordContainer').hide();
        $('#signupOtpContainer').hide();
        $('#signupContainer').show();

    }

    function showSignupOTP(e, userData) {
        if (e) {
            e.preventDefault();
        }

        if(userData && userData.mobile_no) {
            $('#signupOtpMobile').val(userData.mobile_no);
        }

        $('#loginContainer').hide();
        $('#forgotPasswordContainer').hide();
        $('#signupContainer').hide();
        $('#signupOtpContainer').show();
    }

    function showForgotPassword(e) {
        if (e) {
            e.preventDefault();
        }
        $('#loginContainer').hide();
        $('#signupContainer').hide();
        $('#signupOtpContainer').hide();
        $('#forgotPasswordContainer').show();
    }

    function showLogin(e, showOtpSuccessMessage) {
        if (e) {
            e.preventDefault();
        }

        if(showOtpSuccessMessage) {
            $('#loginOtpVerifiedMessage').show();
        } else {
            $('#loginOtpVerifiedMessage').hide();
        }

        $('#signupContainer').hide();
        $('#signupOtpContainer').hide();
        $('#forgotPasswordContainer').hide();
        $('#loginContainer').show();
    }

    function submitSignup(e) {
        if (e) {
            e.preventDefault();
        }
        var formID = 'signupForm';
        klp.utils.clearValidationErrors(formID);
        var isValid = klp.utils.validateRequired(formID);
        if (isValid) {
            var fields = {
                'first_name': $('#signupFirstName'),
                'last_name': $('#signupLastName'),
                'mobile_no': $('#signupPhone'),
                'email': $('#signupEmail'),
                'password': $('#signupPassword'),
                'opted_email': $('#signupOptedEmail')
            };
            var data = klp.utils.getFormData(fields);

            klp.utils.startSubmit(formID);
            var signupXHR = klp.api.signup(data);

            signupXHR.done(function(userData) {
                klp.utils.stopSubmit(formID);

                // TODO: Remove the below block after exotel API is integrated
                alert('Hey, I can\'t send an OTP sms at the moment. So here is your OTP -\n\n' + userData.sms_verification_pin + '\n\nEnter this OTP at the next screen.');

                showSignupOTP(null, userData);
            });

            signupXHR.fail(function(err) {
                //FIXME: deal with errors
                // console.log("signup error", err);
                klp.utils.stopSubmit(formID);
                var errors = JSON.parse(err.responseText);
                if ('detail' in errors && errors.detail === 'duplicate email') {
                    var $field = fields.email;
                    klp.utils.invalidateField($field, "This email address already exists.");
                } else {
                    klp.utils.invalidateErrors(fields, errors);
                }
                //alert("error signing up");
            });
        }
    }

    function submitLogin(e) {
        if (e) {
            e.preventDefault();
        }
        var formID = 'loginForm';
        klp.utils.clearValidationErrors(formID);
        var isValid = klp.utils.validateRequired('loginForm');
        if (isValid) {
            var data = {
                'username': $('#loginUsername').val(),
                'password': $('#loginPassword').val()
            };
            var loginXHR = klp.api.login(data);
            klp.utils.startSubmit(formID);
            loginXHR.done(function(userData) {
                klp.utils.stopSubmit(formID);
                userData.email = data.email;
                klp.auth.loginUser(userData);
                klp.utils.alertMessage("Logged in successfully!", "success");
                if (postLoginCallback) {
                    postLoginCallback();
                }
                t.close();
                //console.log("login done", postLoginCallback);

            });

            loginXHR.fail(function(err) {
                // console.log("login error", err);
                klp.utils.stopSubmit(formID);
                var errors = JSON.parse(err.responseText);
                var $field = $('#loginPassword');
                if (errors.detail || errors.non_field_errors) {
                    klp.utils.invalidateField($field, "Invalid mobile/email/password");
                } else {
                    klp.utils.alertMessage("Login failed due to unknown error. Please contact us if this happens again.", "error");
                }
            });
        }
    }

    function submitForgotPassword(e) {
        if (e) {
            e.preventDefault();
        }
        var formID = 'forgotPasswordForm';

        klp.utils.clearValidationErrors(formID);
        var isValid = klp.utils.validateRequired(formID);
        if (isValid) {
            var data = {
                'email': $('#forgotPasswordEmail').val()
            };
            var url = 'password-reset/request';
            var $xhr = klp.api.do(url, data, 'POST');
            klp.utils.startSubmit(formID);
            $xhr.done(function() {
                klp.utils.stopSubmit(formID);
                klp.utils.alertMessage("Please check your email for password reset instructions", "success");
                t.close();
            });
            $xhr.fail(function(err) {
                klp.utils.stopSubmit(formID);
                var errorJSON = JSON.parse(err.responseText);
                if (errorJSON.detail) {
                    klp.utils.invalidateField($('#forgotPasswordEmail'), errorJSON.detail);

                }
                //klp.utils.alertMessage("Invalid email address", "error");
            });
        }
    }


    function submitSignupOtp(e) {
        if (e) {
            e.preventDefault();
        }
        var formID = 'signupOtpForm';

        klp.utils.clearValidationErrors(formID);
        var isValid = klp.utils.validateRequired(formID);
        if (isValid) {
            var data = {
                'mobile_no': $('#signupOtpMobile').val(),
                'otp': $('#signupOtp').val()
            };
            var url = 'users/otp-update/';
            var $xhr = klp.api.do(url, data, 'POST');
            klp.utils.startSubmit(formID);
            $xhr.done(function() {
                klp.utils.stopSubmit(formID);
                klp.utils.alertMessage("Your mobile number has been verified successfully. Please proceed to login", "success");
                showLogin(null, true);
            });
            $xhr.fail(function(err) {
                klp.utils.stopSubmit(formID);
                var errorJSON = JSON.parse(err.responseText);
                if (errorJSON.detail) {
                    klp.utils.invalidateField($('#signupOtp'), errorJSON.detail);
                } else {
                    klp.utils.alertMessage("We are not able to verify your number do to an unknown error. Please contact us if this happens again.", "error");
                }
            });
        }
    }


})();
